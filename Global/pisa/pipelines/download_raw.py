"""Download PISA data from HuggingFace raw repository."""

from pathlib import Path
from huggingface_hub import hf_hub_download
from .config import RAW_DATA_REPO, PISA_YEARS
import tarfile

def download_pisa_year(year: int, output_dir: Path) -> Path:
    """Download and extract PISA data for a specific year."""
    print(f"📥 Downloading PISA {year} data...")
    
    # Download compressed file
    archive_name = f"pisa_{year}_raw.tar.gz"
    archive_path = hf_hub_download(
        repo_id=RAW_DATA_REPO,
        filename=archive_name,
        repo_type="dataset",
        cache_dir=output_dir / ".cache"
    )
    
    # Extract to output directory
    extract_path = output_dir / str(year)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(output_dir)
    
    print(f"✅ Extracted PISA {year} to {extract_path}")
    return extract_path

def download_all_pisa_data(output_dir: Path = Path("data/Global/pisa/raw")) -> None:
    """Download all PISA years."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for year in PISA_YEARS:
        try:
            download_pisa_year(year, output_dir)
        except Exception as e:
            print(f"❌ Failed to download PISA {year}: {e}")
