#!/usr/bin/env python3
"""
Data Download Module for PISA Analysis
Downloads raw and processed PISA data from HuggingFace repositories.
"""

import os
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Union

try:
    from huggingface_hub import hf_hub_download, snapshot_download
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    exit(1)

class PISADataDownloader:
    """Download and manage PISA data from HuggingFace repositories."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the downloader with optional cache directory."""
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Repository configurations
        self.RAW_REPO = "victoriano/pisa-raw"
        self.PROCESSED_REPO = "victoriano/social-sciences-microdata"
        
        # Local data paths
        self.raw_data_path = Path("data/Global/pisa/raw")
        self.processed_data_path = Path("data/Global/pisa/processed")
        
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
    
    def download_raw_year(self, year: str, force_download: bool = False) -> bool:
        """Download raw PISA data for a specific year."""
        year_path = self.raw_data_path / year
        archive_name = f"pisa_{year}_raw.tar.gz"
        
        # Check if already exists
        if year_path.exists() and not force_download:
            print(f"✅ PISA {year} raw data already exists locally")
            return True
        
        try:
            print(f"📥 Downloading PISA {year} raw data...")
            
            # Download archive
            archive_path = hf_hub_download(
                repo_id=self.RAW_REPO,
                filename=archive_name,
                cache_dir=self.cache_dir,
                repo_type="dataset"
            )
            
            # Extract archive
            print(f"📦 Extracting {archive_name}...")
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=self.raw_data_path)
            
            print(f"✅ PISA {year} raw data downloaded and extracted")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download PISA {year} raw data: {e}")
            return False
    
    def download_all_raw_data(self, years: Optional[List[str]] = None, force_download: bool = False) -> Dict[str, bool]:
        """Download raw PISA data for all or specified years."""
        if years is None:
            years = ["2006", "2009", "2012", "2015", "2018", "2022"]
        
        results = {}
        for year in years:
            results[year] = self.download_raw_year(year, force_download)
        
        successful = [year for year, success in results.items() if success]
        failed = [year for year, success in results.items() if not success]
        
        print(f"\n📊 **Raw Data Download Summary**")
        print(f"✅ Successful: {', '.join(successful) if successful else 'None'}")
        print(f"❌ Failed: {', '.join(failed) if failed else 'None'}")
        
        return results
    
    def download_processed_data(self, force_download: bool = False) -> bool:
        """Download processed PISA data."""
        if self.processed_data_path.exists() and any(self.processed_data_path.iterdir()) and not force_download:
            print("✅ Processed PISA data already exists locally")
            return True
        
        try:
            print("📥 Downloading processed PISA data...")
            
            # Download entire processed folder
            downloaded_path = snapshot_download(
                repo_id=self.PROCESSED_REPO,
                repo_type="dataset",
                allow_patterns="global/pisa/*",
                cache_dir=self.cache_dir
            )
            
            # Copy to local processed directory
            source_path = Path(downloaded_path) / "global" / "pisa"
            if source_path.exists():
                # Clean existing processed data if force download
                if force_download and self.processed_data_path.exists():
                    shutil.rmtree(self.processed_data_path)
                    self.processed_data_path.mkdir(parents=True, exist_ok=True)
                
                # Copy files
                for item in source_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, self.processed_data_path)
                    elif item.is_dir():
                        shutil.copytree(item, self.processed_data_path / item.name, dirs_exist_ok=True)
                
                print("✅ Processed PISA data downloaded successfully")
                return True
            else:
                print("❌ Processed data not found in expected location")
                return False
                
        except Exception as e:
            print(f"❌ Failed to download processed PISA data: {e}")
            return False
    
    def setup_complete_environment(self, raw_years: Optional[List[str]] = None, force_download: bool = False) -> bool:
        """Set up complete PISA data environment."""
        print("🚀 **Setting up complete PISA data environment**")
        
        # Download processed data
        processed_success = self.download_processed_data(force_download)
        
        # Download raw data
        raw_results = self.download_all_raw_data(raw_years, force_download)
        raw_success = any(raw_results.values())
        
        if processed_success and raw_success:
            print("\n🎉 **Environment setup complete!**")
            print("✅ Both raw and processed PISA data are available locally")
            print("📁 Raw data: data/Global/pisa/raw/")
            print("📁 Processed data: data/Global/pisa/processed/")
            return True
        else:
            print("\n⚠️  **Environment setup incomplete**")
            if not processed_success:
                print("❌ Processed data download failed")
            if not raw_success:
                print("❌ All raw data downloads failed")
            return False
    
    def get_download_info(self) -> Dict[str, Union[str, int, List[str]]]:
        """Get information about downloaded data."""
        # Check what's available locally
        raw_years = []
        if self.raw_data_path.exists():
            raw_years = [d.name for d in self.raw_data_path.iterdir() if d.is_dir() and d.name.isdigit()]
        
        processed_files = []
        if self.processed_data_path.exists():
            processed_files = [f.name for f in self.processed_data_path.iterdir()]
        
        info: Dict[str, Union[str, int, List[str]]] = {
            "raw_repo": self.RAW_REPO,
            "processed_repo": self.PROCESSED_REPO,
            "cache_dir": str(self.cache_dir),
            "raw_path": str(self.raw_data_path),
            "processed_path": str(self.processed_data_path),
            "available_raw_years": raw_years,
            "available_processed_files": processed_files
        }
        
        return info


def main():
    """Demo and testing of the data downloader."""
    downloader = PISADataDownloader()
    
    print("🔍 **PISA Data Downloader Demo**")
    print("Available operations:")
    print("1. Download all raw data")
    print("2. Download processed data only")
    print("3. Setup complete environment")
    print("4. Show download info")
    
    # For demo, let's show info and download processed data
    print("\n📊 **Current Status:**")
    info = downloader.get_download_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Download processed data as example
    print("\n🔄 **Downloading processed data...**")
    downloader.download_processed_data()
    
    print("\n📝 **Usage Examples:**")
    print("  # Download specific raw year:")
    print("  downloader.download_raw_year('2022')")
    print("  ")
    print("  # Setup complete environment:")
    print("  downloader.setup_complete_environment()")
    print("  ")
    print("  # Download with force refresh:")
    print("  downloader.download_processed_data(force_download=True)")


if __name__ == "__main__":
    main() 