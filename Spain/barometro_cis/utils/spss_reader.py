"""Helpers to read CIS SPSS (.sav) files and expose human-readable labels."""

from pathlib import Path
from typing import Tuple

import pandas as pd
import pyreadstat


def read_sav_with_labels(sav_path: Path) -> pd.DataFrame:
    """Read a CIS .sav file replacing codes with value labels and columns with variable labels."""
    df, meta = pyreadstat.read_sav(str(sav_path))

    df_labeled = df.copy()
    for col in df.columns:
        if col in meta.variable_value_labels:
            value_labels = meta.variable_value_labels[col]
            df_labeled[col] = df[col].map(value_labels).fillna(df[col])

    df_labeled.columns = [
        meta.column_names_to_labels.get(col, col) for col in df_labeled.columns
    ]
    return df_labeled


def deduplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate column names and suffix remaining duplicates by position."""
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    df.columns = [
        f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col
        for i, col in enumerate(df.columns)
    ]
    return df


def read_sav(sav_path: Path) -> Tuple[pd.DataFrame, "pyreadstat._readstat_parser.metadata_container"]:
    """Thin wrapper around ``pyreadstat.read_sav`` returning the raw frame and metadata."""
    df, meta = pyreadstat.read_sav(str(sav_path))
    return df, meta
