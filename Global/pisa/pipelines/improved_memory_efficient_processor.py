#!/usr/bin/env python3
"""
Improved Memory-Efficient PISA Data Processor
============================================

This script processes PISA data with all fixes for data quality issues and adds year selection.

New Features:
- Includes 2022 data (handles different directory structure)
- Fixed country name mapping 
- Handles missing gender variables gracefully
- Command-line year selection support
- Improved data quality checks

Usage:
    uv run python improved_memory_efficient_processor.py                    # Process all years
    uv run python improved_memory_efficient_processor.py --years 2015 2018  # Process specific years
    uv run python improved_memory_efficient_processor.py --years 2022       # Process only 2022
"""

import polars as pl
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import json
from typing import Dict, List, Optional
import sys
import gc
import warnings
import argparse

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedPISAProcessor:
    """Improved memory-efficient PISA processor with all fixes."""
    
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        """Initialize processor."""
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create output directories
        self.individual_dir = self.processed_dir / "individual_years"
        self.combined_dir = self.processed_dir / "combined"
        self.spain_dir = self.processed_dir / "spain"
        
        for dir_path in [self.individual_dir, self.combined_dir, self.spain_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Essential variables (most important for analysis)
        self.essential_variables = {
            # Core IDs
            'CNTSTUID': 'Student ID',
            'CNT': 'Country',
            'CNTSCHID': 'School ID',
            
            # Demographics (different variable names across years)
            'AGE': 'Age',
            'ST004D01T': 'Gender (2015+)',
            'ST04Q01': 'Gender (2012-)',
            'ST003D01T': 'Gender (alternative)',
            'GENDER': 'Gender (converted)',
            
            # Socioeconomic (available across most years)
            'ESCS': 'Economic Social Cultural Status',
            'WEALTH': 'Wealth Index',
            'HOMEPOS': 'Home Possessions',
            'PARED': 'Parental Education',
            
            # Performance (one per domain)
            'PV1MATH': 'Math Score',
            'PV1READ': 'Reading Score', 
            'PV1SCIE': 'Science Score',
            
            # Key motivation variables
            'JOYREAD': 'Joy of Reading',
            'SCIEEFF': 'Science Self-Efficacy',
            'BELONG': 'School Belonging'
        }
        
        # Complete country mappings
        self.country_mappings = self._get_comprehensive_country_mappings()
        
        # Spain codes for filtering
        self.spain_codes = ['ESP', 'Spain', 'ES', '724']
        
        # Available years
        self.available_years = self.detect_available_years()
        
        logger.info(f"🚀 Improved processor initialized for {len(self.available_years)} years")
    
    def _get_comprehensive_country_mappings(self) -> Dict[str, str]:
        """Complete country code to name mappings."""
        return {
            # Major countries
            'ESP': 'Spain', 'Spain': 'Spain', 'ES': 'Spain', '724': 'Spain',
            'DEU': 'Germany', 'GER': 'Germany', 'Germany': 'Germany',
            'FRA': 'France', 'France': 'France',
            'ITA': 'Italy', 'Italy': 'Italy',
            'GBR': 'United Kingdom', 'United Kingdom': 'United Kingdom',
            'USA': 'United States', 'United States': 'United States',
            'JPN': 'Japan', 'Japan': 'Japan',
            'KOR': 'South Korea', 'South Korea': 'South Korea',
            
            # Nordic countries
            'FIN': 'Finland', 'Finland': 'Finland',
            'SWE': 'Sweden', 'Sweden': 'Sweden',
            'NOR': 'Norway', 'Norway': 'Norway',
            'DNK': 'Denmark', 'Denmark': 'Denmark',
            'ISL': 'Iceland', 'Iceland': 'Iceland',
            
            # Other European countries
            'NLD': 'Netherlands', 'Netherlands': 'Netherlands',
            'BEL': 'Belgium', 'Belgium': 'Belgium',
            'AUT': 'Austria', 'Austria': 'Austria',
            'CHE': 'Switzerland', 'Switzerland': 'Switzerland',
            'IRL': 'Ireland', 'Ireland': 'Ireland',
            'LUX': 'Luxembourg', 'Luxembourg': 'Luxembourg',
            'PRT': 'Portugal', 'Portugal': 'Portugal',
            'GRC': 'Greece', 'Greece': 'Greece',
            
            # Eastern Europe
            'POL': 'Poland', 'Poland': 'Poland',
            'CZE': 'Czech Republic', 'Czech Republic': 'Czech Republic',
            'HUN': 'Hungary', 'Hungary': 'Hungary',
            'SVK': 'Slovakia', 'Slovakia': 'Slovakia',
            'SVN': 'Slovenia', 'Slovenia': 'Slovenia',
            'EST': 'Estonia', 'Estonia': 'Estonia',
            'LVA': 'Latvia', 'Latvia': 'Latvia',
            'LTU': 'Lithuania', 'Lithuania': 'Lithuania',
            'BGR': 'Bulgaria', 'Bulgaria': 'Bulgaria',
            'ROU': 'Romania', 'Romania': 'Romania',
            'HRV': 'Croatia', 'Croatia': 'Croatia',
            'SRB': 'Serbia', 'Serbia': 'Serbia',
            'MNE': 'Montenegro', 'Montenegro': 'Montenegro',
            'MKD': 'North Macedonia', 'North Macedonia': 'North Macedonia',
            'BIH': 'Bosnia and Herzegovina', 'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
            'ALB': 'Albania', 'Albania': 'Albania',
            
            # Post-Soviet countries
            'RUS': 'Russia', 'Russia': 'Russia',
            'UKR': 'Ukraine', 'Ukraine': 'Ukraine',
            'MDA': 'Moldova', 'Moldova': 'Moldova',
            'GEO': 'Georgia', 'Georgia': 'Georgia',
            'AZE': 'Azerbaijan', 'Azerbaijan': 'Azerbaijan',
            'KAZ': 'Kazakhstan', 'Kazakhstan': 'Kazakhstan',
            'KGZ': 'Kyrgyzstan', 'Kyrgyzstan': 'Kyrgyzstan',
            
            # Americas
            'CAN': 'Canada', 'Canada': 'Canada',
            'MEX': 'Mexico', 'Mexico': 'Mexico',
            'BRA': 'Brazil', 'Brazil': 'Brazil',
            'ARG': 'Argentina', 'Argentina': 'Argentina',
            'CHL': 'Chile', 'Chile': 'Chile',
            'PER': 'Peru', 'Peru': 'Peru',
            'COL': 'Colombia', 'Colombia': 'Colombia',
            'URY': 'Uruguay', 'Uruguay': 'Uruguay',
            'CRI': 'Costa Rica', 'Costa Rica': 'Costa Rica',
            'DOM': 'Dominican Republic', 'Dominican Republic': 'Dominican Republic',
            'GTM': 'Guatemala', 'Guatemala': 'Guatemala',
            'PAN': 'Panama', 'Panama': 'Panama',
            
            # Asia-Pacific
            'AUS': 'Australia', 'Australia': 'Australia',
            'NZL': 'New Zealand', 'New Zealand': 'New Zealand',
            'CHN': 'China', 'China': 'China',
            'HKG': 'Hong Kong', 'Hong Kong': 'Hong Kong',
            'MAC': 'Macao', 'Macao': 'Macao',
            'TAP': 'Chinese Taipei', 'Chinese Taipei': 'Chinese Taipei',
            'SGP': 'Singapore', 'Singapore': 'Singapore',
            'THA': 'Thailand', 'Thailand': 'Thailand',
            'MYS': 'Malaysia', 'Malaysia': 'Malaysia',
            'IDN': 'Indonesia', 'Indonesia': 'Indonesia',
            'VNM': 'Vietnam', 'Vietnam': 'Vietnam',
            'PHL': 'Philippines', 'Philippines': 'Philippines',
            
            # Middle East
            'TUR': 'Turkey', 'Turkey': 'Turkey',
            'ISR': 'Israel', 'Israel': 'Israel',
            'QAT': 'Qatar', 'Qatar': 'Qatar',
            'ARE': 'United Arab Emirates', 'United Arab Emirates': 'United Arab Emirates',
            'JOR': 'Jordan', 'Jordan': 'Jordan',
            'LBN': 'Lebanon', 'Lebanon': 'Lebanon',
            
            # Africa
            'TUN': 'Tunisia', 'Tunisia': 'Tunisia',
            
            # Regional aggregates (common in PISA data)
            'Spain (Regions)': 'Spain',
            'Germany (Regions)': 'Germany',
            'Italy (Regions)': 'Italy',
            'B-S-J-G (China)': 'China',
            'B-S-J-Z (China)': 'China'
        }
    
    def detect_available_years(self) -> List[int]:
        """Detect available years including 2022."""
        if not self.raw_dir.exists():
            return []
        
        years = []
        for item in self.raw_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                year = int(item.name)
                if self.has_pisa_files(item):
                    years.append(year)
        
        return sorted(years)
    
    def has_pisa_files(self, year_dir: Path) -> bool:
        """Check for PISA files including 2022 structure (case-insensitive)."""
        patterns = ['*.sav', '*.SAV', '*STU*.sav', '*STU*.SAV']
        
        # Check main directory
        for pattern in patterns:
            if list(year_dir.glob(pattern)):
                return True
        
        # Check subdirectories (including 2022 structure)
        for subdir in year_dir.iterdir():
            if subdir.is_dir():
                for pattern in patterns:
                    if list(subdir.glob(pattern)):
                        return True
        
        return False
    
    def find_student_file(self, year: int) -> Optional[Path]:
        """Find main student questionnaire file including 2022."""
        year_dir = self.raw_dir / str(year)
        
        # 2022 has different structure
        if year == 2022:
            student_dir = year_dir / "student_questionnaire"
            if student_dir.exists():
                patterns = ['*STU_QQQ*.sav', '*STU_QQQ*.SAV', '*STU*.sav', '*STU*.SAV']
                for pattern in patterns:
                    files = list(student_dir.glob(pattern))
                    if files:
                        return files[0]
        
        # Standard structure for other years
        patterns = [
            '*STU_QQQ*.sav', '*STU_QQQ*.SAV', '*STU*.sav', '*STU*.SAV', 'stu_*_converted.sav'
        ]
        
        search_dirs = [year_dir] + [d for d in year_dir.iterdir() if d.is_dir()]
        
        for search_dir in search_dirs:
            for pattern in patterns:
                files = list(search_dir.glob(pattern))
                if files:
                    return files[0]
        
        return None
    
    def load_essential_variables(self, file_path: Path, year: int) -> Optional[pl.DataFrame]:
        """Load only essential variables from SAV file with improved handling."""
        try:
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            logger.info(f"📂 Loading {file_path.name} ({file_size_mb:.1f} MB)")
            
            # Get available columns
            logger.info("   🔍 Checking available columns...")
            df_sample = pd.read_spss(str(file_path), usecols=None)
            available_cols = list(df_sample.columns)
            del df_sample  # Free memory immediately
            gc.collect()
            
            # Find essential variables that exist
            found_vars = []
            for var in self.essential_variables.keys():
                if var in available_cols:
                    found_vars.append(var)
            
            if not found_vars:
                logger.warning(f"   ⚠️  No essential variables found")
                return None
            
            logger.info(f"   ✅ Loading {len(found_vars)} essential variables")
            
            # Read only essential variables
            df = pd.read_spss(str(file_path), usecols=found_vars)
            
            # Convert data types for Polars compatibility
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str)
                elif 'Int' in str(df[col].dtype):
                    df[col] = df[col].astype('float64')
            
            # Convert to Polars
            df_pl = pl.from_pandas(df)
            del df  # Free pandas memory
            gc.collect()
            
            # Add year
            df_pl = df_pl.with_columns([pl.lit(year).alias('pisa_year')])
            
            logger.info(f"   📊 Loaded: {len(df_pl):,} students, {len(df_pl.columns)} variables")
            return df_pl
            
        except Exception as e:
            logger.error(f"   ❌ Error loading {file_path.name}: {e}")
            return None
    
    def enhance_data_improved(self, df: pl.DataFrame, year: int) -> pl.DataFrame:
        """Enhanced data processing with improved country and gender handling."""
        logger.info(f"   🔧 Enhancing {year} data with improved logic...")
        
        df_enhanced = df
        
        # Enhanced gender conversion (handles different variable names)
        gender_vars = ['ST004D01T', 'ST04Q01', 'ST003D01T', 'GENDER']
        gender_var = None
        
        for var in gender_vars:
            if var in df.columns:
                gender_var = var
                break
        
        if gender_var:
            logger.info(f"   📊 Found gender variable: {gender_var}")
            
            # Create string version first to avoid type issues
            df_enhanced = df_enhanced.with_columns([
                pl.col(gender_var).cast(pl.String, strict=False).alias('gender_str')
            ])
            
            # Apply gender mapping (handle both string and numeric values)
            df_enhanced = df_enhanced.with_columns([
                pl.when(
                    (pl.col('gender_str') == '1') | (pl.col('gender_str') == '1.0') |
                    (pl.col('gender_str').str.contains('(?i)female'))
                )
                .then(pl.lit('Female'))
                .when(
                    (pl.col('gender_str') == '2') | (pl.col('gender_str') == '2.0') |
                    (pl.col('gender_str').str.contains('(?i)male'))
                )
                .then(pl.lit('Male'))
                .otherwise(pl.lit('Unknown'))
                .alias('sex')
            ]).drop('gender_str')
        else:
            logger.warning(f"   ⚠️  No gender variable found for {year}")
            df_enhanced = df_enhanced.with_columns([
                pl.lit('Unknown').alias('sex')
            ])
        
        # Enhanced country name mapping
        if 'CNT' in df.columns:
            logger.info(f"   🌍 Mapping country names...")
            
            # Start with original country code
            df_enhanced = df_enhanced.with_columns([
                pl.col('CNT').cast(pl.String, strict=False).alias('country_name')
            ])
            
            # Apply comprehensive country mappings
            country_expr = pl.col('country_name')
            for code, name in self.country_mappings.items():
                country_expr = country_expr.str.replace_all(f"^{code}$", name)
            
            df_enhanced = df_enhanced.with_columns([
                country_expr.alias('country_name')
            ])
        
        # Overall performance calculation
        score_cols = ['PV1MATH', 'PV1READ', 'PV1SCIE']
        available_scores = [col for col in score_cols if col in df.columns]
        if len(available_scores) >= 2:
            avg_expr = pl.concat_list([pl.col(col) for col in available_scores]).list.mean()
            df_enhanced = df_enhanced.with_columns([
                avg_expr.alias('overall_performance')
            ])
        
        # SES category
        if 'ESCS' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.when(pl.col('ESCS') >= 0.5)
                .then(pl.lit('High SES'))
                .when(pl.col('ESCS') >= -0.5)
                .then(pl.lit('Medium SES'))
                .otherwise(pl.lit('Low SES'))
                .alias('ses_category')
            ])
        
        logger.info(f"   ✅ Enhanced: {len(df_enhanced.columns)} total variables")
        return df_enhanced
    
    def process_single_year(self, year: int) -> bool:
        """Process a single year efficiently."""
        logger.info(f"\n🔄 Processing PISA {year}...")
        logger.info("=" * 40)
        
        # Find student file
        student_file = self.find_student_file(year)
        if not student_file:
            logger.warning(f"❌ No student file found for {year}")
            return False
        
        # Load essential variables
        df = self.load_essential_variables(student_file, year)
        if df is None:
            logger.warning(f"❌ Failed to load data for {year}")
            return False
        
        # Enhanced processing
        df = self.enhance_data_improved(df, year)
        
        # Save individual year file
        output_file = self.individual_dir / f"pisa_{year}_improved.parquet"
        df.write_parquet(output_file, compression='zstd')
        
        logger.info(f"✅ PISA {year}: {len(df):,} students, {len(df.columns)} variables")
        logger.info(f"💾 Saved: {output_file.name}")
        
        # Force cleanup
        del df
        gc.collect()
        
        return True
    
    def combine_years(self, years_processed: List[int]) -> None:
        """Combine individual year files with data type harmonization."""
        logger.info("\n🔗 Combining all processed years...")
        
        # Load individual year files
        year_files = []
        for year in years_processed:
            file_path = self.individual_dir / f"pisa_{year}_improved.parquet"
            if file_path.exists():
                year_files.append(file_path)
        
        if not year_files:
            logger.error("❌ No improved year files found")
            return
        
        year_dfs = []
        for file_path in sorted(year_files):
            logger.info(f"   📥 Loading {file_path.name}")
            df = pl.read_parquet(file_path)
            
            # Harmonize data types - cast categorical to string
            df_harmonized = df.clone()
            for col in df.columns:
                if df[col].dtype == pl.Categorical:
                    df_harmonized = df_harmonized.with_columns(
                        pl.col(col).cast(pl.String).alias(col)
                    )
            
            year_dfs.append(df_harmonized)
            logger.info(f"   • {len(df):,} students, {len(df.columns)} variables")
        
        # Combine
        combined_df = pl.concat(year_dfs, how='diagonal')
        
        years = sorted(combined_df['pisa_year'].unique().to_list())
        year_range = f"{min(years)}_{max(years)}"
        total_students = len(combined_df)
        
        logger.info(f"✅ Combined dataset: {total_students:,} students across {len(years)} years ({min(years)}-{max(years)})")
        
        # Save combined international dataset
        combined_file = self.combined_dir / f"pisa_improved_{year_range}.parquet"
        combined_df.write_parquet(combined_file, compression='zstd')
        logger.info(f"💾 International dataset: {combined_file.name}")
        
        # Create Spain dataset
        logger.info("🇪🇸 Creating Spain dataset...")
        
        spain_filter = pl.lit(False)
        for col in ['CNT', 'country_name']:
            if col in combined_df.columns:
                spain_filter = spain_filter | pl.col(col).cast(pl.String).is_in(self.spain_codes)
        
        spain_df = combined_df.filter(spain_filter)
        
        if len(spain_df) > 0:
            spain_file = self.spain_dir / f"spain_improved_{year_range}.parquet"
            spain_df.write_parquet(spain_file, compression='zstd')
            logger.info(f"💾 Spain dataset: {spain_file.name} ({len(spain_df):,} students)")
            
            # Spain summary by year (only include columns that exist)
            agg_exprs = [pl.len().alias('students')]
            
            if 'overall_performance' in spain_df.columns:
                agg_exprs.append(pl.col('overall_performance').mean().alias('avg_performance'))
            if 'ESCS' in spain_df.columns:
                agg_exprs.append(pl.col('ESCS').mean().alias('avg_escs'))
            if 'WEALTH' in spain_df.columns:
                agg_exprs.append(pl.col('WEALTH').mean().alias('avg_wealth'))
            
            spain_summary = (spain_df
                           .group_by('pisa_year')
                           .agg(agg_exprs)
                           .sort('pisa_year'))
            
            logger.info("📊 Spain by year:")
            for row in spain_summary.iter_rows(named=True):
                parts = [f"{row['pisa_year']}: {row['students']:,} students"]
                if 'avg_performance' in row and row['avg_performance']:
                    parts.append(f"performance: {row['avg_performance']:.1f}")
                if 'avg_escs' in row and row['avg_escs']:
                    parts.append(f"ESCS: {row['avg_escs']:.2f}")
                if 'avg_wealth' in row and row['avg_wealth']:
                    parts.append(f"WEALTH: {row['avg_wealth']:.2f}")
                logger.info(f"   {', '.join(parts)}")
        else:
            logger.warning("⚠️  No Spanish students found")
        
        # Cleanup
        del combined_df, year_dfs
        if 'spain_df' in locals():
            del spain_df
        gc.collect()
    
    def run_processing(self, selected_years: Optional[List[int]] = None) -> None:
        """Run improved processing with optional year selection."""
        if selected_years:
            years_to_process = [year for year in selected_years if year in self.available_years]
            logger.info(f"🎯 Processing selected years: {years_to_process}")
        else:
            years_to_process = self.available_years
            logger.info(f"🔄 Processing all available years: {years_to_process}")
        
        logger.info("🚀 STARTING IMPROVED PISA PROCESSING")
        logger.info("=" * 60)
        
        if not years_to_process:
            logger.error("❌ No years to process")
            return
        
        # Process each year individually
        successful_years = []
        for year in years_to_process:
            if self.process_single_year(year):
                successful_years.append(year)
        
        if not successful_years:
            logger.error("❌ No years processed successfully")
            return
        
        # Combine all years
        self.combine_years(successful_years)
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 IMPROVED PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Successfully processed: {len(successful_years)} years")
        logger.info(f"📊 Years: {successful_years}")
        logger.info(f"📁 Individual files: individual_years/pisa_YEAR_improved.parquet")
        logger.info(f"🌍 Combined dataset: combined/pisa_improved_*.parquet")
        logger.info(f"🇪🇸 Spain dataset: spain/spain_improved_*.parquet")
        logger.info(f"\n🎉 Improved processing complete with all fixes!")
        logger.info(f"✅ Includes 2022 data, fixed country names, and proper gender variables")

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Improved PISA data processor with year selection")
    parser.add_argument("--years", nargs="+", type=int, help="Specific years to process (e.g., --years 2015 2018 2022)")
    
    args = parser.parse_args()
    
    print("🚀 **Improved Memory-Efficient PISA Processor**")
    print("📊 Processing PISA data with all quality fixes")
    if args.years:
        print(f"🎯 Selected years: {args.years}")
    
    processor = ImprovedPISAProcessor()
    processor.run_processing(selected_years=args.years)

if __name__ == "__main__":
    main() 