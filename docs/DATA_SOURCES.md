# Data Sources Guide

## 🌍 Geographic Organization

This repository organizes data sources by geographical scope:

### 🌐 Global Sources (`Global/`)
- **PISA**: Programme for International Student Assessment (2006-2022)
- **OECD**: Organisation for Economic Co-operation and Development statistics

### 🇪🇺 European Sources (`Europe/`)  
- **Eurostat**: European Union statistics and indicators

### 🇪🇸 Spain-Specific Sources (`Spain/`)
- *Future datasets focusing on Spanish education, labor, and social policies*

### 🇺🇸 USA-Specific Sources (`USA/`)
- *Future datasets focusing on US education, labor, and social policies*

## 📊 Available Datasets

### PISA (Global/pisa/)
**Source**: OECD Programme for International Student Assessment
**Coverage**: 2006, 2009, 2012, 2015, 2018, 2022
**Countries**: 80+ countries including Spain and European peers
**Key Variables**: Academic performance, student motivation, homework time, socioeconomic status

### Eurostat (Europe/eurostat/)
**Source**: European Union statistics office
**Coverage**: EU member states, various social and economic indicators
**Granularity**: National and regional levels

## 🔄 Data Access Patterns

### By Research Scope
- **Global comparisons**: Use `Global/pisa/` for international educational analysis
- **European policy**: Use `Europe/eurostat/` for EU-specific research
- **National focus**: Use country-specific folders for detailed national analysis

### By Data Type
- **Educational outcomes**: `Global/pisa/`
- **Labor market**: `Europe/eurostat/`, future USA sources
- **Social indicators**: Multiple sources across geographical folders

## 🚀 Getting Started

1. **Choose your geographical scope**
2. **Navigate to the appropriate folder**
3. **Follow the source-specific documentation**
4. **Use shared utilities from `utils/` for common operations**

print("🎓 PISA MICRODATA - Programme for International Student Assessment")
print("=" * 70)
print("\n📊 Why PISA is Perfect for Your Analysis:")
print("- Measures actual student performance (not self-reported)")
print("- Includes detailed background questionnaires")
print("- Has specific variables on study time, motivation, and effort")
print("- Covers 80+ countries including Spain")
print("- Microdata allows individual-level analysis")

print("\n🔑 Key Variables for 'Laziness' Analysis:")
print("EDUCATIONAL ENGAGEMENT:")
print("- TMINS: Minutes spent on homework per week")
print("- MMINS: Minutes spent on mathematics homework")
print("- LMINS: Minutes spent on language homework")
print("- SMINS: Minutes spent on science homework")
print("- ATTEND: School attendance patterns")
print("- LATE: Frequency of arriving late to school")

print("\nMOTIVATION & ATTITUDES:")
print("- MOTIVAT: Motivation to learn")
print("- PERSEV: Perseverance")
print("- OPENPS: Openness to problem solving")
print("- COMPETE: Competitiveness")
print("- WORKMAST: Work mastery orientation")

print("\nEFFORT & ENGAGEMENT:")
print("- BELONG: Sense of belonging at school")
print("- DISCLIMA: Disciplinary climate")
print("- STUDYEF: Study effort indicators")
print("- JOYREAD: Enjoyment of reading")

print("\n📥 How to Access PISA 2022 Microdata:")
print("1. Visit: https://www.oecd.org/pisa/data/2022database/")
print("2. Register for free access")
print("3. Download these files:")
print("   - Student questionnaire data file (CY08_MSU_STU_QQQ.sas7bdat)")
print("   - Student cognitive data (CY08_MSU_STU_COG.sas7bdat)")
print("   - Codebook (CY08_MSU_STU_QQQ_Codebook.xlsx)")
print("4. Convert to CSV/Parquet for analysis with Polars")

print("\n🇪🇸 Spain-Specific Analysis Opportunities:")
print("- Compare Spanish students (CNT='ESP') with:")
print("  * OECD average")
print("  * Other Southern European countries (Italy, Portugal, Greece)")
print("  * Northern European countries (Finland, Netherlands)")
print("- Analyze by regions within Spain (available in microdata)")
print("- Control for socioeconomic status (ESCS variable)")

def print_eurostat_microdata_guide():
    print("\n\n📈 ADDITIONAL OECD DATA SOURCES")
    print("=" * 45)
    
    print("\n1. Programme for the International Assessment of Adult Competencies (PIAAC)")
    print("   - Adult skills and work attitudes")
    print("   - Problem-solving skills")
    print("   - Technology use at work")
    
    print("\n2. OECD Education at a Glance")
    print("   - Educational attainment trends")
    print("   - Education-to-work transitions")
    print("   - Returns to education")
    
    print("\n3. OECD Employment Outlook")
    print("   - Youth employment trends")
    print("   - Labor market dynamics")
    
    print("\n4. Better Life Index")
    print("   - Work-life balance indicators")
    print("   - Life satisfaction measures")

def print_time_use_surveys():
    print("\n\n💡 CREATIVE INDICATORS OF WORK/STUDY ENGAGEMENT")
    print("=" * 55)
    
    print("\n📱 Digital Behavior Indicators:")
    print("- Screen time data (if available)")
    print("- Online learning platform usage")
    print("- Educational app downloads and usage")
    
    print("\n🏫 Educational System Indicators:")
    print("- Grade repetition rates")
    print("- School dropout rates")
    print("- University completion rates")
    print("- Vocational training participation")
    
    print("\n💼 Labor Market Indicators:")
    print("- Youth NEET rates (Not in Education, Employment, or Training)")
    print("- Part-time vs. full-time work preferences")
    print("- Job search duration")
    print("- Skills mismatch indicators")
    
    print("\n🎯 Entrepreneurship Indicators:")
    print("- Youth entrepreneurship rates")
    print("- Start-up creation by age group")
    print("- Innovation indices")

def print_analysis_methodology():
    print("\n\n⚖️  ETHICAL CONSIDERATIONS")
    print("=" * 30)
    
    print("\n🤔 Important Notes:")
    print("- Avoid reinforcing national stereotypes")
    print("- Consider cultural differences in work-life balance values")
    print("- Distinguish between 'laziness' and different cultural priorities")
    print("- Include socioeconomic context in interpretation")
    print("- Present findings with appropriate nuance and context")
    
    print("\n🎯 Focus on Constructive Analysis:")
    print("- Identify factors that promote engagement")
    print("- Understand systemic vs. individual factors")
    print("- Provide actionable insights for policy")

def main():
