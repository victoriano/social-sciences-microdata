#!/usr/bin/env python3
"""
PISA Multi-Year Data Converter (Optimized)
==========================================

Converts PISA data from multiple years to standardized Parquet format
for trend analysis. Automatically detects all available years in raw data folder.

Features:
- Automatically detects all years available in raw data folder
- Processes multiple PISA years in batch
- Handles different file formats (2015-2025: .sav, 2012 and earlier: converted files)
- Creates harmonized variable mappings across years
- Efficient Parquet output with metadata
- Optimized for large files using Polars lazy frames

Usage:
    uv run python harmonize_trends.py
"""

import polars as pl
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple, Union
import sys
import time
import re

try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    HAS_PYREADSTAT = False
    print("⚠️ pyreadstat not found - will attempt CSV fallback for converted files")

# Note: This script works with locally available data in the raw folder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PISA_DATA_DIR = REPO_ROOT / "data" / "Global" / "pisa"

class PISATrendConverter:
    """Convert multi-year PISA data for trend analysis."""
    
    def __init__(self, raw_dir: Optional[str] = None, processed_dir: Optional[str] = None):
        """Initialize converter with data directories."""
        self.raw_dir = Path(raw_dir) if raw_dir else DEFAULT_PISA_DATA_DIR / "raw"
        self.processed_dir = Path(processed_dir) if processed_dir else DEFAULT_PISA_DATA_DIR / "processed"
        
        # Create output directories
        self.trend_dir = self.processed_dir / "trend_analysis"
        self.spain_dir = self.processed_dir / "spain_trends"
        
        for dir_path in [self.processed_dir, self.trend_dir, self.spain_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Automatically detect available years from raw data folder
        self.available_years = self.detect_available_years()
        
        # File format detection (will be determined dynamically)
        self.file_formats = self.determine_file_formats()
        
        # Key variables to harmonize across years
        self.key_variables = {
            # Core identifiers
            'student_id': ['CNTSTUID', 'STIDSTD', 'STUID', 'STDID', 'StIDStd'],
            'country': ['CNT', 'CNTRYID', 'COUNTRY'],
            'school_id': ['CNTSCHID', 'SCHOOLID', 'SCHID', 'SCID'],
            
            # Demographics  
            'gender': ['ST004D01T', 'ST04Q01', 'ST003D01T'],
            'age': ['AGE', 'ST003Q02TA', 'ST003D02T'],
            'grade': ['ST001D01T', 'ST01Q01'],
            
            # Socioeconomic
            'escs': ['ESCS'],  # Economic, social, cultural status
            'wealth': ['WEALTH'],
            'cultural': ['CULTPOSS'],
            
            # Key research variables
            'homework_time': ['TMINS', 'ST057Q01TA', 'ST57Q01', 'ST046Q01TA'],  # Homework minutes
            'motivation': ['MOTIVAT', 'MOTIVA'],
            'belong': ['BELONG'],  # School belonging
            'perseverance': ['PERSEV', 'GRIT'],
            
            # Performance scores
            'math_score': ['PV1MATH', 'PV2MATH', 'PV3MATH', 'PV4MATH', 'PV5MATH'],
            'read_score': ['PV1READ', 'PV2READ', 'PV3READ', 'PV4READ', 'PV5READ'],
            'science_score': ['PV1SCIE', 'PV2SCIE', 'PV3SCIE', 'PV4SCIE', 'PV5SCIE'],
        }
        
        logger.info(f"Initialized PISA converter with {len(self.available_years)} available years: {sorted(self.available_years)}")
    
    def detect_available_years(self) -> List[int]:
        """Automatically detect available PISA years from raw data directory."""
        if not self.raw_dir.exists():
            logger.warning(f"Raw data directory does not exist: {self.raw_dir}")
            return []
        
        available_years = []
        
        # Look for year directories (numeric folder names)
        for item in self.raw_dir.iterdir():
            if item.is_dir():
                # Check if directory name looks like a year (4 digits between 2000-2030)
                if re.match(r'^20[0-3][0-9]$', item.name):
                    try:
                        year = int(item.name)
                        # Check if directory contains PISA data files
                        if self.has_pisa_files(item):
                            available_years.append(year)
                            logger.info(f"Detected PISA year: {year}")
                        else:
                            logger.warning(f"Year directory {year} exists but contains no PISA data files")
                    except ValueError:
                        continue
        
        return sorted(available_years)
    
    def has_pisa_files(self, year_dir: Path) -> bool:
        """Check if a year directory contains PISA data files."""
        # Look for common PISA file patterns
        pisa_patterns = [
            # Modern .sav files
            '*STU_QQQ*.sav', '*STU_QQQ*.SAV',
            '*STU_COG*.sav', '*STU_COG*.SAV', 
            '*STU*.sav', '*STU*.SAV',
            '*COG*.sav', '*COG*.SAV',
            # Converted files
            'stu_*_converted.sav', 'stu_*_converted.csv',
            'cog_*_converted.sav', 'cog_*_converted.csv',
            # Any .sav files (fallback)
            '*.sav', '*.SAV'
        ]
        
        for pattern in pisa_patterns:
            if list(year_dir.glob(pattern)):
                return True
        
        # Also check subdirectories (organized by file type)
        for subdir in year_dir.iterdir():
            if subdir.is_dir():
                for pattern in pisa_patterns:
                    if list(subdir.glob(pattern)):
                        return True
        
        return False
    
    def determine_file_formats(self) -> Dict[int, str]:
        """Determine file format for each available year based on actual files."""
        formats = {}
        
        for year in self.available_years:
            year_dir = self.raw_dir / str(year)
            
            # Check for converted files first (more specific)
            converted_files = (
                list(year_dir.glob('stu_*_converted.*')) + 
                list(year_dir.glob('cog_*_converted.*'))
            )
            
            # Check subdirectories too
            for subdir in year_dir.iterdir():
                if subdir.is_dir():
                    converted_files.extend(list(subdir.glob('stu_*_converted.*')))
                    converted_files.extend(list(subdir.glob('cog_*_converted.*')))
            
            if converted_files:
                formats[year] = 'converted'
                logger.info(f"Year {year}: detected 'converted' format")
            else:
                # Default to .sav format for modern files
                formats[year] = 'sav'
                logger.info(f"Year {year}: detected 'sav' format")
        
        return formats
    
    def find_year_files(self, year: int) -> Dict[str, Optional[Path]]:
        """Find available PISA files for a given year."""
        year_dir = self.raw_dir / str(year)
        
        if not year_dir.exists():
            logger.warning(f"Directory for year {year} not found: {year_dir}")
            return {}
        
        found_files = {}
        file_format = self.file_formats.get(year, 'sav')
        
        # Search both main directory and subdirectories
        search_dirs = [year_dir]
        for subdir in year_dir.iterdir():
            if subdir.is_dir():
                search_dirs.append(subdir)
        
        if file_format == 'sav':
            # Modern PISA years with direct .sav files
            
            # Student questionnaire patterns by year (case-insensitive)
            stu_patterns = {
                2025: ['CY09_MS_STU_PUF.sav', 'CY09_MS_STU_PUF.SAV'],
                2022: ['CY08MSP_STU_QQQ.SAV', 'CY08MSP_STU_QQQ.sav', 'CY08_MSU_STU_QQQ.sav'],
                2018: ['CY07_MSU_STU_QQQ.sav', 'CY07_MSU_STU_QQQ.SAV'], 
                2015: ['CY6_MS_CMB_STU_QQQ.sav', 'CY6_MS_CMB_STU_QQQ.SAV'],
            }
            
            # Cognitive data patterns
            cog_patterns = {
                2025: ['CY09_MS_COG_PUF.sav', 'CY09_MS_COG_PUF.SAV'],
                2022: ['CY08MSP_STU_COG.SAV', 'CY08MSP_STU_COG.sav', 'CY08_MSU_STU_COG.sav'],
                2018: ['CY07_MSU_STU_COG.sav', 'CY07_MSU_STU_COG.SAV'],
                2015: ['CY6_MS_CMB_STU_COG.sav', 'CY6_MS_CMB_STU_COG.SAV'],
            }
            
            # Generic fallback patterns
            generic_stu_patterns = ['*STU_QQQ*.sav', '*STU_QQQ*.SAV', '*STU*.sav', '*STU*.SAV']
            generic_cog_patterns = ['*STU_COG*.sav', '*STU_COG*.SAV', '*COG*.sav', '*COG*.SAV']
            
            # Find student questionnaire
            search_patterns = stu_patterns.get(year, []) + generic_stu_patterns
            for search_dir in search_dirs:
                for pattern in search_patterns:
                    files = list(search_dir.glob(pattern))
                    if files:
                        found_files['student'] = files[0]
                        break
                if 'student' in found_files:
                    break
            
            # Find cognitive data
            search_patterns = cog_patterns.get(year, []) + generic_cog_patterns
            for search_dir in search_dirs:
                for pattern in search_patterns:
                    files = list(search_dir.glob(pattern))
                    if files:
                        found_files['cognitive'] = files[0]
                        break
                if 'cognitive' in found_files:
                    break
            
        elif file_format == 'converted':
            # Converted files from syntax processing
            
            # Look for converted files
            for search_dir in search_dirs:
                stu_files = list(search_dir.glob('stu_*_converted.sav')) or list(search_dir.glob('stu_*_converted.csv'))
                cog_files = list(search_dir.glob('cog_*_converted.sav')) or list(search_dir.glob('cog_*_converted.csv'))
                
                if stu_files and 'student' not in found_files:
                    found_files['student'] = stu_files[0]
                if cog_files and 'cognitive' not in found_files:
                    found_files['cognitive'] = cog_files[0]
        
        # Log findings
        for file_type, file_path in found_files.items():
            if file_path:
                logger.info(f"Found {year} {file_type}: {file_path}")
            else:
                logger.warning(f"Missing {year} {file_type} file")
        
        return found_files
    
    def load_file_data_optimized(self, file_path: Path, key_cols: Optional[List[str]] = None) -> Optional[pl.DataFrame]:
        """Load data from SPSS .sav or CSV file with optimization."""
        try:
            if file_path.suffix.lower() == '.sav':
                if HAS_PYREADSTAT:
                    # Read only specific columns if provided to save memory
                    if key_cols:
                        # First, get metadata to find available columns
                        _, meta = pyreadstat.read_sav(str(file_path), metadataonly=True)
                        available_cols = [col for col in key_cols if col in meta.column_names]
                        
                        if available_cols:
                            df_pandas, _ = pyreadstat.read_sav(str(file_path), usecols=available_cols)
                        else:
                            # Read all if no key columns are available
                            df_pandas, _ = pyreadstat.read_sav(str(file_path))
                    else:
                        df_pandas, _ = pyreadstat.read_sav(str(file_path))
                    
                    # Convert to Polars immediately
                    df = pl.from_pandas(df_pandas)
                    # Free pandas memory
                    del df_pandas
                    
                    logger.info(f"Loaded .sav file: {len(df)} rows, {len(df.columns)} columns")
                    return df
                else:
                    logger.error(f"Cannot read .sav file {file_path.name} - pyreadstat not available")
                    return None
            
            elif file_path.suffix.lower() == '.csv':
                # CSV files - use Polars lazy loading
                if key_cols:
                    df = pl.read_csv(file_path, columns=key_cols)
                else:
                    df = pl.read_csv(file_path)
                logger.info(f"Loaded CSV file: {len(df)} rows, {len(df.columns)} columns")
                return df
            
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")
            return None
    
    def get_required_columns_for_year(self, year: int) -> List[str]:
        """Get all possible column names we need for a given year."""
        # Flatten all possible variable names
        all_cols = []
        for var_list in self.key_variables.values():
            all_cols.extend(var_list)
        
        # Add year-specific common columns
        if year >= 2015:
            # Modern PISA uses these patterns
            all_cols.extend(['CNT', 'CNTSTUID', 'CNTSCHID'])
        else:
            # Older PISA uses these
            all_cols.extend(['COUNTRY', 'SCHOOLID', 'StIDStd'])
            
        return list(set(all_cols))  # Remove duplicates
    
    def harmonize_variables(self, df: pl.DataFrame, year: int) -> pl.DataFrame:
        """Harmonize variable names across PISA years."""
        
        # Create mapping for this year
        year_mapping = {}
        available_cols = df.columns
        
        for standard_name, possible_names in self.key_variables.items():
            for possible_name in possible_names:
                if possible_name in available_cols:
                    year_mapping[possible_name] = standard_name
                    break
        
        # Apply mapping
        if year_mapping:
            df = df.rename(year_mapping)
            logger.info(f"Harmonized {len(year_mapping)} variables for {year}")
        
        # Add year column
        df = df.with_columns([
            pl.lit(year).alias('pisa_year')
        ])
        
        # Keep only harmonized variables plus year
        harmonized_vars = list(self.key_variables.keys()) + ['pisa_year']
        available_harmonized = [col for col in harmonized_vars if col in df.columns]
        
        df = df.select(available_harmonized)
        
        return df
    
    def process_year_data(self, year: int) -> Optional[pl.DataFrame]:
        """Process all data for a given PISA year with optimization."""
        logger.info(f"\n🔄 Processing PISA {year} data...")
        
        # Find files for this year
        year_files = self.find_year_files(year)
        
        if not year_files:
            logger.warning(f"No files found for PISA {year}")
            return None
        
        year_data = None
        
        # Get required columns for optimization
        required_cols = self.get_required_columns_for_year(year)
        
        # The student questionnaire already contains plausible values and the
        # background variables used by this student-level trend dataset.  The
        # cognitive item file is unnecessary here. Joining on student_id alone
        # across countries/schools can multiply student records.
        student_file = year_files.get('student')
        files_to_load = [('student', student_file)] if student_file else []

        for file_type, file_path in files_to_load:
            if file_path is None:
                continue
                
            # Load data with column selection for optimization
            df = self.load_file_data_optimized(file_path, required_cols)
            if df is None:
                continue
            
            # Harmonize variables
            df = self.harmonize_variables(df, year)
            
            if year_data is None:
                year_data = df
                logger.info(f"Initialized with {file_type} data")
        
        if year_data is not None:
            logger.info(f"✅ PISA {year}: {len(year_data)} students, {len(year_data.columns)} variables")
            
            # Save individual year data
            output_file = self.trend_dir / f"pisa_{year}_harmonized.parquet"
            year_data.write_parquet(output_file)
            logger.info(f"Saved: {output_file.name}")
        
        return year_data
    
    def filter_spain_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Filter data for Spain only."""
        if 'country' not in df.columns:
            logger.warning("No country variable found - cannot filter Spain")
            return df
        
        # Spain country codes in different PISA years
        spain_codes = ['ESP', 'ES', '724']  # String formats only
        
        spain_df = df.filter(
            pl.col('country').cast(pl.String).is_in(spain_codes)
        )
        
        logger.info(f"Filtered Spain: {len(spain_df)} students from {len(df)} total")
        return spain_df
    
    def create_trend_analysis_files(self, all_years_data: List[pl.DataFrame]) -> None:
        """Create combined files for trend analysis."""
        
        if not all_years_data:
            logger.error("No data available for trend analysis")
            return
        
        # Harmonize data types across years before combining
        harmonized_data = []
        for df in all_years_data:
            # Convert key ID columns to string for consistency
            df_harmonized = df.clone()
            for col in ['student_id', 'school_id', 'country']:
                if col in df_harmonized.columns:
                    df_harmonized = df_harmonized.with_columns(
                        pl.col(col).cast(pl.String, strict=False).alias(col)
                    )
            
            # Convert score columns to float for consistency
            score_cols = ['math_score', 'read_score', 'science_score']
            for col in score_cols:
                if col in df_harmonized.columns:
                    df_harmonized = df_harmonized.with_columns(
                        pl.col(col).cast(pl.Float64, strict=False).alias(col)
                    )
            
            harmonized_data.append(df_harmonized)
        
        # Combine all years - use diagonal to handle different schemas
        combined_df = pl.concat(harmonized_data, how='diagonal')

        # Student identifiers are not globally unique: they can repeat across
        # countries and, in older cycles, across schools.  This composite key
        # is the minimum safe identity for a student record.
        identity = ['pisa_year', 'country', 'school_id', 'student_id']
        if all(col in combined_df.columns for col in identity):
            duplicate_count = combined_df.height - combined_df.select(
                pl.struct(identity).n_unique()
            ).item()
            if duplicate_count:
                raise ValueError(f'{duplicate_count} duplicate student identities; inspect source files')
        logger.info(f"Combined dataset: {len(combined_df)} total students across {len(all_years_data)} years")
        
        # Get year range for filename
        years = sorted(combined_df['pisa_year'].unique().to_list())
        year_range = f"{min(years)}_{max(years)}" if len(years) > 1 else str(years[0])
        
        # Save combined international data
        combined_file = self.trend_dir / f"pisa_combined_{year_range}.parquet"
        combined_df.write_parquet(combined_file)
        logger.info(f"Saved combined data: {combined_file.name}")
        
        # Create Spain-only trend data
        spain_combined = self.filter_spain_data(combined_df)
        if len(spain_combined) > 0:
            spain_file = self.spain_dir / f"spain_trends_{year_range}.parquet"
            spain_combined.write_parquet(spain_file)
            logger.info(f"Saved Spain trends: {spain_file.name}")
            
            # Summary by year for Spain
            spain_summary = (spain_combined
                           .group_by('pisa_year')
                           .agg([
                               pl.count().alias('student_count'),
                               pl.col('homework_time').mean().alias('avg_homework_minutes'),
                               pl.col('math_score').mean().alias('avg_math_score'),
                               pl.col('escs').mean().alias('avg_socioeconomic_status')
                           ])
                           .sort('pisa_year'))
            
            summary_file = self.spain_dir / f"spain_summary_{year_range}.csv"
            spain_summary.write_csv(summary_file)
            logger.info(f"Saved Spain summary: {summary_file.name}")
    
    def create_metadata_files(self, processed_years: List[int]) -> None:
        """Create metadata and documentation files."""
        
        # Create year range for file naming
        year_range = f"{min(processed_years)}_{max(processed_years)}" if len(processed_years) > 1 else str(processed_years[0])
        
        metadata = {
            'processing_date': datetime.now().isoformat(),
            'processed_years': processed_years,
            'year_range': year_range,
            'file_formats': {str(year): self.file_formats.get(year, 'unknown') for year in processed_years},
            'key_variables': self.key_variables,
            'output_files': {
                'combined_international': f'trend_analysis/pisa_combined_{year_range}.parquet',
                'spain_trends': f'spain_trends/spain_trends_{year_range}.parquet', 
                'spain_summary': f'spain_trends/spain_summary_{year_range}.csv'
            },
            'notes': {
                'harmonization': 'Variables harmonized across years using key_variables mapping',
                'spain_filtering': 'Spain identified using country codes: ESP, ES, 724',
                'missing_data': 'Missing values preserved as null/NaN in Parquet format',
                'optimization': 'Uses column selection and Polars for efficient processing',
                'auto_detection': 'Years automatically detected from raw data directory'
            }
        }
        
        metadata_file = self.processed_dir / f"processing_metadata_{year_range}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata: {metadata_file.name}")
    
    def run_trend_conversion(self) -> None:
        """Run the complete multi-year conversion process."""
        logger.info("🚀 STARTING PISA TREND DATA CONVERSION (OPTIMIZED)")
        logger.info("=" * 60)
        
        # Check which years have data available
        available_years = []
        for year in self.available_years:
            year_files = self.find_year_files(year)
            if year_files:
                available_years.append(year)
        
        if not available_years:
            logger.error("❌ No PISA data files found!")
            logger.error("Please download PISA data files and place them in:")
            for year in self.available_years:
                format_info = "(.sav files)" if self.file_formats.get(year) == 'sav' else "(converted files from syntax processing)"
                logger.error(f"  data/Global/pisa/raw/{year}/ {format_info}")
            logger.error("\nFor years 2012 and earlier, run this first:")
            logger.error("  uv run python process_spss_syntax.py")
            return
        
        logger.info(f"Found data for years: {available_years}")
        
        # Process each year
        all_years_data = []
        processing_results = {}
        
        for year in available_years:
            year_data = self.process_year_data(year)
            if year_data is not None:
                all_years_data.append(year_data)
                processing_results[year] = True
            else:
                processing_results[year] = False
        
        # Create trend analysis files
        if all_years_data:
            logger.info(f"\n📊 Creating trend analysis files...")
            self.create_trend_analysis_files(all_years_data)
            self.create_metadata_files(list(processing_results.keys()))
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 TREND CONVERSION SUMMARY")
        logger.info("=" * 60)
        
        for year, success in processing_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED" 
            format_info = f"({self.file_formats.get(year, 'unknown')} format)"
            logger.info(f"PISA {year}: {status} {format_info}")
        
        successful_years = [year for year, success in processing_results.items() if success]
        if successful_years:
            year_span = f"{min(successful_years)}-{max(successful_years)}"
            logger.info(f"\n🎉 CONVERSION COMPLETE!")
            logger.info(f"📊 Processed {len(successful_years)} years: {successful_years}")
            logger.info(f"📈 Trend analysis span: {year_span} ({max(successful_years) - min(successful_years)} years)")
            logger.info(f"📁 Output files created in: {self.processed_dir}")
            logger.info(f"🇪🇸 Spain-specific analysis ready!")
            logger.info(f"\n📝 Next steps:")
            logger.info(f"   1. Open youth_trends_demo.ipynb for interactive analysis")
            logger.info(f"   2. Run trend analysis on Spain vs international data")
            logger.info(f"   3. Examine homework time and motivation trends")
        else:
            logger.error("⚠️ All conversions failed. Check error messages above.")

def get_available_years_from_raw(raw_dir: Optional[str] = None) -> List[str]:
    """Get list of available years from raw data directory."""
    raw_path = Path(raw_dir) if raw_dir else DEFAULT_PISA_DATA_DIR / "raw"
    if not raw_path.exists():
        return []
    
    available_years = []
    for item in raw_path.iterdir():
        if item.is_dir() and re.match(r'^20[0-3][0-9]$', item.name):
            # Quick check for PISA files
            pisa_patterns = ['*.sav', '*.SAV', '*STU*.sav', '*COG*.sav']
            has_files = False
            for pattern in pisa_patterns:
                if list(item.glob(pattern)) or any(list(subdir.glob(pattern)) for subdir in item.iterdir() if subdir.is_dir()):
                    has_files = True
                    break
            if has_files:
                available_years.append(item.name)
    
    return sorted(available_years)

def main():
    """Main function."""
    print("🚀 **PISA Trend Data Converter (All Available Years)**")
    print("📊 Converting PISA data to standardized format for trend analysis")
    
    # Check what years are available
    available_years = get_available_years_from_raw()
    if not available_years:
        print("❌ **No PISA data found in ../data/raw/**")
        print("Please ensure PISA data files are available in:")
        print("  ../data/raw/2015/, ../data/raw/2018/, ../data/raw/2022/, etc.")
        print("Download data using: uv run python download_raw.py")
        return
    
    print(f"📂 **Found data for years: {', '.join(available_years)}**")
    
    converter = PISATrendConverter()
    converter.run_trend_conversion()

if __name__ == "__main__":
    main()
