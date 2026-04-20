#!/usr/bin/env python3
"""Publish the CIS Barómetro dataset to HuggingFace Hub.

Two repositories are used (see ``config.py`` for the IDs):

- **Processed** (public): the tidy ``processed_barometros.parquet`` plus the
  catalogue CSV are uploaded to ``victoriano/social-sciences-microdata``
  under ``spain/barometro_cis/``. This is the fixed, consumable endpoint.
- **Raw** (private): the ``MD{codigo}/`` folders extracted by
  ``download_raw.py`` go to ``victoriano/barometro-cis-raw``. Keeping them
  private respects the CIS reuse conditions while still letting us
  reproduce the pipeline from a mirror.

Consume from Python with::

    from huggingface_hub import hf_hub_download
    import pandas as pd

    path = hf_hub_download(
        repo_id="victoriano/social-sciences-microdata",
        filename="spain/barometro_cis/processed_barometros.parquet",
        repo_type="dataset",
    )
    df = pd.read_parquet(path)

Authentication is picked up from ``HF_TOKEN`` or ``huggingface-cli login``.
"""

import argparse
from pathlib import Path
from typing import Iterable

from huggingface_hub import HfApi
from huggingface_hub.errors import RepositoryNotFoundError

from Spain.barometro_cis.config import (
    INDEX_FILE,
    PROCESSED_DATA_PATH,
    PROCESSED_DATA_REPO,
    PROCESSED_DIR,
    RAW_DATA_REPO,
    RAW_DIR,
)

IGNORE_PATTERNS = [".DS_Store", "__pycache__", "*.pyc", ".git"]


def ensure_repo(api: HfApi, repo_id: str, private: bool) -> None:
    try:
        api.repo_info(repo_id, repo_type="dataset")
        print(f"✅ Repo {repo_id} exists (private={private})", flush=True)
    except RepositoryNotFoundError:
        print(f"📝 Creating {repo_id} (private={private})", flush=True)
        api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)


def upload_processed(
    api: HfApi,
    processed_dir: Path,
    index_file: Path,
    repo_id: str = PROCESSED_DATA_REPO,
    path_in_repo: str = PROCESSED_DATA_PATH,
) -> None:
    """Upload the processed parquet + catalogue CSV to the public repo."""
    processed_parquet = processed_dir / "processed_barometros.parquet"
    if not processed_parquet.exists():
        raise FileNotFoundError(f"Missing {processed_parquet} — run preprocess first")
    if not index_file.exists():
        raise FileNotFoundError(f"Missing {index_file} — run fetch_index first")

    ensure_repo(api, repo_id, private=False)

    print(f"🚀 Uploading {processed_parquet.name} → {repo_id}/{path_in_repo}/", flush=True)
    api.upload_file(
        path_or_fileobj=str(processed_parquet),
        path_in_repo=f"{path_in_repo}/processed_barometros.parquet",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Refresh processed CIS Barómetros parquet",
    )

    print(f"🚀 Uploading {index_file.name} → {repo_id}/{path_in_repo}/", flush=True)
    api.upload_file(
        path_or_fileobj=str(index_file),
        path_in_repo=f"{path_in_repo}/barometros_index.csv",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Refresh CIS Barómetros catalogue index",
    )

    # Upload a minimal README describing what's in this subpath. Keeping it at
    # the subpath level avoids clobbering READMEs of other sources (e.g. PISA)
    # that may share the same repo.
    readme = (
        "# CIS Barómetros — processed dataset\n\n"
        "Tidy, month-indexed Parquet produced by the pipeline at\n"
        "<https://github.com/victoriano/social-sciences-microdata>.\n\n"
        "## Files\n\n"
        "- `processed_barometros.parquet` — one row per respondent, columns in\n"
        "  Spanish (variable labels from the CIS SPSS metadata). Includes a\n"
        "  monthly `date_of_study` rebuilt via the catalogue index.\n"
        "- `barometros_index.csv` — the catalogue entry for every estudio the\n"
        "  pipeline considered, including slug and download date.\n\n"
        "## Quick start\n\n"
        "```python\n"
        "from huggingface_hub import hf_hub_download\n"
        "import pandas as pd\n\n"
        f"path = hf_hub_download(\n"
        f'    repo_id="{repo_id}",\n'
        f'    filename="{path_in_repo}/processed_barometros.parquet",\n'
        f'    repo_type="dataset",\n'
        f")\n"
        "df = pd.read_parquet(path)\n"
        "```\n"
    )
    readme_path = processed_dir / ".hf_readme.md"
    readme_path.write_text(readme)
    api.upload_file(
        path_or_fileobj=str(readme_path),
        path_in_repo=f"{path_in_repo}/README.md",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Refresh CIS Barómetros README",
    )
    readme_path.unlink(missing_ok=True)


def upload_raw(
    api: HfApi,
    raw_dir: Path,
    repo_id: str = RAW_DATA_REPO,
    subdirs: Iterable[str] | None = None,
) -> None:
    """Upload every MD{codigo}/ sub-folder to the private raw repo."""
    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} does not exist")

    ensure_repo(api, repo_id, private=True)

    targets = sorted(p for p in raw_dir.iterdir() if p.is_dir() and p.name.startswith("MD"))
    if subdirs is not None:
        wanted = set(subdirs)
        targets = [p for p in targets if p.name in wanted]

    if not targets:
        print("⚠️  No MD* folders to upload", flush=True)
        return

    print(f"🚀 Uploading {len(targets)} raw MD folders → {repo_id}", flush=True)
    # ``upload_folder`` diffs against the remote tree, so re-runs only push new
    # or changed files even though we pass the whole directory.
    api.upload_folder(
        folder_path=str(raw_dir),
        repo_id=repo_id,
        repo_type="dataset",
        path_in_repo="",
        ignore_patterns=IGNORE_PATTERNS,
        commit_message="Refresh raw CIS Barómetro archives",
    )
    print(f"✅ Raw upload complete", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload CIS Barómetro data to HuggingFace Hub")
    parser.add_argument("--processed", action="store_true", help="Upload the processed parquet + index")
    parser.add_argument("--raw", action="store_true", help="Upload the raw MD{codigo} folders to the private repo")
    parser.add_argument("--all", action="store_true", help="Upload both processed and raw")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Local raw directory")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR, help="Local processed directory")
    parser.add_argument("--index", type=Path, default=INDEX_FILE, help="Local catalogue CSV")
    args = parser.parse_args()

    if not (args.processed or args.raw or args.all):
        parser.error("Choose at least one of --processed / --raw / --all")

    api = HfApi()

    if args.processed or args.all:
        upload_processed(api, args.processed_dir, args.index)

    if args.raw or args.all:
        upload_raw(api, args.raw_dir)


if __name__ == "__main__":
    main()
