#!/usr/bin/env python3
"""
PISA SPSS Syntax Processor
===========================

This script processes older PISA data (2012 and earlier) that comes in 
SPSS syntax + TXT format instead of direct .sav files.

Converts SPSS syntax + TXT files to .sav format for use with our 
standard conversion pipeline.

Usage:
    uv run python process_spss_syntax.py
"""

import pandas as pd
import polars as pl
from pathlib import Path
import logging
import re
from typing import Dict, List, Optional, Tuple
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SPSSSyntaxProcessor:
    """Process PISA SPSS syntax files and TXT data."""
    
    def __init__(self, raw_dir: str = "data/Global/pisa/raw"):
        """Initialize processor."""
        self.raw_dir = Path(raw_dir)
        
        # Years that use syntax + TXT format
        self.syntax_years = [2006, 2009, 2012]
        
    def find_syntax_files(self, year: int) -> Dict[str, Dict[str, Optional[Path]]]:
        """Find SPSS syntax and TXT files for a given year."""
        year_dir = self.raw_dir / str(year)
        
        if not year_dir.exists():
            logger.warning(f"Directory for year {year} not found: {year_dir}")
            return {}
        
        found_files = {}
        
        # File patterns by year
        if year == 2012:
            # 2012 patterns
            file_patterns = {
                'stu': {
                    'syntax': "SPSS syntax to read in student questionnaire data file.txt",
                    'data': "INT_STU12_DEC03.txt"
                },
                'cog': {
                    'syntax': "SPSS syntax to read in cognitive item response data file.txt", 
                    'data': "INT_COG12_DEC03.txt"
                },
                'sch': {
                    'syntax': "SPSS syntax to read in school questionnaire data file.txt",
                    'data': "INT_SCQ12_DEC03.txt"
                }
            }
        elif year == 2009:
            # 2009 patterns
            file_patterns = {
                'stu': {
                    'syntax': "PISA2009_SPSS_student.txt",
                    'data': "INT_STQ09_DEC11.txt"
                },
                'cog': {
                    'syntax': "PISA2009_SPSS_cognitive_item.txt",
                    'data': "INT_COG09_TD_DEC11.txt"
                },
                'sch': {
                    'syntax': "PISA2009_SPSS_school.txt", 
                    'data': "INT_SCQ09_Dec11.txt"
                }
            }
        elif year == 2006:
            # 2006 patterns
            file_patterns = {
                'stu': {
                    'syntax': "PISA2006_SPSS_student.txt",
                    'data': "INT_Stu06_Dec07.txt"
                },
                'cog': {
                    'syntax': "PISA2006_SPSS_cognitive_item.txt",
                    'data': "INT_Cogn06_T_Dec07.txt"
                },
                'sch': {
                    'syntax': "PISA2006_SPSS_school.txt",
                    'data': "INT_Sch06_Dec07.txt"
                }
            }
        else:
            logger.warning(f"Unknown year pattern for {year}")
            return {}
        
        # Check if files exist
        for file_type, patterns in file_patterns.items():
            syntax_file = year_dir / patterns['syntax']
            data_file = year_dir / patterns['data']
            
            if syntax_file.exists() and data_file.exists():
                found_files[file_type] = {
                    'syntax': syntax_file,
                    'data': data_file
                }
                logger.info(f"Found {year} {file_type}: {syntax_file.name} + {data_file.name}")
            else:
                logger.warning(f"Missing {year} {file_type} files:")
                if not syntax_file.exists():
                    logger.warning(f"  - Missing syntax: {patterns['syntax']}")
                if not data_file.exists():
                    logger.warning(f"  - Missing data: {patterns['data']}")
                found_files[file_type] = {'syntax': None, 'data': None}
        
        return found_files
    
    def parse_spss_syntax(self, syntax_file: Path) -> Dict:
        """Parse SPSS syntax file to extract variable information."""
        logger.info(f"Parsing SPSS syntax: {syntax_file.name}")
        
        try:
            with open(syntax_file, 'r', encoding='utf-8', errors='ignore') as f:
                syntax_content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            with open(syntax_file, 'r', encoding='latin-1', errors='ignore') as f:
                syntax_content = f.read()
        
        variables = {}
        variable_labels = {}
        value_labels = {}
        
        # Parse variable definitions - look for DATA LIST FILE
        in_data_list = False
        lines = syntax_content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if we're starting DATA LIST
            if 'DATA LIST FILE' in line.upper():
                in_data_list = True
                continue
                
            # Check if we're ending DATA LIST (look for EXECUTE or similar)
            if in_data_list and (line.endswith('.') and not re.match(r'^\s*\w+\s+\d+', line)):
                in_data_list = False
                continue
                
            # Parse variable definitions within DATA LIST
            if in_data_list:
                # Match patterns like: CNT  1 - 3  (A) or ST01Q01  23 - 24  (F,0)
                # Also handle variations with more spaces
                var_match = re.match(r'^\s*(\w+)\s+(\d+)\s*-\s*(\d+)\s*(\([^)]+\))?', line)
                if var_match:
                    var_name = var_match.group(1)
                    start_pos = int(var_match.group(2))
                    end_pos = int(var_match.group(3))
                    format_spec = var_match.group(4) if var_match.group(4) else ''
                    
                    variables[var_name] = {
                        'start': start_pos - 1,  # Convert to 0-based
                        'end': end_pos,
                        'width': end_pos - start_pos + 1,
                        'format': format_spec
                    }
        
        # Parse variable labels (simpler approach)
        var_label_section = False
        for i, line in enumerate(lines):
            if 'VARIABLE LABELS' in line.upper():
                var_label_section = True
                continue
            
            if var_label_section:
                # End of labels section
                if line.strip() == '' or 'EXECUTE' in line.upper() or 'FORMATS' in line.upper():
                    var_label_section = False
                    continue
                    
                # Match label patterns like: CNT "Country code 3-character"
                label_match = re.match(r'^\s*(\w+)\s+"([^"]*)"', line)
                if label_match:
                    var_name = label_match.group(1)
                    label = label_match.group(2)
                    variable_labels[var_name] = label
        
        logger.info(f"Parsed {len(variables)} variables from syntax")
        return {
            'variables': variables,
            'variable_labels': variable_labels,
            'value_labels': value_labels
        }
    
    def read_fixed_width_data(self, txt_file: Path, syntax_info: Dict) -> pd.DataFrame:
        """Read fixed-width TXT data using SPSS syntax information."""
        logger.info(f"Reading fixed-width data: {txt_file.name}")
        
        variables = syntax_info['variables']
        
        if not variables:
            logger.error("No variable information found in syntax")
            return pd.DataFrame()
        
        # Prepare column specifications for pandas
        colspecs = []
        names = []
        
        for var_name, var_info in variables.items():
            colspecs.append((var_info['start'], var_info['end']))
            names.append(var_name)
        
        try:
            # Read fixed-width file
            df = pd.read_fwf(
                txt_file,
                colspecs=colspecs,
                names=names,
                dtype=str  # Read everything as string first
            )
            
            # Convert numeric columns
            for var_name, var_info in variables.items():
                if var_info.get('format') and 'A' not in var_info.get('format', ''):
                    # Numeric variable
                    try:
                        df[var_name] = pd.to_numeric(df[var_name], errors='coerce')
                    except:
                        pass  # Keep as string if conversion fails
            
            logger.info(f"Read {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error reading fixed-width data: {e}")
            return pd.DataFrame()
    
    def process_year_syntax_data(self, year: int) -> bool:
        """Process all syntax+TXT files for a given year."""
        logger.info(f"\n🔄 Processing PISA {year} syntax + TXT data...")
        
        found_files = self.find_syntax_files(year)
        if not found_files:
            logger.warning(f"No syntax files found for {year}")
            return False
        
        year_success = True
        
        for file_type, files in found_files.items():
            if files['syntax'] is None or files['data'] is None:
                logger.warning(f"Skipping {file_type} - missing files")
                continue
                
            try:
                # Parse SPSS syntax
                syntax_info = self.parse_spss_syntax(files['syntax'])
                
                if not syntax_info['variables']:
                    logger.error(f"No variables found in {file_type} syntax")
                    continue
                
                # Read TXT data
                df = self.read_fixed_width_data(files['data'], syntax_info)
                
                if df.empty:
                    logger.error(f"No data read from {file_type} TXT file")
                    continue
                
                # Save as SPSS .sav file for compatibility with our pipeline
                output_dir = self.raw_dir / str(year)
                output_file = output_dir / f"{file_type}_{year}_converted.sav"
                
                # Use pyreadstat to save as SPSS format
                try:
                    import pyreadstat
                    
                    # Prepare metadata
                    variable_labels = syntax_info.get('variable_labels', {})
                    
                    # Note: pyreadstat write_sav has different parameters
                    # Just save without labels for now - the data is what's important
                    pyreadstat.write_sav(
                        df, 
                        str(output_file)
                    )
                    
                    logger.info(f"✅ Converted {file_type} to .sav: {output_file.name}")
                    
                except ImportError:
                    # Fallback: save as CSV (can be read by our conversion pipeline)
                    output_file = output_dir / f"{file_type}_{year}_converted.csv"
                    df.to_csv(output_file, index=False)
                    logger.info(f"✅ Converted {file_type} to CSV: {output_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {year} {file_type}: {e}")
                year_success = False
        
        return year_success
    
    def run_syntax_processing(self) -> None:
        """Run syntax processing for all available years."""
        logger.info("🔄 STARTING SPSS SYNTAX PROCESSING")
        logger.info("=" * 50)
        
        # Check which syntax years have data
        available_years = []
        for year in self.syntax_years:
            year_dir = self.raw_dir / str(year)
            if year_dir.exists():
                # Use the actual file finding logic to check
                found_files = self.find_syntax_files(year)
                if found_files and any(files['syntax'] is not None and files['data'] is not None 
                                     for files in found_files.values()):
                    available_years.append(year)
        
        if not available_years:
            logger.error("❌ No SPSS syntax + TXT files found!")
            logger.error("Please download PISA syntax files and place them in:")
            for year in self.syntax_years:
                logger.error(f"  data/Global/pisa/raw/{year}/ (for PISA {year} files)")
            logger.error("\nRequired for each year:")
            logger.error("  - SPSS syntax files (.sps)")
            logger.error("  - TXT data files (.txt)")
            return
        
        logger.info(f"Found syntax data for years: {available_years}")
        
        # Process each year
        processing_results = {}
        for year in available_years:
            success = self.process_year_syntax_data(year)
            processing_results[year] = success
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("🎯 SYNTAX PROCESSING SUMMARY")
        logger.info("=" * 50)
        
        for year, success in processing_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"PISA {year}: {status}")
        
        successful_years = [year for year, success in processing_results.items() if success]
        if successful_years:
            logger.info(f"\n🚀 SYNTAX PROCESSING COMPLETE!")
            logger.info("Converted files are now available as .sav or .csv format")
            logger.info("Next step: Run the standard conversion script:")
            logger.info("  uv run python convert_pisa_trend_data.py")
        else:
            logger.error("\n⚠️ All syntax processing failed. Check error messages above.")

def main():
    """Main function."""
    processor = SPSSSyntaxProcessor()
    processor.run_syntax_processing()

if __name__ == "__main__":
    main() 