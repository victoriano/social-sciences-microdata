# Proposed Repository Structure

## Overview
This structure aligns with your HuggingFace repositories and organizes scripts by their function in the data pipeline.

```
social-sciences-microdata/
│
├── README.md                      # Main documentation
├── pyproject.toml                 # Project dependencies
├── uv.lock                        # Lock file
├── .gitignore                     # Excludes data files
│
├── pipelines/                     # Data processing pipelines
│   ├── __init__.py
│   ├── pisa/                      # PISA-specific pipeline
│   │   ├── __init__.py
│   │   ├── download.py            # Download from HF raw repo
│   │   ├── process.py             # Main processing logic
│   │   ├── convert_trend_data.py  # Trend analysis processing
│   │   ├── upload.py              # Upload to HF processed repo
│   │   └── config.py              # PISA-specific configurations
│   │
│   ├── eurostat/                  # Future: Eurostat pipeline
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── process.py
│   │   └── upload.py
│   │
│   └── oecd/                      # Future: Other OECD data
│       ├── __init__.py
│       ├── download.py
│       ├── process.py
│       └── upload.py
│
├── processors/                    # Shared processing utilities
│   ├── __init__.py
│   ├── spss_processor.py          # SPSS file handling
│   ├── data_harmonizer.py        # Cross-year harmonization
│   └── metadata_generator.py     # Metadata creation
│
├── utils/                         # General utilities
│   ├── __init__.py
│   ├── hf_manager.py             # HuggingFace operations
│   ├── data_validator.py         # Data validation
│   └── constants.py              # Shared constants
│
├── analysis/                      # Analysis scripts
│   ├── __init__.py
│   ├── youth_analysis.py         # Youth unemployment analysis
│   └── examples/                 # Example notebooks
│       └── youth_demo.ipynb
│
├── docs/                         # Documentation
│   ├── PISA_GUIDE.md
│   ├── MIGRATION_SUMMARY.md
│   └── DATA_SOURCES.md
│
├── scripts/                      # Standalone scripts
│   ├── run_pisa_pipeline.py      # Full PISA pipeline
│   ├── download_all.py           # Download all datasets
│   └── validate_data.py          # Data validation
│
└── tests/                        # Unit tests
    ├── __init__.py
    ├── test_processors.py
    └── test_pipelines.py
```

## HuggingFace Repository Structure

### Raw Data Repository: `victoriano/pisa-raw` (private)
```
pisa_2006_raw.tar.gz
pisa_2009_raw.tar.gz
pisa_2012_raw.tar.gz
pisa_2015_raw.tar.gz
pisa_2018_raw.tar.gz
pisa_2022_raw.tar.gz
```

### Processed Data Repository: `victoriano/social-sciences-microdata`
```
global/
├── pisa/
│   ├── trend_analysis/
│   │   ├── pisa_2015_harmonized.parquet
│   │   ├── pisa_2018_harmonized.parquet
│   │   ├── pisa_2022_harmonized.parquet
│   │   └── pisa_combined_2006_2022.parquet
│   ├── spain_trends/
│   │   ├── spain_summary_by_year.csv
│   │   └── spain_trends_2006_2022.parquet
│   └── processing_metadata.json
│
├── eurostat/
│   └── (future datasets)
│
└── oecd/
    └── (future datasets)
```

## Key Benefits

1. **Clear Pipeline Structure**: Each data source has its own pipeline directory
2. **Reusable Components**: Shared processors and utilities
3. **Scalable**: Easy to add new data sources (Eurostat, World Bank, etc.)
4. **Mirrors HF Structure**: Local `pipelines/pisa/` processes data for `global/pisa/`
5. **Separation of Concerns**: Processing logic separate from analysis scripts
6. **Testable**: Organized structure facilitates unit testing 