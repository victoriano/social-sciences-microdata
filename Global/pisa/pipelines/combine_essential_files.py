#!/usr/bin/env python3
"""
Combine Essential PISA Files
============================

Combines individual year PISA essential files into comprehensive datasets.
Handles data type harmonization between years.

Usage:
    uv run python combine_essential_files.py
"""

import polars as pl
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_essential_files():
    """Combine individual year essential files."""
    
    # Paths
    individual_dir = Path("../data/processed/individual_years")
    combined_dir = Path("../data/processed/combined")
    spain_dir = Path("../data/processed/spain")
    
    combined_dir.mkdir(exist_ok=True)
    spain_dir.mkdir(exist_ok=True)
    
    logger.info("🔗 Combining individual year files...")
    
    # Find essential files
    essential_files = list(individual_dir.glob("pisa_*_essential.parquet"))
    essential_files = sorted(essential_files)
    
    if not essential_files:
        logger.error("❌ No essential files found")
        return
    
    logger.info(f"📥 Found {len(essential_files)} files to combine")
    
    # Load and harmonize data types
    year_dfs = []
    for file_path in essential_files:
        logger.info(f"   Loading {file_path.name}")
        df = pl.read_parquet(file_path)
        
        # Harmonize data types - cast everything to string first for categorical columns
        df_harmonized = df.clone()
        
        # Convert problematic columns to string
        for col in df.columns:
            if df[col].dtype == pl.Categorical:
                df_harmonized = df_harmonized.with_columns(
                    pl.col(col).cast(pl.String).alias(col)
                )
        
        year_dfs.append(df_harmonized)
        logger.info(f"   • {len(df):,} students, {len(df.columns)} variables")
    
    # Combine using diagonal concatenation
    logger.info("🔄 Combining all years...")
    combined_df = pl.concat(year_dfs, how='diagonal')
    
    # Summary
    years = sorted(combined_df['pisa_year'].unique().to_list())
    year_range = f"{min(years)}_{max(years)}"
    total_students = len(combined_df)
    
    logger.info(f"✅ Combined dataset: {total_students:,} students across {len(years)} years ({min(years)}-{max(years)})")
    
    # Save combined international dataset
    combined_file = combined_dir / f"pisa_essential_{year_range}.parquet"
    combined_df.write_parquet(combined_file, compression='zstd')
    logger.info(f"💾 International dataset: {combined_file.name}")
    
    # Create Spain dataset
    logger.info("🇪🇸 Creating Spain dataset...")
    spain_codes = ['ESP', 'Spain', 'ES', '724']
    
    # Filter for Spain
    spain_filter = pl.lit(False)
    for col in ['CNT', 'country_name']:
        if col in combined_df.columns:
            spain_filter = spain_filter | pl.col(col).cast(pl.String).is_in(spain_codes)
    
    spain_df = combined_df.filter(spain_filter)
    
    if len(spain_df) > 0:
        spain_file = spain_dir / f"spain_essential_{year_range}.parquet"
        spain_df.write_parquet(spain_file, compression='zstd')
        logger.info(f"💾 Spain dataset: {spain_file.name} ({len(spain_df):,} students)")
        
        # Spain summary by year
        spain_summary = (spain_df
                       .group_by('pisa_year')
                       .agg([
                           pl.count().alias('students'),
                           pl.col('overall_performance').mean().alias('avg_performance'),
                           pl.col('ESCS').mean().alias('avg_escs'),
                           pl.col('WEALTH').mean().alias('avg_wealth')
                       ])
                       .sort('pisa_year'))
        
        logger.info("📊 Spain by year:")
        for row in spain_summary.iter_rows(named=True):
            perf = f"{row['avg_performance']:.1f}" if row['avg_performance'] else "N/A"
            escs = f"{row['avg_escs']:.2f}" if row['avg_escs'] else "N/A"
            logger.info(f"   {row['pisa_year']}: {row['students']:,} students, performance: {perf}, ESCS: {escs}")
        
        # Save Spain summary
        summary_file = spain_dir / f"spain_summary_{year_range}.csv"
        spain_summary.write_csv(summary_file)
        logger.info(f"💾 Spain summary: {summary_file.name}")
    else:
        logger.warning("⚠️  No Spanish students found")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("🎯 COMBINATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Total students: {total_students:,}")
    logger.info(f"✅ Years processed: {years}")
    logger.info(f"✅ Spain students: {len(spain_df):,}")
    logger.info(f"✅ Variables: {len(combined_df.columns)}")
    logger.info(f"📁 Files created:")
    logger.info(f"   🌍 International: {combined_file}")
    logger.info(f"   🇪🇸 Spain: {spain_file if len(spain_df) > 0 else 'None'}")
    logger.info("\n🎉 All PISA essential datasets ready for analysis!")

if __name__ == "__main__":
    combine_essential_files() 