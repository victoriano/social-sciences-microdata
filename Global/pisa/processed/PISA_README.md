# PISA Data - Programme for International Student Assessment

## Overview
This directory contains processed PISA (Programme for International Student Assessment) data from 2006-2022, optimized for research and analysis.

## Structure
- `trend_analysis/` - Multi-year trend analysis datasets
- `spain_trends/` - Spain-specific trend data
- `processing_metadata.json` - Processing metadata and variable information

## Data Description
- **Source**: OECD PISA Programme
- **Years**: 2006, 2009, 2012, 2015, 2018, 2022
- **Format**: Parquet files for optimal performance
- **Key Variables**: Academic performance, socioeconomic status, study habits, motivation

## Usage
The processed data is ready for analysis with modern data science tools (Polars, Pandas, etc.).

## Citation
If you use this data in your research, please cite:
- OECD (2023), Programme for International Student Assessment (PISA)
- This processed dataset: `victoriano/social-sciences-microdata`

## Processing Details
Data was processed using the young-lazy-people analysis framework:
- Standardized variable names across years
- Unified country codes and identifiers
- Optimized data types for analysis
- Spain-specific trend extraction

## License
This processed data follows the OECD PISA data usage guidelines.
