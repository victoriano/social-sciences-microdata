#!/usr/bin/env python3
"""
Memory-Efficient PISA Data Processor
===================================

This script processes PISA data with aggressive memory optimization for large datasets.
Processes one year at a time with essential variables only.

Features:
- Ultra-memory efficient processing
- Processes years individually 
- Focuses on essential target variables only
- Creates both individual year files and combined dataset
- Spanish student filtering

Usage:
    uv run python memory_efficient_processor.py
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

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryEfficientPISAProcessor:
    """Memory-efficient PISA processor for large datasets."""
    
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
        
        # Essential variables only (most important for analysis)
        self.essential_variables = {
            # Core IDs
            'CNTSTUID': 'Student ID',
            'CNT': 'Country',
            'CNTSCHID': 'School ID',
            
            # Demographics
            'AGE': 'Age',
            'ST004D01T': 'Gender',
            
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
        
        # Country mappings for Spain
        self.spain_codes = ['ESP', 'Spain', 'ES', '724']
        
        # Available years
        self.available_years = self.detect_available_years()
        
        logger.info(f"🚀 Memory-efficient processor initialized for {len(self.available_years)} years")
    
    def detect_available_years(self) -> List[int]:
        """Detect available years."""
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
        """Check for PISA files."""
        patterns = ['*.sav', '*STU*.sav']
        for pattern in patterns:
            if list(year_dir.glob(pattern)) or any(list(subdir.glob(pattern)) for subdir in year_dir.iterdir() if subdir.is_dir()):
                return True
        return False
    
    def find_student_file(self, year: int) -> Optional[Path]:
        """Find main student questionnaire file for year."""
        year_dir = self.raw_dir / str(year)
        
        # Search patterns
        patterns = [
            '*STU_QQQ*.sav', '*STU*.sav', 'stu_*_converted.sav'
        ]
        
        search_dirs = [year_dir] + [d for d in year_dir.iterdir() if d.is_dir()]
        
        for search_dir in search_dirs:
            for pattern in patterns:
                files = list(search_dir.glob(pattern))
                if files:
                    return files[0]
        
        return None
    
    def load_essential_variables(self, file_path: Path, year: int) -> Optional[pl.DataFrame]:
        """Load only essential variables from SAV file."""
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
    
    def enhance_minimal(self, df: pl.DataFrame) -> pl.DataFrame:
        """Add minimal enhancements."""
        logger.info("   🔧 Adding essential enhancements...")
        
        df_enhanced = df
        
        # Convert gender (handle different data types by casting to string first)
        if 'ST004D01T' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.col('ST004D01T').cast(pl.String).alias('ST004D01T_str')
            ])
            
            df_enhanced = df_enhanced.with_columns([
                pl.when(
                    (pl.col('ST004D01T_str') == '1') |
                    (pl.col('ST004D01T_str').str.contains('(?i)female'))
                )
                .then(pl.lit('Female'))
                .when(
                    (pl.col('ST004D01T_str') == '2') |
                    (pl.col('ST004D01T_str').str.contains('(?i)male'))
                )
                .then(pl.lit('Male'))
                .otherwise(pl.lit('Unknown'))
                .alias('sex')
            ]).drop('ST004D01T_str')
        
        # Country name (simplified)
        if 'CNT' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.when(pl.col('CNT').cast(pl.String).is_in(['ESP', 'ES', '724']))
                .then(pl.lit('Spain'))
                .otherwise(pl.col('CNT').cast(pl.String))
                .alias('country_name')
            ])
        
        # Overall performance
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
        
        # Enhance minimally
        df = self.enhance_minimal(df)
        
        # Save individual year file
        output_file = self.individual_dir / f"pisa_{year}_essential.parquet"
        df.write_parquet(output_file, compression='zstd')
        
        logger.info(f"✅ PISA {year}: {len(df):,} students, {len(df.columns)} variables")
        logger.info(f"💾 Saved: {output_file.name}")
        
        # Force cleanup
        del df
        gc.collect()
        
        return True
    
    def combine_years(self) -> None:
        """Combine individual year files."""
        logger.info("\n🔗 Combining all years...")
        
        # Load individual year files
        year_files = list(self.individual_dir.glob("pisa_*_essential.parquet"))
        if not year_files:
            logger.error("❌ No individual year files found")
            return
        
        year_dfs = []
        for file_path in sorted(year_files):
            logger.info(f"   📥 Loading {file_path.name}")
            df = pl.read_parquet(file_path)
            year_dfs.append(df)
        
        # Combine
        combined_df = pl.concat(year_dfs, how='diagonal')
        
        years = sorted(combined_df['pisa_year'].unique().to_list())
        year_range = f"{min(years)}_{max(years)}"
        
        logger.info(f"✅ Combined: {len(combined_df):,} students across {len(years)} years")
        
        # Save combined dataset
        combined_file = self.combined_dir / f"pisa_essential_{year_range}.parquet"
        combined_df.write_parquet(combined_file, compression='zstd')
        logger.info(f"💾 Combined dataset: {combined_file.name}")
        
        # Create Spain dataset
        spain_filter = pl.lit(False)
        for col in ['CNT', 'country_name']:
            if col in combined_df.columns:
                spain_filter = spain_filter | pl.col(col).cast(pl.String).is_in(self.spain_codes)
        
        spain_df = combined_df.filter(spain_filter)
        
        if len(spain_df) > 0:
            spain_file = self.spain_dir / f"spain_essential_{year_range}.parquet"
            spain_df.write_parquet(spain_file, compression='zstd')
            logger.info(f"🇪🇸 Spain dataset: {spain_file.name} ({len(spain_df):,} students)")
            
            # Spain summary
            spain_summary = (spain_df
                           .group_by('pisa_year')
                           .agg([
                               pl.count().alias('students'),
                               pl.col('overall_performance').mean().alias('avg_performance'),
                               pl.col('ESCS').mean().alias('avg_escs')
                           ])
                           .sort('pisa_year'))
            
            logger.info("📊 Spain by year:")
            for row in spain_summary.iter_rows(named=True):
                logger.info(f"   {row['pisa_year']}: {row['students']:,} students")
        
        # Cleanup
        del combined_df, year_dfs
        if 'spain_df' in locals():
            del spain_df
        gc.collect()
    
    def run_processing(self) -> None:
        """Run memory-efficient processing."""
        logger.info("🚀 STARTING MEMORY-EFFICIENT PISA PROCESSING")
        logger.info("=" * 60)
        logger.info(f"📅 Available years: {self.available_years}")
        
        if not self.available_years:
            logger.error("❌ No PISA data found")
            return
        
        # Process each year individually
        successful_years = []
        for year in self.available_years:
            if self.process_single_year(year):
                successful_years.append(year)
        
        if not successful_years:
            logger.error("❌ No years processed successfully")
            return
        
        # Combine all years
        self.combine_years()
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Successfully processed: {len(successful_years)} years")
        logger.info(f"📊 Years: {successful_years}")
        logger.info(f"📁 Individual files: individual_years/")
        logger.info(f"🌍 Combined dataset: combined/")
        logger.info(f"🇪🇸 Spain dataset: spain/")
        logger.info(f"\n🎉 Memory-efficient processing complete!")
        logger.info(f"Essential variables extracted for comprehensive analysis")

def main():
    """Main function."""
    print("🚀 **Memory-Efficient PISA Processor**")
    print("📊 Processing large PISA datasets with aggressive memory optimization")
    
    processor = MemoryEfficientPISAProcessor()
    processor.run_processing()

if __name__ == "__main__":
    main() 