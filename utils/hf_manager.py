"""Utilities for HuggingFace Hub operations."""

from pathlib import Path
from typing import Optional, List
from huggingface_hub import HfApi, create_repo

class HFManager:
    """Manager for HuggingFace Hub operations."""
    
    def __init__(self):
        self.api = HfApi()
    
    def ensure_repo_exists(self, repo_id: str, private: bool = False) -> None:
        """Ensure a HuggingFace repository exists."""
        try:
            self.api.create_repo(
                repo_id=repo_id,
                repo_type="dataset",
                private=private,
                exist_ok=True
            )
            print(f"✅ Repository {repo_id} ready")
        except Exception as e:
            print(f"⚠️  Repository check: {e}")
    
    def upload_directory(
        self,
        local_dir: Path,
        repo_id: str,
        path_in_repo: str = "",
        ignore_patterns: Optional[List[str]] = None
    ) -> bool:
        """Upload a directory to HuggingFace Hub."""
        if ignore_patterns is None:
            ignore_patterns = [".DS_Store", "__pycache__", "*.pyc", ".git"]
        
        try:
            self.api.upload_folder(
                folder_path=str(local_dir),
                repo_id=repo_id,
                repo_type="dataset",
                path_in_repo=path_in_repo,
                ignore_patterns=ignore_patterns
            )
            print(f"✅ Uploaded to {repo_id}/{path_in_repo}")
            return True
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
