# Social Sciences Microdata Analysis 📊

A comprehensive data analysis framework for social sciences research using microdata from multiple international sources, organized by geographical scope.

## 🎯 Research Focus

This repository provides tools and analysis for:
- **Educational outcomes** and student performance trends
- **Youth engagement** and work-study patterns  
- **Cross-national comparisons** using standardized datasets
- **Longitudinal analysis** of social and economic indicators

## 🏗️ Repository Structure

```
social-sciences-microdata/
├── Global/                                 ← Global/international data sources
│   ├── pisa/                              ← PISA educational data (2006-2022)
│   │   ├── analysis/                      ← Analysis scripts and notebooks
│   │   ├── docs/                         ← Documentation and guides
│   │   ├── pipelines/                    ← Data processing pipelines
│   │   ├── scripts/                      ← PISA-specific utility scripts
│   │   └── utils/                        ← Utility functions
│   └── oecd/                             ← OECD statistics and indicators
│       ├── analysis/
│       ├── docs/
│       ├── pipelines/
│       └── utils/
├── Europe/                                ← European data sources
│   └── eurostat/                         ← European statistics
│       ├── analysis/
│       ├── docs/
│       ├── pipelines/
│       └── utils/
├── Spain/                                 ← Spain-specific data sources
│   ├── barometro_cis/                     ← CIS Barómetros (monthly public-opinion microdata)
│   │   ├── analysis/
│   │   ├── docs/
│   │   ├── pipelines/
│   │   └── utils/
│   └── epf_ine/                           ← INE Encuesta de Presupuestos Familiares
│       ├── analysis/
│       ├── docs/
│       ├── pipelines/
│       └── utils/
├── USA/                                   ← USA-specific data sources
│   └── [Future USA-specific datasets]
├── utils/                                 ← Shared utilities and constants
└── docs/                                  ← Project-level documentation
```

## 🌍 Data Sources by Geography

### 🌐 Global Sources
- **PISA (Programme for International Student Assessment)**: Educational performance and student attitudes (2006-2022)
- **OECD Statistics**: Various economic and social indicators

### 🇪🇺 European Sources  
- **Eurostat**: European Union statistics and indicators

### 🇪🇸 Spain-Specific Sources
- **Barómetro del CIS**: Monthly public-opinion microdata published by the Centro de Investigaciones Sociológicas (since 2013)
- **Encuesta de Presupuestos Familiares (INE)**: Annual household budget survey with ECOICOP expenditure codes (since 2016, including fixed-width 2023)

### 🇺🇸 USA-Specific Sources
- *Future datasets focusing on US education, labor, and social policies*

## 🚀 Quick Start

### 1. **Environment Setup**
```bash
# Install dependencies with uv
uv sync

# Create data directories
mkdir -p data/Global/pisa data/Europe/eurostat data/Spain data/USA
```

### 2. **Choose Your Research Scope**

#### **Global Analysis (PISA)**
```bash
# Download PISA data
cd Global/pisa
python scripts/download_all.py             # Download from HuggingFace
python pipelines/preprocess.py
python scripts/run_pisa_pipeline.py        # Run complete pipeline

# Run analysis
python analysis/spain_trends.py
jupyter lab analysis/notebooks/pisa_demo.ipynb
```

#### **European Analysis (Eurostat)**
```bash
# Work with European data
cd Europe/eurostat
python pipelines/download_raw.py
python pipelines/preprocess.py
```

### 3. **Cross-Regional Analysis**
```bash
# Future: Cross-source analysis scripts will be added at root level
# when we have multiple data sources available
# python run_comparative_analysis.py
# python run_cross_regional_study.py
```

## 📊 Available Datasets

### PISA (Global/pisa/)
- **Years**: 2006, 2009, 2012, 2015, 2018, 2022
- **Countries**: 80+ countries including Spain, European peers, OECD countries
- **Key Variables**: Academic performance, student motivation, homework time, socioeconomic status
- **Sample Analysis**: Youth engagement trends in Spain vs. international peers

### Eurostat (Europe/eurostat/)
- **Focus**: European Union statistics
- **Coverage**: Education, employment, social conditions
- **Granularity**: National and regional levels

## 🔄 Data Processing Pipeline

### **Step 1: Download Raw Data**
```bash
# Each source has its own download pipeline
cd Global/pisa && python pipelines/download_raw.py
cd Europe/eurostat && python pipelines/download_raw.py
```

### **Step 2: Preprocess & Harmonize**
```bash
# Convert to standardized formats
python pipelines/preprocess.py          # Source-specific preprocessing
python pipelines/harmonize_trends.py    # Multi-year harmonization
```

### **Step 3: Analysis & Visualization**
```bash
# Run analysis scripts
python analysis/spain_trends.py
python analysis/cross_country_comparison.py
```

## 🎯 Research Examples

### **Youth Engagement Analysis (PISA)**
Examine whether Spanish youth are becoming less engaged in education:
- Homework time trends (2012-2022)
- Motivation and belonging patterns
- International comparisons with European peers

### **Cross-National Education Comparison**
Compare educational outcomes across:
- **Global scope**: PISA international rankings
- **European scope**: EU education indicators
- **National scope**: Spain-specific trends

## 📚 Documentation Structure

- **`docs/`**: Project-level documentation
- **`Global/pisa/docs/`**: PISA-specific guides and documentation
- **`Europe/eurostat/docs/`**: Eurostat-specific documentation
- **Each data source** has its own README and download guides

## 🛠️ Technical Details

- **Language**: Python with modern libraries
- **Package Manager**: `uv` (fast, reliable dependency management)
- **Data Processing**: Polars (performance) + Pandas (compatibility)
- **Storage**: HuggingFace repositories for large datasets
- **Format**: Parquet (efficient) + CSV (compatibility)
- **Shared Utilities**: Common constants and functions in `utils/`

## 🚀 Getting Started by Research Interest

### **🎓 Education Research**
```bash
cd Global/pisa
# Follow PISA documentation for educational analysis
```

### **🏛️ European Policy Research**
```bash
cd Europe/eurostat
# Follow Eurostat documentation for EU policy analysis
```

### **🇪🇸 Spain-Specific Research**
```bash
# CIS Barómetros — public-opinion microdata
uv run python -m Spain.barometro_cis.pipelines.fetch_index
uv run python -m Spain.barometro_cis.pipelines.download_raw --start 01/2023 --end 07/2024
uv run python -m Spain.barometro_cis.pipelines.merge_sav --start 01/2023 --end 07/2024 --filter-nans
uv run python -m Spain.barometro_cis.pipelines.preprocess

# INE Encuesta de Presupuestos Familiares
uv run python -m Spain.epf_ine.pipelines.download_raw --years 2016 2017 2018 2019 2020 2021 2022
uv run python -m Spain.epf_ine.pipelines.spss_to_parquet --format parquet
uv run python -m Spain.epf_ine.pipelines.build_gastos_master
```

### **🌍 Cross-Regional Comparative Research**
```bash
# Future: Cross-source analysis scripts will be added at root level
# when we have multiple data sources available
# python run_comparative_analysis.py
# python run_cross_regional_study.py
```

## 📈 Future Expansion

The geographical structure allows for easy addition of new data sources:
- **Spain/**: ported *Barómetro del CIS* and *Encuesta de Presupuestos Familiares*; next up: Microdatos Elecciones Generales
- **USA/**: NAEP, Census Bureau, Department of Education data
- **Global/**: World Bank, UNESCO, other international sources

## 🔍 Key Research Questions

✅ **Cross-national education comparisons** (Global/pisa)
✅ **European policy impact analysis** (Europe/eurostat)  
✅ **Youth engagement trends** (Global/pisa + Europe/eurostat)
✅ **Socioeconomic factors** in education (Multi-source)

---

**Goal**: Provide a comprehensive, geographically-organized framework for social sciences research using high-quality microdata with proper statistical controls and international comparability. 
<!-- pages-deploy-check: 2026-09-09 (verifying Cloudflare Pages git integration; safe to delete) -->
