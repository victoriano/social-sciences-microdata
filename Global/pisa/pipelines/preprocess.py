#!/usr/bin/env python3
"""
PISA Data Conversion Script
===========================

This script converts PISA 2022 SPSS (.sav) files to Parquet format for fast analysis with Polars.
Run this script after downloading PISA data files to data/Global/pisa/raw/

Usage:
    uv run python convert_pisa_data.py
"""

import pandas as pd
import polars as pl
from pathlib import Path
import logging
from typing import Dict, List
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PISADataConverter:
    """Convert PISA SPSS files to Parquet format."""
    
    def __init__(self, raw_dir: str = "data/Global/pisa/raw", processed_dir: str = "data/Global/pisa/processed"):
        """Initialize converter with input and output directories."""
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        
        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Expected PISA file patterns
        self.file_patterns = {
            'student_questionnaire': 'STU_QQQ.sav',
            'student_cognitive': 'STU_COG.sav', 
            'school_questionnaire': 'SCH_QQQ.sav'
        }
        
    def find_pisa_files(self) -> Dict[str, Path]:
        """Find PISA data files in the raw directory."""
        found_files = {}
        
        for file_type, pattern in self.file_patterns.items():
            matching_files = list(self.raw_dir.glob(f"*{pattern}"))
            if matching_files:
                found_files[file_type] = matching_files[0]
                logger.info(f"Found {file_type}: {matching_files[0].name}")
            else:
                logger.warning(f"No file found matching pattern '*{pattern}'")
        
        return found_files
    
    def convert_spss_to_parquet(self, spss_file: Path, output_name: str) -> bool:
        """Convert a single SPSS file to Parquet format."""
        try:
            logger.info(f"Converting {spss_file.name}...")
            
            # Read SPSS file with pandas
            logger.info("Reading SPSS file (this may take a few minutes)...")
            df_pandas = pd.read_spss(str(spss_file))
            
            # Convert to Polars (faster and more memory efficient)
            logger.info("Converting to Polars DataFrame...")
            df_polars = pl.from_pandas(df_pandas)
            
            # Save as Parquet
            output_path = self.processed_dir / f"{output_name}.parquet"
            logger.info(f"Saving to {output_path}...")
            df_polars.write_parquet(output_path)
            
            # Log basic info
            logger.info(f"✅ Converted successfully!")
            logger.info(f"   Shape: {df_polars.shape}")
            logger.info(f"   Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error converting {spss_file.name}: {e}")
            return False
    
    def extract_spain_data(self, df_path: Path, output_name: str) -> bool:
        """Extract only Spanish data for faster analysis."""
        try:
            logger.info(f"Extracting Spanish data from {df_path.name}...")
            
            # Read full dataset
            df = pl.read_parquet(df_path)
            
            # Filter for Spain (CNT = 'ESP')
            if 'CNT' in df.columns:
                spain_df = df.filter(pl.col('CNT') == 'ESP')
                
                # Save Spain-only data
                spain_path = self.processed_dir / f"{output_name}_spain.parquet"
                spain_df.write_parquet(spain_path)
                
                logger.info(f"✅ Spanish data extracted!")
                logger.info(f"   Spanish students: {len(spain_df)}")
                logger.info(f"   Spain file size: {spain_path.stat().st_size / 1024 / 1024:.1f} MB")
                
                return True
            else:
                logger.warning("No 'CNT' column found - cannot filter by country")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error extracting Spanish data: {e}")
            return False
    
    def get_spain_key_variables(self) -> Dict[str, List[str]]:
        """Define key variables for Spain youth analysis."""
        return {
            'student_questionnaire': [
                'CNT',           # Country code
                'TMINS',         # Time spent on homework
                'MOTIVAT',       # Motivation indices
                'BELONG',        # School belonging
                'ESCS',          # Socioeconomic status
                'PERSEV',        # Perseverance
                'COMPETE',       # Competitiveness
                'ST004D01T',     # Gender
                'AGE',           # Age
                'WORKMAST',      # Work mastery
                'OPENPS',        # Openness to problem solving
            ],
            'student_cognitive': [
                'CNT',           # Country code
                'PVMATH1', 'PVMATH2', 'PVMATH3', 'PVMATH4', 'PVMATH5',  # Math scores
                'PVREAD1', 'PVREAD2', 'PVREAD3', 'PVREAD4', 'PVREAD5',  # Reading scores
                'PVSCIE1', 'PVSCIE2', 'PVSCIE3', 'PVSCIE4', 'PVSCIE5',  # Science scores
            ]
        }
    
    def create_analysis_ready_dataset(self) -> bool:
        """Create a combined, analysis-ready dataset for Spain youth analysis."""
        try:
            logger.info("Creating analysis-ready dataset...")
            
            # Check if processed files exist
            student_q_path = self.processed_dir / "student_questionnaire.parquet"
            student_c_path = self.processed_dir / "student_cognitive.parquet"
            
            if not student_q_path.exists() or not student_c_path.exists():
                logger.error("Missing processed data files. Run conversion first.")
                return False
            
            # Read datasets
            df_questionnaire = pl.read_parquet(student_q_path)
            df_cognitive = pl.read_parquet(student_c_path)
            
            # Get key variables
            key_vars = self.get_spain_key_variables()
            
            # Select key variables (if they exist)
            q_vars = [var for var in key_vars['student_questionnaire'] if var in df_questionnaire.columns]
            c_vars = [var for var in key_vars['student_cognitive'] if var in df_cognitive.columns]
            
            df_q_subset = df_questionnaire.select(q_vars)
            df_c_subset = df_cognitive.select(c_vars)
            
            # Merge datasets on CNT and student ID (if available)
            # For now, just save separately
            analysis_q_path = self.processed_dir / "analysis_student_questionnaire.parquet"
            analysis_c_path = self.processed_dir / "analysis_student_cognitive.parquet"
            
            df_q_subset.write_parquet(analysis_q_path)
            df_c_subset.write_parquet(analysis_c_path)
            
            # Create Spain-only analysis dataset
            spain_q = df_q_subset.filter(pl.col('CNT') == 'ESP')
            spain_c = df_c_subset.filter(pl.col('CNT') == 'ESP')
            
            spain_q.write_parquet(self.processed_dir / "spain_analysis_questionnaire.parquet")
            spain_c.write_parquet(self.processed_dir / "spain_analysis_cognitive.parquet")
            
            logger.info("✅ Analysis-ready datasets created!")
            logger.info(f"   Questionnaire variables: {len(q_vars)}")
            logger.info(f"   Cognitive variables: {len(c_vars)}")
            logger.info(f"   Spanish students (questionnaire): {len(spain_q)}")
            logger.info(f"   Spanish students (cognitive): {len(spain_c)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating analysis dataset: {e}")
            return False
    
    def run_conversion(self) -> None:
        """Run the complete conversion process."""
        logger.info("🔄 Starting PISA Data Conversion Process")
        logger.info("=" * 50)
        
        # Find PISA files
        found_files = self.find_pisa_files()
        
        if not found_files:
            logger.error("❌ No PISA data files found!")
            logger.error("Please download PISA 2022 data files and place them in data/pisa/raw/")
            logger.error("Required files:")
            for file_type, pattern in self.file_patterns.items():
                logger.error(f"  - *{pattern}")
            sys.exit(1)
        
        # Convert each file
        conversion_results = {}
        for file_type, file_path in found_files.items():
            success = self.convert_spss_to_parquet(file_path, file_type)
            conversion_results[file_type] = success
        
        # Create analysis-ready datasets if conversions successful
        if all(conversion_results.values()):
            logger.info("\n📊 Creating analysis-ready datasets...")
            self.create_analysis_ready_dataset()
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("🎯 CONVERSION SUMMARY")
        logger.info("=" * 50)
        
        for file_type, success in conversion_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{file_type}: {status}")
        
        if all(conversion_results.values()):
            logger.info("\n🚀 Ready for analysis!")
            logger.info("Next steps:")
            logger.info("1. Run: uv run jupyter notebook youth_analysis_demo.ipynb")
            logger.info("2. Or run: uv run python youth_analysis.py")
        else:
            logger.info("\n⚠️ Some conversions failed. Check error messages above.")

def main():
    """Main function."""
    converter = PISADataConverter()
    converter.run_conversion()

if __name__ == "__main__":
    main() 