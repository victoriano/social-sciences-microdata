#!/usr/bin/env python3
"""
PISA Variable Catalog Creator - FAST VERSION

This script quickly samples SAV files to create a basic variable catalog.
Prioritizes speed over completeness.
"""

import logging
import sys
import pandas as pd
import polars as pl
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import warnings
import time

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FastPISAVariableCatalog:
    """Fast version - samples tiny bits of data for basic metadata."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.catalog_file = self.processed_dir / "pisa_variable_catalog_fast.parquet"
        
        # Ensure processed directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def find_all_sav_files(self) -> List[Tuple[str, str, Path]]:
        """Find all SAV files."""
        files = []
        
        logger.info("🔍 Scanning for SAV files...")
        
        for year_dir in self.raw_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = year_dir.name
                
                for sav_file in year_dir.rglob("*.sav"):
                    dataset_type = self.classify_dataset(sav_file.name)
                    files.append((year, dataset_type, sav_file))
        
        logger.info(f"Found {len(files)} SAV files")
        return files
    
    def classify_dataset(self, filename: str) -> str:
        """Classify dataset type."""
        f = filename.lower()
        if 'stu_qqq' in f or 'student' in f:
            return 'student_questionnaire'
        elif 'stu_cog' in f or 'cognitive' in f:
            return 'student_cognitive'
        elif 'sch_qqq' in f or 'school' in f:
            return 'school_questionnaire'
        elif 'par_qqq' in f or 'parent' in f:
            return 'parent_questionnaire'
        else:
            return 'unknown'
    
    def fast_sample_file(self, file_path: Path, year: str, dataset_type: str) -> List[Dict[str, Any]]:
        """Super fast sampling - get column names and basic info with random 100 rows."""
        logger.info(f"⚡ Quick sampling: {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
        
        variables = []
        start_time = time.time()
        
        try:
            # No timeout - process all files completely
            logger.info(f"   🔄 Reading file (no timeout)...")
            
            # Read the full file
            df = pd.read_spss(str(file_path), usecols=None)
            
            # Use random sample of 100 rows if file has more than 100 rows
            if len(df) > 100:
                df = df.sample(n=100, random_state=42)
            
            # Don't limit columns - sample all of them
            logger.info(f"   📊 Sampling {len(df)} rows, {len(df.columns)} columns")
            
            # Get basic info for each column
            for col in df.columns:
                # Get some basic statistics
                non_null_count = df[col].count()
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                null_percentage = (null_count / len(df)) * 100
                
                # Get sample values
                sample_values = df[col].dropna().head(5).tolist()
                
                # Determine if numeric or categorical
                is_numeric = pd.api.types.is_numeric_dtype(df[col])
                
                var_info = {
                    'variable_name': col,
                    'year': year,
                    'dataset_type': dataset_type,
                    'file_name': file_path.name,
                    'data_type': str(df[col].dtype),
                    'sample_size': len(df),
                    'non_null_count': non_null_count,
                    'null_count': null_count,
                    'null_percentage': null_percentage,
                    'unique_count': unique_count,
                    'has_data': not df[col].empty,
                    'sample_values': str(sample_values),
                    'is_numeric': is_numeric
                }
                
                # Add numeric statistics if numeric
                if is_numeric and non_null_count > 0:
                    var_info.update({
                        'min_value': float(df[col].min()),
                        'max_value': float(df[col].max()),
                        'median_value': float(df[col].median()),
                        'mean_value': float(df[col].mean()),
                        'categorical_values': None
                    })
                else:
                    # For categorical, get unique values
                    if unique_count <= 20:  # Only for reasonable number of categories
                        unique_vals = df[col].dropna().unique().tolist()
                        var_info.update({
                            'min_value': None,
                            'max_value': None,
                            'median_value': None,
                            'mean_value': None,
                            'categorical_values': str(unique_vals)
                        })
                    else:
                        var_info.update({
                            'min_value': None,
                            'max_value': None,
                            'median_value': None,
                            'mean_value': None,
                            'categorical_values': f"Too many categories ({unique_count})"
                        })
                
                variables.append(var_info)
            
            elapsed = time.time() - start_time
            logger.info(f"   ✅ {len(variables)} variables in {elapsed:.1f}s")
            
        except Exception as e:
            logger.error(f"   ❌ Error reading {file_path.name}: {e}")
            variables.append({
                'variable_name': 'ERROR',
                'year': year,
                'dataset_type': dataset_type,
                'file_name': file_path.name,
                'data_type': 'error',
                'sample_size': 0,
                'non_null_count': 0,
                'null_count': 0,
                'null_percentage': 0,
                'unique_count': 0,
                'has_data': False,
                'sample_values': str(e),
                'is_numeric': False,
                'min_value': None,
                'max_value': None,
                'median_value': None,
                'mean_value': None,
                'categorical_values': None
            })
        
        return variables
    
    def create_fast_catalog(self) -> None:
        """Create catalog quickly."""
        logger.info("⚡ Creating FAST PISA Variable Catalog")
        logger.info("=" * 60)
        
        # Find all files
        all_files = self.find_all_sav_files()
        
        if not all_files:
            logger.error("❌ No SAV files found")
            return
        
        all_variables = []
        
        # Process each file with progress
        for i, (year, dataset_type, file_path) in enumerate(all_files, 1):
            logger.info(f"\n[{i}/{len(all_files)}] Processing {year}/{dataset_type}")
            
            # Show file size but don't skip
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            logger.info(f"   📂 File size: {file_size_mb:.1f} MB")
            
            # Sample the file
            variables = self.fast_sample_file(file_path, year, dataset_type)
            all_variables.extend(variables)
        
        # Create and save catalog
        if all_variables:
            df = pl.DataFrame(all_variables)
            
            logger.info(f"\n💾 Saving catalog to {self.catalog_file}")
            df.write_parquet(self.catalog_file, compression='zstd')
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("🎯 FAST CATALOG SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✅ Total entries: {len(all_variables):,}")
            logger.info(f"✅ Files processed: {len(all_files)}")
            logger.info(f"✅ Years: {sorted(set(var['year'] for var in all_variables))}")
            logger.info(f"✅ Dataset types: {sorted(set(var['dataset_type'] for var in all_variables))}")
            
            # Show sample
            logger.info("\n📋 Sample entries:")
            sample = df.filter(pl.col('variable_name') != 'FILE_EXISTS').head(10)
            for row in sample.iter_rows(named=True):
                logger.info(f"   • {row['variable_name']} ({row['year']}, {row['dataset_type']})")
        
        else:
            logger.warning("⚠️  No variables found")
    
    def search_catalog(self, search_term: str) -> None:
        """Search the catalog."""
        if not self.catalog_file.exists():
            logger.error("❌ Catalog not found. Run with --create first.")
            return
        
        logger.info(f"🔍 Searching for: '{search_term}'")
        
        df = pl.read_parquet(self.catalog_file)
        
        matches = df.filter(
            pl.col('variable_name').str.contains(search_term, literal=False)
        )
        
        logger.info(f"Found {len(matches)} matches:")
        for row in matches.iter_rows(named=True):
            logger.info(f"   • {row['variable_name']} ({row['year']}, {row['dataset_type']})")
    
    def create_aggregated_catalog(self) -> None:
        """Create aggregated catalog grouping variables by name across all files."""
        logger.info("📊 Creating Aggregated Variable Catalog")
        logger.info("=" * 60)
        
        # First create the detailed catalog
        self.create_fast_catalog()
        
        # Load the detailed catalog
        if not self.catalog_file.exists():
            logger.error("❌ Detailed catalog not found")
            return
        
        df = pl.read_parquet(self.catalog_file)
        
        # Group by variable name and aggregate
        logger.info("🔄 Aggregating variables by name...")
        
        aggregated_vars = []
        
        # Group by variable name
        for var_name in df['variable_name'].unique():
            var_df = df.filter(pl.col('variable_name') == var_name)
            
            # Skip error/timeout entries
            if var_name in ['ERROR', 'TIMEOUT', 'FILE_EXISTS']:
                continue
            
            # Collect years and dataset types
            years = sorted(var_df['year'].unique().to_list())
            dataset_types = sorted(var_df['dataset_type'].unique().to_list())
            files = sorted(var_df['file_name'].unique().to_list())
            
            # Get statistics from all instances
            null_percentages = []
            min_values = []
            max_values = []
            median_values = []
            categorical_values = []
            data_types = []
            
            for row in var_df.iter_rows(named=True):
                if row['null_percentage'] is not None:
                    null_percentages.append(row['null_percentage'])
                if row['min_value'] is not None:
                    min_values.append(row['min_value'])
                if row['max_value'] is not None:
                    max_values.append(row['max_value'])
                if row['median_value'] is not None:
                    median_values.append(row['median_value'])
                if row['categorical_values'] and row['categorical_values'] != 'None':
                    categorical_values.append(row['categorical_values'])
                if row['data_type']:
                    data_types.append(row['data_type'])
            
            # Determine if mostly numeric
            is_numeric = any('float' in dt or 'int' in dt for dt in data_types)
            
            # Create aggregated entry
            agg_var = {
                'variable_name': var_name,
                'appears_in_years': years,
                'appears_in_dataset_types': dataset_types,
                'appears_in_files': files,
                'total_appearances': len(var_df),
                'is_numeric': is_numeric,
                'data_types': list(set(data_types)),
                'avg_null_percentage': sum(null_percentages) / len(null_percentages) if null_percentages else 0,
                'min_null_percentage': min(null_percentages) if null_percentages else 0,
                'max_null_percentage': max(null_percentages) if null_percentages else 0,
            }
            
            if is_numeric and min_values:
                agg_var.update({
                    'overall_min_value': min(min_values),
                    'overall_max_value': max(max_values),
                    'avg_median_value': sum(median_values) / len(median_values) if median_values else None,
                    'categorical_values_seen': None
                })
            else:
                # Combine categorical values from all instances
                all_categorical = set()
                for cat_str in categorical_values:
                    if cat_str and cat_str != 'None' and not cat_str.startswith('Too many'):
                        try:
                            # Parse the string representation of list
                            import ast
                            cat_list = ast.literal_eval(cat_str)
                            if isinstance(cat_list, list):
                                all_categorical.update(str(x) for x in cat_list)
                        except:
                            pass
                
                agg_var.update({
                    'overall_min_value': None,
                    'overall_max_value': None,
                    'avg_median_value': None,
                    'categorical_values_seen': list(all_categorical)[:20] if all_categorical else None  # Limit to 20 values
                })
            
            aggregated_vars.append(agg_var)
        
        # Create DataFrame and save
        if aggregated_vars:
            agg_df = pl.DataFrame(aggregated_vars)
            
            # Save aggregated catalog
            agg_catalog_file = self.processed_dir / "pisa_variable_catalog_aggregated.parquet"
            logger.info(f"💾 Saving aggregated catalog to {agg_catalog_file}")
            agg_df.write_parquet(agg_catalog_file, compression='zstd')
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("🎯 AGGREGATED CATALOG SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✅ Unique variables: {len(aggregated_vars):,}")
            
            # Variables by frequency
            freq_counts = {}
            for var in aggregated_vars:
                freq = len(var['appears_in_years'])
                freq_counts[freq] = freq_counts.get(freq, 0) + 1
            
            logger.info(f"📊 Variable frequency distribution:")
            for freq in sorted(freq_counts.keys(), reverse=True):
                logger.info(f"   • {freq} year(s): {freq_counts[freq]} variables")
            
            # Show examples of most common variables
            most_common = sorted(aggregated_vars, key=lambda x: len(x['appears_in_years']), reverse=True)[:10]
            logger.info(f"\n🔝 Most common variables (appear in most years):")
            for var in most_common:
                logger.info(f"   • {var['variable_name']}: {var['appears_in_years']} ({len(var['appears_in_years'])} years)")
            
            # Show examples of variables with good data quality (low null percentage)
            good_quality = [v for v in aggregated_vars if v['avg_null_percentage'] < 10]
            logger.info(f"\n✨ Variables with <10% null values: {len(good_quality)} variables")
            
        else:
            logger.warning("⚠️  No variables to aggregate")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fast PISA variable catalog")
    parser.add_argument("--create", action="store_true", help="Create detailed catalog")
    parser.add_argument("--aggregate", action="store_true", help="Create aggregated catalog (groups by variable name)")
    parser.add_argument("--search", type=str, help="Search catalog")
    
    args = parser.parse_args()
    
    creator = FastPISAVariableCatalog()
    
    if args.aggregate:
        creator.create_aggregated_catalog()
    elif args.create:
        creator.create_fast_catalog()
    elif args.search:
        creator.search_catalog(args.search)
    else:
        creator.create_fast_catalog()
        print("\nUsage examples:")
        print("  --create        Create detailed catalog")
        print("  --aggregate     Create aggregated catalog (groups by variable name)")
        print("  --search JOY    Search for variables containing 'JOY'")


if __name__ == "__main__":
    main() 