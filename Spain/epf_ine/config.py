"""Configuration for Encuesta de Presupuestos Familiares (EPF) data pipeline."""

from pathlib import Path

# HuggingFace repositories
RAW_DATA_REPO = "victoriano/epf-ine-raw"
PROCESSED_DATA_REPO = "victoriano/social-sciences-microdata"
PROCESSED_DATA_PATH = "spain/epf_ine"

# INE download endpoint. Each year ships as ``datos_{year}.zip`` which unpacks
# into SPSS + CSV + fixed-width copies (except 2023 which is fixed-width only).
BASE_URL = "https://www.ine.es/ftp/microdatos/epf2006/datos_{year}.zip"

# Years available with the post-2016 (ECOICOP) codification.
POST_2016_YEARS = list(range(2016, 2024))
FIXED_WIDTH_ONLY_YEARS = [2023]

# Default local data layout
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "Spain" / "epf_ine"
RAW_SPSS_DIR = DATA_DIR / "raw" / "spss"
RAW_TXT_DIR = DATA_DIR / "raw" / "txt"
PARQUET_DIR = DATA_DIR / "interim" / "parquet"
CSV_INTERIM_DIR = DATA_DIR / "interim" / "csv"
ENRICHED_DIR = DATA_DIR / "processed" / "enriched_2023"
PROCESSED_DIR = DATA_DIR / "processed"

# Columns we keep from the household file when joining into the gastos master.
HOGAR_COLUMNS_TO_KEEP = [
    "CCAA", "NUTS1", "DENSIDAD", "NMIEMB", "TAMANO", "TIPHOGAR1", "EDADSP",
    "SEXOSP", "PAISNACSP", "NACIONASP", "ECIVILLEGALSP", "UNIONSP",
    "CONVIVENCIASP", "ESTUDIOSSP", "SITUACTSP", "IMPEXACPSP", "INTERINPSP",
    "OCUPA", "OCUPARED", "ACTESTB", "ACTESTBRED", "SITPROF", "SECTOR",
    "CONTRATO", "TIPOCONT", "SITSOCI", "SITSOCIRE", "REGTEN", "TIPOEDIF",
    "ZONARES", "TIPOCASA", "NHABIT", "ANNOCON", "SUPERF", "AGUACALI",
    "FUENAGUA", "CALEF", "IMPEXAC", "INTERIN", "COMIMH",
]

# 2023 fixed-width filenames as shipped by INE.
FIXED_WIDTH_2023 = {
    "hogar": "Fichero de usuario de hogar a2023IMPAJUSTE.txt",
    "gastos": "Fichero de usuario de gastos a2023AJUSTE.txt",
    "miembros": "Fichero de usuario de miembros a2023IMPAJUSTE.txt",
}
