import numpy as np
import pandas as pd
from typing import Dict, Iterable, Tuple

from lib.numpy_pack import unpackArray

try:  # optional Dask support
    import dask.dataframe as dd  # type: ignore
except ImportError:  # pragma: no cover
    dd = None


ArraySummary = Dict[str, np.ndarray]


def _decode_values(series: Iterable, dtype=np.float16) -> np.ndarray:
    arrays = [unpackArray(val, dtype).astype(np.float64) for val in series]
    if not arrays:
        return np.empty((0, 0), dtype=np.float64)
    return np.vstack(arrays)


def _partition_summary(pdf: pd.DataFrame, values_column: str, dtype) -> pd.DataFrame:
    arrays = _decode_values(pdf[values_column], dtype)
    if arrays.size == 0:
        return pd.DataFrame(
            columns=[
                "sum_values",
                "count_values",
                "outer_sum",
                "outer_count",
                "nan_counts",
                "value_sample",
            ]
        )

    mask = ~np.isnan(arrays)
    filled = np.nan_to_num(arrays, nan=0.0)

    sum_values = np.nansum(arrays, axis=0)
    count_values = mask.sum(axis=0)

    mask_float = mask.astype(np.float64)
    outer_sum = filled.T @ filled
    outer_count = mask_float.T @ mask_float

    nan_counts = np.isnan(arrays).sum(axis=1)
    sample = filled[mask]
    if sample.size > 5000:
        sample = np.random.default_rng(0).choice(sample, size=5000, replace=False)

    return pd.DataFrame(
        {
            "sum_values": [sum_values],
            "count_values": [count_values],
            "outer_sum": [outer_sum],
            "outer_count": [outer_count],
            "nan_counts": [nan_counts],
            "value_sample": [sample],
        }
    )


def _combine_summaries(summaries: pd.DataFrame) -> ArraySummary:
    if summaries.empty:
        raise ValueError("No data available to compute statistics")

    sum_values = np.sum(np.stack(summaries["sum_values"]), axis=0)
    count_values = np.sum(np.stack(summaries["count_values"]), axis=0)
    outer_sum = np.sum(np.stack(summaries["outer_sum"]), axis=0)
    outer_count = np.sum(np.stack(summaries["outer_count"]), axis=0)
    nan_counts = np.concatenate(summaries["nan_counts"].to_list())
    value_sample = np.concatenate(summaries["value_sample"].to_list())

    return {
        "sum_values": sum_values,
        "count_values": count_values,
        "outer_sum": outer_sum,
        "outer_count": outer_count,
        "nan_counts": nan_counts,
        "value_sample": value_sample,
    }


def compute_statistics(frame, values_column="Values", dtype=np.float16) -> ArraySummary:
    if dd is not None and isinstance(frame, dd.DataFrame):
        meta = pd.DataFrame(
            {
                "sum_values": pd.Series(dtype="object"),
                "count_values": pd.Series(dtype="object"),
                "outer_sum": pd.Series(dtype="object"),
                "outer_count": pd.Series(dtype="object"),
                "nan_counts": pd.Series(dtype="object"),
                "value_sample": pd.Series(dtype="object"),
            }
        )
        summaries = frame.map_partitions(
            _partition_summary,
            values_column,
            dtype,
            meta=meta,
        ).compute()
    elif isinstance(frame, pd.DataFrame):
        summaries = _partition_summary(frame, values_column, dtype)
    else:
        raise TypeError("Frame must be a pandas or Dask dataframe")

    return _combine_summaries(summaries)


def covariance_from_summary(summary: ArraySummary) -> Tuple[np.ndarray, np.ndarray]:
    sum_values = summary["sum_values"]
    count_values = summary["count_values"]
    outer_sum = summary["outer_sum"]
    outer_count = summary["outer_count"]

    mean = np.divide(sum_values, count_values, out=np.zeros_like(sum_values), where=count_values > 0)

    with np.errstate(invalid="ignore"):
        cov = np.divide(outer_sum, outer_count, out=np.zeros_like(outer_sum), where=outer_count > 0)
    cov = cov - np.outer(mean, mean)
    cov = np.nan_to_num(cov)

    eigval, eigvec = np.linalg.eigh(cov)
    idx = np.argsort(eigval)[::-1]
    eigval = eigval[idx]
    eigvec = eigvec[:, idx]

    return mean, (eigval, eigvec)
