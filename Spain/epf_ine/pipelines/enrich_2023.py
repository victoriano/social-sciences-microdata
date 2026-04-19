#!/usr/bin/env python3
"""Enrich EPF 2023 intermediate CSVs with human-readable labels.

Reads the intermediate CSVs produced by ``process_fixed_width_2023.py`` and
replaces code values with labels from ``utils/label_mappings.py``. For the
``gastos`` file it also casts amount columns (stored with two implicit
decimals) to floats.
"""

import argparse
from pathlib import Path

import pandas as pd

from Spain.epf_ine.config import CSV_INTERIM_DIR, ENRICHED_DIR
from Spain.epf_ine.utils.label_mappings import FILE_MAPPINGS

GASTOS_CAST_COLUMNS = [
    "GASTO", "PORCENDES", "PORCENIMP", "CANTIDAD", "GASTOMON",
    "GASTNOM1", "GASTNOM2", "GASTNOM3", "GASTNOM4", "GASTNOM5",
]


def apply_gastos_castings(df: pd.DataFrame) -> pd.DataFrame:
    for column in GASTOS_CAST_COLUMNS:
        if column in df.columns:
            # The fixed-width file stores amounts as integers where the last
            # two digits are decimals. Rebuild the float value explicitly.
            df[column] = df[column].astype(str)
            df[column] = df[column].apply(
                lambda value: float(value[:-2] + "." + value[-2:]) if value.isdigit() else None
            )
    if "FACTOR" in df.columns:
        df["FACTOR"] = pd.to_numeric(df["FACTOR"], errors="coerce").astype("float64")
    return df


def enrich_csv(input_file: Path, output_file: Path, mapping: dict, is_gastos: bool) -> None:
    df = pd.read_csv(input_file)

    for column, column_mapping in mapping.items():
        if column in df.columns:
            df[column] = df[column].map(column_mapping).fillna(df[column])

    if is_gastos:
        df = apply_gastos_castings(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, decimal=".", float_format="%.2f")
    print(f"✅ Enriched file saved as {output_file}")


FILES_TO_PROCESS = [
    ("EPFmhogar_2023.csv", FILE_MAPPINGS["miembros"], False),
    ("EPFgastos_2023.csv", FILE_MAPPINGS["gastos"], True),
    ("EPFhogar_2023.csv", FILE_MAPPINGS["hogar"], False),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich EPF 2023 intermediate CSVs with labels")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=CSV_INTERIM_DIR / "2023",
        help="Directory with intermediate CSVs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ENRICHED_DIR,
        help="Directory where enriched CSVs will be written",
    )
    args = parser.parse_args()

    for filename, mapping, is_gastos in FILES_TO_PROCESS:
        input_file = args.input_dir / filename
        output_file = args.output_dir / filename
        if not input_file.exists():
            print(f"⚠️  {input_file} not found; skipping")
            continue
        enrich_csv(input_file, output_file, mapping, is_gastos)

    print("🎉 Enrichment process completed")


if __name__ == "__main__":
    main()
