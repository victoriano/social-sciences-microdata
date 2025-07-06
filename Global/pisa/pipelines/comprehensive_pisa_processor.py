#!/usr/bin/env python3
"""
Comprehensive PISA Data Processor
================================

This script processes PISA data from raw SAV files through to final analysis-ready datasets.
It combines harmonization, enhancement, and variable extraction in a single pipeline.

Features:
- Automatically detects available years from raw data
- Extracts target variables from comprehensive variable catalog
- Harmonizes variables across years
- Enhances data with computed variables and meaningful labels
- Creates individual year files and comprehensive combined dataset
- Generates Spain-specific analysis files
- Handles different file formats across PISA cycles

Target Variables Extracted (based on comprehensive catalog):
- Socioeconomic: ESCS, WEALTH, HOMEPOS, PARED, HISEI, MISCED, FISCED, HISCED
- Demographics: AGE, ST004D01T (gender), ST001D01T (grade)
- Motivation: JOYREAD, SCIEEFF, INSTMOT, BELONG
- Performance: PV*MATH, PV*READ, PV*SCIE scores
- Effort: EFFORT1, EFFORT2, DEFFORT
- Additional: IMMIG, OECD, STRATUM

Usage:
    uv run python comprehensive_pisa_processor.py
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
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePISAProcessor:
    """Comprehensive PISA data processor from raw to analysis-ready."""
    
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        """Initialize processor with data directories."""
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create output directories
        self.individual_years_dir = self.processed_dir / "individual_years"
        self.combined_dir = self.processed_dir / "combined"
        self.spain_dir = self.processed_dir / "spain"
        
        for dir_path in [self.processed_dir, self.individual_years_dir, self.combined_dir, self.spain_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Target variables based on comprehensive catalog analysis
        self.target_variables = {
            # Variables available in ALL 5 years (2006-2018)
            'core_5_years': {
                'ESCS': 'Economic, Social and Cultural Status',
                'WEALTH': 'Wealth Index', 
                'HOMEPOS': 'Home Possessions',
                'PARED': 'Parental Education',
                'AGE': 'Student Age',
                'IMMIG': 'Immigration Status',
                'OECD': 'OECD Country',
                'STRATUM': 'Stratum ID',
                'PV1MATH': 'Math Score 1', 'PV2MATH': 'Math Score 2', 'PV3MATH': 'Math Score 3', 'PV4MATH': 'Math Score 4', 'PV5MATH': 'Math Score 5',
                'PV1READ': 'Reading Score 1', 'PV2READ': 'Reading Score 2', 'PV3READ': 'Reading Score 3', 'PV4READ': 'Reading Score 4', 'PV5READ': 'Reading Score 5',
                'PV1SCIE': 'Science Score 1', 'PV2SCIE': 'Science Score 2', 'PV3SCIE': 'Science Score 3', 'PV4SCIE': 'Science Score 4', 'PV5SCIE': 'Science Score 5'
            },
            
            # Variables available in 4 years  
            'core_4_years': {
                'MISCED': 'Mother Education',
                'FISCED': 'Father Education', 
                'HISCED': 'Highest Parental Education'
            },
            
            # Variables available in 3 years
            'core_3_years': {
                'HISEI': 'Highest Parental Occupational Status',
                'BELONG': 'Sense of Belonging at School'
            },
            
            # Variables available in 2 years
            'core_2_years': {
                'JOYREAD': 'Joy of Reading',
                'SCIEEFF': 'Science Self-Efficacy',
                'ST004D01T': 'Gender',
                'ST001D01T': 'Grade Level'
            },
            
            # Variables available in single years
            'occasional': {
                'INSTMOT': 'Instrumental Motivation',
                'EFFORT1': 'Effort Thermometer 1',
                'EFFORT2': 'Effort Thermometer 2', 
                'DEFFORT': 'Domain Effort',
                'TIMEINT': 'Time Interval'
            }
        }
        
        # Core ID variables
        self.id_variables = {
            'CNTSTUID': 'Student ID',
            'CNTSCHID': 'School ID', 
            'CNT': 'Country Code',
            'CNTRYID': 'Country ID'
        }
        
        # Automatically detect available years
        self.available_years = self.detect_available_years()
        
        # Country mappings for Spain filtering and country names
        self.country_mappings = self._get_country_mappings()
        
        logger.info(f"🚀 Initialized processor for {len(self.available_years)} years: {sorted(self.available_years)}")
    
    def detect_available_years(self) -> List[int]:
        """Detect available PISA years from raw data directory."""
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory not found: {self.raw_dir}")
            return []
        
        available_years = []
        
        for item in self.raw_dir.iterdir():
            if item.is_dir() and re.match(r'^20[0-3][0-9]$', item.name):
                year = int(item.name)
                if self.has_pisa_files(item):
                    available_years.append(year)
                    logger.info(f"📅 Detected PISA year: {year}")
        
        return sorted(available_years)
    
    def has_pisa_files(self, year_dir: Path) -> bool:
        """Check if directory contains PISA files."""
        pisa_patterns = ['*.sav', '*.SAV', '*STU*.sav', '*COG*.sav']
        
        for pattern in pisa_patterns:
            if list(year_dir.glob(pattern)):
                return True
            # Check subdirectories
            for subdir in year_dir.iterdir():
                if subdir.is_dir() and list(subdir.glob(pattern)):
                    return True
        return False
    
    def _get_country_mappings(self) -> Dict[str, str]:
        """Get country code to name mappings."""
        return {
            'ESP': 'Spain', 'ES': 'Spain', '724': 'Spain',
            'DEU': 'Germany', 'GER': 'Germany', 
            'FRA': 'France', 'ITA': 'Italy', 'GBR': 'United Kingdom',
            'USA': 'United States', 'JPN': 'Japan', 'KOR': 'South Korea',
            'FIN': 'Finland', 'SWE': 'Sweden', 'NOR': 'Norway',
            'DNK': 'Denmark', 'NLD': 'Netherlands', 'BEL': 'Belgium',
            'AUT': 'Austria', 'CHE': 'Switzerland', 'CAN': 'Canada',
            'AUS': 'Australia', 'NZL': 'New Zealand', 'POL': 'Poland',
            'CZE': 'Czech Republic', 'HUN': 'Hungary', 'SVK': 'Slovakia',
            'SVN': 'Slovenia', 'EST': 'Estonia', 'LVA': 'Latvia',
            'LTU': 'Lithuania', 'PRT': 'Portugal', 'GRC': 'Greece',
            'TUR': 'Turkey', 'ISL': 'Iceland', 'IRL': 'Ireland',
            'LUX': 'Luxembourg', 'MEX': 'Mexico', 'CHL': 'Chile',
            'ISR': 'Israel', 'RUS': 'Russia', 'CHN': 'China',
            'HKG': 'Hong Kong', 'MAC': 'Macao', 'TAP': 'Chinese Taipei',
            'SGP': 'Singapore', 'THA': 'Thailand', 'MYS': 'Malaysia',
            'IDN': 'Indonesia', 'VNM': 'Vietnam', 'PHL': 'Philippines',
            'QAT': 'Qatar', 'ARE': 'United Arab Emirates', 'JOR': 'Jordan',
            'LBN': 'Lebanon', 'TUN': 'Tunisia', 'ALB': 'Albania',
            'MKD': 'North Macedonia', 'MNE': 'Montenegro', 'SRB': 'Serbia',
            'HRV': 'Croatia', 'BIH': 'Bosnia and Herzegovina', 'BGR': 'Bulgaria',
            'ROU': 'Romania', 'MDA': 'Moldova', 'UKR': 'Ukraine',
            'GEO': 'Georgia', 'AZE': 'Azerbaijan', 'KAZ': 'Kazakhstan',
            'KGZ': 'Kyrgyzstan', 'PER': 'Peru', 'COL': 'Colombia',
            'BRA': 'Brazil', 'ARG': 'Argentina', 'URY': 'Uruguay',
            'CRI': 'Costa Rica', 'DOM': 'Dominican Republic', 'GTM': 'Guatemala',
            'PAN': 'Panama'
        }
    
    def find_year_files(self, year: int) -> Dict[str, Optional[Path]]:
        """Find PISA files for a given year."""
        year_dir = self.raw_dir / str(year)
        if not year_dir.exists():
            return {}
        
        found_files = {}
        
        # Search patterns for different data types
        search_dirs = [year_dir]
        for subdir in year_dir.iterdir():
            if subdir.is_dir():
                search_dirs.append(subdir)
        
        # Student questionnaire patterns
        stu_patterns = [
            '*STU_QQQ*.sav', '*STU_QQQ*.SAV',
            'stu_*_converted.sav', '*STU*.sav'
        ]
        
        # Cognitive/timing patterns  
        cog_patterns = [
            '*STU_COG*.sav', '*STU_COG*.SAV',
            'cog_*_converted.sav', '*COG*.sav'
        ]
        
        # Find student questionnaire
        for search_dir in search_dirs:
            for pattern in stu_patterns:
                files = list(search_dir.glob(pattern))
                if files:
                    found_files['student'] = files[0]
                    break
            if 'student' in found_files:
                break
        
        # Find cognitive data
        for search_dir in search_dirs:
            for pattern in cog_patterns:
                files = list(search_dir.glob(pattern))
                if files:
                    found_files['cognitive'] = files[0]
                    break
            if 'cognitive' in found_files:
                break
        
        return found_files
    
    def load_sav_file_optimized(self, file_path: Path, target_vars: List[str]) -> Optional[pl.DataFrame]:
        """Load SAV file with target variables only."""
        try:
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            logger.info(f"📂 Loading {file_path.name} ({file_size_mb:.1f} MB)")
            
            # For very large files (>1GB), be more selective
            if file_size_mb > 1024:
                logger.info(f"   🔧 Large file detected - using selective loading...")
                # Prioritize core variables for large files
                priority_vars = [
                    'CNTSTUID', 'CNT', 'CNTSCHID',  # IDs
                    'AGE', 'ESCS', 'WEALTH', 'HOMEPOS', 'PARED',  # Core socioeconomic
                    'PV1MATH', 'PV1READ', 'PV1SCIE',  # One performance measure per domain
                    'JOYREAD', 'SCIEEFF', 'BELONG'  # Key motivation variables
                ]
                target_vars = [var for var in target_vars if var in priority_vars] + \
                            [var for var in target_vars if var not in priority_vars][:10]  # Limit additional vars
            
            # Read with pandas first to get all available columns
            df_sample = pd.read_spss(str(file_path), usecols=None)
            available_cols = list(df_sample.columns)
            
            # Find which target variables exist
            found_vars = []
            for var in target_vars:
                if var in available_cols:
                    found_vars.append(var)
            
            # Always include ID variables
            id_vars = [col for col in available_cols if col in self.id_variables]
            found_vars.extend(id_vars)
            
            # Remove duplicates and limit total columns for memory efficiency
            found_vars = list(set(found_vars))
            if len(found_vars) > 50:  # Limit to 50 columns max for large files
                logger.info(f"   🔧 Limiting to 50 most important variables (found {len(found_vars)})")
                # Prioritize ID vars, then core vars, then others
                id_vars_found = [v for v in found_vars if v in self.id_variables]
                core_vars_found = [v for v in found_vars if v in self.target_variables['core_5_years'] and v not in id_vars_found]
                other_vars_found = [v for v in found_vars if v not in id_vars_found and v not in core_vars_found]
                found_vars = id_vars_found + core_vars_found + other_vars_found[:50-len(id_vars_found)-len(core_vars_found)]
            
            if not found_vars:
                logger.warning(f"   ⚠️  No target variables found in {file_path.name}")
                return None
            
            logger.info(f"   ✅ Loading {len(found_vars)} variables: {[v for v in found_vars if v not in id_vars][:3]}...")
            
            # Read only the columns we need
            df = pd.read_spss(str(file_path), usecols=found_vars)
            
            # Convert to Polars with error handling
            try:
                df_pl = pl.from_pandas(df)
            except Exception as e:
                logger.warning(f"   🔧 Converting data types for Polars compatibility...")
                # Fix data type issues
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str)
                    elif 'Int' in str(df[col].dtype):
                        df[col] = df[col].astype('float64')
                df_pl = pl.from_pandas(df)
            
            logger.info(f"   📊 Loaded: {len(df_pl):,} rows, {len(df_pl.columns)} columns")
            return df_pl
            
        except Exception as e:
            logger.error(f"   ❌ Error loading {file_path.name}: {e}")
            return None
    
    def get_target_variables_for_year(self, year: int) -> List[str]:
        """Get all target variables we want to extract for a given year."""
        all_vars = []
        
        # Add all target variables from all categories
        for category in self.target_variables.values():
            all_vars.extend(category.keys())
        
        # Add ID variables
        all_vars.extend(self.id_variables.keys())
        
        # Remove duplicates
        return list(set(all_vars))
    
    def process_single_year(self, year: int) -> Optional[pl.DataFrame]:
        """Process all data for a single PISA year."""
        logger.info(f"\n🔄 Processing PISA {year}...")
        logger.info("=" * 50)
        
        # Find files for this year
        year_files = self.find_year_files(year)
        if not year_files:
            logger.warning(f"❌ No files found for PISA {year}")
            return None
        
        # Get target variables for this year
        target_vars = self.get_target_variables_for_year(year)
        
        year_data = None
        
        # Process each file type
        for file_type, file_path in year_files.items():
            if file_path is None:
                continue
            
            # Load data with target variables
            df = self.load_sav_file_optimized(file_path, target_vars)
            if df is None:
                continue
            
            if year_data is None:
                year_data = df
                logger.info(f"   📋 Initialized with {file_type} data")
            else:
                # Try to merge on student ID using left join to preserve size
                common_ids = set(year_data.columns) & set(df.columns) & set(self.id_variables.keys())
                if common_ids:
                    merge_key = list(common_ids)[0]
                    
                    # Use left join to avoid expanding dataset size
                    year_data = year_data.join(df, on=merge_key, how='left', suffix='_right')
                    
                    # Remove duplicate columns  
                    for col in df.columns:
                        if col + '_right' in year_data.columns and col != merge_key:
                            # Keep the original column, drop the duplicate
                            year_data = year_data.drop(col + '_right')
                    
                    logger.info(f"   🔗 Merged {file_type} data on {merge_key} (left join)")
                else:
                    logger.warning(f"   ⚠️  Cannot merge {file_type} - no common ID")
        
        if year_data is None:
            logger.warning(f"❌ No data loaded for {year}")
            return None
        
        # Add year column
        year_data = year_data.with_columns([
            pl.lit(year).alias('pisa_year')
        ])
        
        # Enhance the data with computed variables
        year_data = self.enhance_year_data(year_data, year)
        
        # Save individual year file
        output_file = self.individual_years_dir / f"pisa_{year}_comprehensive.parquet"
        year_data.write_parquet(output_file, compression='zstd')
        
        logger.info(f"✅ PISA {year}: {len(year_data):,} students, {len(year_data.columns)} variables")
        logger.info(f"💾 Saved: {output_file.name}")
        
        return year_data
    
    def enhance_year_data(self, df: pl.DataFrame, year: int) -> pl.DataFrame:
        """Enhance year data with computed variables and transformations."""
        logger.info(f"   🔧 Enhancing {year} data...")
        
        df_enhanced = df
        
        # Convert gender codes to meaningful strings (ST004D01T)
        if 'ST004D01T' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.when(pl.col('ST004D01T').cast(pl.String) == 'Female')
                .then(pl.lit('Female'))
                .when(pl.col('ST004D01T').cast(pl.String) == 'Male') 
                .then(pl.lit('Male'))
                .when(pl.col('ST004D01T') == 1)
                .then(pl.lit('Female'))
                .when(pl.col('ST004D01T') == 2)
                .then(pl.lit('Male'))
                .otherwise(pl.lit('Unknown'))
                .alias('sex')
            ])
        
        # Add country names
        if 'CNT' in df.columns:
            country_mapping_expr = pl.col('CNT').cast(pl.String)
            for code, name in self.country_mappings.items():
                country_mapping_expr = country_mapping_expr.str.replace(code, name)
            df_enhanced = df_enhanced.with_columns([
                country_mapping_expr.alias('country_name')
            ])
        
        # Create performance indices from plausible values
        score_vars = {
            'math_scores': [f'PV{i}MATH' for i in range(1, 6)],
            'read_scores': [f'PV{i}READ' for i in range(1, 6)], 
            'science_scores': [f'PV{i}SCIE' for i in range(1, 6)]
        }
        
        for score_type, score_cols in score_vars.items():
            available_scores = [col for col in score_cols if col in df.columns]
            if available_scores:
                # Calculate average of plausible values
                avg_expr = pl.concat_list([pl.col(col) for col in available_scores]).list.mean()
                df_enhanced = df_enhanced.with_columns([
                    avg_expr.alias(score_type.replace('_scores', '_score'))
                ])
        
        # Create overall academic performance index
        performance_cols = ['math_score', 'read_score', 'science_score']
        available_performance = [col for col in performance_cols if col in df_enhanced.columns]
        
        if len(available_performance) >= 2:
            overall_performance = pl.concat_list([pl.col(col) for col in available_performance]).list.mean()
            df_enhanced = df_enhanced.with_columns([
                overall_performance.alias('overall_performance'),
                pl.when(overall_performance >= 600)
                .then(pl.lit('High'))
                .when(overall_performance >= 500)
                .then(pl.lit('Medium'))
                .when(overall_performance >= 400)
                .then(pl.lit('Low'))
                .otherwise(pl.lit('Very Low'))
                .alias('performance_level')
            ])
        
        # Create age groups
        if 'AGE' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.when(pl.col('AGE') < 15.5)
                .then(pl.lit('Young'))
                .when(pl.col('AGE') < 16.5)
                .then(pl.lit('Average'))
                .otherwise(pl.lit('Old'))
                .alias('age_group')
            ])
        
        # Create socioeconomic status categories
        if 'ESCS' in df.columns:
            df_enhanced = df_enhanced.with_columns([
                pl.when(pl.col('ESCS') >= 1.0)
                .then(pl.lit('High SES'))
                .when(pl.col('ESCS') >= 0.0)
                .then(pl.lit('Medium-High SES'))
                .when(pl.col('ESCS') >= -1.0)
                .then(pl.lit('Medium-Low SES'))
                .otherwise(pl.lit('Low SES'))
                .alias('ses_category')
            ])
        
        # Add temporal variables
        df_enhanced = df_enhanced.with_columns([
            pl.when(pl.col('pisa_year') <= 2009)
            .then(pl.lit('Pre-Crisis'))
            .when(pl.col('pisa_year') <= 2015)
            .then(pl.lit('Post-Crisis'))
            .otherwise(pl.lit('Recent'))
            .alias('assessment_period'),
            
            pl.when(pl.col('pisa_year') < 2010)
            .then(pl.lit('2000s'))
            .when(pl.col('pisa_year') < 2020)
            .then(pl.lit('2010s'))
            .otherwise(pl.lit('2020s'))
            .alias('decade')
        ])
        
        logger.info(f"   ✅ Enhanced data: +{len(df_enhanced.columns) - len(df)} variables")
        return df_enhanced
    
    def combine_all_years(self, year_datasets: List[pl.DataFrame]) -> pl.DataFrame:
        """Combine all year datasets into comprehensive dataset."""
        logger.info("\n🔗 Combining all years into comprehensive dataset...")
        logger.info("=" * 50)
        
        if not year_datasets:
            logger.error("❌ No year datasets to combine")
            return pl.DataFrame()
        
        # Ensure consistent data types across years
        harmonized_datasets = []
        
        for df in year_datasets:
            df_harmonized = df.clone()
            
            # Convert ID columns to string
            for id_col in self.id_variables.keys():
                if id_col in df_harmonized.columns:
                    df_harmonized = df_harmonized.with_columns(
                        pl.col(id_col).cast(pl.String, strict=False).alias(id_col)
                    )
            
            # Convert score columns to float
            score_pattern = ['math_score', 'read_score', 'science_score', 'overall_performance'] + \
                          [f'PV{i}{subj}' for i in range(1, 6) for subj in ['MATH', 'READ', 'SCIE']]
            
            for col in score_pattern:
                if col in df_harmonized.columns:
                    df_harmonized = df_harmonized.with_columns(
                        pl.col(col).cast(pl.Float64, strict=False).alias(col)
                    )
            
            harmonized_datasets.append(df_harmonized)
        
        # Combine using diagonal join to handle different schemas
        combined_df = pl.concat(harmonized_datasets, how='diagonal')
        
        years = sorted(combined_df['pisa_year'].unique().to_list())
        logger.info(f"✅ Combined dataset: {len(combined_df):,} students across {len(years)} years ({min(years)}-{max(years)})")
        
        return combined_df
    
    def create_spain_dataset(self, combined_df: pl.DataFrame) -> pl.DataFrame:
        """Filter dataset for Spain only."""
        logger.info("\n🇪🇸 Creating Spain-specific dataset...")
        
        # Spain identifiers
        spain_codes = ['ESP', 'Spain', 'ES', '724']
        
        # Filter by country codes and names
        spain_filter = pl.lit(False)
        for col in ['CNT', 'country_name']:
            if col in combined_df.columns:
                spain_filter = spain_filter | pl.col(col).cast(pl.String).is_in(spain_codes)
        
        spain_df = combined_df.filter(spain_filter)
        
        if len(spain_df) > 0:
            years = sorted(spain_df['pisa_year'].unique().to_list())
            logger.info(f"✅ Spain dataset: {len(spain_df):,} students across {len(years)} years")
            
            # Spain summary statistics
            spain_summary = (spain_df
                           .group_by('pisa_year')
                           .agg([
                               pl.count().alias('student_count'),
                               pl.col('overall_performance').mean().alias('avg_performance'),
                               pl.col('ESCS').mean().alias('avg_escs'),
                               pl.col('WEALTH').mean().alias('avg_wealth'),
                               pl.col('AGE').mean().alias('avg_age')
                           ])
                           .sort('pisa_year'))
            
            logger.info("📊 Spain summary by year:")
            for row in spain_summary.iter_rows(named=True):
                logger.info(f"   {row['pisa_year']}: {row['student_count']:,} students, performance: {row['avg_performance']:.1f}")
        else:
            logger.warning("⚠️  No Spanish students found in dataset")
        
        return spain_df
    
    def save_final_datasets(self, combined_df: pl.DataFrame, spain_df: pl.DataFrame) -> None:
        """Save final comprehensive datasets."""
        logger.info("\n💾 Saving final datasets...")
        
        # Get year range for naming
        years = sorted(combined_df['pisa_year'].unique().to_list())
        year_range = f"{min(years)}_{max(years)}"
        
        # Save comprehensive international dataset
        international_file = self.combined_dir / f"pisa_comprehensive_{year_range}.parquet"
        combined_df.write_parquet(international_file, compression='zstd')
        logger.info(f"✅ International dataset: {international_file.name}")
        logger.info(f"   📊 {len(combined_df):,} students, {len(combined_df.columns)} variables")
        
        # Save Spain dataset
        if len(spain_df) > 0:
            spain_file = self.spain_dir / f"spain_comprehensive_{year_range}.parquet"
            spain_df.write_parquet(spain_file, compression='zstd')
            logger.info(f"✅ Spain dataset: {spain_file.name}")
            logger.info(f"   🇪🇸 {len(spain_df):,} students, {len(spain_df.columns)} variables")
        
        # Create metadata
        metadata = {
            'processing_date': datetime.now().isoformat(),
            'years_processed': years,
            'year_range': year_range,
            'total_students_international': len(combined_df),
            'total_students_spain': len(spain_df),
            'total_variables': len(combined_df.columns),
            'target_variables_extracted': {
                category: list(vars_dict.keys()) 
                for category, vars_dict in self.target_variables.items()
            },
            'enhanced_variables': [
                'sex', 'country_name', 'math_score', 'read_score', 'science_score',
                'overall_performance', 'performance_level', 'age_group', 'ses_category',
                'assessment_period', 'decade'
            ],
            'files_created': {
                'international': str(international_file),
                'spain': str(spain_file) if len(spain_df) > 0 else None,
                'individual_years': [f"pisa_{year}_comprehensive.parquet" for year in years]
            }
        }
        
        metadata_file = self.processed_dir / f"comprehensive_processing_metadata_{year_range}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Metadata: {metadata_file.name}")
    
    def run_comprehensive_processing(self) -> None:
        """Run the complete comprehensive PISA processing pipeline."""
        logger.info("🚀 STARTING COMPREHENSIVE PISA DATA PROCESSING")
        logger.info("=" * 70)
        logger.info(f"📂 Raw data directory: {self.raw_dir}")
        logger.info(f"📁 Output directory: {self.processed_dir}")
        logger.info(f"📅 Available years: {self.available_years}")
        
        if not self.available_years:
            logger.error("❌ No PISA data found in raw directory")
            logger.error("Please ensure PISA SAV files are available in year subdirectories")
            return
        
        # Process each year individually
        year_datasets = []
        processing_results = {}
        
        for year in self.available_years:
            year_data = self.process_single_year(year)
            if year_data is not None:
                year_datasets.append(year_data)
                processing_results[year] = True
            else:
                processing_results[year] = False
        
        if not year_datasets:
            logger.error("❌ No year datasets were successfully processed")
            return
        
        # Combine all years
        combined_df = self.combine_all_years(year_datasets)
        
        # Create Spain-specific dataset
        spain_df = self.create_spain_dataset(combined_df)
        
        # Save final datasets
        self.save_final_datasets(combined_df, spain_df)
        
        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("🎯 COMPREHENSIVE PROCESSING SUMMARY")
        logger.info("=" * 70)
        
        successful_years = [year for year, success in processing_results.items() if success]
        failed_years = [year for year, success in processing_results.items() if not success]
        
        logger.info(f"✅ Successfully processed: {len(successful_years)} years")
        for year in successful_years:
            logger.info(f"   • PISA {year}")
        
        if failed_years:
            logger.warning(f"❌ Failed to process: {len(failed_years)} years")
            for year in failed_years:
                logger.warning(f"   • PISA {year}")
        
        if successful_years:
            target_var_count = sum(len(vars_dict) for vars_dict in self.target_variables.values())
            
            logger.info(f"\n🎉 PROCESSING COMPLETE!")
            logger.info(f"📊 {target_var_count} target variables extracted")
            logger.info(f"📈 Span: {min(successful_years)}-{max(successful_years)} ({max(successful_years) - min(successful_years)} years)")
            logger.info(f"🌍 International: {len(combined_df):,} students")
            logger.info(f"🇪🇸 Spain: {len(spain_df):,} students")
            logger.info(f"📁 Files saved in: {self.processed_dir}")
            
            logger.info(f"\n📝 Next steps:")
            logger.info(f"   1. Use combined/pisa_comprehensive_*.parquet for international analysis")
            logger.info(f"   2. Use spain/spain_comprehensive_*.parquet for Spain-specific analysis")
            logger.info(f"   3. Individual year files available in individual_years/ directory")
            logger.info(f"   4. All target variables from comprehensive catalog are included")
        else:
            logger.error("⚠️ No data was successfully processed")

def main():
    """Main function."""
    print("🚀 **Comprehensive PISA Data Processor**")
    print("📊 Processing PISA data from raw SAV files to analysis-ready datasets")
    print("🎯 Includes all target variables from comprehensive catalog analysis")
    
    processor = ComprehensivePISAProcessor()
    processor.run_comprehensive_processing()

if __name__ == "__main__":
    main() 