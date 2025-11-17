#!/usr/bin/env python3
"""
Convert all CSV files in ~/flight_data into individual Parquet files.

The script streams the CSVs in manageable chunks, so it can be run on
machines with limited RAM.  Each CSV is converted to a Parquet file with
the same stem in the target directory (default: ~/flight_data).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

NULLABLE_INT_COLUMNS = {"CRS_DEP_TIME", "CRS_ARR_TIME"}


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert flight CSV files into a Parquet dataset."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path.home() / "flight_data",
        help="Directory containing the flight CSV files (default: %(default)s)",
    )
    parser.add_argument(
        "--pattern",
        default="*.csv",
        help="Glob pattern to match CSV files (relative to --input-dir).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "flight_data",
        help="Directory where the Parquet files will be written (default: %(default)s)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=250_000,
        help="Number of rows to load per chunk when reading CSVs.",
    )
    return parser.parse_args(argv)


def find_csv_files(input_dir: Path, pattern: str) -> list[Path]:
    files = sorted(input_dir.glob(pattern))
    return [path for path in files if path.is_file()]


def check_headers(csv_files: Iterable[Path]) -> tuple[list[str], dict[str, dict[str, list[str] | bool]]]:
    reference_columns: list[str] | None = None
    mismatches: dict[str, dict[str, list[str] | bool]] = {}

    for csv_path in csv_files:
        columns = list(pd.read_csv(csv_path, nrows=0).columns)
        if reference_columns is None:
            reference_columns = columns
            continue

        ref_set = set(reference_columns)
        cur_set = set(columns)
        missing = sorted(ref_set - cur_set)
        extra = sorted(cur_set - ref_set)
        order_diff = columns != reference_columns

        if missing or extra or order_diff:
            mismatches[csv_path.name] = {
                "missing": missing,
                "extra": extra,
                "order_mismatch": order_diff and not (missing or extra),
            }

    if reference_columns is None:
        raise FileNotFoundError("No CSV files were found to inspect.")

    return reference_columns, mismatches


def convert_csvs_to_parquet(
    csv_files: Iterable[Path],
    output_dir: Path,
    chunksize: int,
) -> None:
    if not csv_files:
        raise FileNotFoundError("No CSV files were found to convert.")

    output_dir.mkdir(parents=True, exist_ok=True)

    for csv_path in csv_files:
        output_path = output_dir / f"{csv_path.stem}.parquet"
        if output_path.exists():
            output_path.unlink()

    writer: Optional[pq.ParquetWriter] = None
    total_rows = 0

    try:
            for chunk in pd.read_csv(csv_path, chunksize=chunksize):
                for column in NULLABLE_INT_COLUMNS:
                    if column in chunk.columns:
                        chunk[column] = pd.to_numeric(chunk[column], errors="coerce").astype("Int64")

                table = pa.Table.from_pandas(chunk, preserve_index=False)
                if writer is None:
                    writer = pq.ParquetWriter(output_path, table.schema)
                writer.write_table(table)
                total_rows += len(chunk)
    finally:
        if writer is not None:
            writer.close()

        if writer is None:
            empty_df = pd.read_csv(csv_path, nrows=0)
            empty_table = pa.Table.from_pandas(empty_df, preserve_index=False)
            pq.write_table(empty_table, output_path)
            print(f"{csv_path.name}: wrote empty Parquet file to {output_path}")
        else:
            print(f"{csv_path.name}: wrote {total_rows} rows to {output_path}")


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)

    csv_files = find_csv_files(args.input_dir, args.pattern)
    if not csv_files:
        print(f"No CSV files found in {args.input_dir} matching {args.pattern}", file=sys.stderr)
        return 1

    try:
        reference_columns, mismatches = check_headers(csv_files)
    except Exception as exc:  # pragma: no cover
        print(f"Unable to inspect CSV headers: {exc}", file=sys.stderr)
        return 1

    if mismatches:
        print("Header mismatches detected:")
        for filename, details in mismatches.items():
            missing = details["missing"]
            extra = details["extra"]
            order_mismatch = details["order_mismatch"]

            print(f"- {filename}:")
            if missing:
                print(f"    missing columns: {', '.join(missing)}")
            if extra:
                print(f"    unexpected columns: {', '.join(extra)}")
            if order_mismatch:
                print("    column order differs from the reference file.")

        print("Fix the header differences before converting to Parquet.")
        return 1

    try:
        convert_csvs_to_parquet(csv_files, args.output_dir, args.chunksize)
    except Exception as exc:  # pragma: no cover
        print(f"Error while converting CSV files: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

