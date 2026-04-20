#!/usr/bin/env python3
"""Post-process the merged Barómetros CSV into a tidy Parquet dataset.

Steps
-----
1. Rebuild the study date from ``Mes`` + ``Año`` columns.
2. Collapse the three "principal problem" columns into a single list column.
3. Coerce numeric-but-comma-formatted columns to floats.
4. Reorder columns so the grouped variables in ``config.VARIABLE_GROUPS`` come
   first and administrative fields (study code, year, month, record number) go
   last.
5. Write a Parquet file ready for analysis.
"""

import argparse
from pathlib import Path

import pandas as pd

from Spain.barometro_cis.config import (
    INDEX_FILE,
    INTERIM_DIR,
    MONTH_MAP,
    PROCESSED_DIR,
    VARIABLE_GROUPS,
)


def build_date_of_study(df: pd.DataFrame, index_file: Path) -> pd.DataFrame:
    """Reconstruct ``date_of_study`` with fallbacks for older barómetros.

    Priority:
      1. ``Mes/Año de realización`` columns (present in newer barómetros).
      2. The ``codigo_cis`` column joined onto the catalogue index
         (``fetch_index.py`` output) — this covers every Barómetro.
    """
    # Primary: mes + año columns
    if "Mes de realización" in df.columns and "Año de realización" in df.columns:
        df["Mes_numero"] = df["Mes de realización"].map(MONTH_MAP)
        primary = pd.to_datetime(
            df["Mes_numero"].astype(str) + "/" + df["Año de realización"].astype(str) + "/01",
            format="%m/%Y/%d",
            errors="coerce",
        )
    else:
        primary = pd.Series(pd.NaT, index=df.index)

    df["date_of_study"] = primary

    # Fallback: join codigo_cis onto the catalogue index to pull `fecha`.
    if "codigo_cis" in df.columns and index_file.exists():
        idx = pd.read_csv(index_file, usecols=["codigo", "fecha"])
        idx["fecha"] = pd.to_datetime(idx["fecha"], errors="coerce")
        lookup = dict(zip(idx["codigo"].astype(int), idx["fecha"]))
        fallback = df["codigo_cis"].astype(int).map(lookup)
        # Force the 1st day of the month so monthly series are clean.
        fallback = fallback.dt.to_period("M").dt.to_timestamp()
        df["date_of_study"] = df["date_of_study"].fillna(fallback)

    return df


def build_principal_problems(df: pd.DataFrame) -> pd.DataFrame:
    df["Principales Problemas"] = df.apply(
        lambda row: [
            prob
            for prob in [row.get("Primer problema"), row.get("Segundo problema"), row.get("Tercer problema")]
            if pd.notna(prob)
        ],
        axis=1,
    )
    return df


def coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")
    return df


def order_columns(df: pd.DataFrame) -> pd.DataFrame:
    all_variables = [var for group in VARIABLE_GROUPS.values() for var in group]
    all_columns = df.columns.tolist()

    columns_to_move = [
        "Número de registro",
        "Código del estudio",
        "Año de realización",
        "Mes de realización",
    ]
    for col in columns_to_move + ["Mes_numero"]:
        if col in all_columns:
            all_columns.remove(col)

    ordered = ["date_of_study"] + [
        var for var in all_variables if var in all_columns and var not in columns_to_move
    ]
    remaining = [col for col in all_columns if col not in ordered and col not in columns_to_move]
    ordered.extend(remaining)
    ordered.extend(columns_to_move)

    return df[ordered].copy()


def summarize_null_columns(df: pd.DataFrame) -> None:
    no_nulls = df.columns[df.notnull().all()].tolist()
    with_nulls = df.columns[df.isnull().any()].tolist()
    print(f"📊 {len(no_nulls)} columns without nulls, {len(with_nulls)} with nulls")


def preprocess(input_file: Path, output_file: Path, index_file: Path = INDEX_FILE) -> None:
    print(f"📥 Reading merged barómetros from {input_file}")
    if input_file.suffix == ".parquet":
        df = pd.read_parquet(input_file)
    else:
        df = pd.read_csv(input_file)

    df = build_date_of_study(df, index_file)
    df = build_principal_problems(df)
    df = coerce_numeric(df, ["Edad de la persona entrevistada", "Ponderación autonómica"])
    df_ordered = order_columns(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_ordered.to_parquet(output_file, index=False, engine="pyarrow", compression="snappy")
    print(f"✅ Processed data saved to {output_file}")

    summarize_null_columns(df_ordered)


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess merged Barómetros CSV into a Parquet dataset")
    parser.add_argument(
        "--input",
        type=Path,
        default=INTERIM_DIR / "filtered_merged_barometros.parquet",
        help="Input merged file (Parquet preferred; falls back to CSV by extension)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_DIR / "processed_barometros.parquet",
        help="Output Parquet file",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=INDEX_FILE,
        help="Catalogue CSV used as fallback to recover the study date",
    )
    args = parser.parse_args()
    preprocess(args.input, args.output, args.index)


if __name__ == "__main__":
    main()
