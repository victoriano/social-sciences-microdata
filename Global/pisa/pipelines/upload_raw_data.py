#!/usr/bin/env python3
"""
Upload raw PISA data to HuggingFace Hub in compressed format by year.
This approach is more reliable than DVC for large datasets.
"""

import os
import tarfile
from pathlib import Path
from typing import Optional

try:
    from huggingface_hub import HfApi
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    exit(1)

def create_year_archive(year: str, raw_data_path: Path) -> Optional[Path]:
    """Create a compressed tar archive for a specific year."""
    year_path = raw_data_path / year
    if not year_path.exists():
        print(f"❌ Year {year} directory not found")
        return None
    
    archive_path = raw_data_path / f"pisa_{year}_raw.tar.gz"
    
    print(f"📦 Creating archive for {year}...")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(year_path, arcname=year)
    
    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"✅ Created {archive_path.name} ({size_mb:.1f} MB)")
    return archive_path

def upload_to_hf(archive_path: Path, repo_id: str, folder_in_repo: str = "") -> bool:
    """Upload an archive to HuggingFace Hub."""
    api = HfApi()
    
    try:
        print(f"🚀 Uploading {archive_path.name} to {repo_id}...")
        api.upload_file(
            path_or_fileobj=str(archive_path),
            path_in_repo=f"{folder_in_repo}/{archive_path.name}" if folder_in_repo else archive_path.name,
            repo_id=repo_id,
            repo_type="dataset"
        )
        print(f"✅ Successfully uploaded {archive_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {archive_path.name}: {e}")
        return False

def main() -> None:
    """Main upload process."""
    raw_data_path = Path("../data/raw")
    repo_id = "victoriano/pisa-raw"
    
    # Ensure the HF repo exists
    api = HfApi()
    try:
        api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=True)
        print(f"✅ Repository {repo_id} ready")
    except Exception as e:
        print(f"⚠️  Repository might already exist: {e}")
    
    # PISA years to process
    years = ["2006", "2009", "2012", "2015", "2018", "2022"]
    
    successful_uploads = []
    failed_uploads = []
    
    for year in years:
        print(f"\n📅 Processing PISA {year}...")
        
        # Create archive
        archive_path = create_year_archive(year, raw_data_path)
        if archive_path is None:
            failed_uploads.append(year)
            continue
        
        # Upload to HuggingFace
        if upload_to_hf(archive_path, repo_id):
            successful_uploads.append(year)
            # Clean up local archive after successful upload
            archive_path.unlink()
            print(f"🗑️  Cleaned up local archive for {year}")
        else:
            failed_uploads.append(year)
    
    # Summary
    print(f"\n📊 **Upload Summary**")
    print(f"✅ Successful: {', '.join(successful_uploads) if successful_uploads else 'None'}")
    print(f"❌ Failed: {', '.join(failed_uploads) if failed_uploads else 'None'}")
    
    if successful_uploads:
        print(f"\n🎉 Raw PISA data uploaded to: https://huggingface.co/datasets/{repo_id}")
        print("📝 Next: Upload processed data to social-sciences-microdata repo")

if __name__ == "__main__":
    main() 