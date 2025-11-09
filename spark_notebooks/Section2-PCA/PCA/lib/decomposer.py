import numpy as np
import pandas as pd
import warnings
from typing import Any, Dict, Iterable

try:  # Optional Dask support
    import dask.dataframe as dd  # type: ignore
except ImportError:  # pragma: no cover - dask not installed
    dd = None

from lib.numpy_pack import packArray, unpackArray  # kept for backwards compatibility

try:  # pragma: no cover - optional Spark support
    from pyspark.sql import Row as _SparkRow  # type: ignore
except ImportError:
    _SparkRow = None


class SimpleRow(dict):
    """Lightweight Row replacement for environments without pyspark."""

    def asDict(self) -> Dict[str, Any]:
        return dict(self)

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - attribute passthrough
        try:
            return self[item]
        except KeyError as exc:  # pragma: no cover - keep original behaviour
            raise AttributeError(item) from exc


Row = _SparkRow or SimpleRow  # expose Row symbol for legacy callers


class Eigen_decomp:
    """Approximate a function with an orthonormal set of functions."""

    def __init__(self, x, f, mean, U):
        self.U = U
        self.x = x
        self.mean = mean
        self.f = f
        self.startup_flag = True
        self.C = np.dot(np.nan_to_num(f - mean), self.U)
        self.C = np.array(self.C).flatten()
        self.m, self.n = np.shape(self.U)
        self.coeff = {f"c{i}": self.C[i] for i in range(self.C.shape[0])}

    def compute_var_explained(self):
        """Return variance explained statistics for the decomposition."""

        def compute_var(vector):
            v = np.array(np.nan_to_num(vector), dtype=np.float64)
            return np.dot(v, v)

        k = self.U.shape[1]
        residual_var = np.zeros(k + 1)
        residual = self.f
        total_energy = compute_var(residual)
        residual = residual - self.mean
        residual_var[0] = compute_var(residual)

        for i in range(k):
            g = self.U[:, i] * self.coeff[f"c{i}"]
            g = np.array(g).flatten()
            residual = residual - g
            residual_var[i + 1] = compute_var(residual)

        _residuals = residual_var / residual_var[0]
        _residuals[0] = residual_var[0] / total_energy

        return (
            ("total_energy", total_energy),
            ("fraction residual var after mean, eig1,eig2,...", _residuals),
            ("eigen-vector coefficients", self.coeff),
        )


def _row_to_dict(row: Any) -> Dict[str, Any]:
    if row is None:
        raise ValueError("row cannot be None")
    if isinstance(row, dict):
        return dict(row)
    if isinstance(row, pd.Series):
        return row.to_dict()
    if hasattr(row, "asDict"):
        return row.asDict()
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    raise TypeError(f"Unsupported row type: {type(row)!r}")


def _extract_series(values: Any, value_dtype=np.float16) -> np.ndarray:
    if isinstance(values, (bytes, bytearray, memoryview)):
        return np.array(unpackArray(values, value_dtype), dtype=np.float64)
    return np.array(values, dtype=np.float64)


def _decompose_record(
    row_dict: Dict[str, Any],
    EigVec: np.ndarray,
    Mean: np.ndarray,
    values_column: str,
    value_dtype=np.float16,
) -> Dict[str, Any]:
    if values_column not in row_dict:
        raise KeyError(f"Column '{values_column}' not found in row")
    series = _extract_series(row_dict[values_column], value_dtype)
    recon = Eigen_decomp(None, series, Mean, EigVec)
    total_var, residuals, coeff = recon.compute_var_explained()

    result = dict(row_dict)
    result["total_var"] = float(total_var[1])
    result["res_mean"] = float(residuals[1][0])
    for i in range(1, residuals[1].shape[0]):
        result[f"res_{i}"] = float(residuals[1][i])
        result[f"coeff_{i}"] = float(coeff[1][f"c{i-1}"])
    return result


def _build_meta(existing: pd.Series, EigVec: np.ndarray) -> pd.DataFrame:
    meta_types: Dict[str, Any] = {col: dtype for col, dtype in existing.items()}
    meta_types["total_var"] = np.float64
    meta_types["res_mean"] = np.float64
    for i in range(1, EigVec.shape[1] + 1):
        meta_types[f"res_{i}"] = np.float64
        meta_types[f"coeff_{i}"] = np.float64
    return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in meta_types.items()})


def _partition_decompose(
    pdf: pd.DataFrame,
    EigVec: np.ndarray,
    Mean: np.ndarray,
    values_column: str,
    value_dtype,
    meta_template: pd.DataFrame,
) -> pd.DataFrame:
    if pdf.empty:
        return meta_template.copy()

    records = [
        _decompose_record(row.to_dict(), EigVec, Mean, values_column, value_dtype)
        for _, row in pdf.iterrows()
    ]
    result = pd.DataFrame(records)
    missing_cols = [col for col in meta_template.columns if col not in result.columns]
    for col in missing_cols:
        result[col] = pd.Series(dtype=meta_template[col].dtype)
    result = result[meta_template.columns]
    for col, dtype in meta_template.dtypes.items():
        try:
            result[col] = result[col].astype(dtype, copy=False)
        except Exception:  # pragma: no cover - dtype conversion best effort
            pass
    return result


def decompose_dataframe(*args, **kwargs):
    """Run the eigen decomposition across a pandas or Dask dataframe.

    Legacy signature ``decompose_dataframe(sqlContext, df, EigVec, Mean)`` is
    supported for backwards compatibility—the ``sqlContext`` argument is
    ignored. The modern interface is ``decompose_dataframe(df, EigVec, Mean, ...)``.
    """

    if len(args) == 4:
        warnings.warn(
            "Passing sqlContext as the first argument is deprecated. "
            "Call decompose_dataframe(df, EigVec, Mean) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        _, df, EigVec, Mean = args
    elif len(args) == 3:
        df, EigVec, Mean = args
    else:
        raise TypeError("decompose_dataframe expects 3 or 4 positional arguments")

    values_column = kwargs.pop("values_column", "Values")
    value_dtype = kwargs.pop("value_dtype", np.float16)
    if kwargs:
        raise TypeError(f"Unexpected keyword arguments: {list(kwargs.keys())}")

    if dd is not None and isinstance(df, dd.DataFrame):
        meta_template = _build_meta(df._meta.dtypes, EigVec)
        return df.map_partitions(
            _partition_decompose,
            EigVec,
            Mean,
            values_column,
            value_dtype,
            meta_template,
            meta=meta_template,
        )

    if isinstance(df, pd.DataFrame):
        meta_template = _build_meta(df.dtypes, EigVec)
        return _partition_decompose(
            df,
            EigVec,
            Mean,
            values_column,
            value_dtype,
            meta_template,
        )

    if isinstance(df, Iterable):
        return [
            _decompose_record(_row_to_dict(row), EigVec, Mean, values_column, value_dtype)
            for row in df
        ]

    raise TypeError(
        "Unsupported dataframe type. Provide a pandas or Dask dataframe (or iterable of rows)."
    )

