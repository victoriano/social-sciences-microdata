#!/usr/bin/env python3
"""Run the complete PISA data pipeline."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from pisa.pipelines.download_raw import download_pisa_raw
from pisa.pipelines.preprocess import preprocess_all_years
from pisa.pipelines.harmonize_trends import harmonize_pisa_trends
from pisa.pipelines.upload_processed import upload_processed_data

def main():
    """Run the complete PISA pipeline."""
    print("🚀 Starting PISA data pipeline...")
    
    # Step 1: Download raw data
    print("\n📥 Step 1: Downloading raw data from HuggingFace...")
    download_pisa_raw()
    
    # Step 2: Preprocess data
    print("\n⚙️  Step 2: Preprocessing data...")
    preprocess_all_years()
    
    # Step 3: Harmonize trends
    print("\n🔄 Step 3: Harmonizing trends across years...")
    harmonize_pisa_trends()
    
    # Step 4: Upload processed data
    print("\n📤 Step 4: Uploading processed data to HuggingFace...")
    upload_processed_data()
    
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main()
