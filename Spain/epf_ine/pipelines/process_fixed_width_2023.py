#!/usr/bin/env python3
"""Parse the 2023 EPF fixed-width text files into intermediate CSVs.

For historical reasons INE only ships EPF 2023 as fixed-width files; the SPSS
conversion pipeline does not apply. This script uses the column specs from
``utils/fixed_width_specs.py`` to produce three intermediate CSVs (hogares,
gastos, miembros), which are then enriched with labels by ``enrich_2023.py``.
"""

import argparse
from pathlib import Path

import pandas as pd

from Spain.epf_ine.config import CSV_INTERIM_DIR, FIXED_WIDTH_2023, RAW_TXT_DIR
from Spain.epf_ine.utils.fixed_width_specs import FIXED_WIDTH_SPECS


def read_fixed_width(path: Path, col_specs, col_names) -> pd.DataFrame:
    return pd.read_fwf(path, colspecs=col_specs, names=col_names, encoding="latin-1")


def convert_file(kind: str, txt_dir: Path, output_dir: Path) -> None:
    col_specs, col_names = FIXED_WIDTH_SPECS[kind]
    source = txt_dir / FIXED_WIDTH_2023[kind]
    if not source.exists():
        print(f"⚠️  {source} not found; skipping")
        return

    print(f"📄 Parsing {kind} from {source.name}")
    df = read_fixed_width(source, col_specs, col_names)

    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"EPF{kind.capitalize()}_2023.csv"
    # Preserve the legacy naming used downstream by enrich_2023.py
    legacy_names = {
        "hogar": "EPFhogar_2023.csv",
        "gastos": "EPFgastos_2023.csv",
        "miembros": "EPFmhogar_2023.csv",
    }
    out = output_dir / legacy_names[kind]
    df.to_csv(out, index=False)
    print(f"✅ Wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert EPF 2023 fixed-width files to CSV")
    parser.add_argument("--txt-dir", type=Path, default=RAW_TXT_DIR, help="Directory with the 3 .txt files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CSV_INTERIM_DIR / "2023",
        help="Where intermediate CSVs land",
    )
    parser.add_argument(
        "--kinds",
        nargs="+",
        choices=list(FIXED_WIDTH_SPECS.keys()),
        default=list(FIXED_WIDTH_SPECS.keys()),
        help="Which files to parse (default: all three)",
    )
    args = parser.parse_args()

    for kind in args.kinds:
        convert_file(kind, args.txt_dir, args.output_dir)


if __name__ == "__main__":
    main()
