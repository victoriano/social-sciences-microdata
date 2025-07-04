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