#!/usr/bin/env python3
"""Merge student-level PISA cycle files without multiplying respondents."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import polars as pl


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROCESSED_DIR = REPO_ROOT / "data" / "Global" / "pisa" / "processed"
IDENTITY_COLUMNS = ["pisa_year", "country", "school_id", "student_id"]


def discover_cycle_files(processed_dir: Path) -> list[Path]:
    trend_dir = processed_dir / "trend_analysis"
    return sorted(
        path
        for path in trend_dir.glob("pisa_*_harmonized.parquet")
        if path.stem.removeprefix("pisa_").removesuffix("_harmonized").isdigit()
    )


def deduplicate_students(frame: pl.DataFrame) -> tuple[pl.DataFrame, int]:
    if not all(column in frame.columns for column in IDENTITY_COLUMNS):
        missing = [column for column in IDENTITY_COLUMNS if column not in frame.columns]
        raise ValueError(f"Cannot identify students; missing columns: {missing}")

    before = frame.height
    essential = ['pisa_year','country','student_id']
    if frame.select(pl.any_horizontal(pl.col(essential).is_null()).any()).item():
        raise ValueError('Missing student identity')
    # Some countries suppress school IDs in their PUF. Accept those only when
    # country/year/student alone identifies the respondent without ambiguity.
    if frame.filter(pl.col('school_id').is_null()).height:
        unique_records = frame.unique()
        ambiguous = unique_records.with_columns(pl.len().over(essential).alias('_n')).filter(pl.col('school_id').is_null() & (pl.col('_n')>1))
        if ambiguous.height:
            raise ValueError('Missing school identity and ambiguous student ID')
    deduplicated = frame.unique()
    if deduplicated.select(pl.struct(IDENTITY_COLUMNS).n_unique()).item() != deduplicated.height:
        raise ValueError('Conflicting records for a student identity; refusing arbitrary deduplication')
    return deduplicated, before - deduplicated.height


def merge_cycles(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> dict:
    cycle_files = discover_cycle_files(processed_dir)
    if not cycle_files:
        raise FileNotFoundError(
            f"No individual cycle files found in {processed_dir / 'trend_analysis'}"
        )

    frames = []
    duplicates_removed = 0
    for path in cycle_files:
        scan = pl.scan_parquet(path)
        before = scan.select(pl.len()).collect().item()
        frame = scan.unique().collect(engine='streaming')
        duplicates_removed += before - frame.height
        frame = frame.with_columns(pl.col(['country','school_id','student_id']).cast(pl.String))
        frame, removed = deduplicate_students(frame)
        duplicates_removed += removed
        frames.append(frame)
    combined = pl.concat(frames, how="diagonal_relaxed")
    combined, removed = deduplicate_students(combined)
    duplicates_removed += removed
    combined = combined.sort(["pisa_year", "country", "school_id", "student_id"])

    years = sorted(combined.get_column("pisa_year").unique().to_list())
    year_range = f"{years[0]}_{years[-1]}"
    trend_dir = processed_dir / "trend_analysis"
    spain_dir = processed_dir / "spain_trends"
    spain_dir.mkdir(parents=True, exist_ok=True)

    combined_path = trend_dir / f"pisa_combined_{year_range}.parquet"
    combined.write_parquet(combined_path)

    spain = combined.filter(pl.col("country").cast(pl.String) == "ESP")
    spain_path = spain_dir / f"spain_trends_{year_range}.parquet"
    spain.write_parquet(spain_path)

    aggregations = [pl.len().alias("student_count")]
    for column, alias in [
        ("math_score", "avg_math_score_pv1_unweighted"),
        ("read_score", "avg_read_score_pv1_unweighted"),
        ("science_score", "avg_science_score_pv1_unweighted"),
        ("escs", "avg_escs_unweighted"),
        ("wealth", "avg_wealth_unweighted"),
        ("cultural", "avg_cultural_possessions_unweighted"),
    ]:
        if column in spain.columns:
            aggregations.append(pl.col(column).mean().alias(alias))

    summary = spain.group_by("pisa_year").agg(aggregations).sort("pisa_year")
    summary_path = spain_dir / f"spain_summary_{year_range}.csv"
    summary.write_csv(summary_path)

    counts = {
        str(row[0]): row[1]
        for row in combined.group_by("pisa_year")
        .agg(pl.len().alias("student_count"))
        .sort("pisa_year")
        .iter_rows()
    }
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "years": years,
        "source_files": [str(path) for path in cycle_files],
        "identity_columns": IDENTITY_COLUMNS,
        "duplicates_removed": duplicates_removed,
        "student_counts": counts,
        "outputs": {
            "combined": str(combined_path),
            "spain": str(spain_path),
            "spain_summary": str(summary_path),
        },
        "warning": (
            "Legacy score columns contain only the first plausible value and summaries "
            "are unweighted. Use the analysis-ready weighted dataset for inference."
        ),
    }
    metadata_path = processed_dir / f"merge_metadata_{year_range}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    args = parser.parse_args()
    metadata = merge_cycles(args.processed_dir)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
