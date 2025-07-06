# PISA Data Processing Summary

## 🎉 Processing Complete!

Successfully processed PISA data from raw SAV files into comprehensive, analysis-ready datasets using a unified pipeline.

## 📊 Datasets Created

### 1. International Dataset
**File:** `data/processed/combined/pisa_essential_2006_2018.parquet`
- **Students:** 2,526,220 across 5 PISA cycles
- **Years:** 2006, 2009, 2012, 2015, 2018 
- **Variables:** 20 essential variables
- **Size:** 64 MB (compressed)

### 2. Spain-Specific Dataset  
**File:** `data/processed/spain/spain_essential_2006_2018.parquet`
- **Students:** 113,483 Spanish students
- **Years:** 2006, 2009, 2012, 2015, 2018
- **Variables:** 20 essential variables  
- **Size:** 2.9 MB (compressed)

### 3. Individual Year Files
**Directory:** `data/processed/individual_years/`
- `pisa_2006_essential.parquet` - 398,750 students
- `pisa_2009_essential.parquet` - 515,958 students  
- `pisa_2012_essential.parquet` - 480,174 students
- `pisa_2015_essential.parquet` - 519,334 students
- `pisa_2018_essential.parquet` - 612,004 students

## 🔧 Variables Included

### Core Identifiers
- `CNTSTUID` - Student ID
- `CNT` - Country code  
- `CNTSCHID` - School ID
- `pisa_year` - Assessment year

### Demographics
- `AGE` - Student age
- `ST004D01T` - Original gender variable
- `sex` - Enhanced gender (Female/Male/Unknown)
- `country_name` - Full country names

### Socioeconomic Status
- `ESCS` - Economic, Social & Cultural Status index
- `WEALTH` - Wealth index
- `HOMEPOS` - Home possessions
- `PARED` - Parental education
- `ses_category` - SES categories (High/Medium/Low)

### Academic Performance  
- `PV1MATH` - Math plausible value 1
- `PV1READ` - Reading plausible value 1
- `PV1SCIE` - Science plausible value 1
- `overall_performance` - Average across domains

### Motivation & Attitudes
- `JOYREAD` - Joy of reading (2009, 2018)
- `SCIEEFF` - Science self-efficacy (2006, 2015)  
- `BELONG` - School belonging (2003, 2012, 2015, 2018)

## 🇪🇸 Spain Dataset Highlights

### Students by Year:
- **2006:** 19,604 students (avg performance: 495.2)
- **2009:** 25,887 students (avg performance: 489.1)  
- **2012:** 25,313 students (avg performance: 497.7)
- **2015:** 6,736 students (avg performance: 495.6)
- **2018:** 35,943 students (avg performance: 488.4)

### Total Spanish Students: 113,483 across 12 years

## 📈 Key Analysis Capabilities

### 1. Longitudinal Trend Analysis
- Track changes in performance, motivation, and socioeconomic factors over 12 years
- Compare Spain's trajectory against international trends
- Analyze the impact of the 2008 financial crisis on educational outcomes

### 2. Socioeconomic Equity Studies  
- Examine SES gaps using ESCS, WEALTH, and HOMEPOS
- Study the relationship between family background and performance
- Compare equity patterns between Spain and other countries

### 3. Motivation & Engagement Research
- Analyze reading enjoyment trends (JOYREAD)
- Study science self-efficacy patterns (SCIEEFF)
- Examine school belonging across different contexts

### 4. Cross-National Comparisons
- Compare Spain against similar countries
- Benchmark performance against OECD averages
- Study cultural and policy differences

## 🚀 Getting Started

### Load International Dataset
```python
import polars as pl

# Load full international dataset
df = pl.read_parquet('data/processed/combined/pisa_essential_2006_2018.parquet')
print(f"Loaded {len(df):,} students from {len(df['pisa_year'].unique())} years")
```

### Load Spain-Only Dataset
```python
# Load Spain-specific dataset
spain_df = pl.read_parquet('data/processed/spain/spain_essential_2006_2018.parquet')
print(f"Loaded {len(spain_df):,} Spanish students")

# Quick summary by year
summary = spain_df.group_by('pisa_year').agg([
    pl.len().alias('students'),
    pl.col('overall_performance').mean().alias('avg_performance')
]).sort('pisa_year')
print(summary)
```

### Filter by Country
```python
# Compare Spain with other countries
countries_of_interest = ['Spain', 'Finland', 'Germany', 'France']
comparison_df = df.filter(pl.col('country_name').is_in(countries_of_interest))
```

### Analyze Trends Over Time
```python
# Performance trends by year
trends = df.group_by(['pisa_year', 'country_name']).agg([
    pl.col('overall_performance').mean().alias('avg_performance'),
    pl.col('ESCS').mean().alias('avg_ses')
]).sort(['country_name', 'pisa_year'])
```

## 📁 File Structure

```
data/processed/
├── combined/
│   └── pisa_essential_2006_2018.parquet      # Main international dataset
├── spain/
│   ├── spain_essential_2006_2018.parquet     # Spain-only dataset  
│   └── spain_summary_2006_2018.csv           # Spain summary statistics
└── individual_years/
    ├── pisa_2006_essential.parquet            # Individual year files
    ├── pisa_2009_essential.parquet            
    ├── pisa_2012_essential.parquet
    ├── pisa_2015_essential.parquet
    └── pisa_2018_essential.parquet
```

## 🔄 Processing Pipeline Used

1. **Memory-Efficient Processing** - Processed years individually to handle large files
2. **Essential Variable Selection** - Focused on most important variables for analysis  
3. **Data Type Harmonization** - Standardized categorical/string variables across years
4. **Enhanced Variables** - Added computed variables (sex, country_name, overall_performance, ses_category)
5. **Quality Validation** - Verified data consistency and completeness

## 📊 Data Quality Notes

- **Missing Values:** Preserved as null/NaN for proper statistical analysis
- **Performance Scores:** Used first plausible value (PV1) for each domain, computed overall average
- **Gender Variable:** Harmonized different coding schemes across years  
- **Country Names:** Converted codes to full country names for readability
- **SES Categories:** Created meaningful categories from continuous ESCS values

## 🎯 Recommended Next Steps

1. **Exploratory Analysis** - Start with summary statistics and visualizations
2. **Trend Analysis** - Focus on key indicators over time  
3. **Comparative Studies** - Spain vs international or similar countries
4. **Policy Impact Analysis** - Examine changes around key policy periods
5. **Equity Research** - Deep dive into socioeconomic gaps and their evolution

## 📚 Variable Availability by Year

| Variable | 2006 | 2009 | 2012 | 2015 | 2018 |
|----------|------|------|------|------|------|
| Core IDs | ✅ | ✅ | ✅ | ✅ | ✅ |
| Demographics | ✅ | ✅ | ✅ | ✅ | ✅ |
| Performance | ✅ | ✅ | ✅ | ✅ | ✅ |
| ESCS/SES | ✅ | ✅ | ✅ | ✅ | ✅ |
| JOYREAD | ❌ | ✅ | ❌ | ❌ | ✅ |
| SCIEEFF | ✅ | ❌ | ❌ | ✅ | ❌ |
| BELONG | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## 🏆 Processing Success Summary

✅ **5 Years Processed** - 2006, 2009, 2012, 2015, 2018  
✅ **2.5M+ Students** - Comprehensive international dataset  
✅ **113K+ Spanish Students** - Complete Spain longitudinal sample  
✅ **20 Essential Variables** - All key research variables included  
✅ **Memory Optimized** - Efficient processing of multi-GB files  
✅ **Analysis Ready** - Clean, harmonized, enhanced datasets  

**All PISA essential datasets are ready for comprehensive longitudinal analysis!** 🎉 