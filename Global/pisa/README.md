# PISA Data Management and Analysis Guide

## Overview
This directory contains tools and pipelines for managing PISA (Programme for International Student Assessment) data. PISA assesses 15-year-old students' abilities in mathematics, reading, and science literacy, along with their motivation, engagement, and learning strategies.

**Configured coverage**: cycles 2000–2025. Configuration is not evidence that a cycle has been downloaded or validated. The local legacy trend archive covers 2006–2022; the new pipeline adds 2025 and a separate survey-design-aware Spain comparison for 2022–2025.

## September 2026 update

See [Spain 2022–2025: reproducibility and methodology](analysis/README_2025.md)
for the validated workflow. Use that workflow instead of the legacy examples
below for survey-weighted comparisons. New PUF data are kept local; adding 2025
to a downloader's configuration does not mean it is present on Hugging Face.

## Data Storage Strategy
PISA data is stored in HuggingFace repositories for efficient access and version control:

- **Raw Data**: `victoriano/pisa-raw` (private) - Original OECD data files
- **Processed Data**: `victoriano/social-sciences-microdata/global/pisa/` - Cleaned and harmonized data

## 🔒 Access Requirements

### Option 1: Using HuggingFace Repository (Recommended)
**⚠️ IMPORTANT**: This option is only available to the repository author and approved collaborators to comply with OECD PISA terms of use. The raw data repository is private and requires proper access credentials.

```bash
cd Global/pisa/
python scripts/download_from_hf.py    # Download from HuggingFace (requires access)
python pipelines/preprocess.py        # Clean and process data
python pipelines/harmonize_trends.py  # Harmonize across years
```

**Prerequisites for HuggingFace download:**
- Access to `victoriano/pisa-raw` private repository
- HuggingFace CLI authentication: `huggingface-cli login`
- Compliance with OECD PISA data usage terms

### Option 2: Download from OECD (Public Access)
If you don't have access to the private HuggingFace repository, download directly from OECD:
```bash
python scripts/download_from_oecd.py  # Download from OECD (public)
python scripts/run_pisa_pipeline.py   # Run full pipeline
```

**OECD PISA Data Source**: [https://webfs.oecd.org/pisa2022/index.html](https://webfs.oecd.org/pisa2022/index.html)

## OECD Download Script Usage

### Public Access to PISA Data
Use the `download_from_oecd.py` script to download PISA data directly from the OECD website:

```bash
# Download all years and file types
python scripts/download_from_oecd.py

# Download specific years
python scripts/download_from_oecd.py --years 2018 2022

# Download specific file types
python scripts/download_from_oecd.py --file-types student_questionnaire cognitive_item

# Download with force (overwrite existing)
python scripts/download_from_oecd.py --years 2022 --force

# Check current status
python scripts/download_from_oecd.py --status

# List available file types for a year
python scripts/download_from_oecd.py --list-file-types 2022
```

### Available File Types by Year

**Recent Years (2015-2025)** - SPSS compressed files:
- `student_questionnaire` - Student questionnaire data
- `school_questionnaire` - School questionnaire data  
- `teacher_questionnaire` - Teacher questionnaire data
- `cognitive_item` - Cognitive performance data
- `questionnaire_timing` - Questionnaire timing data
- `creative_thinking` - Creative thinking data (2022 only)
- `financial_literacy` - Financial literacy data
- `cognitive_process` - Cognitive process data (2025)

**Historical Years (2003-2012)** - TXT files + SPSS syntax:
- `student_questionnaire_data` + `student_questionnaire_syntax`
- `school_questionnaire_data` + `school_questionnaire_syntax`
- `parent_questionnaire_data` + `parent_questionnaire_syntax` (2006-2012)
- `cognitive_item_data` + `cognitive_item_syntax`
- `scored_cognitive_data` + `scored_cognitive_syntax` (2006-2012)

**PISA 2000** - TXT files + SPSS syntax (Special format):
- `database_manual` - Manual for the PISA 2000 Database (PDF)
- `test_item_response_data` + `test_item_response_syntax`
- `school_questionnaire_data` + `school_questionnaire_syntax`
- `student_math_data` + `student_math_syntax`
- `student_reading_data` + `student_reading_syntax`
- `student_science_data` + `student_science_syntax`

## Data Structure

### Raw Data
- **Format**: Compressed tar.gz files organized by year
- **Source**: OECD PISA Database or HuggingFace repository
- **Location**: `raw/` directory

### Processed Data
- **Format**: Parquet files optimized for analysis
- **Features**: Cleaned, harmonized variables across years
- **Location**: `processed/` directory

## Available PISA Years and Focus Areas

### Recent Years (SPSS .sav format - Easy Processing)
- **PISA 2025** ⭐ Science focus
- **PISA 2022** ⭐ Mathematics focus
- **PISA 2018** ⭐ Reading focus  
- **PISA 2015** ⭐ Science focus

### Historical Years (SPSS syntax + TXT format - Extra Processing)
- **PISA 2012** ⭐ Mathematics focus
- **PISA 2009** Reading focus
- **PISA 2006** Science focus
- **PISA 2003** Mathematics focus (First cycle)
- **PISA 2000** Reading focus (Inaugural cycle)

## Key Variables for Analysis

### Student Questionnaire (`STU_QQQ` files)
- `CNT`: Country code (filter for 'ESP' = Spain)
- `TMINS`: Minutes spent on homework per week
- `MOTIVAT`: Motivation indices
- `BELONG`: School belonging scale
- `ESCS`: Economic, social, cultural status
- `PERSEV`: Perseverance scale
- `COMPETE`: Competitiveness
- `ST004D01T`: Gender
- `AGE`: Student age

### Cognitive Performance (`STU_COG` files)
- `PVMATH1-PVMATH10`: Math performance (plausible values)
- `PVREAD1-PVREAD10`: Reading performance
- `PVSCIE1-PVSCIE10`: Science performance

### School Questionnaire (`SCH_QQQ` files)
- School climate variables
- Resources and policies
- Contextual information

## Manual Download from OECD (If Needed)

### Step 1: Access OECD PISA Database
1. Go to: https://www.oecd.org/pisa/data/2022database/
2. Navigate to "PISA 2022 Data" section
3. Choose **SPSS™** format (recommended over SAS™)

### Step 2: Required Files
Download these essential files:
```
✅ REQUIRED:
1. Student questionnaire data file    → CY08_MSU_STU_QQQ.sav.zip
2. Cognitive item data file          → CY08_MSU_STU_COG.sav.zip  
3. School questionnaire data file    → CY08_MSU_SCH_QQQ.sav.zip

📚 DOCUMENTATION:
4. Student questionnaire codebook    → CY08_MSU_STU_QQQ_Codebook.xlsx
5. Cognitive data codebook          → CY08_MSU_STU_COG_Codebook.xlsx
```

### Step 3: File Placement
```
Global/pisa/
├── raw/                             ← Place downloaded files here
│   ├── CY08_MSU_STU_QQQ.sav        ← Student questionnaire
│   ├── CY08_MSU_STU_COG.sav        ← Cognitive data
│   ├── CY08_MSU_SCH_QQQ.sav        ← School questionnaire
│   └── codebooks/
├── processed/                       ← Converted files
├── analysis/
└── pipelines/
```

## HuggingFace Download Script Usage

### Single Script for All Downloads
Use the unified `download_from_hf.py` script for all HuggingFace downloads:

```bash
# Download everything (raw + processed)
python scripts/download_from_hf.py

# Download only raw data
python scripts/download_from_hf.py --raw-only

# Download only processed data
python scripts/download_from_hf.py --processed-only

# Download specific years
python scripts/download_from_hf.py --years 2018 2022

# Force re-download existing data
python scripts/download_from_hf.py --force

# Check current status
python scripts/download_from_hf.py --status
```

## Data Processing Pipeline

### 1. Raw Data Processing
```python
# Convert SPSS to Parquet using modern tools
import polars as pl
import pandas as pd

# Load SPSS file
df_pandas = pd.read_spss('raw/CY08_MSU_STU_QQQ.sav')
df_polars = pl.from_pandas(df_pandas)

# Save as Parquet
df_polars.write_parquet('processed/student_questionnaire.parquet')
```

### 2. Data Harmonization
The harmonization pipeline standardizes variables across different PISA years:
- Consistent variable names
- Standardized scales
- Missing value handling
- Country code normalization

### 3. Analysis-Ready Data
Final processed data includes:
- Clean variable names
- Documented scales
- Consistent missing value codes
- Optimized data types

## Project Structure

```
Global/pisa/
├── analysis/                        # Analysis notebooks and scripts
│   ├── notebooks/
│   │   └── pisa_demo.ipynb         # Demonstration analysis
│   ├── spain_trends.py             # Spain-specific trend analysis
│   └── youth_unemployment.py       # Youth engagement analysis
├── config.py                       # Configuration settings
├── docs/                           # Legacy documentation
├── pipelines/                      # Data processing pipelines
│   ├── download_raw.py             # Download from HuggingFace
│   ├── preprocess.py              # Clean and process data
│   ├── harmonize_trends.py        # Harmonize across years
│   └── upload_processed.py        # Upload to HuggingFace
├── scripts/                        # Utility scripts
│   ├── download_all.py            # Download from OECD
│   ├── run_pisa_pipeline.py       # Run full pipeline
│   └── upload_raw_data.py         # Upload raw data
└── utils/                          # Utility functions
    ├── spss_reader.py             # SPSS file handling
    └── variable_mappings.py       # Variable harmonization
```

## System Requirements

- **Memory**: 4-8GB RAM for full dataset processing
- **Storage**: 2-5GB for raw data, 1-2GB for processed data
- **Python**: 3.8+ with uv package manager
- **Dependencies**: Listed in `pyproject.toml`

## Dependencies Installation

```bash
# Install with uv (recommended)
uv pip install polars pandas pyarrow spss-reader requests

# Or using pip
pip install polars pandas pyarrow spss-reader requests
```

## Important Notes

1. **File Sizes**: PISA files are large (100-500MB each)
2. **Registration**: May require free registration on OECD website
3. **Backup**: Keep original files as backup
4. **Memory**: Loading full PISA data requires adequate RAM
5. **Formats**: Different years use different file formats

## Common Use Cases

### Spain Youth Engagement Analysis
```python
import polars as pl

# Load processed data
df = pl.read_parquet('processed/student_questionnaire.parquet')

# Filter for Spain
spain_data = df.filter(pl.col('CNT') == 'ESP')

# Analyze homework time trends
homework_trends = spain_data.group_by('year').agg([
    pl.col('TMINS').mean().alias('avg_homework_minutes'),
    pl.col('MOTIVAT').mean().alias('avg_motivation')
])
```

### Cross-Country Comparisons
```python
# Compare Spain with other countries
comparison = df.filter(
    pl.col('CNT').is_in(['ESP', 'FRA', 'DEU', 'ITA'])
).group_by(['CNT', 'year']).agg([
    pl.col('PVMATH1').mean().alias('avg_math_score'),
    pl.col('ESCS').mean().alias('avg_socioeconomic_status')
])
```

## Support

- **Technical Issues**: Check file integrity and complete downloads
- **Memory Issues**: Consider data sampling for testing
- **OECD Support**: pisa@oecd.org
- **Pipeline Issues**: Check logs in `pipelines/` directory

## Next Steps

1. **Download Data**: Use `pipelines/download_raw.py` or manual OECD download
2. **Process Data**: Run preprocessing and harmonization pipelines
3. **Analyze**: Use notebooks in `analysis/` or create your own
4. **Explore**: Check `analysis/notebooks/pisa_demo.ipynb` for examples

---

**Last Updated**: September 2026
