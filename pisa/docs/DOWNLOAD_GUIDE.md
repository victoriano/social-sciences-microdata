# PISA Data Download Guide

## Overview
PISA data is stored in HuggingFace repositories for efficient access and version control.

## Repositories
- **Raw Data**: `victoriano/pisa-raw` (private)
- **Processed Data**: `victoriano/social-sciences-microdata/global/pisa/`

## Download Process

### 1. Download Raw Data
```bash
cd pisa/
python pipelines/download_raw.py
```

### 2. Process Data
```bash
python pipelines/preprocess.py
python pipelines/harmonize_trends.py
```

### 3. Upload Processed Data
```bash
python pipelines/upload_processed.py
```

## Data Structure
- Raw data: Compressed tar.gz files by year
- Processed data: Parquet files optimized for analysis
