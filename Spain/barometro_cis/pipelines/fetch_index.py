#!/usr/bin/env python3
"""Fetch the catalogue of CIS Barómetros and save it as a CSV index.

Queries the CIS "estudios" endpoint for every Barómetro ever published and
stores a trimmed index with ``id``, ``codigo``, ``titulo``, ``fecha`` and
``ficheros`` columns. The output is used downstream by ``download_raw.py`` to
decide which .zip packages to pull.
"""

import argparse
from pathlib import Path

import pandas as pd
import requests

from Spain.barometro_cis.config import CATALOG_URL, INDEX_FILE, REFERER_URL

# Minimum headers the CIS catalogue backend expects. A real browser-like
# User-Agent is required; the cookie is refreshed on each request so we only
# send `accept`/`origin`/`referer`.
HEADERS = {
    "accept": "*/*",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "origin": "https://www.cis.es",
    "referer": REFERER_URL,
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
}

PAYLOAD = {
    "cndColeccionCod": "2",
    "cndColeccion": "Barómetros CIS",
    "registrosPorPagina": "-1",
    "cndFechaEstudioDesde": "",
    "cndFechaEstudioHasta": "",
    "cndFiltroArbol": "",
    "cndTematicoCod": "",
    "cndTematico": "",
}


def fetch_index(output_file: Path) -> pd.DataFrame:
    print(f"📥 Fetching Barómetro CIS catalogue from {CATALOG_URL}")
    response = requests.post(CATALOG_URL, headers=HEADERS, data=PAYLOAD, timeout=60)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data["lista"], columns=["id", "codigo", "titulo", "fecha", "ficheros"])
    df = df[df["titulo"].str.startswith("BARÓMETRO")]
    df["fecha"] = pd.to_datetime(df["fecha"], format="%d-%m-%Y")
    df = df.sort_values(by="fecha", ascending=False)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"✅ Saved {len(df)} Barómetro entries to {output_file}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CIS Barómetro catalogue")
    parser.add_argument(
        "--output",
        type=Path,
        default=INDEX_FILE,
        help=f"Output CSV file (default: {INDEX_FILE})",
    )
    args = parser.parse_args()
    fetch_index(args.output)


if __name__ == "__main__":
    main()
