#!/usr/bin/env python3
"""
PISA Data Downloader from HuggingFace

This script downloads PISA data from private HuggingFace repositories.
Access is restricted to comply with OECD PISA terms of use.

Repository Structure:
- Raw data: victoriano/pisa-raw (path: data/raw/{year}/{file_type}/)
- Processed data: victoriano/social-sciences-microdata (path: global/pisa/)

New Structure (post-reorganization):
data/raw/
  ├── 2000/
  │   ├── student_questionnaire/
  │   ├── school_questionnaire/  
  │   ├── cognitive_item/
  │   └── documentation/
  ├── 2003/
  └── ... (other years)
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from huggingface_hub import hf_hub_download, snapshot_download, list_repo_files
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"
PROCESSED_REPO = "victoriano/social-sciences-microdata"
AVAILABLE_YEARS = ["2000", "2003", "2006", "2009", "2012", "2015", "2018", "2022"]

# File type mappings to match OECD structure
FILE_TYPE_MAPPINGS = {
    'student_questionnaire': 'Student questionnaire data and control files',
    'school_questionnaire': 'School questionnaire data and control files', 
    'cognitive_item': 'Cognitive item response data and control files',
    'parent_questionnaire': 'Parent questionnaire data and control files',
    'questionnaire_additional': 'Additional questionnaire data',
    'documentation': 'README files, manuals, and documentation',
    'other': 'Converted files and other data'
}

class PISAHFDownloader:
    """Download PISA data from HuggingFace repositories with new structure."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize downloader with paths."""
        self.base_path = base_path or Path(".")
        self.data_path = self.base_path / "data"
        self.raw_path = self.data_path / "raw"
        self.processed_path = self.base_path / "processed"
        
        # Create directories
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
    
    def get_available_file_types(self, year: str) -> List[str]:
        """Get available file types for a specific year."""
        if year not in AVAILABLE_YEARS:
            return []
        
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            year_prefix = f"data/raw/{year}/"
            file_types = set()
            
            for file_path in files:
                if file_path.startswith(year_prefix):
                    # Extract file type: data/raw/2022/student_questionnaire/file.sav
                    path_parts = file_path.split('/')
                    if len(path_parts) >= 4:
                        file_type = path_parts[3]  # student_questionnaire, etc.
                        file_types.add(file_type)
            
            return sorted(list(file_types))
        except Exception as e:
            print(f"❌ Error getting file types for {year}: {e}")
            return []
    
    def download_file_type(self, year: str, file_type: str, force: bool = False) -> bool:
        """Download specific file type for a year."""
        if year not in AVAILABLE_YEARS:
            print(f"❌ Year {year} not available. Available years: {', '.join(AVAILABLE_YEARS)}")
            return False
        
        # Local path
        local_type_path = self.raw_path / year / file_type
        
        # Check if already exists
        if local_type_path.exists() and any(local_type_path.iterdir()) and not force:
            print(f"✅ {year}/{file_type} already exists locally")
            return True
        
        try:
            print(f"📥 Downloading PISA {year} {file_type}...")
            
            # Get all files for this year/file_type
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            year_type_prefix = f"data/raw/{year}/{file_type}/"
            target_files = [f for f in files if f.startswith(year_type_prefix)]
            
            if not target_files:
                print(f"❌ No files found for {year}/{file_type}")
                return False
            
            # Create directory
            local_type_path.mkdir(parents=True, exist_ok=True)
            
            # Download each file
            success_count = 0
            for file_path in target_files:
                try:
                    filename = Path(file_path).name
                    local_file_path = local_type_path / filename
                    
                    print(f"  📄 Downloading {filename}...")
                    
                    downloaded_file = hf_hub_download(
                        repo_id=RAW_REPO,
                        filename=file_path,
                        repo_type="dataset",
                        local_dir=self.base_path,
                        local_dir_use_symlinks=False
                    )
                    
                    print(f"  ✅ Downloaded {filename}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed to download {filename}: {e}")
            
            if success_count > 0:
                print(f"✅ Downloaded {success_count}/{len(target_files)} files for {year}/{file_type}")
                return True
            else:
                print(f"❌ Failed to download any files for {year}/{file_type}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to download {year}/{file_type}: {e}")
            return False
    
    def download_year(self, year: str, file_types: Optional[List[str]] = None, force: bool = False) -> Dict[str, bool]:
        """Download all file types for a specific year."""
        if year not in AVAILABLE_YEARS:
            print(f"❌ Year {year} not available. Available years: {', '.join(AVAILABLE_YEARS)}")
            return {}
        
        # Get available file types if not specified
        if file_types is None:
            file_types = self.get_available_file_types(year)
        
        if not file_types:
            print(f"❌ No file types available for {year}")
            return {}
        
        print(f"📥 Downloading PISA {year} data...")
        print(f"   File types: {', '.join(file_types)}")
        
        results = {}
        for file_type in file_types:
            results[file_type] = self.download_file_type(year, file_type, force)
        
        # Summary
        successful = [ft for ft, success in results.items() if success]
        failed = [ft for ft, success in results.items() if not success]
        
        print(f"\n📊 {year} Summary:")
        if successful:
            print(f"✅ Successful: {', '.join(successful)}")
        if failed:
            print(f"❌ Failed: {', '.join(failed)}")
        
        return results
    
    def download_all_raw(self, years: Optional[List[str]] = None, 
                        file_types: Optional[List[str]] = None, 
                        force: bool = False) -> Dict[str, Dict[str, bool]]:
        """Download raw data for multiple years."""
        if years is None:
            years = AVAILABLE_YEARS
        
        print(f"📥 Downloading raw data for years: {', '.join(years)}")
        if file_types:
            print(f"   File types: {', '.join(file_types)}")
        
        all_results = {}
        for year in years:
            all_results[year] = self.download_year(year, file_types, force)
        
        # Overall summary
        total_successful = sum(sum(1 for success in year_results.values() if success) 
                             for year_results in all_results.values())
        total_attempted = sum(len(year_results) for year_results in all_results.values())
        
        print(f"\n🎯 Overall Summary:")
        print(f"✅ Total successful downloads: {total_successful}/{total_attempted}")
        
        return all_results
    
    def download_processed_data(self, force: bool = False) -> bool:
        """Download processed PISA data."""
        if self.processed_path.exists() and any(self.processed_path.iterdir()) and not force:
            print("✅ Processed data already exists locally")
            return True
        
        try:
            print("📥 Downloading processed PISA data...")
            
            # Download processed data folder
            downloaded_path = snapshot_download(
                repo_id=PROCESSED_REPO,
                repo_type="dataset",
                allow_patterns="global/pisa/*"
            )
            
            # Copy to local processed directory
            source_path = Path(downloaded_path) / "global" / "pisa"
            if source_path.exists():
                if force and self.processed_path.exists():
                    shutil.rmtree(self.processed_path)
                    self.processed_path.mkdir(parents=True, exist_ok=True)
                
                # Copy files
                for item in source_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, self.processed_path)
                    elif item.is_dir():
                        shutil.copytree(item, self.processed_path / item.name, dirs_exist_ok=True)
                
                print("✅ Processed data downloaded successfully")
                return True
            else:
                print("❌ Processed data not found in expected location")
                return False
                
        except Exception as e:
            print(f"❌ Failed to download processed data: {e}")
            return False
    
    def setup_complete_environment(self, raw_years: Optional[List[str]] = None, 
                                 raw_file_types: Optional[List[str]] = None,
                                 force: bool = False) -> bool:
        """Set up complete PISA environment with both raw and processed data."""
        print("🚀 Setting up complete PISA environment...")
        
        # Download processed data
        processed_ok = self.download_processed_data(force)
        
        # Download raw data
        raw_results = self.download_all_raw(raw_years, raw_file_types, force)
        raw_ok = any(any(year_results.values()) for year_results in raw_results.values())
        
        if processed_ok and raw_ok:
            print("\n🎉 Environment setup complete!")
            print(f"📁 Raw data: {self.raw_path}")
            print(f"📁 Processed data: {self.processed_path}")
            return True
        else:
            print("\n⚠️  Environment setup incomplete")
            return False
    
    def show_repository_structure(self) -> None:
        """Show the structure of the HuggingFace repository."""
        try:
            print("📊 **HuggingFace Repository Structure**\n")
            
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            # Organize by year and file type
            structure = {}
            for file_path in files:
                if file_path.startswith('data/raw/'):
                    parts = file_path.split('/')
                    if len(parts) >= 4:
                        year = parts[2]
                        file_type = parts[3]
                        filename = parts[4] if len(parts) > 4 else ''
                        
                        if year not in structure:
                            structure[year] = {}
                        if file_type not in structure[year]:
                            structure[year][file_type] = []
                        
                        if filename:
                            structure[year][file_type].append(filename)
            
            for year in sorted(structure.keys()):
                print(f"📅 **PISA {year}:**")
                year_data = structure[year]
                
                for file_type in sorted(year_data.keys()):
                    files = year_data[file_type]
                    description = FILE_TYPE_MAPPINGS.get(file_type, 'Unknown file type')
                    print(f"   📁 {file_type} ({len(files)} files)")
                    print(f"      {description}")
                    
                    for filename in sorted(files):
                        icon = "📄" if filename.endswith(('.txt', '.sav', '.SAV')) else "📋" if 'SPSS' in filename else "📖"
                        print(f"      {icon} {filename}")
                print()
                
        except Exception as e:
            print(f"❌ Error showing repository structure: {e}")
    
    def status(self) -> Dict[str, Any]:
        """Get current status of local data."""
        # Check raw data
        raw_structure = {}
        if self.raw_path.exists():
            for year_dir in self.raw_path.iterdir():
                if year_dir.is_dir() and year_dir.name.isdigit():
                    year = year_dir.name
                    raw_structure[year] = []
                    
                    for file_type_dir in year_dir.iterdir():
                        if file_type_dir.is_dir():
                            file_count = len(list(file_type_dir.glob('*')))
                            raw_structure[year].append({
                                'file_type': file_type_dir.name,
                                'file_count': file_count
                            })
        
        # Check processed data
        processed_files = []
        if self.processed_path.exists():
            processed_files = [f.name for f in self.processed_path.rglob('*') if f.is_file()]
        
        return {
            "raw_path": str(self.raw_path),
            "processed_path": str(self.processed_path),
            "raw_structure": raw_structure,
            "processed_files": processed_files,
            "total_raw_years": len(raw_structure),
            "total_processed_files": len(processed_files)
        }


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download PISA data from HuggingFace")
    parser.add_argument("--years", nargs="*", help="Specific years to download (default: all)")
    parser.add_argument("--file-types", nargs="*", help="Specific file types to download (default: all)")
    parser.add_argument("--processed-only", action="store_true", help="Download only processed data")
    parser.add_argument("--raw-only", action="store_true", help="Download only raw data")
    parser.add_argument("--force", action="store_true", help="Force re-download existing data")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--show-structure", action="store_true", help="Show repository structure")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = PISAHFDownloader()
    
    # Show repository structure
    if args.show_structure:
        downloader.show_repository_structure()
        return
    
    # Show status
    if args.status:
        print("📊 **Current Local Status:**\n")
        status = downloader.status()
        
        print(f"📁 Raw data path: {status['raw_path']}")
        print(f"📁 Processed data path: {status['processed_path']}")
        print(f"📊 Total raw years: {status['total_raw_years']}")
        print(f"📊 Total processed files: {status['total_processed_files']}")
        
        if status['raw_structure']:
            print("\n📅 **Raw Data Structure:**")
            for year, file_types in status['raw_structure'].items():
                print(f"   PISA {year}:")
                for ft_info in file_types:
                    print(f"     📁 {ft_info['file_type']}: {ft_info['file_count']} files")
        else:
            print("\n📅 No raw data found locally")
        
        if status['processed_files']:
            print(f"\n📊 **Processed Files:** {len(status['processed_files'])} files")
        else:
            print("\n📊 No processed data found locally")
        
        return
    
    # Download logic
    if args.processed_only:
        downloader.download_processed_data(args.force)
    elif args.raw_only:
        downloader.download_all_raw(args.years, getattr(args, 'file_types', None), args.force)
    else:
        downloader.setup_complete_environment(args.years, getattr(args, 'file_types', None), args.force)


if __name__ == "__main__":
    main() 