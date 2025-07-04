#!/usr/bin/env python3
"""
Comprehensive Guide to Youth Work and Study Data Sources
========================================================

This script provides detailed information about accessing high-quality microdata
for analyzing youth work and study patterns, with a focus on Spain.
"""

def print_pisa_microdata_guide():
    """Detailed guide for accessing PISA microdata."""
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
    """Guide for Eurostat microdata access."""
    print("\n\n🇪🇺 EUROSTAT MICRODATA - European Statistical System")
    print("=" * 60)
    
    print("\n📊 Key Datasets for Youth Analysis:")
    print("1. EU-LFS: European Union Labour Force Survey")
    print("   - Quarterly employment data for ages 15-24")
    print("   - Work patterns, job search behavior")
    print("   - Education-work transitions")
    print("   - Access: https://ec.europa.eu/eurostat/web/microdata")
    
    print("\n2. EU-SILC: Statistics on Income and Living Conditions")
    print("   - Household income and social conditions")
    print("   - Educational participation")
    print("   - Youth not in employment, education or training (NEET)")
    
    print("\n3. Adult Education Survey (AES)")
    print("   - Lifelong learning participation")
    print("   - Skills development attitudes")
    
    print("\n🔑 Key Variables for Work Attitudes:")
    print("- SEEKWORK: Job search intensity")
    print("- AVAISTAR: Availability to start work")
    print("- EDUCSTAT: Education status")
    print("- WORKTIME: Working time preferences")
    print("- TEMPREAS: Reasons for temporary work")

def print_oecd_additional_sources():
    """Information about additional OECD data sources."""
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
    """Information about time use surveys."""
    print("\n\n⏰ TIME USE SURVEYS - Direct Measurement of 'Laziness'")
    print("=" * 55)
    
    print("\n📊 Why Time Use Data is Crucial:")
    print("- Objective measurement of how young people spend their time")
    print("- Shows actual behavior vs. reported attitudes")
    print("- Can identify leisure vs. productive activities")
    
    print("\n🇪🇸 Spanish Time Use Survey (Encuesta de Empleo del Tiempo)")
    print("- Conducted by INE (Instituto Nacional de Estadística)")
    print("- Latest: 2009-2010 (new one planned)")
    print("- Shows time spent on:")
    print("  * Study and homework")
    print("  * Work (paid and unpaid)")
    print("  * Leisure activities")
    print("  * Social activities")
    print("  * Screen time")
    
    print("\n🌍 International Time Use Database:")
    print("- Centre for Time Use Research (Oxford)")
    print("- Harmonized multinational time use data")
    print("- Allows direct Spain vs. international comparisons")

def print_alternative_indicators():
    """Creative indicators for measuring work/study engagement."""
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
    """Methodology recommendations for the analysis."""
    print("\n\n🔬 RECOMMENDED ANALYSIS METHODOLOGY")
    print("=" * 45)
    
    print("\n1. DESCRIPTIVE ANALYSIS:")
    print("   - Compare Spain to OECD average and peer countries")
    print("   - Trend analysis over time (2015-2023)")
    print("   - Regional analysis within Spain")
    
    print("\n2. MULTIVARIATE ANALYSIS:")
    print("   - Control for socioeconomic factors (ESCS)")
    print("   - Gender and age differences")
    print("   - School/institutional effects")
    
    print("\n3. CAUSAL INFERENCE:")
    print("   - Propensity score matching")
    print("   - Instrumental variables if available")
    print("   - Difference-in-differences for policy changes")
    
    print("\n4. ROBUSTNESS CHECKS:")
    print("   - Multiple datasets (PISA + Eurostat + Time Use)")
    print("   - Different measures of 'laziness/engagement'")
    print("   - Sensitivity to outliers and missing data")

def print_ethical_considerations():
    """Important ethical considerations for the analysis."""
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
    """Run the complete data sources guide."""
    print("🔍 COMPREHENSIVE GUIDE TO YOUTH WORK & STUDY DATA")
    print("=" * 60)
    print("Objective Analysis of Youth Engagement Patterns in Spain")
    print("=" * 60)
    
    print_pisa_microdata_guide()
    print_eurostat_microdata_guide()
    print_oecd_additional_sources()
    print_time_use_surveys()
    print_alternative_indicators()
    print_analysis_methodology()
    print_ethical_considerations()
    
    print("\n\n🚀 GETTING STARTED:")
    print("1. Start with PISA 2022 microdata (strongest for your research question)")
    print("2. Supplement with Eurostat youth employment data")
    print("3. Add time use data if available")
    print("4. Use the analysis framework in youth_analysis.py")
    print("5. Consider cultural context in your interpretation")
    
    print("\n📧 Need Help? Contact:")
    print("- OECD PISA team: pisa@oecd.org")
    print("- Eurostat: estat-user-support@ec.europa.eu")
    print("- Spanish INE: www.ine.es")

if __name__ == "__main__":
    main() 