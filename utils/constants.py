"""Shared constants across all datasets."""

# HuggingFace repository names
HF_RAW_REPOS = {
    "pisa": "victoriano/pisa-raw",
    "eurostat": "victoriano/eurostat-raw",  # Future
    "oecd": "victoriano/oecd-raw"  # Future
}

HF_PROCESSED_REPO = "victoriano/social-sciences-microdata"

# Common country codes
EU_COUNTRIES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

# Spain-specific constants
SPAIN_CODES = ["ES", "ESP", "724"]  # Different coding systems
