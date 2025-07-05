#!/usr/bin/env python3
"""
Upload processed PISA data to social-sciences-microdata HuggingFace repository.
Structure: global/pisa/
"""

import os
from pathlib import Path
from typing import List, Optional

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    exit(1)

def upload_directory_to_hf(
    local_dir: Path, 
    repo_id: str, 
    folder_in_repo: str = "",
    ignore_patterns: Optional[List[str]] = None
) -> bool:
    """Upload a directory to HuggingFace Hub."""
    api = HfApi()
    
    if ignore_patterns is None:
        ignore_patterns = [".DS_Store", "__pycache__", "*.pyc", ".git"]
    
    try:
        print(f"🚀 Uploading {local_dir} to {repo_id}/{folder_in_repo}...")
        
        api.upload_folder(
            folder_path=str(local_dir),
            repo_id=repo_id,
            repo_type="dataset",
            path_in_repo=folder_in_repo,
            ignore_patterns=ignore_patterns
        )
        
        print(f"✅ Successfully uploaded to {repo_id}/{folder_in_repo}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload {local_dir}: {e}")
        return False

def create_readme_content() -> str:
    """Create README content for the PISA data."""
    return """# PISA Data - Programme for International Student Assessment

## Overview
This directory contains processed PISA (Programme for International Student Assessment) data from 2006-2022, optimized for research and analysis.

## Structure
- `trend_analysis/` - Multi-year trend analysis datasets
- `spain_trends/` - Spain-specific trend data
- `processing_metadata.json` - Processing metadata and variable information

## Data Description
- **Source**: OECD PISA Programme
- **Years**: 2006, 2009, 2012, 2015, 2018, 2022
- **Format**: Parquet files for optimal performance
- **Key Variables**: Academic performance, socioeconomic status, study habits, motivation

## Usage
The processed data is ready for analysis with modern data science tools (Polars, Pandas, etc.).

## Citation
If you use this data in your research, please cite:
- OECD (2023), Programme for International Student Assessment (PISA)
- This processed dataset: `victoriano/social-sciences-microdata`

## Processing Details
Data was processed using the young-lazy-people analysis framework:
- Standardized variable names across years
- Unified country codes and identifiers
- Optimized data types for analysis
- Spain-specific trend extraction

## License
This processed data follows the OECD PISA data usage guidelines.
"""

def create_metadata_file(processed_dir: Path) -> Path:
    """Create a metadata file for the processed data."""
    metadata_path = processed_dir / "PISA_README.md"
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(create_readme_content())
    
    print(f"📝 Created {metadata_path}")
    return metadata_path

def main() -> None:
    """Main upload process for processed data."""
    processed_dir = Path("data/Global/pisa/processed")
    repo_id = "victoriano/social-sciences-microdata"
    target_folder = "global/pisa"
    
    # Ensure the HF repo exists
    api = HfApi()
    try:
        api.create_repo(repo_id, repo_type="dataset", private=False, exist_ok=True)
        print(f"✅ Repository {repo_id} ready")
    except Exception as e:
        print(f"⚠️  Repository might already exist: {e}")
    
    # Create metadata file
    metadata_path = create_metadata_file(processed_dir)
    
    # Upload processed data
    success = upload_directory_to_hf(
        local_dir=processed_dir,
        repo_id=repo_id,
        folder_in_repo=target_folder,
        ignore_patterns=[".DS_Store", "__pycache__", "*.pyc", ".git"]
    )
    
    if success:
        print(f"\n🎉 **Processed PISA data uploaded successfully!**")
        print(f"📍 Location: https://huggingface.co/datasets/{repo_id}")
        print(f"📂 Path: {target_folder}/")
        print(f"📊 Size: ~79MB of optimized research data")
        print(f"\n📝 **Next Steps:**")
        print("1. Create data download scripts")
        print("2. Update processing scripts to use HuggingFace data")
        print("3. Clean up local Git tracking")
    else:
        print(f"\n❌ **Upload failed**")
        print("Check network connection and HuggingFace authentication")
    
    # Clean up metadata file
    if metadata_path.exists():
        metadata_path.unlink()

if __name__ == "__main__":
    main() 