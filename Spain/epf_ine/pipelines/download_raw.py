#!/usr/bin/env python3
"""Download and unzip annual EPF microdata packages from INE.

Each year ships as ``datos_{year}.zip`` which may contain multiple nested
zips. We extract them all and move the SPSS ``.sav`` files to
``config.RAW_SPSS_DIR`` with a ``{year}_{original_name}`` filename.
"""

import argparse
import os
import shutil
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

from Spain.epf_ine.config import BASE_URL, POST_2016_YEARS, RAW_SPSS_DIR


def download_file(url: str, dest: Path) -> None:
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(dest, "wb") as fh, tqdm(
        desc=dest.name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            size = fh.write(chunk)
            bar.update(size)


def extract_nested_zips(folder: Path) -> None:
    for root, _dirs, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(".zip"):
                nested = Path(root) / name
                with zipfile.ZipFile(nested, "r") as zf:
                    zf.extractall(nested.parent)


def move_spss_files(folder: Path, year: int, spss_dir: Path) -> None:
    for root, dirs, _files in os.walk(folder):
        if "SPSS" in dirs:
            spss_folder = Path(root) / "SPSS"
            for name in os.listdir(spss_folder):
                if name.endswith(".sav"):
                    src = spss_folder / name
                    dst = spss_dir / f"{year}_{name}"
                    shutil.move(str(src), dst)


def process_year(year: int, spss_dir: Path) -> None:
    url = BASE_URL.format(year=year)
    zip_path = Path(f"datos_{year}.zip")
    temp_dir = Path(f"temp_{year}")

    print(f"📥 Downloading EPF {year} from {url}")
    download_file(url, zip_path)

    print(f"📦 Unzipping {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_dir)

    extract_nested_zips(temp_dir)
    move_spss_files(temp_dir, year, spss_dir)

    shutil.rmtree(temp_dir)
    zip_path.unlink()
    print(f"✅ Finished EPF {year}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download raw EPF microdata from INE")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=POST_2016_YEARS,
        help="Specific years to download (default: all post-2016 years)",
    )
    parser.add_argument(
        "--spss-dir",
        type=Path,
        default=RAW_SPSS_DIR,
        help="Directory where .sav files will land",
    )
    args = parser.parse_args()

    args.spss_dir.mkdir(parents=True, exist_ok=True)
    for year in args.years:
        process_year(year, args.spss_dir)

    print("🎉 Done downloading EPF years")


if __name__ == "__main__":
    main()
