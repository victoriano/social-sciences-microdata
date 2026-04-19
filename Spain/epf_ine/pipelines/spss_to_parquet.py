#!/usr/bin/env python3
"""Convert EPF .sav files to labeled CSV or Parquet, one sub-folder per year."""

import argparse
from pathlib import Path

import pyreadstat

from Spain.epf_ine.config import PARQUET_DIR, RAW_SPSS_DIR


def read_with_fallback_encoding(path: Path):
    try:
        return pyreadstat.read_sav(str(path), encoding="latin1")
    except pyreadstat.ReadstatError as err:
        print(f"⚠️  latin1 failed for {path.name}: {err}; retrying with utf-8")
        return pyreadstat.read_sav(str(path), encoding="utf-8")


def convert_one(sav_file: Path, output_dir: Path, output_format: str) -> None:
    print(f"📄 Processing {sav_file.name}")
    try:
        df, meta = read_with_fallback_encoding(sav_file)
    except pyreadstat.ReadstatError as err:
        print(f"❌ Skipping {sav_file.name}: {err}")
        return

    year = sav_file.stem.split("_")[0]
    year_dir = output_dir / year
    year_dir.mkdir(parents=True, exist_ok=True)

    out_file = year_dir / f"{sav_file.stem}.{output_format}"

    # Replace numeric codes with value labels
    for column in df.columns:
        if column in meta.variable_value_labels:
            df[column] = df[column].map(meta.variable_value_labels[column]).fillna(df[column])

    # Force object columns to strings to keep value labels intact
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str)

    if output_format == "csv":
        labels = {col: meta.column_names_to_labels.get(col, col) for col in df.columns}
        df.to_csv(out_file, index=False, header=labels.values())
    elif output_format == "parquet":
        df.to_parquet(out_file, index=False)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"✅ Saved {out_file}")


def convert_spss_files(year: int | None, output_format: str, spss_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    if year:
        sav_files = list(spss_dir.glob(f"{year}_*.sav"))
    else:
        sav_files = list(spss_dir.glob("*.sav"))

    if not sav_files:
        print(f"⚠️  No .sav files matched in {spss_dir}")
        return

    print(f"📊 Converting {len(sav_files)} .sav files → {output_format}")
    for sav_file in sav_files:
        convert_one(sav_file, output_dir, output_format)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert EPF SPSS files to CSV or Parquet")
    parser.add_argument("--year", type=int, help="Specific year to convert (default: all)")
    parser.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default="parquet",
        help="Output format (default: parquet)",
    )
    parser.add_argument("--spss-dir", type=Path, default=RAW_SPSS_DIR, help="Directory with .sav files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PARQUET_DIR,
        help="Output directory (organised per year)",
    )
    args = parser.parse_args()

    convert_spss_files(args.year, args.format, args.spss_dir, args.output_dir)


if __name__ == "__main__":
    main()
