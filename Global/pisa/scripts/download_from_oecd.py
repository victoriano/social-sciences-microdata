#!/usr/bin/env python3
"""
PISA Data Downloader from OECD

This script downloads PISA data directly from the OECD website.
Source: https://webfs.oecd.org/pisa2022/index.html

Data Format by Year:
- 2015-2022: SPSS/SAS compressed files (.zip)
- 2000-2012: TXT files + SPSS/SAS control files (.txt)

Coverage: All PISA cycles from 2000 to 2022
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
from urllib.parse import urljoin, urlparse
import time
import argparse
from tqdm import tqdm

# Base URL for OECD PISA data
OECD_BASE_URL = "https://webfs.oecd.org/"

# PISA data configurations by year
PISA_CONFIG = {
    2022: {
        'url_pattern': 'https://webfs.oecd.org/pisa2022/{filename}',
        'files': {
            'student_questionnaire': 'STU_QQQ_SPSS.zip',
            'student_performance': 'STU_PER_SPSS.zip',
            'school_questionnaire': 'SCH_QQQ_SPSS.zip',
            'teacher_questionnaire': 'TCH_QQQ_SPSS.zip',
            'parent_questionnaire': 'PAR_QQQ_SPSS.zip',
            'financial_literacy': 'FIN_LIT_SPSS.zip',
            'creative_thinking': 'CRT_THK_SPSS.zip'
        }
    },
    2018: {
        'url_pattern': 'https://webfs.oecd.org/pisa2018/{filename}',
        'files': {
            'student_questionnaire': 'SPSS_STU_QQQ.zip',
            'student_performance': 'SPSS_STU_PER.zip',
            'school_questionnaire': 'SPSS_SCH_QQQ.zip',
            'teacher_questionnaire': 'SPSS_TCH_QQQ.zip',
            'parent_questionnaire': 'SPSS_PAR_QQQ.zip',
            'financial_literacy': 'SPSS_FIN_LIT.zip'
        }
    },
    2015: {
        'url_pattern': 'https://webfs.oecd.org/pisa2015/{filename}',
        'files': {
            'student_questionnaire': 'CY6_MS_STU_QQQ_v2.zip',
            'student_performance': 'CY6_MS_STU_PER_v2.zip',
            'school_questionnaire': 'CY6_MS_SCH_QQQ_v2.zip',
            'teacher_questionnaire': 'CY6_MS_TCH_QQQ_v2.zip',
            'parent_questionnaire': 'CY6_MS_PAR_QQQ_v2.zip',
            'financial_literacy': 'CY6_MS_FIN_LIT_v2.zip'
        }
    },
    2012: {
        'url_pattern': 'https://webfs.oecd.org/pisa2012/{filename}',
        'files': {
            'student_questionnaire': 'PISA2012_SPSS_student_questionnaire.zip',
            'student_performance': 'PISA2012_SPSS_student_performance.zip',
            'school_questionnaire': 'PISA2012_SPSS_school_questionnaire.zip',
            'teacher_questionnaire': 'PISA2012_SPSS_teacher_questionnaire.zip',
            'parent_questionnaire': 'PISA2012_SPSS_parent_questionnaire.zip',
            'financial_literacy': 'PISA2012_SPSS_financial_literacy.zip'
        }
    },
    2009: {
        'url_pattern': 'https://webfs.oecd.org/pisa2009/{filename}',
        'files': {
            'student_questionnaire': 'PISA2009_SPSS_student_questionnaire.zip',
            'student_performance': 'PISA2009_SPSS_student_performance.zip',
            'school_questionnaire': 'PISA2009_SPSS_school_questionnaire.zip',
            'teacher_questionnaire': 'PISA2009_SPSS_teacher_questionnaire.zip',
            'parent_questionnaire': 'PISA2009_SPSS_parent_questionnaire.zip'
        }
    },
    2006: {
        'url_pattern': 'https://webfs.oecd.org/pisa2006/{filename}',
        'files': {
            'student_questionnaire': 'PISA2006_SPSS_student_questionnaire.zip',
            'student_performance': 'PISA2006_SPSS_student_performance.zip',
            'school_questionnaire': 'PISA2006_SPSS_school_questionnaire.zip',
            'teacher_questionnaire': 'PISA2006_SPSS_teacher_questionnaire.zip',
            'parent_questionnaire': 'PISA2006_SPSS_parent_questionnaire.zip'
        }
    },
    2003: {
        'url_pattern': 'https://webfs.oecd.org/pisa2003/{filename}',
        'files': {
            'student_questionnaire': 'PISA2003_SPSS_student_questionnaire.zip',
            'student_performance': 'PISA2003_SPSS_student_performance.zip',
            'school_questionnaire': 'PISA2003_SPSS_school_questionnaire.zip',
            'teacher_questionnaire': 'PISA2003_SPSS_teacher_questionnaire.zip',
            'parent_questionnaire': 'PISA2003_SPSS_parent_questionnaire.zip'
        }
    },
    2000: {
        'url_pattern': 'https://webfs.oecd.org/pisa2000/{filename}',
        'files': {
            'student_questionnaire': 'PISA2000_SPSS_student_questionnaire.zip',
            'student_performance': 'PISA2000_SPSS_student_performance.zip',
            'school_questionnaire': 'PISA2000_SPSS_school_questionnaire.zip',
            'teacher_questionnaire': 'PISA2000_SPSS_teacher_questionnaire.zip',
            'parent_questionnaire': 'PISA2000_SPSS_parent_questionnaire.zip'
        }
    }
}

class PISAOECDDownloader:
    """Download PISA data from OECD website."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize downloader with paths."""
        self.base_path = base_path or Path(".")
        self.raw_path = self.base_path / "data" / "raw"
        self.raw_path.mkdir(parents=True, exist_ok=True)
        
        # Create session for efficient downloading
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_file(self, url: str, local_path: Path, description: str = "") -> bool:
        """Download a file from URL to local path."""
        try:
            print(f"📥 Downloading {description or url}...")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Create parent directory if it doesn't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with progress indication
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Simple progress indication
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Downloaded {description or local_path.name}")
            return True
            
        except requests.RequestException as e:
            print(f"\n❌ Failed to download {description or url}: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Error downloading {description or url}: {e}")
            return False
    
    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract a zip file."""
        try:
            print(f"📦 Extracting {zip_path.name}...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            print(f"✅ Extracted to {extract_to}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to extract {zip_path}: {e}")
            return False
    
    def download_year(self, year: int, file_types: Optional[List[str]] = None, force: bool = False) -> bool:
        """Download PISA data for a specific year."""
        if year not in PISA_CONFIG:
            print(f"❌ Year {year} not supported. Available years: {', '.join(map(str, sorted(PISA_CONFIG.keys())))}")
            return False
        
        config = PISA_CONFIG[year]
        year_path = self.raw_path / str(year)
        
        # Check if already exists
        if year_path.exists() and not force:
            print(f"⏭️  Data for {year} already exists. Use --force to re-download.")
            return True
        
        # Use all available file types if not specified
        if file_types is None:
            file_types = list(config['files'].keys())
        
        available_types = list(config['files'].keys())
        invalid_types = [ft for ft in file_types if ft not in available_types]
        
        if invalid_types:
            print(f"❌ Invalid file types for {year}: {', '.join(invalid_types)}")
            print(f"   Available types: {', '.join(available_types)}")
            return False
        
        print(f"📥 Downloading PISA {year} data...")
        print(f"   Output directory: {year_path}")
        print(f"   File types: {', '.join(file_types)}")
        
        # Create year directory
        year_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for file_type in file_types:
            filename = config['files'][file_type]
            url = config['url_pattern'].format(filename=filename)
            
            # Create subdirectory for this file type
            type_dir = year_path / file_type
            type_dir.mkdir(exist_ok=True)
            
            # Download file
            zip_path = type_dir / filename
            
            print(f"\n  📁 {file_type}:")
            print(f"     URL: {url}")
            print(f"     Saving to: {zip_path}")
            
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Write file with progress feedback
                total_size = int(response.headers.get('content-length', 0))
                with open(zip_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"     Progress: {percent:.1f}%", end='\r')
                
                print(f"     ✅ Downloaded: {zip_path}")
                
                # Extract ZIP file
                print(f"     📦 Extracting {filename}...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(type_dir)
                
                print(f"     ✅ Extracted to: {type_dir}")
                
                # Delete ZIP file after successful extraction
                zip_path.unlink()
                print(f"     🗑️  Deleted ZIP file: {zip_path}")
                
                success_count += 1
                
            except requests.exceptions.RequestException as e:
                print(f"     ❌ Failed to download {file_type}: {e}")
                continue
            except zipfile.BadZipFile as e:
                print(f"     ❌ Failed to extract {file_type}: {e}")
                continue
            except Exception as e:
                print(f"     ❌ Unexpected error with {file_type}: {e}")
                continue
        
        if success_count == len(file_types):
            print(f"\n✅ Successfully downloaded all {year} data!")
        elif success_count > 0:
            print(f"\n⚠️  Downloaded {success_count}/{len(file_types)} file types for {year}")
        else:
            print(f"\n❌ Failed to download any data for {year}")
        
        return success_count > 0
    
    def download_multiple_years(self, years: List[int], file_types: Optional[List[str]] = None, force: bool = False) -> Dict[str, bool]:
        """Download PISA data for multiple years."""
        results = {}
        
        print(f"📥 Downloading PISA data for years: {', '.join(map(str, years))}")
        
        for year in years:
            print(f"\n{'='*60}")
            print(f"Processing year: {year}")
            print(f"{'='*60}")
            
            results[str(year)] = self.download_year(year, file_types, force)
        
        # Overall summary
        print(f"\n{'='*60}")
        print("📊 Download Summary:")
        print(f"{'='*60}")
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for year, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {year}: {status}")
        
        print(f"\n📈 Overall: {successful}/{total} years downloaded successfully")
        
        return results
    
    def get_available_file_types(self, year: int) -> List[str]:
        """Get available file types for a specific year."""
        if year not in PISA_CONFIG:
            return []
        
        return list(PISA_CONFIG[year]['files'].keys())
    
    def status(self) -> Dict[str, Any]:
        """Get current status of local data."""
        status = {}
        
        for year in PISA_CONFIG.keys():
            year_path = self.raw_path / str(year)
            
            if year_path.exists():
                files = list(year_path.glob("*"))
                status[str(year)] = {
                    "exists": True,
                    "files_count": len(files),
                    "files": [f.name for f in files]
                }
            else:
                status[str(year)] = {
                    "exists": False,
                    "files_count": 0,
                    "files": []
                }
        
        return status

def get_available_years() -> List[int]:
    """Get list of available PISA years."""
    return list(PISA_CONFIG.keys())

def get_file_types(year: int) -> List[str]:
    """Get available file types for a given year."""
    if year not in PISA_CONFIG:
        return []
    return list(PISA_CONFIG[year]['files'].keys())

def show_status():
    """Show available years and file types."""
    print("Available PISA years and file types:")
    for year in sorted(PISA_CONFIG.keys()):
        available_types = get_file_types(year)
        print(f"\n{year}:")
        for file_type in available_types:
            print(f"  - {file_type}")
    
    print(f"\nSupported years: {', '.join(map(str, sorted(PISA_CONFIG.keys())))}")

def download_year(year: int, file_types: Optional[List[str]] = None, output_dir: Optional[str] = None) -> bool:
    """Download PISA data for a specific year."""
    if year not in PISA_CONFIG:
        print(f"Error: Year {year} not supported")
        print(f"Available years: {', '.join(map(str, sorted(PISA_CONFIG.keys())))}")
        return False
    
    config = PISA_CONFIG[year]
    
    # Use default output directory if not specified
    if output_dir is None:
        output_dir_path = Path(__file__).parent.parent / "data" / "raw" / str(year)
    else:
        output_dir_path = Path(output_dir)
    
    # Use all available file types if not specified
    if file_types is None:
        file_types = list(config['files'].keys())
    
    # Validate file types
    available_types = list(config['files'].keys())
    invalid_types = [ft for ft in file_types if ft not in available_types]
    if invalid_types:
        print(f"Error: Invalid file types for {year}: {', '.join(invalid_types)}")
        print(f"Available types: {', '.join(available_types)}")
        return False
    
    print(f"Downloading PISA {year} data...")
    print(f"Output directory: {output_dir_path}")
    print(f"File types: {', '.join(file_types)}")
    
    success = True
    
    for file_type in file_types:
        filename = config['files'][file_type]
        url = config['url_pattern'].format(filename=filename)
        
        # Create subdirectory for this file type
        type_dir = output_dir_path / file_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # Download file
        zip_path = type_dir / filename
        
        print(f"\nDownloading {file_type}...")
        print(f"  URL: {url}")
        print(f"  Saving to: {zip_path}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Write file with progress bar
            total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"  {filename}") as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            print(f"  ✓ Downloaded: {zip_path}")
            
            # Extract ZIP file
            print(f"  Extracting {filename}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(type_dir)
            
            print(f"  ✓ Extracted to: {type_dir}")
            
            # Delete ZIP file after successful extraction
            zip_path.unlink()
            print(f"  ✓ Deleted ZIP file: {zip_path}")
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Failed to download {file_type}: {e}")
            success = False
            continue
        except zipfile.BadZipFile as e:
            print(f"  ✗ Failed to extract {file_type}: {e}")
            success = False
            continue
        except Exception as e:
            print(f"  ✗ Unexpected error with {file_type}: {e}")
            success = False
            continue
    
    if success:
        print(f"\n✓ Successfully downloaded all PISA {year} data!")
    else:
        print(f"\n✗ Some downloads failed for PISA {year}")
    
    return success

def download_multiple_years(years: List[int], file_types: Optional[List[str]] = None, output_dir: Optional[str] = None) -> bool:
    """Download PISA data for multiple years."""
    print(f"Downloading PISA data for years: {', '.join(map(str, years))}")
    
    overall_success = True
    
    for year in years:
        print(f"\n{'='*50}")
        success = download_year(year, file_types, output_dir)
        if not success:
            overall_success = False
    
    print(f"\n{'='*50}")
    if overall_success:
        print("✓ All downloads completed successfully!")
    else:
        print("✗ Some downloads failed. Check the output above for details.")
    
    return overall_success

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Download PISA data from OECD website")
    parser.add_argument("--years", nargs="+", type=int, help="Years to download (e.g., 2022 2018)")
    parser.add_argument("--file-types", nargs="+", 
                       help="File types to download (e.g., student_questionnaire school_questionnaire)")
    parser.add_argument("--output-dir", type=str, help="Output directory (default: data/raw/)")
    parser.add_argument("--status", action="store_true", help="Show available years and file types")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if not args.years:
        # Default to downloading recent years
        years = [2022, 2018]
        print(f"No years specified. Downloading recent years: {', '.join(map(str, years))}")
    else:
        years = args.years
    
    # Validate years
    available_years = get_available_years()
    invalid_years = [y for y in years if y not in available_years]
    if invalid_years:
        print(f"Error: Invalid years: {', '.join(map(str, invalid_years))}")
        print(f"Available years: {', '.join(map(str, sorted(available_years)))}")
        return
    
    # Handle single year vs multiple years
    if len(years) == 1:
        success = download_year(years[0], args.file_types, args.output_dir)
    else:
        success = download_multiple_years(years, args.file_types, args.output_dir)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 