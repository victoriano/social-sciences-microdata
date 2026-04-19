#!/usr/bin/env python3
"""Merge CIS Barómetro .sav files into a single labeled CSV.

For every Barómetro whose ``codigo`` falls in the requested date range, this
pipeline reads the ``{codigo}.sav`` file, swaps codes for their value labels,
renames columns to their variable labels and appends rows to one CSV. An
optional post-processing step drops columns whose share of missing values
exceeds a configurable threshold.
"""

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

from Spain.barometro_cis.config import INDEX_FILE, INTERIM_DIR, RAW_DIR
from Spain.barometro_cis.utils.spss_reader import deduplicate_columns, read_sav_with_labels


def filter_studies_by_date(index_file: Path, start_month: str, end_month: str) -> pd.DataFrame:
    df = pd.read_csv(index_file)
    df["fecha"] = pd.to_datetime(df["fecha"])

    start_date = datetime.strptime(start_month, "%m/%Y")
    end_date = datetime.strptime(end_month, "%m/%Y") + relativedelta(months=1) - relativedelta(days=1)

    return df[(df["fecha"] >= start_date) & (df["fecha"] <= end_date)]


def merge_sav_files(codes, raw_dir: Path, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    first = True

    for code in codes:
        sav_path = raw_dir / f"MD{code}" / f"{code}.sav"
        if not sav_path.exists():
            print(f"⚠️  Missing SAV file {sav_path}, skipping")
            continue

        print(f"📄 Processing {sav_path.name}")
        df = read_sav_with_labels(sav_path)
        df = deduplicate_columns(df)
        # Every value lands in the CSV as a string to preserve the labels
        # introduced by ``read_sav_with_labels``.
        df = df.astype(str)

        if first:
            df.to_csv(output_file, index=False, mode="w")
            first = False
        else:
            existing = pd.read_csv(output_file, dtype=object, low_memory=False)
            merged = pd.concat([existing, df], axis=0, ignore_index=True)
            merged.to_csv(output_file, index=False, mode="w")

        print(f"✅ Merged MD{code} into {output_file.name}")


def filter_columns_with_nans(input_file: Path, output_file: Path, threshold: float) -> None:
    df = pd.read_csv(input_file, dtype=object, low_memory=False)
    nan_share = df.isnull().mean()
    kept = nan_share[nan_share < threshold].index.tolist()
    df[kept].to_csv(output_file, index=False)
    print(f"✅ Filtered columns (<{threshold:.0%} nulls) saved to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge CIS Barómetro .sav files into a CSV")
    parser.add_argument("--start", required=True, help="Start month in MM/YYYY format")
    parser.add_argument("--end", required=True, help="End month in MM/YYYY format")
    parser.add_argument("--index", type=Path, default=INDEX_FILE, help="Catalogue CSV")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Directory with raw SAV files")
    parser.add_argument(
        "--output",
        type=Path,
        default=INTERIM_DIR / "merged_barometros.csv",
        help="Output merged CSV file",
    )
    parser.add_argument(
        "--filter-nans",
        action="store_true",
        help="Produce an additional CSV dropping columns with too many nulls",
    )
    parser.add_argument(
        "--nan-threshold",
        type=float,
        default=0.5,
        help="Column-wise null share above which the column is dropped (default: 0.5)",
    )
    args = parser.parse_args()

    filtered = filter_studies_by_date(args.index, args.start, args.end)
    print(f"📊 {len(filtered)} Barómetros in range {args.start} → {args.end}")

    merge_sav_files(filtered["codigo"], args.raw_dir, args.output)

    if args.filter_nans:
        filtered_path = args.output.with_name(f"filtered_{args.output.name}")
        filter_columns_with_nans(args.output, filtered_path, args.nan_threshold)


if __name__ == "__main__":
    main()
