#!/usr/bin/env python3
"""Download raw CIS Barómetro microdata packages for a given date range.

Reads the catalogue produced by ``fetch_index.py``, filters it by month, and
downloads + unzips every ``MD{codigo}.zip`` file into the raw data directory.
"""

import argparse
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from Spain.barometro_cis.config import DOWNLOAD_URL, INDEX_FILE, RAW_DIR


def download_and_unzip(codigo: str, raw_dir: Path) -> bool:
    url = DOWNLOAD_URL.format(codigo=codigo)
    zip_path = raw_dir / f"MD{codigo}.zip"

    response = requests.get(url, timeout=300)
    if response.status_code != 200:
        print(f"❌ Failed to download MD{codigo} (status {response.status_code})")
        return False

    zip_path.write_bytes(response.content)
    print(f"📥 Downloaded {zip_path.name}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(raw_dir / f"MD{codigo}")
        print(f"✅ Unzipped MD{codigo}")
        zip_path.unlink()
        return True
    except zipfile.BadZipFile:
        print(f"⚠️  MD{codigo}.zip is not a valid zip, skipping")
        zip_path.unlink()
        return False


def filter_index(index_file: Path, start_month: str, end_month: str) -> pd.DataFrame:
    df = pd.read_csv(index_file)
    df["fecha"] = pd.to_datetime(df["fecha"])

    start_date = datetime.strptime(start_month, "%m/%Y")
    end_date = datetime.strptime(end_month, "%m/%Y") + relativedelta(months=1) - relativedelta(days=1)

    return df[(df["fecha"] >= start_date) & (df["fecha"] <= end_date)]


def clear_dir(target: Path) -> None:
    if not target.exists():
        return
    for item in target.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    print(f"🧹 Cleared {target}")


def download_range(
    start_month: str,
    end_month: str,
    index_file: Path = INDEX_FILE,
    raw_dir: Path = RAW_DIR,
    clear: bool = False,
) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    if clear:
        clear_dir(raw_dir)

    filtered = filter_index(index_file, start_month, end_month)
    print(f"📊 {len(filtered)} Barómetros in range {start_month} → {end_month}")

    for codigo in filtered["codigo"]:
        download_and_unzip(str(codigo), raw_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download raw CIS Barómetro data")
    parser.add_argument("--start", required=True, help="Start month in MM/YYYY format")
    parser.add_argument("--end", required=True, help="End month in MM/YYYY format")
    parser.add_argument("--index", type=Path, default=INDEX_FILE, help="Catalogue CSV")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Output directory")
    parser.add_argument("--clear", action="store_true", help="Clear raw directory first")
    args = parser.parse_args()

    download_range(args.start, args.end, args.index, args.raw_dir, args.clear)


if __name__ == "__main__":
    main()
