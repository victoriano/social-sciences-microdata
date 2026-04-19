#!/usr/bin/env python3
"""Join EPF year-by-year gastos/hogar/mhogar Parquets into a single master table.

Looks for files matching ``{year}_EPF{gastos|hogar|mhogar}_*.parquet`` in the
per-year interim directory, concatenates them, joins ``hogar`` attributes onto
the gastos rows and writes a consolidated Parquet file ready for Graphext or
DuckDB analysis.
"""

import argparse
from glob import glob
from pathlib import Path

import pandas as pd

from Spain.epf_ine.config import HOGAR_COLUMNS_TO_KEEP, PARQUET_DIR, PROCESSED_DIR


def merge_files(parquet_dir: Path, file_pattern: str) -> pd.DataFrame:
    all_files = glob(str(parquet_dir / "**" / file_pattern), recursive=True)
    print(f"📊 Found {len(all_files)} files matching {file_pattern}")
    frames = [pd.read_parquet(f) for f in all_files]
    merged = pd.concat(frames, ignore_index=True)
    print(f"   → merged shape: {merged.shape}")
    return merged


def build_master(parquet_dir: Path, output_path: Path) -> None:
    print("📥 Merging gastos files")
    gastos_df = merge_files(parquet_dir, "*_EPFgastos_*.parquet")

    print("📥 Merging hogar files")
    hogar_df = merge_files(parquet_dir, "*_EPFhogar_*.parquet")

    print("📥 Merging mhogar files")
    merge_files(parquet_dir, "*_EPFmhogar_*.parquet")  # loaded for completeness

    print("🔗 Joining gastos and hogar dataframes")
    merged_df = pd.merge(
        gastos_df,
        hogar_df[["ANOENC", "NUMERO"] + HOGAR_COLUMNS_TO_KEEP],
        on=["ANOENC", "NUMERO"],
        how="left",
    )

    print("🔧 Coercing numeric columns")
    if "COMIMH" in merged_df.columns:
        merged_df["COMIMH"] = pd.to_numeric(merged_df["COMIMH"], errors="coerce")

    for col in merged_df.columns:
        if merged_df[col].dtype == "object":
            try:
                merged_df[col] = pd.to_numeric(merged_df[col], errors="raise")
                print(f"   → {col} converted to numeric")
            except ValueError:
                pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_parquet(output_path, index=False)
    print(f"✅ Saved master dataset to {output_path} (shape {merged_df.shape})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the EPF gastos master Parquet")
    parser.add_argument(
        "--parquet-dir",
        type=Path,
        default=PARQUET_DIR,
        help="Directory with per-year EPF Parquet files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_DIR / "gastos_master.parquet",
        help="Output Parquet path",
    )
    args = parser.parse_args()

    build_master(args.parquet_dir, args.output)


if __name__ == "__main__":
    main()
