"""Configuration for Barómetro del CIS data pipeline."""

from pathlib import Path

# HuggingFace repositories
RAW_DATA_REPO = "victoriano/barometro-cis-raw"
PROCESSED_DATA_REPO = "victoriano/social-sciences-microdata"
PROCESSED_DATA_PATH = "spain/barometro_cis"

# CIS site endpoints (site redesigned in 2025 — see docs/data_sources.md).
# Catalogue pages are server-side rendered HTML; pagination via ``&start=N``
# (1-based) with ``&delta=200`` items per page (capped at 200). Each estudio
# detail page contains the direct ``MD{codigo}.zip`` document link that we
# use to download the microdata.
BASE_URL = "https://www.cis.es"
CATALOG_URL = f"{BASE_URL}/es/estudios/catalogo"
CATALOG_QUERY = {
    "catalogo": "estudio",
    "sort": "createDateBDE-",
    "t": "0",
    "delta": "200",
}
ESTUDIO_URL = f"{BASE_URL}/es/estudios/{{slug}}"
REFERER_URL = f"{CATALOG_URL}?catalogo=estudio"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# Default local data layout (mirrors new repo convention: data/ outside of source tree)
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "Spain" / "barometro_cis"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_FILE = INTERIM_DIR / "barometros_index.csv"

# Spanish month → number mapping, used when rebuilding the study date.
MONTH_MAP = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12",
}

# Variable groups used when ordering columns in the processed dataset.
VARIABLE_GROUPS = {
    "Estudio": [
        "Estudio", "Código del estudio", "Año de realización",
        "Mes de realización", "Número de registro",
    ],
    "Demografía": [
        "Sexo de la persona entrevistada", "Edad de la persona entrevistada",
        "Religiosidad de la persona entrevistada", "Frecuencia de asistencia a oficios religiosos",
        "Estado civil de la persona entrevistada", "Estudios de la persona entrevistada",
        "Nivel de estudios alcanzado por la persona entrevistada",
        "Escolarización de la persona entrevistada",
        "Población activa e inactiva", "Situación laboral de la persona entrevistada",
        "Ocupación de la persona entrevistada",
        "Clase social subjetiva de la persona entrevistada", "Identificación subjetiva de clase",
        "Nivel de ingresos netos del hogar", "Escala de autoubicación ideológica (1-10)",
        "Nacionalidad de la persona entrevistada",
        "Provincia", "Municipio", "Comunidad autónoma", "Tamaño de municipio",
    ],
    "Opiniones": [
        "Principales Problemas",
        "Primer problema", "Segundo problema", "Tercer problema",
        "Valoración de la situación económica personal actual",
        "Valoración de la situación económica general de España",
    ],
    "Voto": [
        "Intención de voto en unas supuestas elecciones generales",
        "Intención de voto en unas supuestas elecciones generales [recodificada]",
        "Recuerdo de voto en las elecciones generales de 2023",
        "Recuerdo de voto en las elecciones generales de 2023 de los votantes [recodificada]",
        "Partido político que considera más cercano a sus ideas",
        "Preferencia personal como presidente del Gobierno central",
        "Intención de voto alternativo en supuestas elecciones generales",
        "Intención de voto alternativo en supuestas elecciones generales [recodificada]",
    ],
}
