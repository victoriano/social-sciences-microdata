#!/usr/bin/env python3
"""
PISA Data Downloader from OECD

This script downloads PISA data directly from the OECD website.
Source: https://webfs.oecd.org/pisa2022/index.html

Data Format by Year:
- 2015-2025: SPSS/SAS compressed files (.zip)
- 2000-2012: TXT files + SPSS/SAS control files (.txt)

Coverage: All PISA cycles from 2000 to 2025
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

# Download configuration
DOWNLOAD_DELAY = 1.0  # Be respectful to OECD servers
OECD_BASE_URL = "https://webfs.oecd.org/"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PISA_DATA_DIR = REPO_ROOT / "data" / "Global" / "pisa"

# Browser headers to avoid anti-bot blocking
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"macOS"',
    'Sec-CH-UA-Platform-Version': '"13.0.0"',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
}

# PISA Download Configuration - URL pattern and file naming for different years
PISA_CONFIG = {
    2025: {
        'url_pattern': 'https://webfs.oecd.org/pisa2022/2025/{filename}',
        'format': 'compressed',
        'files': {
            'student_questionnaire': 'CY09_MS_STU_PUF.zip',
            'school_questionnaire': 'CY09_MS_SCH_PUF.zip',
            'teacher_questionnaire': 'CY09_MS_TCH_PUF.zip',
            'cognitive_item': 'CY09_MS_COG_PUF.zip',
            'cognitive_process': 'CY09_MS_COG_PROCESS_PUF.zip',
            'questionnaire_timing': 'CY09_MS_STU_TT_PUF.zip',
        }
    },
    2022: {
        'url_pattern': 'https://webfs.oecd.org/pisa2022/{filename}',
        'format': 'compressed',
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
        'format': 'compressed',
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
        'format': 'compressed',
        'files': {
            'student_questionnaire': 'SPSS_STU_QQQ.zip',
            'school_questionnaire': 'SPSS_SCH_QQQ.zip',
            'teacher_questionnaire': 'SPSS_TCH_QQQ.zip',
            'cognitive_item': 'SPSS_STU_COG.zip',
            'questionnaire_timing': 'SPSS_STU_TIM.zip',
            'financial_literacy': 'SPSS_FIN_LIT.zip'
        }
    },
    2012: {
        'base_url': 'https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2012-datasets/',
        'format': 'txt_with_control',
        'files': {
            'student_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_STU12_DEC03.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2012_SPSS_student.txt'
            },
            'school_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_SCH12_DEC03.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2012_SPSS_school.txt'
            },
            'parent_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_PAR12_DEC03.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2012_SPSS_parent.txt'
            },
            'cognitive_item': {
                'txt': 'data-sets-in-txt-format/INT_COG12_DEC03.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2012_SPSS_cognitive_item.txt'
            },
            'scored_cognitive': {
                'txt': 'data-sets-in-txt-format/INT_COG12_S_DEC03.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2012_SPSS_scored_cognitive.txt'
            }
        }
    },
    2009: {
        'base_url': 'https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2009-datasets/',
        'format': 'txt_with_control',
        'files': {
            'student_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_STU09_DEC11.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2009_SPSS_student.txt'
            },
            'school_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_SCH09_DEC11.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2009_SPSS_school.txt'
            },
            'parent_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_PAR09_DEC11.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2009_SPSS_parent.txt'
            },
            'cognitive_item': {
                'txt': 'data-sets-in-txt-format/INT_COG09_TD_DEC11.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2009_SPSS_cognitive_item.txt'
            },
            'scored_cognitive': {
                'txt': 'data-sets-in-txt-format/INT_COG09_S_DEC11.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2009_SPSS_scored_cognitive.txt'
            }
        }
    },
    2006: {
        'base_url': 'https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2006-datasets/',
        'format': 'txt_with_control',
        'files': {
            'student_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_STU06_DEC07.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2006_SPSS_student.txt'
            },
            'school_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_SCH06_DEC07.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2006_SPSS_school.txt'
            },
            'parent_questionnaire': {
                'txt': 'data-sets-in-txt-format/INT_PAR06_DEC07.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2006_SPSS_parent.txt'
            },
            'cognitive_item': {
                'txt': 'data-sets-in-txt-format/INT_COG06_T_DEC07.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2006_SPSS_cognitive_item.txt'
            },
            'scored_cognitive': {
                'txt': 'data-sets-in-txt-format/INT_COG06_S_DEC07.txt',
                'spss_control': 'sas-and-spss-control-files/PISA2006_SPSS_scored_cognitive.txt'
            }
        }
    },
    2003: {
        'base_url': 'https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2003-datasets/',
        'format': 'zip_with_control',
        'files': {
            'student_questionnaire': {
                'zip': 'data-sets-in-txt-formats/INT_stui_2003_v2.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2003_SPSS_student.txt'
            },
            'school_questionnaire': {
                'zip': 'data-sets-in-txt-formats/INT_schi_2003.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2003_SPSS_school.txt'
            },
            'cognitive_item': {
                'zip': 'data-sets-in-txt-formats/INT_cogn_2003.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2003_SPSS_cognitive_item.txt'
            }
        }
    },
    2000: {
        'base_url': 'https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2000-datasets/',
        'format': 'zip_with_control',
        'files': {
            'student_math': {
                'zip': 'data-sets-in-txt-formats/intstud_math.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2000_SPSS_student_math.txt'
            },
            'student_reading': {
                'zip': 'data-sets-in-txt-formats/intstud_read.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2000_SPSS_student_reading.txt'
            },
            'student_science': {
                'zip': 'data-sets-in-txt-formats/intstud_scie.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2000_SPSS_student_science.txt'
            },
            'school_questionnaire': {
                'zip': 'data-sets-in-txt-formats/intscho.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2000_SPSS_school.txt'
            },
            'cognitive_item': {
                'zip': 'data-sets-in-txt-formats/intcogn_v4.zip',
                'spss_control': 'sas-and-spss-control-files/PISA2000_SPSS_cognitive_item.txt'
            }
        }
    }
}

class PISAOECDDownloader:
    """Download PISA data from OECD website."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize downloader with paths."""
        self.base_path = Path(base_path) if base_path else DEFAULT_PISA_DATA_DIR
        self.raw_path = self.base_path / "raw"
        self.raw_path.mkdir(parents=True, exist_ok=True)
        
        # Create session for efficient downloading
        self.session = requests.Session()
        self.session.headers.update(BROWSER_HEADERS)
    
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
        print(f"   Format: {config['format']}")
        
        # Create year directory
        year_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for file_type in file_types:
            file_info = config['files'][file_type]
            
            # Create subdirectory for this file type
            type_dir = year_path / file_type
            type_dir.mkdir(exist_ok=True)
            
            print(f"\n  📁 {file_type}:")
            
            try:
                if config['format'] == 'compressed':
                    # Handle ZIP files (2015, 2018, 2022, 2025)
                    filename = file_info
                    url = config['url_pattern'].format(filename=filename)
                    zip_path = type_dir / filename
                    
                    print(f"     URL: {url}")
                    print(f"     Saving to: {zip_path}")
                    
                    response = requests.get(url, stream=True, headers=BROWSER_HEADERS)
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
                    
                elif config['format'] == 'txt_with_control':
                    # Handle TXT files with control files (2000-2012)
                    base_url = config['base_url']
                    txt_path = file_info['txt']
                    control_path = file_info['spss_control']
                    
                    # Download TXT data file
                    txt_url = base_url + txt_path
                    txt_filename = Path(txt_path).name
                    txt_local_path = type_dir / txt_filename
                    
                    print(f"     TXT URL: {txt_url}")
                    print(f"     TXT Saving to: {txt_local_path}")
                    
                    response = requests.get(txt_url, stream=True, headers=BROWSER_HEADERS)
                    response.raise_for_status()
                    
                    with open(txt_local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"     ✅ Downloaded TXT: {txt_local_path}")
                    
                    # Add delay before next request
                    time.sleep(DOWNLOAD_DELAY)
                    
                    # Download SPSS control file
                    control_url = base_url + control_path
                    control_filename = Path(control_path).name
                    control_local_path = type_dir / control_filename
                    
                    print(f"     Control URL: {control_url}")
                    print(f"     Control Saving to: {control_local_path}")
                    
                    response = requests.get(control_url, stream=True, headers=BROWSER_HEADERS)
                    response.raise_for_status()
                    
                    with open(control_local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"     ✅ Downloaded Control: {control_local_path}")
                
                elif config['format'] == 'zip_with_control':
                    # Handle ZIP files with control files (2003, possibly others)
                    base_url = config['base_url']
                    zip_path = file_info['zip']
                    control_path = file_info['spss_control']
                    
                    # Download ZIP data file
                    zip_url = base_url + zip_path
                    zip_filename = Path(zip_path).name
                    zip_local_path = type_dir / zip_filename
                    
                    print(f"     ZIP URL: {zip_url}")
                    print(f"     ZIP Saving to: {zip_local_path}")
                    
                    response = requests.get(zip_url, stream=True, headers=BROWSER_HEADERS)
                    response.raise_for_status()
                    
                    # Write file with progress feedback
                    total_size = int(response.headers.get('content-length', 0))
                    with open(zip_local_path, 'wb') as f:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"     Progress: {percent:.1f}%", end='\r')
                    
                    print(f"     ✅ Downloaded ZIP: {zip_local_path}")
                    
                    # Extract ZIP file
                    print(f"     📦 Extracting {zip_filename}...")
                    with zipfile.ZipFile(zip_local_path, 'r') as zip_ref:
                        zip_ref.extractall(type_dir)
                    
                    print(f"     ✅ Extracted to: {type_dir}")
                    
                    # Delete ZIP file after successful extraction
                    zip_local_path.unlink()
                    print(f"     🗑️  Deleted ZIP file: {zip_local_path}")
                    
                    # Add delay before next request
                    time.sleep(DOWNLOAD_DELAY)
                    
                    # Download SPSS control file
                    control_url = base_url + control_path
                    control_filename = Path(control_path).name
                    control_local_path = type_dir / control_filename
                    
                    print(f"     Control URL: {control_url}")
                    print(f"     Control Saving to: {control_local_path}")
                    
                    response = requests.get(control_url, stream=True, headers=BROWSER_HEADERS)
                    response.raise_for_status()
                    
                    with open(control_local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"     ✅ Downloaded Control: {control_local_path}")
                
                else:
                    print(f"     ❌ Unknown format: {config['format']}")
                    continue
                
                success_count += 1
                
                # Add delay between file types
                if success_count < len(file_types):
                    time.sleep(DOWNLOAD_DELAY)
                
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
            # Show manual download instructions for protected years
            if show_manual_download_instructions(year):
                print(f"\n💡 **Tip**: Older PISA years require manual download due to website protection.")
        
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
        output_dir_path = DEFAULT_PISA_DATA_DIR / "raw" / str(year)
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
    print(f"Format: {config['format']}")
    
    success = True
    
    for file_type in file_types:
        file_info = config['files'][file_type]
        
        # Create subdirectory for this file type
        type_dir = output_dir_path / file_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nDownloading {file_type}...")
        
        if config['format'] == 'compressed':
            # Handle ZIP files (2015, 2018, 2022, 2025)
            filename = file_info
            url = config['url_pattern'].format(filename=filename)
            zip_path = type_dir / filename
            
            print(f"  URL: {url}")
            print(f"  Saving to: {zip_path}")
            
            try:
                response = requests.get(url, stream=True, headers=BROWSER_HEADERS)
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
                
        elif config['format'] == 'txt_with_control':
            # Handle TXT files with control files (2000-2012)
            base_url = config['base_url']
            txt_path = file_info['txt']
            control_path = file_info['spss_control']
            
            # Download TXT data file
            txt_url = base_url + txt_path
            txt_filename = Path(txt_path).name
            txt_local_path = type_dir / txt_filename
            
            print(f"  TXT URL: {txt_url}")
            print(f"  TXT Saving to: {txt_local_path}")
            
            try:
                response = requests.get(txt_url, stream=True, headers=BROWSER_HEADERS)
                response.raise_for_status()
                
                with open(txt_local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"  ✓ Downloaded TXT: {txt_local_path}")
                
                # Add delay before next request
                time.sleep(DOWNLOAD_DELAY)
                
                # Download SPSS control file
                control_url = base_url + control_path
                control_filename = Path(control_path).name
                control_local_path = type_dir / control_filename
                
                print(f"  Control URL: {control_url}")
                print(f"  Control Saving to: {control_local_path}")
                
                response = requests.get(control_url, stream=True, headers=BROWSER_HEADERS)
                response.raise_for_status()
                
                with open(control_local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"  ✓ Downloaded Control: {control_local_path}")
                
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Failed to download {file_type}: {e}")
                success = False
                continue
            except Exception as e:
                print(f"  ✗ Unexpected error with {file_type}: {e}")
                success = False
                continue
        
        elif config['format'] == 'zip_with_control':
            # Handle ZIP files with control files (2003, possibly others)
            base_url = config['base_url']
            zip_path = file_info['zip']
            control_path = file_info['spss_control']
            
            # Download ZIP data file
            zip_url = base_url + zip_path
            zip_filename = Path(zip_path).name
            zip_local_path = type_dir / zip_filename
            
            print(f"  ZIP URL: {zip_url}")
            print(f"  ZIP Saving to: {zip_local_path}")
            
            try:
                response = requests.get(zip_url, stream=True, headers=BROWSER_HEADERS)
                response.raise_for_status()
                
                # Write file with progress bar
                total_size = int(response.headers.get('content-length', 0))
                with open(zip_local_path, 'wb') as f:
                    if total_size > 0:
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"  {zip_filename}") as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                
                print(f"  ✓ Downloaded ZIP: {zip_local_path}")
                
                # Extract ZIP file
                print(f"  Extracting {zip_filename}...")
                with zipfile.ZipFile(zip_local_path, 'r') as zip_ref:
                    zip_ref.extractall(type_dir)
                
                print(f"  ✓ Extracted to: {type_dir}")
                
                # Delete ZIP file after successful extraction
                zip_local_path.unlink()
                print(f"  ✓ Deleted ZIP file: {zip_local_path}")
                
                # Add delay before next request
                time.sleep(DOWNLOAD_DELAY)
                
                # Download SPSS control file
                control_url = base_url + control_path
                control_filename = Path(control_path).name
                control_local_path = type_dir / control_filename
                
                print(f"  Control URL: {control_url}")
                print(f"  Control Saving to: {control_local_path}")
                
                response = requests.get(control_url, stream=True, headers=BROWSER_HEADERS)
                response.raise_for_status()
                
                with open(control_local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"  ✓ Downloaded Control: {control_local_path}")
                
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
        
        else:
            print(f"  ✗ Unknown format: {config['format']}")
            success = False
            continue
    
    if success:
        print(f"\n✓ Successfully downloaded all PISA {year} data!")
    else:
        print(f"\n✗ Some downloads failed for PISA {year}")
        # Show manual download instructions for protected years
        if show_manual_download_instructions(year):
            print(f"\n💡 **Tip**: Older PISA years require manual download due to website protection.")
    
    return success

def download_multiple_years(years: List[int], file_types: Optional[List[str]] = None, output_dir: Optional[str] = None) -> bool:
    """Download PISA data for multiple years."""
    print(f"Downloading PISA data for years: {', '.join(map(str, years))}")
    
    overall_success = True
    
    for year in years:
        print(f"\n{'='*50}")
        year_output = str(Path(output_dir) / str(year)) if output_dir else None
        success = download_year(year, file_types, year_output)
        if not success:
            overall_success = False
    
    print(f"\n{'='*50}")
    if overall_success:
        print("✓ All downloads completed successfully!")
    else:
        print("✗ Some downloads failed. Check the output above for details.")
    
    return overall_success

def show_manual_download_instructions(year: int):
    """Show manual download instructions for Cloudflare-protected years."""
    if year not in PISA_CONFIG:
        return
    
    config = PISA_CONFIG[year]
    
    if config['format'] in ['txt_with_control', 'zip_with_control']:
        print(f"\n📋 **Manual Download Required for PISA {year}**")
        print(f"   Due to Cloudflare anti-bot protection, these files must be downloaded manually:")
        
        base_url = config['base_url']
        
        print(f"\n🔗 **Download Links:**")
        for file_type, file_info in config['files'].items():
            if config['format'] == 'txt_with_control':
                data_url = base_url + file_info['txt']
                control_url = base_url + file_info['spss_control']
                print(f"   {file_type}:")
                print(f"     📄 Data: {data_url}")
                print(f"     📋 Control: {control_url}")
            elif config['format'] == 'zip_with_control':
                data_url = base_url + file_info['zip']
                control_url = base_url + file_info['spss_control']
                print(f"   {file_type}:")
                print(f"     📦 Data: {data_url}")
                print(f"     📋 Control: {control_url}")
        
        print(f"\n💾 **Save Files To:**")
        print(f"   {DEFAULT_PISA_DATA_DIR / 'raw' / str(year) / '[file_type]'}")
        
        print(f"\n🎯 **Instructions:**")
        print(f"   1. Click each link above in your browser")
        print(f"   2. Save files to the specified directory structure")
        print(f"   3. Extract ZIP files if needed")
        print(f"   4. Use control files (.txt) to load data into SPSS/SAS")
        
        return True
    return False

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
        years = [2025, 2022]
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
