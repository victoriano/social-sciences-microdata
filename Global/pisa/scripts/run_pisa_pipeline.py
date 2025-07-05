#!/usr/bin/env python3
"""Run the complete PISA data pipeline."""

import subprocess
import sys
from pathlib import Path

def run_python_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status."""
    print(f"\n{description}")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], check=True, capture_output=False)
        
        print(f"✅ {description} completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    """Run the complete PISA pipeline."""
    print("🚀 Starting PISA data pipeline...")
    print("=" * 60)
    
    # Ask user for data source
    print("Select data source:")
    print("1. HuggingFace (requires access to private repository)")
    print("2. OECD (public access)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Please enter 1 or 2")
    
    # Define pipeline steps based on choice
    if choice == "1":
        download_script = "download_from_hf.py"
        download_desc = "📥 Step 1: Downloading data from HuggingFace"
    else:
        download_script = "download_from_oecd.py"
        download_desc = "📥 Step 1: Downloading data from OECD"
    
    pipeline_steps = [
        (download_script, download_desc),
        ("../pipelines/preprocess.py", "⚙️  Step 2: Preprocessing data"),
        ("../pipelines/harmonize_trends.py", "🔄 Step 3: Harmonizing trends across years"),
        ("../pipelines/upload_processed.py", "📤 Step 4: Uploading processed data to HuggingFace"),
    ]
    
    # Run each step
    results = {}
    for script_path, description in pipeline_steps:
        success = run_python_script(script_path, description)
        results[script_path] = success
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at: {description}")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE SUMMARY")
    print("=" * 60)
    
    successful_steps = [desc for (script, desc), success in zip(pipeline_steps, results.values()) if success]
    failed_steps = [desc for (script, desc), success in zip(pipeline_steps, results.values()) if not success]
    
    if successful_steps:
        print("✅ Successful steps:")
        for step in successful_steps:
            print(f"   - {step}")
    
    if failed_steps:
        print("❌ Failed steps:")
        for step in failed_steps:
            print(f"   - {step}")
    
    if all(results.values()):
        print("\n🎉 **Pipeline completed successfully!**")
        return True
    else:
        print("\n⚠️  **Pipeline completed with errors**")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
