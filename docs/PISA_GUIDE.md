# PISA 2022 Data Download Guide
## Step-by-Step Instructions for Youth Work & Study Analysis

### 🎯 **Required Files for Your Analysis**

For analyzing youth work and study patterns in Spain, you need these **3 essential files**:

1. **Student questionnaire data file** ⭐ (MOST IMPORTANT)
   - Contains: homework time, motivation, study habits, background info
   - Variables: TMINS, MOTIVAT, BELONG, ESCS, CNT (country), etc.

2. **Cognitive item data file** ⭐ (PERFORMANCE DATA)
   - Contains: Math, Reading, Science performance scores
   - Variables: PVMATH, PVREAD, PVSCIE (plausible values)

3. **School questionnaire data file** (OPTIONAL BUT RECOMMENDED)
   - Contains: School-level variables, context information
   - Variables: School climate, resources, policies

### 📥 **Download Instructions**

#### Step 1: Access the OECD PISA Database
1. Go to: https://www.oecd.org/pisa/data/2022database/
2. Scroll down to the "PISA 2022 Data" section
3. You'll see both SAS™ and SPSS™ formats - **choose SPSS™** (easier to work with)

#### Step 2: Download These Specific Files
Click on **SPSS™ Data Files (Compressed)** section and download:

```
✅ REQUIRED DOWNLOADS:
1. Student questionnaire data file          → CY08_MSU_STU_QQQ.sav.zip
2. Cognitive item data file                 → CY08_MSU_STU_COG.sav.zip  
3. School questionnaire data file           → CY08_MSU_SCH_QQQ.sav.zip

📚 HELPFUL DOCUMENTATION:
4. Student questionnaire codebook           → CY08_MSU_STU_QQQ_Codebook.xlsx
5. Cognitive data codebook                  → CY08_MSU_STU_COG_Codebook.xlsx
```

**Note**: The exact filenames might be slightly different, but look for files containing:
- `STU_QQQ` = Student questionnaire 
- `STU_COG` = Student cognitive (performance)
- `SCH_QQQ` = School questionnaire

#### Step 3: File Placement in Your Project

After downloading, place files in your project like this:

```
young_lazy_people/
├── data/
│   └── pisa/
│       ├── raw/                          ← Place downloaded files here
│       │   ├── CY08_MSU_STU_QQQ.sav     ← Student questionnaire (unzipped)
│       │   ├── CY08_MSU_STU_COG.sav     ← Cognitive data (unzipped)
│       │   ├── CY08_MSU_SCH_QQQ.sav     ← School questionnaire (unzipped)
│       │   ├── CY08_MSU_STU_QQQ_Codebook.xlsx
│       │   └── CY08_MSU_STU_COG_Codebook.xlsx
│       └── processed/                    ← Converted files will go here
├── youth_analysis.py
└── data_sources_guide.py
```

### 🔧 **File Conversion Process**

Since PISA data comes in SPSS (.sav) format, you'll need to convert to CSV/Parquet for analysis with Polars:

#### Option 1: Using Python (Recommended)
```python
import pandas as pd
import polars as pl

# Convert SPSS to Parquet
df_pandas = pd.read_spss('data/pisa/raw/CY08_MSU_STU_QQQ.sav')
df_polars = pl.from_pandas(df_pandas)
df_polars.write_parquet('data/pisa/processed/student_questionnaire.parquet')
```

#### Option 2: Using R (Alternative)
```r
library(haven)
library(arrow)

data <- read_sav("data/pisa/raw/CY08_MSU_STU_QQQ.sav")
write_parquet(data, "data/pisa/processed/student_questionnaire.parquet")
```

### 🇪🇸 **Key Variables for Spain Analysis**

Once you have the data, focus on these variables:

#### Student Questionnaire File:
- `CNT`: Country code (filter for 'ESP' = Spain)
- `TMINS`: Minutes spent on homework per week
- `MOTIVAT`: Motivation indices
- `BELONG`: School belonging scale
- `ESCS`: Economic, social, cultural status
- `PERSEV`: Perseverance scale
- `COMPETE`: Competitiveness
- `ST004D01T`: Gender
- `AGE`: Student age

#### Cognitive File:
- `PVMATH1-PVMATH10`: Math performance (plausible values)
- `PVREAD1-PVREAD10`: Reading performance
- `PVSCIE1-PVSCIE10`: Science performance

### ⚠️ **Important Notes**

1. **File Sizes**: PISA files are large (100-500MB each)
2. **Registration**: You may need to register (free) on the OECD website
3. **Unzip**: Extract .sav files from the downloaded .zip files
4. **Backup**: Keep original .sav files as backup
5. **Memory**: Loading full PISA data requires 4-8GB RAM

### 🚀 **Quick Start After Download**

1. **Create the directory structure:**
```bash
mkdir -p data/pisa/raw data/pisa/processed
```

2. **Place your downloaded .sav files in `data/pisa/raw/`**

3. **Run the conversion script** (I'll create this for you)

4. **Start analysis** with the Jupyter notebook

### 📧 **Need Help?**
- OECD PISA Help: pisa@oecd.org
- Technical issues: Check file integrity, ensure complete downloads
- Memory issues: Consider sampling the data first for testing

---
**Next step**: Once you download these files, I'll help you convert them and start the analysis! 

---

# PISA Trend Analysis Guide: Spain Youth "Laziness" 2006-2022
## Analyzing 16+ Years of Educational Engagement Patterns

### 🎯 **Why Multi-Year Analysis is CRUCIAL for Your Research**

✅ **Long-term Trends**: See if Spanish youth are becoming more or less engaged over 16+ years  
✅ **Policy Impact**: Identify effects of educational reforms across multiple cycles
✅ **Generational Changes**: Compare different cohorts of students over nearly two decades
✅ **Historical Context**: Include pre-financial crisis baseline (2006)
✅ **Robust Conclusions**: Avoid one-year anomalies with comprehensive time series
✅ **International Context**: See if trends are Spain-specific or global patterns

### 📊 **All Available PISA Years for Maximum Impact**

#### **🥇 PRIORITY DOWNLOADS (Essential for trend analysis):**

1. **PISA 2022** ⭐⭐⭐ (MOST RECENT)
   - Focus: Mathematics
   - **Format**: SPSS .sav files ✅ Easy to process
   - **Variables**: TMINS (homework), MOTIVAT, BELONG, PERSEV

2. **PISA 2018** ⭐⭐⭐ (READING FOCUS)
   - Focus: Reading literacy  
   - **Format**: SPSS .sav files ✅ Easy to process
   - **Variables**: Reading motivation, learning strategies, ICT use

3. **PISA 2015** ⭐⭐ (SCIENCE FOCUS)
   - Focus: Science literacy
   - **Format**: SPSS .sav files ✅ Easy to process
   - **Variables**: Science motivation, career expectations

4. **PISA 2012** ⭐⭐ (MATH FOCUS + POST-CRISIS)
   - Focus: Mathematics (same as 2022 - perfect comparison!)
   - **Format**: ⚠️ SPSS syntax + TXT files (requires extra step)
   - **Variables**: Math motivation, perseverance, work ethic

#### **🥈 EXTENDED ANALYSIS (For historical perspective):**

5. **PISA 2009** ⭐ (PRE-SMARTPHONE BASELINE)
   - Focus: Reading literacy
   - **Format**: ⚠️ SPSS syntax + TXT files
   - **Key for**: Pre-digital natives baseline, economic crisis start

6. **PISA 2006** ⭐ (PRE-CRISIS BASELINE)
   - Focus: Science literacy  
   - **Format**: ⚠️ SPSS syntax + TXT files
   - **Key for**: Pre-2008 financial crisis baseline, 16+ year trends

### ⚠️ **IMPORTANT: Different File Formats by Year**

#### **Years 2015-2022: SPSS .sav Files (EASY)**
- **Format**: Direct .sav files
- **Processing**: Simple conversion to Parquet
- **Files needed**: `STU_QQQ.sav`, `STU_COG.sav`

#### **Years 2012 and Earlier: SPSS Syntax + TXT (EXTRA STEP)**
- **Format**: SPSS syntax files + TXT data files
- **Processing**: Run SPSS syntax first, then convert
- **Files needed**: 
  - SPSS syntax files (`.sps`)
  - TXT data files (`.txt`)
  - Control files for data structure

### 🚀 **Updated Strategy: Phased Approach for Maximum Efficiency**

#### **RECOMMENDED DOWNLOAD SEQUENCE:**

**Phase 1: Quick Modern Trend (EASY START - 4 years)**
- **PISA 2022** + **PISA 2018** 
- Both use .sav files - immediate processing
- Solid 4-year trend for testing framework

**Phase 2: Strong Recent Trend (7 years)**
- Add **PISA 2015**
- Still .sav format - easy addition
- 2015-2022 covers recent education reforms

**Phase 3: Complete Decade (10 years)**
- Add **PISA 2012** 
- Requires SPSS syntax processing
- 2012-2022 covers economic crisis recovery + full decade

**Phase 4: Historical Perspective (13+ years)**
- Add **PISA 2009** 
- 2009-2022 includes pre-smartphone era

**Phase 5: Complete Historical Analysis (16+ years)**
- Add **PISA 2006**
- 2006-2022 full span with pre-crisis baseline
- Ultimate long-term trend analysis

### 📁 **Complete File Structure for All Years**

```
young_lazy_people/
├── data/
│   └── pisa/
│       ├── raw/
│       │   ├── 2022/                    ← .sav files (easy)
│       │   │   ├── CY08_MSU_STU_QQQ.sav
│       │   │   └── CY08_MSU_STU_COG.sav
│       │   ├── 2018/                    ← .sav files (easy)
│       │   │   ├── CY07_MSU_STU_QQQ.sav
│       │   │   └── CY07_MSU_STU_COG.sav
│       │   ├── 2015/                    ← .sav files (easy)
│       │   │   └── [2015 .sav files]
│       │   ├── 2012/                    ← SYNTAX + TXT (needs processing)
│       │   │   ├── INT_STU12_DEC03.txt  ← Student data (TXT)
│       │   │   ├── INT_STU12_DEC03.sps  ← SPSS syntax
│       │   │   ├── INT_COG12_DEC03.txt  ← Cognitive data (TXT)  
│       │   │   └── INT_COG12_DEC03.sps  ← SPSS syntax
│       │   ├── 2009/                    ← SYNTAX + TXT (needs processing)
│       │   │   ├── [Student TXT + SPS files]
│       │   │   └── [Cognitive TXT + SPS files]
│       │   └── 2006/                    ← SYNTAX + TXT (needs processing)
│       │       ├── [Student TXT + SPS files]
│       │       └── [Cognitive TXT + SPS files]
│       └── processed/
│           ├── trend_analysis/
│           └── spain_trends/
├── convert_pisa_trend_data.py           ← Handles all formats (2006-2022)
├── process_spss_syntax.py               ← For 2012 and earlier
└── youth_trends_demo.ipynb
```

### 🔄 **Download Process by Format**

#### **Modern PISA (2015-2022): Direct .sav Files**
1. Visit PISA database for the year
2. Download from "SPSS™ Data Files (Compressed)"
3. Extract .sav files to year folder
4. Run conversion script ✅

#### **Older PISA (2012 and earlier): Syntax + TXT**
1. Visit PISA database for the year
2. Download **both**:
   - **SPSS™ Control Files** (syntax files .sps)
   - **Data sets in TXT format** (data files .txt)
3. Place both in year folder
4. Run SPSS syntax processing first: `uv run python process_spss_syntax.py`
5. Then run conversion: `uv run python convert_pisa_trend_data.py`

### 📈 **Powerful Analysis Capabilities with Extended Timeline**

#### **Short-term Trends (2018-2022)**
- Post-COVID impact analysis
- Recent policy effects (LOMLOE 2020)
- Digital learning acceleration

#### **Medium-term Trends (2015-2022)**
- Education reform impacts (LOMCE 2013)
- Smartphone adoption effects
- 7-year engagement patterns

#### **Long-term Trends (2012-2022)**
- Economic crisis recovery (2012-2015+)
- Full decade analysis
- Policy cycle impacts

#### **Historical Trends (2009-2022)**
- Pre/post smartphone adoption
- Digital natives emergence
- 13+ year engagement evolution

#### **Complete Historical Analysis (2006-2022)**
- Pre-financial crisis baseline
- 16+ year comprehensive trends
- Generational shifts across nearly two decades
- Economic, technological, and policy impact analysis

### 💡 **Processing SPSS Syntax + TXT Files**

For PISA 2012, 2009, and 2006, you'll need to:

1. **Download both file types**:
   - SPSS syntax files (`.sps`)
   - TXT data files (`.txt`)

2. **Run syntax processing**:
   ```bash
   # Process all older years at once
   uv run python process_spss_syntax.py
   ```

3. **Then run standard conversion**:
   ```bash
   # Convert all years (modern + converted) to trend format
   uv run python convert_pisa_trend_data.py
   ```

### 🎯 **Expected Powerful Findings with Extended Timeline**

With up to 16+ years of data, you'll be able to answer:

✅ **"Are Spanish youth becoming lazier over time?"**
- 4-year trend: 2018-2022 (immediate)
- 7-year trend: 2015-2022 (strong analysis)
- 10-year trend: 2012-2022 (comprehensive)
- 13+ year trend: 2009-2022 (historical perspective)
- 16+ year trend: 2006-2022 (complete generational analysis)

✅ **"What major events influenced youth engagement?"**
- Financial crisis effects (2006 → 2009 → 2012)
- Education policy impacts (LOMCE 2013, LOMLOE 2020)
- Technology adoption (smartphones 2009-2015, social media)
- COVID-19 effects (2022 data)

✅ **"How do generational cohorts differ?"**
- Pre-digital natives (2006 baseline)
- Digital transition generation (2009-2012)
- Digital natives (2015-2022)

✅ **"Is Spain unique or following global patterns?"**
- Compare with consistent methodology across 16+ years
- Identify Spain-specific vs. global youth trends

### 🚀 **Next Steps - Complete Strategy**

1. **Start Easy**: Download PISA 2022 + 2018 (.sav files - immediate!)
2. **Build Momentum**: Add PISA 2015 (also .sav - easy addition)
3. **Add Decade View**: Include PISA 2012 (syntax processing required)
4. **Historical Context**: Add PISA 2009 (pre-smartphone baseline)
5. **Complete Analysis**: Add PISA 2006 (pre-crisis baseline)

This gives you **immediate results** with modern data, **strong trends** with recent years, and **comprehensive historical analysis** with the complete 16+ year dataset!

### 📊 **Complete File Format Summary**

| Year | Format | Difficulty | Focus | Historical Value |
|------|--------|------------|-------|------------------|
| 2022 | .sav files | ✅ Easy | Math | Current state, post-COVID |
| 2018 | .sav files | ✅ Easy | Reading | Recent policy effects |
| 2015 | .sav files | ✅ Easy | Science | Post-reform baseline |
| 2012 | Syntax + TXT | ⚠️ Extra step | Math | Post-crisis recovery |
| 2009 | Syntax + TXT | ⚠️ Extra step | Reading | Pre-smartphone baseline |
| 2006 | Syntax + TXT | ⚠️ Extra step | Science | Pre-crisis baseline |

**Recommendation**: Start with the easy ones (2015-2022) for immediate trend analysis, then expand historically as needed! 