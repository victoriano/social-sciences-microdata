#!/usr/bin/env python3
"""
PISA Data Downloader from HuggingFace

This script downloads PISA data from private HuggingFace repositories.
Access is restricted to comply with OECD PISA terms of use.

Repository Structure:
- Raw data: victoriano/pisa-raw (files: pisa_{year}_raw.tar.gz)
- Processed data: victoriano/social-sciences-microdata (path: global/pisa/)
"""

import os
import sys
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from huggingface_hub import hf_hub_download, snapshot_download
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"
PROCESSED_REPO = "victoriano/social-sciences-microdata"
AVAILABLE_YEARS = ["2000", "2003", "2006", "2009", "2012", "2015", "2018", "2022"]

class PISAHFDownloader:
    """Download PISA data from HuggingFace repositories."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize downloader with paths."""
        self.base_path = base_path or Path(".")
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        
        # Create directories
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
    
    def download_raw_year(self, year: str, force: bool = False) -> bool:
        """Download raw PISA data for a specific year."""
        if year not in AVAILABLE_YEARS:
            print(f"❌ Year {year} not available. Available years: {', '.join(AVAILABLE_YEARS)}")
            return False
        
        year_path = self.raw_path / year
        
        # Check if already exists
        if year_path.exists() and not force:
            print(f"✅ PISA {year} already exists locally")
            return True
        
        try:
            print(f"📥 Downloading PISA {year} raw data...")
            
            # Download archive
            archive_name = f"pisa_{year}_raw.tar.gz"
            archive_path = hf_hub_download(
                repo_id=RAW_REPO,
                filename=archive_name,
                repo_type="dataset"
            )
            
            # Extract to year folder
            print(f"📦 Extracting to {year_path}...")
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=self.raw_path)
            
            print(f"✅ PISA {year} downloaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download PISA {year}: {e}")
            return False
    
    def download_all_raw(self, years: Optional[List[str]] = None, force: bool = False) -> Dict[str, bool]:
        """Download raw data for multiple years."""
        if years is None:
            years = AVAILABLE_YEARS
        
        print(f"📥 Downloading raw data for years: {', '.join(years)}")
        
        results = {}
        for year in years:
            results[year] = self.download_raw_year(year, force)
        
        # Summary
        successful = [year for year, success in results.items() if success]
        failed = [year for year, success in results.items() if not success]
        
        print(f"\n📊 Summary:")
        print(f"✅ Successful: {', '.join(successful) if successful else 'None'}")
        print(f"❌ Failed: {', '.join(failed) if failed else 'None'}")
        
        return results
    
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
    
    def setup_complete_environment(self, raw_years: Optional[List[str]] = None, force: bool = False) -> bool:
        """Set up complete PISA environment with both raw and processed data."""
        print("🚀 Setting up complete PISA environment...")
        
        # Download processed data
        processed_ok = self.download_processed_data(force)
        
        # Download raw data
        raw_results = self.download_all_raw(raw_years, force)
        raw_ok = any(raw_results.values())
        
        if processed_ok and raw_ok:
            print("\n🎉 Environment setup complete!")
            print(f"📁 Raw data: {self.raw_path}")
            print(f"📁 Processed data: {self.processed_path}")
            return True
        else:
            print("\n⚠️  Environment setup incomplete")
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get current status of local data."""
        raw_years = []
        if self.raw_path.exists():
            raw_years = [d.name for d in self.raw_path.iterdir() if d.is_dir() and d.name.isdigit()]
        
        processed_files = []
        if self.processed_path.exists():
            processed_files = [f.name for f in self.processed_path.iterdir() if f.is_file()]
        
        return {
            "raw_path": str(self.raw_path),
            "processed_path": str(self.processed_path),
            "available_raw_years": sorted(raw_years),
            "processed_files": processed_files,
            "total_raw_years": len(raw_years),
            "total_processed_files": len(processed_files)
        }


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download PISA data from HuggingFace")
    parser.add_argument("--years", nargs="*", help="Specific years to download (default: all)")
    parser.add_argument("--processed-only", action="store_true", help="Download only processed data")
    parser.add_argument("--raw-only", action="store_true", help="Download only raw data")
    parser.add_argument("--force", action="store_true", help="Force re-download existing data")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = PISAHFDownloader()
    
    # Show status
    if args.status:
        print("📊 Current Status:")
        status = downloader.status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    # Download logic
    if args.processed_only:
        downloader.download_processed_data(args.force)
    elif args.raw_only:
        downloader.download_all_raw(args.years, args.force)
    else:
        downloader.setup_complete_environment(args.years, args.force)


if __name__ == "__main__":
    main() 