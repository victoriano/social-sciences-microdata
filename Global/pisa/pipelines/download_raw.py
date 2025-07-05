"""Download PISA data from HuggingFace repository."""

import subprocess
import sys
from pathlib import Path

def main():
    """Download raw PISA data from HuggingFace."""
    print("📥 Downloading PISA raw data from HuggingFace...")
    
    # Path to the unified download script
    script_path = Path(__file__).parent.parent / "scripts" / "download_from_hf.py"
    
    try:
        # Run the download script with raw-only flag
        result = subprocess.run([
            sys.executable, str(script_path), "--raw-only"
        ], check=True, capture_output=False)
        
        print("\n✅ Raw data download pipeline completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Raw data download pipeline failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Raw data download pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
