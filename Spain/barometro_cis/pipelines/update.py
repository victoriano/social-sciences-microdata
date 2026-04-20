#!/usr/bin/env python3
"""End-to-end CIS Barómetro refresh.

Chains every step of the pipeline so a monthly refresh is a single command:

    uv run python -m Spain.barometro_cis.pipelines.update --since 2020

The end date defaults to the current day. Every step is idempotent — the
script only performs work for things that actually changed:

1. ``fetch_index`` always re-queries the CIS catalogue so newly published
   Barómetros become visible. It's a cheap HTML scrape.
2. ``download_raw`` skips ``MD{codigo}`` folders that are already present.
3. ``merge_sav`` reuses labeled parquets already on disk and skips the
   concat / output step entirely when the merged parquet is already newer
   than every labeled parquet (see ``merge_sav.outputs_up_to_date``).
4. ``preprocess`` re-writes the final parquet only when the filtered
   merged parquet is newer than the processed output.
"""

import argparse
from datetime import date
from pathlib import Path

from Spain.barometro_cis.config import (
    INDEX_FILE,
    INTERIM_DIR,
    PROCESSED_DIR,
    RAW_DIR,
)
from Spain.barometro_cis.pipelines.download_raw import download_range
from Spain.barometro_cis.pipelines.fetch_index import fetch_index
from Spain.barometro_cis.pipelines.merge_sav import run_merge
from Spain.barometro_cis.pipelines.preprocess import preprocess

MERGED_PARQUET = INTERIM_DIR / "merged_barometros.parquet"
FILTERED_MERGED_PARQUET = INTERIM_DIR / "filtered_merged_barometros.parquet"
PROCESSED_PARQUET = PROCESSED_DIR / "processed_barometros.parquet"


def parse_month(value: str) -> str:
    """Accept ``YYYY`` or ``MM/YYYY`` and return the canonical ``MM/YYYY``."""
    value = value.strip()
    if "/" in value:
        month, year = value.split("/", 1)
        return f"{int(month):02d}/{int(year):04d}"
    # Plain year → January of that year
    return f"01/{int(value):04d}"


def default_end_month() -> str:
    today = date.today()
    return f"{today.month:02d}/{today.year:04d}"


def processed_is_current(processed: Path, merged: Path) -> bool:
    """True when the processed parquet is newer than the filtered merged input."""
    if not processed.exists() or not merged.exists():
        return False
    return processed.stat().st_mtime >= merged.stat().st_mtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh the CIS Barómetro dataset end-to-end")
    parser.add_argument(
        "--since",
        default="2020",
        help="Start month (YYYY or MM/YYYY). Default: 2020 — i.e. all Barómetros since Jan 2020.",
    )
    parser.add_argument(
        "--until",
        default=None,
        help="End month (YYYY or MM/YYYY). Default: current month.",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip re-downloading the catalogue (useful for offline re-runs).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run the concat + preprocess even when outputs are already up to date.",
    )
    parser.add_argument(
        "--nan-threshold",
        type=float,
        default=0.5,
        help="Column-wise null share above which the column is dropped (default: 0.5)",
    )
    args = parser.parse_args()

    start = parse_month(args.since)
    end = parse_month(args.until) if args.until else default_end_month()

    print(f"🚀 Refreshing CIS Barómetros in range {start} → {end}", flush=True)

    if args.skip_index:
        print("⏩ --skip-index set: reusing existing catalogue CSV", flush=True)
    else:
        print("\n─── Step 1/4: fetch_index ───", flush=True)
        fetch_index(INDEX_FILE)

    print("\n─── Step 2/4: download_raw ───", flush=True)
    download_range(start, end, INDEX_FILE, RAW_DIR, clear=False)

    print("\n─── Step 3/4: merge_sav ───", flush=True)
    summary = run_merge(
        start=start,
        end=end,
        index_file=INDEX_FILE,
        raw_dir=RAW_DIR,
        output_parquet=MERGED_PARQUET,
        write_csv=False,
        filter_nans=True,
        nan_threshold=args.nan_threshold,
        force=args.force,
    )

    print("\n─── Step 4/4: preprocess ───", flush=True)
    if not args.force and summary["skipped_concat"] and processed_is_current(
        PROCESSED_PARQUET, FILTERED_MERGED_PARQUET
    ):
        print(
            f"⏩ {PROCESSED_PARQUET.name} is already newer than {FILTERED_MERGED_PARQUET.name}; skipping preprocess",
            flush=True,
        )
    else:
        preprocess(FILTERED_MERGED_PARQUET, PROCESSED_PARQUET, INDEX_FILE)

    print(
        f"\n✅ Done. Merged {summary['merged']} barómetros"
        f"{' (concat skipped)' if summary['skipped_concat'] else ''}"
        f", {summary['failures']} SAV files unreadable.",
        flush=True,
    )


if __name__ == "__main__":
    main()
