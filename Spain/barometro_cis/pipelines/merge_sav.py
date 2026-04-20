#!/usr/bin/env python3
"""Merge CIS Barómetro .sav files into a single labeled dataset.

Per Barómetro whose ``codigo`` falls in the requested date range this
pipeline reads the ``{codigo}.sav`` file, swaps codes for value labels,
renames columns to variable labels and writes an intermediate labeled
Parquet into ``interim/labeled/``. At the end all labeled parquets are
concatenated in memory and written out as:

- ``merged_barometros.parquet`` — primary artefact (≈10x smaller than CSV
  and orders of magnitude faster to read back).
- ``merged_barometros.csv`` — optional, only when ``--write-csv`` is set.
- ``filtered_merged_barometros.parquet`` / ``.csv`` — optional, only when
  ``--filter-nans`` is set.

Unreadable SAV files (e.g. SPSS-encrypted exports) are skipped and reported
at the end instead of aborting the whole run.
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from dateutil.relativedelta import relativedelta

from Spain.barometro_cis.config import INDEX_FILE, INTERIM_DIR, RAW_DIR
from Spain.barometro_cis.utils.spss_reader import deduplicate_columns, read_sav_with_labels

LABELED_DIR = INTERIM_DIR / "labeled"


def filter_studies_by_date(index_file: Path, start_month: str, end_month: str) -> pd.DataFrame:
    df = pd.read_csv(index_file)
    df["fecha"] = pd.to_datetime(df["fecha"])

    start_date = datetime.strptime(start_month, "%m/%Y")
    end_date = datetime.strptime(end_month, "%m/%Y") + relativedelta(months=1) - relativedelta(days=1)

    return df[(df["fecha"] >= start_date) & (df["fecha"] <= end_date)]


def sav_to_parquet(codigo: int, raw_dir: Path, labeled_dir: Path) -> Path | None:
    """Convert one .sav to a labeled intermediate parquet; skip on read error."""
    sav_path = raw_dir / f"MD{codigo}" / f"{codigo}.sav"
    if not sav_path.exists():
        print(f"⚠️  Missing SAV file {sav_path}, skipping", flush=True)
        return None

    parquet_path = labeled_dir / f"MD{codigo}.parquet"
    if parquet_path.exists():
        return parquet_path

    print(f"📄 Processing {sav_path.name}", flush=True)
    try:
        df = read_sav_with_labels(sav_path)
    except Exception as err:
        print(f"❌ Could not read {sav_path.name}: {err}", flush=True)
        return None

    df = deduplicate_columns(df)
    # Every value lands as string so labeled codes are preserved downstream.
    df = df.astype(str)

    labeled_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    print(f"✅ Wrote labeled parquet {parquet_path.name} ({len(df)} rows)", flush=True)
    return parquet_path


def concat_parquets(paths: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        df = pd.read_parquet(path)
        # Tag every row with the CIS estudio codigo derived from the filename.
        # Early Barómetros (pre-2020) do not ship "Mes/Año de realización"
        # columns, so we need this to recover the study date downstream.
        codigo = int(path.stem.removeprefix("MD"))
        df["codigo_cis"] = codigo
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=0, ignore_index=True, sort=False)


def drop_sparse_columns(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    # Treat empty strings, "nan" (from stringified floats) and actual NaN as missing.
    missing_mask = df.isin(["", "nan", "NaN", "None"]) | df.isnull()
    share = missing_mask.mean()
    kept = share[share < threshold].index.tolist()
    return df[kept]


def write_outputs(
    df: pd.DataFrame,
    output_parquet: Path,
    output_csv: Path | None,
    filtered_parquet: Path | None,
    filtered_csv: Path | None,
    nan_threshold: float | None,
) -> None:
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_parquet, index=False)
    print(f"✅ Wrote {output_parquet} ({len(df)} rows × {len(df.columns)} cols)", flush=True)

    if output_csv is not None:
        df.to_csv(output_csv, index=False)
        print(f"✅ Wrote {output_csv}", flush=True)

    if nan_threshold is None:
        return

    filtered = drop_sparse_columns(df, nan_threshold)
    print(
        f"✂️  Kept {len(filtered.columns)}/{len(df.columns)} columns with <{nan_threshold:.0%} missing",
        flush=True,
    )

    if filtered_parquet is not None:
        filtered.to_parquet(filtered_parquet, index=False)
        print(f"✅ Wrote {filtered_parquet}", flush=True)
    if filtered_csv is not None:
        filtered.to_csv(filtered_csv, index=False)
        print(f"✅ Wrote {filtered_csv}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge CIS Barómetro .sav files into a dataset")
    parser.add_argument("--start", required=True, help="Start month in MM/YYYY format")
    parser.add_argument("--end", required=True, help="End month in MM/YYYY format")
    parser.add_argument("--index", type=Path, default=INDEX_FILE, help="Catalogue CSV")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Directory with raw SAV files")
    parser.add_argument(
        "--output-parquet",
        type=Path,
        default=INTERIM_DIR / "merged_barometros.parquet",
        help="Output merged Parquet file",
    )
    parser.add_argument("--write-csv", action="store_true", help="Also write the full merged CSV")
    parser.add_argument(
        "--filter-nans",
        action="store_true",
        help="Produce an additional dataset dropping columns with too many nulls",
    )
    parser.add_argument(
        "--nan-threshold",
        type=float,
        default=0.5,
        help="Column-wise null share above which the column is dropped (default: 0.5)",
    )
    args = parser.parse_args()

    filtered_index = filter_studies_by_date(args.index, args.start, args.end)
    print(f"📊 {len(filtered_index)} Barómetros in range {args.start} → {args.end}", flush=True)

    parquet_paths: list[Path] = []
    failures = 0
    for codigo in filtered_index["codigo"]:
        path = sav_to_parquet(int(codigo), args.raw_dir, LABELED_DIR)
        if path is None:
            failures += 1
            continue
        parquet_paths.append(path)

    if not parquet_paths:
        print("⚠️  Nothing to merge; aborting", flush=True)
        return

    print(f"🔗 Merging {len(parquet_paths)} labeled parquets", flush=True)
    merged = concat_parquets(parquet_paths)

    out_parquet = args.output_parquet
    out_csv = out_parquet.with_suffix(".csv") if args.write_csv else None
    filtered_parquet = out_parquet.with_name(f"filtered_{out_parquet.name}") if args.filter_nans else None
    filtered_csv = (
        out_parquet.with_name(f"filtered_{out_parquet.stem}.csv")
        if args.filter_nans and args.write_csv
        else None
    )

    write_outputs(
        merged,
        out_parquet,
        out_csv,
        filtered_parquet,
        filtered_csv,
        args.nan_threshold if args.filter_nans else None,
    )

    print(f"🎉 Merge complete — {len(parquet_paths)} barómetros merged, {failures} skipped", flush=True)


if __name__ == "__main__":
    main()
