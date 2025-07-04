#!/usr/bin/env python3
"""Run the complete PISA data pipeline."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from pipelines.pisa.download import download_all_pisa_data
from pipelines.pisa.process import process_all_pisa_data
from pipelines.pisa.upload import upload_processed_data

def main():
    """Run the complete pipeline."""
    print("🚀 Starting PISA data pipeline...")
    
    # Step 1: Download raw data
    print("\n📥 Step 1: Downloading raw data from HuggingFace...")
    download_all_pisa_data()
    
    # Step 2: Process data
    print("\n⚙️  Step 2: Processing data...")
    process_all_pisa_data()
    
    # Step 3: Upload processed data
    print("\n📤 Step 3: Uploading processed data to HuggingFace...")
    upload_processed_data()
    
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main()
