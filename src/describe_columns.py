"""Describe columns in a CSV: unique values and counts.

Usage:
    python src/describe_columns.py \
        --csv data/raw/coupons.csv \
        --max-values 10

Outputs a human-readable summary to stdout.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

import pandas as pd


def describe_columns(csv_path: str, max_values: int = 10, show_na: bool = True) -> None:
    """Read CSV and print per-column summaries.

    Args:
        csv_path: path to CSV file
        max_values: maximum number of unique values to display per column
        show_na: whether to include NaN counts in value breakdowns
    """
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        print(f"Error reading CSV '{csv_path}': {e}", file=sys.stderr)
        raise

    total_rows = len(df)
    print(f"File: {csv_path}\nRows: {total_rows}\nColumns: {len(df.columns)}\n")

    for col in df.columns:
        series = df[col]
        non_null = series.notna().sum()
        unique_count = series.nunique(dropna=not show_na)
        dtype = series.dtype

        print(f"Column: {col}")
        print(f"  - dtype: {dtype}")
        print(f"  - non-null: {non_null} ({non_null/total_rows:.2%})")
        print(f"  - unique values: {unique_count}")

        # Show value counts (include NaN optionally)
        try:
            vc = series.value_counts(dropna=not show_na)
        except Exception:
            # fallback for unhashable types
            vc = pd.Series(dtype="int64")

        if unique_count == 0:
            print("  - NOTE: column contains no values")
        elif unique_count <= max_values:
            # show all
            for val, cnt in vc.items():
                display_val = repr(val)
                print(f"    {display_val}: {cnt}")
        else:
            # show top N
            print(f"  - Top {max_values} values:")
            for val, cnt in vc.head(max_values).items():
                display_val = repr(val)
                print(f"    {display_val}: {cnt}")
            # show sample of other unique values (non-exhaustive)
            remaining = unique_count - max_values
            print(f"  - ...and {remaining} more unique values (not shown)")

        print("")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Describe columns in a CSV file with unique value counts")
    p.add_argument("--csv", default="data/raw/coupons.csv", help="Path to CSV file")
    p.add_argument("--max-values", type=int, default=10, help="Max unique values to display per column")
    p.add_argument("--no-na", dest="show_na", action="store_false", help="Do not include NaN in value counts")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    describe_columns(args.csv, max_values=args.max_values, show_na=args.show_na)


if __name__ == "__main__":
    main()
