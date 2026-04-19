#!/usr/bin/env python3
"""Fetch the catalogue of CIS Barómetros and save it as a CSV index.

Scrapes the server-side rendered catalogue pages at
``https://www.cis.es/es/estudios/catalogo`` (new site, 2025 redesign),
paginates with ``start=N&delta=200`` and keeps only entries whose title
starts with "Barómetro" (i.e. the *Barómetros CIS* collection).

Each row of the output CSV contains ``codigo``, ``titulo``, ``fecha`` and
``slug`` — the last column is later used by ``download_raw.py`` to locate
the detail page and extract the MD{codigo}.zip download URL.
"""

import argparse
import re
import urllib.parse
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests

from Spain.barometro_cis.config import (
    CATALOG_QUERY,
    CATALOG_URL,
    INDEX_FILE,
    REFERER_URL,
    USER_AGENT,
)

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "referer": REFERER_URL,
    "user-agent": USER_AGENT,
}

# Regex to pull every <article class="jdt-card ..."> block out of the page.
ARTICLE_RE = re.compile(r"<article[^>]*class=\"[^\"]*jdt-card[^\"]*\"[^>]*>(.*?)</article>", re.DOTALL)
TITLE_HREF_RE = re.compile(
    r"<a[^>]+href=\"(?P<href>[^\"]+)\"[^>]+class=\"card-content__title[^\"]*\"[^>]+title=\"(?P<title>[^\"]+)\"",
    re.DOTALL,
)
DATE_RE = re.compile(r"<li>\s*(\d{2}/\d{2}/\d{4})\s*</li>")
CODIGO_RE = re.compile(r"Estudio\s+(\d{3,5})")
TOTAL_RE = re.compile(r"de\s+(\d+)\s+elementos")


def build_url(start: int) -> str:
    query = dict(CATALOG_QUERY)
    query["start"] = str(start)
    return f"{CATALOG_URL}?{urllib.parse.urlencode(query)}"


def fetch_page(session: requests.Session, start: int) -> str:
    url = build_url(start)
    response = session.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.text


def parse_page(html: str) -> Iterator[dict]:
    for block in ARTICLE_RE.finditer(html):
        body = block.group(1)
        title_match = TITLE_HREF_RE.search(body)
        if not title_match:
            continue
        date_match = DATE_RE.search(body)
        codigo_match = CODIGO_RE.search(body)
        if not (date_match and codigo_match):
            continue
        href = title_match.group("href")
        slug = href.rstrip("/").rsplit("/", 1)[-1]
        yield {
            "codigo": int(codigo_match.group(1)),
            "titulo": title_match.group("title").strip(),
            "fecha": date_match.group(1),
            "slug": slug,
            "url": href,
        }


def total_elements(html: str) -> int | None:
    match = TOTAL_RE.search(html)
    return int(match.group(1)) if match else None


def fetch_index(output_file: Path, only_barometros: bool = True) -> pd.DataFrame:
    session = requests.Session()
    session.headers.update({"user-agent": USER_AGENT})

    print(f"📥 Fetching CIS catalogue from {CATALOG_URL}")
    first = fetch_page(session, start=1)
    total = total_elements(first)
    if total is None:
        raise RuntimeError("Could not find total elements count in the catalogue page")
    delta = int(CATALOG_QUERY["delta"])
    pages = (total + delta - 1) // delta
    print(f"📊 {total} estudios across {pages} pages of {delta}")

    rows: list[dict] = list(parse_page(first))
    print(f"   page 1 → {len(rows)} items")

    for page in range(2, pages + 1):
        html = fetch_page(session, start=page)
        page_rows = list(parse_page(html))
        rows.extend(page_rows)
        print(f"   page {page} → {len(page_rows)} items (running total {len(rows)})")

    df = pd.DataFrame(rows)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")

    if only_barometros:
        before = len(df)
        df = df[df["titulo"].str.startswith("Barómetro")].reset_index(drop=True)
        print(f"🎯 Filtered to {len(df)} Barómetros (from {before} estudios)")

    df = df.sort_values("fecha", ascending=False).reset_index(drop=True)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"✅ Saved index with {len(df)} rows to {output_file}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CIS catalogue and filter to Barómetros")
    parser.add_argument("--output", type=Path, default=INDEX_FILE, help=f"Output CSV file (default: {INDEX_FILE})")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Keep every estudio in the catalogue (default: only titles starting with Barómetro)",
    )
    args = parser.parse_args()
    fetch_index(args.output, only_barometros=not args.all)


if __name__ == "__main__":
    main()
