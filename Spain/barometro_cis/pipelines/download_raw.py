#!/usr/bin/env python3
"""Download raw CIS Barómetro microdata packages for a given date range.

For every Barómetro whose ``fecha`` falls in the requested window, this
pipeline:

1. Opens the detail page ``/es/estudios/{slug}`` (whose URL was captured by
   ``fetch_index.py``).
2. Extracts the direct ``MD{codigo}.zip`` link from the Liferay document
   service — the href has the form
   ``/documents/{groupId}/{folderId}/MD{codigo}.zip/{uuid}?version=…&t=…``.
3. Downloads and unzips the archive into ``RAW_DIR/MD{codigo}``.
"""

import argparse
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from Spain.barometro_cis.config import (
    BASE_URL,
    ESTUDIO_URL,
    INDEX_FILE,
    RAW_DIR,
    USER_AGENT,
)


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "user-agent": USER_AGENT,
}

# The estudio page embeds the signed download URL in a custom element
# ``<data-file url="…/MD{codigo}.zip/{uuid}?version=…&amp;t=…">``. Each UUID +
# timestamp is specific to the estudio so we capture the whole URL verbatim.
ZIP_HREF_RE_TEMPLATE = (
    r'(?P<href>https?://[^"]*?/documents/\d+/\d+/MD{codigo}\.zip/[0-9a-f-]+\?[^"]*)"'
)


def find_zip_url(session: requests.Session, slug: str, codigo: int) -> str | None:
    url = ESTUDIO_URL.format(slug=slug)
    response = session.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    pattern = re.compile(ZIP_HREF_RE_TEMPLATE.format(codigo=codigo))
    match = pattern.search(response.text)
    if not match:
        return None
    href = match.group("href").replace("&amp;", "&")
    if not href.startswith("http"):
        href = BASE_URL + href
    return href


def download_and_unzip(
    session: requests.Session,
    codigo: int,
    slug: str,
    raw_dir: Path,
) -> bool:
    target_dir = raw_dir / f"MD{codigo}"
    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"⏩ MD{codigo} already present in {target_dir}")
        return True

    zip_url = find_zip_url(session, slug, codigo)
    if not zip_url:
        print(f"❌ No MD{codigo}.zip link found on estudio page ({slug})")
        return False

    response = session.get(zip_url, headers=HEADERS, timeout=600, stream=True)
    if response.status_code != 200:
        print(f"❌ Download MD{codigo} returned status {response.status_code}")
        return False

    zip_path = raw_dir / f"MD{codigo}.zip"
    with open(zip_path, "wb") as fh:
        for chunk in response.iter_content(chunk_size=1 << 15):
            fh.write(chunk)
    print(f"📥 Downloaded {zip_path.name} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
    except zipfile.BadZipFile:
        print(f"⚠️  MD{codigo}.zip is not a valid archive, skipping")
        zip_path.unlink()
        return False

    zip_path.unlink()
    print(f"✅ Unzipped MD{codigo} into {target_dir}")
    return True


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

    session = requests.Session()
    session.headers.update({"user-agent": USER_AGENT})

    successes = 0
    for row in filtered.itertuples():
        if download_and_unzip(session, int(row.codigo), row.slug, raw_dir):
            successes += 1

    print(f"🎉 Done — {successes}/{len(filtered)} Barómetros downloaded")


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
