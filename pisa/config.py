"""Configuration for PISA data processing pipeline."""

# HuggingFace repositories
RAW_DATA_REPO = "victoriano/pisa-raw"
PROCESSED_DATA_REPO = "victoriano/social-sciences-microdata"
PROCESSED_DATA_PATH = "global/pisa"

# PISA years
PISA_YEARS = [2006, 2009, 2012, 2015, 2018, 2022]

# Key variables for analysis
KEY_VARIABLES = {
    "student_id": ["CNTSTUID", "StIDStd"],
    "country": ["CNTRYID", "Country"],
    "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    "reading_score": ["PV1READ", "PV2READ", "PV3READ", "PV4READ", "PV5READ"],
    "science_score": ["PV1SCIE", "PV2SCIE", "PV3SCIE", "PV4SCIE", "PV5SCIE"],
    "socioeconomic_status": ["ESCS"],
    "study_time": ["MMINS", "LMINS", "SMINS"],
    "motivation": ["INTMAT", "INSTMOT", "SUBNORM"]
}
