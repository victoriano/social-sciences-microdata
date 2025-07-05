#!/usr/bin/env python3
"""
Youth Work and Study Patterns Analysis
======================================

This script analyzes whether young people in Spain show different work and study 
patterns compared to their international peers using objective data.

Data Sources:
- PISA: Educational performance and attitudes
- OECD: Various youth-related statistics
- Eurostat: Employment and education data
"""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouthAnalysis:
    """Main class for analyzing youth work and study patterns."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the analysis with a data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different data sources
        (self.data_dir / "Global" / "pisa").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "Global" / "oecd").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "Europe" / "eurostat").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def get_pisa_data_info(self) -> Dict:
        """Get information about available PISA datasets."""
        pisa_info = {
            "pisa_2022": {
                "description": "Most recent PISA data",
                "url": "https://www.oecd.org/pisa/data/2022database/",
                "key_variables": [
                    "Student performance in Reading, Mathematics, Science",
                    "Student background questionnaire",
                    "School questionnaire", 
                    "Time spent on homework and study",
                    "Attitudes toward learning",
                    "Career aspirations"
                ]
            },
            "pisa_2018": {
                "description": "PISA 2018 with focus on reading",
                "url": "https://www.oecd.org/pisa/data/2018database/",
                "key_variables": [
                    "Reading literacy performance",
                    "Student engagement and motivation",
                    "Learning time and strategies"
                ]
            }
        }
        return pisa_info
    
    def download_pisa_data(self, year: int = 2022) -> bool:
        """
        Download PISA data for specified year.
        Note: PISA data is large and requires manual download from OECD website.
        """
        logger.info(f"PISA {year} data needs to be downloaded manually from:")
        logger.info(f"https://www.oecd.org/pisa/data/{year}database/")
        
        # Create instructions file
        instructions_file = self.data_dir / "Global" / "pisa" / f"pisa_{year}_download_instructions.txt"
        with open(instructions_file, 'w') as f:
            f.write(f"PISA {year} Data Download Instructions\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"1. Visit: https://www.oecd.org/pisa/data/{year}database/\n")
            f.write("2. Download the Student questionnaire data file (SAS or SPSS format)\n")
            f.write("3. Look for files containing:\n")
            f.write("   - Student performance data\n")
            f.write("   - Student background questionnaire\n")
            f.write("   - School questionnaire\n")
            f.write("4. Save files in the data/Global/pisa/ directory\n")
            f.write("5. Key variables to focus on:\n")
            f.write("   - ESCS: Economic, social and cultural status\n")
            f.write("   - TMINS: Time spent on homework\n")
            f.write("   - MOTIVAT: Motivation indicators\n")
            f.write("   - BELONG: Sense of belonging at school\n")
            f.write("   - Country codes: ESP (Spain), compare with other EU countries\n")
        
        logger.info(f"Download instructions saved to: {instructions_file}")
        return True
    
    def get_eurostat_data(self) -> pl.DataFrame:
        """Download youth employment and education data from Eurostat API."""
        logger.info("Downloading Eurostat youth employment data...")
        
        # Youth unemployment rate (ages 15-24)
        url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_a"
        params = {
            'format': 'JSON',
            'lang': 'en',
            'age': 'Y15-24',
            'unit': 'PC_ACT',
            'geo': 'EU27_2020,ES,DE,FR,IT,PT,GR',  # Spain vs other EU countries
            'time': '2015:2023'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process the data (this is a simplified example)
            # In reality, you'd need to parse the complex JSON structure
            logger.info("Successfully downloaded Eurostat data")
            return pl.DataFrame()  # Placeholder
            
        except requests.RequestException as e:
            logger.error(f"Error downloading Eurostat data: {e}")
            return pl.DataFrame()
    
    def analyze_work_attitudes(self, df: pl.DataFrame) -> Dict:
        """Analyze work-related attitudes and behaviors."""
        if df.is_empty():
            logger.warning("No data available for work attitudes analysis")
            return {}
        
        # This would contain actual analysis once data is loaded
        analysis_results = {
            "spain_vs_eu_avg": {},
            "key_findings": [],
            "statistical_tests": {}
        }
        
        return analysis_results
    
    def analyze_study_patterns(self, df: pl.DataFrame) -> Dict:
        """Analyze study patterns and educational engagement."""
        if df.is_empty():
            logger.warning("No data available for study patterns analysis")
            return {}
        
        # Analysis framework for study patterns
        study_metrics = [
            "time_spent_homework",
            "school_engagement_score", 
            "learning_motivation",
            "academic_performance",
            "educational_aspirations"
        ]
        
        analysis_results = {
            "spain_rankings": {},
            "peer_comparisons": {},
            "trend_analysis": {},
            "correlation_analysis": {}
        }
        
        return analysis_results
    
    def create_visualizations(self, spain_data: Dict, comparison_data: Dict) -> None:
        """Create comprehensive visualizations of the analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Youth Work and Study Patterns: Spain vs International Comparison', 
                    fontsize=16, fontweight='bold')
        
        # Placeholder visualizations (would use real data)
        
        # 1. Study time comparison
        axes[0, 0].set_title('Average Study Time per Week')
        axes[0, 0].set_ylabel('Hours per week')
        
        # 2. Work attitudes comparison  
        axes[0, 1].set_title('Work Motivation Scores')
        axes[0, 1].set_ylabel('Motivation Index')
        
        # 3. Academic performance trends
        axes[1, 0].set_title('Academic Performance Trends')
        axes[1, 0].set_ylabel('PISA Score')
        
        # 4. Employment patterns
        axes[1, 1].set_title('Youth Employment Rates')
        axes[1, 1].set_ylabel('Employment Rate (%)')
        
        plt.tight_layout()
        plt.savefig(self.data_dir / "youth_analysis_overview.png", dpi=300, bbox_inches='tight')
        logger.info("Visualizations saved to youth_analysis_overview.png")
        
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        report = """
# Youth Work and Study Patterns Analysis Report

## Executive Summary
This analysis examines whether young people in Spain demonstrate different work and study patterns compared to their international peers using objective data from multiple sources.

## Key Findings

### Educational Engagement
- [Results would be populated with actual analysis]

### Work Attitudes and Behaviors  
- [Results would be populated with actual analysis]

### Cross-Country Comparisons
- [Results would be populated with actual analysis]

## Methodology
1. **Data Sources**: PISA educational assessment, Eurostat employment data, OECD statistics
2. **Analysis Period**: 2015-2023 (latest available data)
3. **Countries Compared**: Spain vs EU27 average, Germany, France, Italy, Portugal
4. **Statistical Methods**: Descriptive statistics, regression analysis, trend analysis

## Recommendations for Further Analysis
1. Include additional time-use survey data
2. Analyze regional variations within Spain
3. Control for socioeconomic factors
4. Examine generational differences

## Data Sources and Limitations
- PISA data provides robust educational metrics but is collected every 3 years
- Eurostat data offers comprehensive employment statistics
- Cultural and contextual factors may influence cross-country comparisons
"""
        
        report_file = self.data_dir / "analysis_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Analysis report saved to: {report_file}")
        return report

def main():
    """Main execution function."""
    print("🔍 Youth Work and Study Patterns Analysis")
    print("=" * 50)
    
    # Initialize analysis
    analysis = YouthAnalysis()
    
    # Show available datasets
    print("\n📊 Available Data Sources:")
    pisa_info = analysis.get_pisa_data_info()
    for dataset, info in pisa_info.items():
        print(f"\n{dataset.upper()}:")
        print(f"  Description: {info['description']}")
        print(f"  URL: {info['url']}")
        print("  Key Variables:")
        for var in info['key_variables']:
            print(f"    - {var}")
    
    # Create download instructions
    print("\n📥 Setting up data download instructions...")
    analysis.download_pisa_data(2022)
    
    # Try to get some sample data
    print("\n🌐 Attempting to download Eurostat data...")
    eurostat_data = analysis.get_eurostat_data()
    
    # Generate sample visualizations
    print("\n📈 Creating sample visualizations...")
    analysis.create_visualizations({}, {})
    
    # Generate report template
    print("\n📋 Generating analysis report template...")
    report = analysis.generate_report()
    
    print("\n✅ Setup complete! Next steps:")
    print("1. Download PISA data manually (see instructions in data/Global/pisa/)")
    print("2. Run the analysis with: python youth_analysis.py")
    print("3. Review the generated report and visualizations")
    print("\n🎯 This framework provides a solid foundation for objective analysis of youth work and study patterns!")

if __name__ == "__main__":
    main() 