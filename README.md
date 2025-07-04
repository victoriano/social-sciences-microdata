# Youth Work and Study Patterns: Spain 2012-2022 Analysis 📊

A comprehensive data analysis project examining whether young people in Spain have become more "lazy" at work/study compared to international peers, using objective PISA educational data.

## 🎯 Research Question

**Are young people in Spain becoming more disengaged from work/study compared to international peers?**

Using PISA data (2012-2022) to analyze:
- ✅ Homework time trends  
- ✅ Student motivation patterns
- ✅ School belonging and engagement
- ✅ Academic performance correlations  
- ✅ Socioeconomic controls

## 🏗️ Project Structure

```
young_lazy_people/
├── README.md                           ← This file
├── pyproject.toml                      ← Dependencies (uv package manager)
├── youth_analysis.py                   ← Main analysis framework
├── convert_pisa_data.py               ← Single-year conversion (easy start)
├── convert_pisa_trend_data.py         ← Multi-year trend analysis (full power)
├── process_spss_syntax.py             ← Process older PISA formats (2012 and earlier)
├── data_sources_guide.py              ← Available datasets guide
├── PISA_DOWNLOAD_GUIDE.md             ← Step-by-step download instructions
├── PISA_TREND_ANALYSIS_GUIDE.md       ← Multi-year analysis strategy
├── youth_analysis_demo.ipynb          ← Interactive analysis notebook
└── data/
    └── pisa/
        ├── raw/                        ← Place downloaded PISA files here
        │   ├── 2022/                   ← PISA 2022 (.sav files)
        │   ├── 2018/                   ← PISA 2018 (.sav files)
        │   ├── 2015/                   ← PISA 2015 (.sav files)
        │   └── 2012/                   ← PISA 2012 (syntax + TXT files)
        └── processed/                  ← Generated analysis files
            ├── trend_analysis/         ← Multi-year combined data
            └── spain_trends/           ← Spain-specific analysis
```

## 🚀 Quick Start (Easiest Path)

### 1. **Setup Environment**
```bash
# Clone/navigate to project directory
cd young_lazy_people

# Install dependencies with uv
uv sync
```

### 2. **Start with Easy Data (Recommended)**
**Phase 1: Test Framework (PISA 2022 + 2018)**
- Both use `.sav` files (easy processing)
- Download from OECD PISA database
- 4-year trend analysis immediately available

**Phase 2: Add PISA 2015** 
- Also `.sav` format (easy addition)
- 7-year trend (2015-2022)

**Phase 3: Complete with PISA 2012**
- Requires syntax processing (extra step)
- Full 10-year trend (2012-2022)

### 3. **Download Data**

#### **EASY YEARS (2015-2022): Direct .sav Files**
1. Visit PISA database for year (see `PISA_DOWNLOAD_GUIDE.md`)
2. Download from **"SPSS™ Data Files (Compressed)"**
3. Extract `.sav` files to `data/pisa/raw/{year}/`
4. Run conversion ✅

#### **OLDER YEARS (2012 and earlier): Syntax + TXT Files**
1. Visit PISA database for year
2. Download **both**:
   - **SPSS™ Control Files** (syntax `.sps` files)
   - **Data sets in TXT format** (data `.txt` files)
3. Place both in `data/pisa/raw/{year}/`
4. Run syntax processing first: `uv run python process_spss_syntax.py`
5. Then run conversion: `uv run python convert_pisa_trend_data.py`

### 4. **Run Analysis**

#### **Option A: Single Year (Start Here)**
```bash
# For testing with one year (e.g. PISA 2022)
uv run python convert_pisa_data.py

# Run sample analysis
uv run python youth_analysis.py
```

#### **Option B: Multi-Year Trends (Full Power)**
```bash
# Process older formats first (if using 2012 data)
uv run python process_spss_syntax.py

# Convert all years for trend analysis
uv run python convert_pisa_trend_data.py

# Interactive analysis
jupyter lab youth_analysis_demo.ipynb
```

## 📁 File Format Summary

| Year | Format | Difficulty | Files Needed | Processing |
|------|--------|------------|--------------|------------|
| 2022 | .sav files | ✅ Easy | `CY08_MSU_STU_QQQ.sav`, `CY08_MSU_STU_COG.sav` | Direct conversion |
| 2018 | .sav files | ✅ Easy | `CY07_MSU_STU_QQQ.sav`, `CY07_MSU_STU_COG.sav` | Direct conversion |
| 2015 | .sav files | ✅ Easy | `CY6_MS_CM_STU_QQQ.sav`, etc. | Direct conversion |
| 2012 | Syntax + TXT | ⚠️ Extra step | `.sps` syntax + `.txt` data files | `process_spss_syntax.py` first |

## 🔄 Processing Pipeline

### **Modern PISA (2015-2022)**
```bash
Download .sav files → convert_pisa_trend_data.py → Analysis ready!
```

### **Older PISA (2012 and earlier)**
```bash
Download .sps + .txt files → process_spss_syntax.py → convert_pisa_trend_data.py → Analysis ready!
```

## 📊 Key Variables Analyzed

### **Primary Research Variables**
- **TMINS**: Homework time (minutes per week)
- **MOTIVAT**: Student motivation indices
- **BELONG**: School belonging scale
- **PERSEV**: Perseverance and grit measures

### **Control Variables**
- **ESCS**: Economic, social, cultural status
- **CNT**: Country identifier  
- **Gender, Age, Grade**: Demographics

### **Performance Outcomes**
- **Math, Reading, Science scores**: PISA plausible values

## 🎯 Analysis Capabilities

✅ **Cross-country comparisons** (Spain vs OECD average)  
✅ **10-year trend analysis** (2012-2022)  
✅ **Statistical significance testing**  
✅ **Socioeconomic controls**  
✅ **Policy impact assessment**  
✅ **Regional differences within Spain**  

## 📈 Expected Findings

The analysis will answer:

1. **"Are Spanish youth becoming less engaged over time?"**
   - Homework time trends: 2012 vs 2022
   - Motivation changes across decade
   - International context and comparisons

2. **"What factors influenced these changes?"**
   - Economic crisis effects (2012-2015)
   - Education policy reforms (LOMCE 2013, LOMLOE 2020)
   - Technology/smartphone adoption impacts

3. **"Is Spain unique or following global patterns?"**
   - Compare Spain's trajectory with Germany, France, Finland
   - Identify Spain-specific vs. global youth trends

## 🛠️ Technical Details

- **Language**: Python with modern libraries
- **Package Manager**: `uv` (fast, reliable)
- **Data Processing**: Polars (fast) + Pandas (compatibility)
- **Statistical Analysis**: scipy, statsmodels
- **Visualization**: matplotlib, seaborn
- **Data Format**: Parquet (efficient), CSV (compatibility)

## 📚 Documentation

- **`PISA_DOWNLOAD_GUIDE.md`**: Step-by-step download instructions
- **`PISA_TREND_ANALYSIS_GUIDE.md`**: Multi-year strategy and recommendations
- **`data_sources_guide.py`**: Comprehensive data sources overview

## ⚡ Performance Tips

1. **Start small**: Begin with PISA 2022 + 2018 (easy `.sav` files)
2. **Batch processing**: Download multiple years in parallel
3. **Memory efficient**: Polars handles large datasets efficiently
4. **Focus variables**: Load only needed columns initially

## 🔍 Ethical Considerations

- ✅ Avoid reinforcing stereotypes about Spanish youth
- ✅ Consider cultural differences in work-life balance values  
- ✅ Include socioeconomic context in interpretations
- ✅ Focus on constructive analysis rather than judgment

## 🚀 Next Steps

1. **Download PISA data** following the guides
2. **Run conversion scripts** based on file formats
3. **Execute trend analysis** using processed data
4. **Generate insights** about youth engagement patterns
5. **Create visualizations** for findings presentation

---

**Goal**: Provide objective, data-driven analysis of youth engagement trends in Spain using internationally comparable PISA data, with proper controls and statistical rigor. 