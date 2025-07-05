#!/usr/bin/env python3
"""
Retry Failed HuggingFace Moves

This script retries the failed file moves from the previous reorganization
with better rate limiting handling.
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import List, Dict

try:
    from huggingface_hub import HfApi, list_repo_files, hf_hub_download, upload_file, delete_file
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"
RETRY_DELAY = 60  # seconds between retries
MAX_RETRIES = 3
RATE_LIMIT_SLEEP = 3600  # 1 hour sleep when rate limited

class HFRetryMover:
    """Retry failed HuggingFace moves with rate limiting handling."""
    
    def __init__(self):
        """Initialize the retry mover."""
        self.api = HfApi()
        
    def check_rate_limit_status(self) -> bool:
        """Check if we're still rate limited by trying a simple API call."""
        try:
            print("🔍 Checking HuggingFace API rate limit status...")
            
            # Simple API call to test rate limiting
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            print("✅ API accessible - rate limit appears to be reset!")
            return False  # Not rate limited
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                print("⏳ Still rate limited - API returns 429 error")
                return True  # Still rate limited
            else:
                print(f"❌ Different API error: {error_msg}")
                return False  # Not a rate limit issue
    
    def get_remaining_moves(self) -> List[Dict[str, str]]:
        """Get files that still need to be moved."""
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            # Find files still in data/raw/ structure
            remaining_moves = []
            for file_path in files:
                if file_path.startswith('data/raw/'):
                    # data/raw/2009/cognitive_item/file.txt -> 2009/cognitive_item/file.txt
                    parts = file_path.split('/')
                    if len(parts) >= 5:
                        year = parts[2]
                        file_type = parts[3]
                        filename = '/'.join(parts[4:])
                        
                        new_path = f"{year}/{file_type}/{filename}"
                        
                        remaining_moves.append({
                            'old_path': file_path,
                            'new_path': new_path,
                            'filename': filename,
                            'year': year,
                            'file_type': file_type
                        })
            
            return remaining_moves
            
        except Exception as e:
            print(f"❌ Error getting remaining moves: {e}")
            return []
    
    def move_file_with_retry(self, move_info: Dict[str, str]) -> bool:
        """Move a single file with retry logic."""
        old_path = move_info['old_path']
        new_path = move_info['new_path']
        filename = move_info['filename']
        year = move_info['year']
        file_type = move_info['file_type']
        
        for attempt in range(MAX_RETRIES):
            try:
                print(f"📄 Moving {filename} ({year}/{file_type}) - Attempt {attempt + 1}")
                
                # Use temporary directory for download
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Download file
                    local_file = hf_hub_download(
                        repo_id=RAW_REPO,
                        filename=old_path,
                        repo_type="dataset",
                        local_dir=temp_path,
                        local_dir_use_symlinks=False
                    )
                    
                    # Upload to new location
                    upload_file(
                        path_or_fileobj=local_file,
                        path_in_repo=new_path,
                        repo_id=RAW_REPO,
                        repo_type="dataset"
                    )
                    
                    # Delete old file
                    delete_file(
                        path_in_repo=old_path,
                        repo_id=RAW_REPO,
                        repo_type="dataset"
                    )
                    
                    print(f"  ✅ Moved successfully")
                    return True
                    
            except Exception as e:
                error_msg = str(e)
                
                if "429" in error_msg or "rate" in error_msg.lower():
                    print(f"  ⏳ Rate limited - sleeping {RATE_LIMIT_SLEEP//60} minutes...")
                    time.sleep(RATE_LIMIT_SLEEP)
                    continue
                elif attempt < MAX_RETRIES - 1:
                    print(f"  ⚠️  Attempt {attempt + 1} failed: {error_msg}")
                    print(f"  ⏳ Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"  ❌ Failed after {MAX_RETRIES} attempts: {error_msg}")
                    return False
        
        return False
    
    def retry_all_moves(self, dry_run: bool = True) -> bool:
        """Retry all remaining moves."""
        remaining_moves = self.get_remaining_moves()
        
        if not remaining_moves:
            print("🎉 No files need to be moved - all done!")
            return True
        
        print(f"📋 Found {len(remaining_moves)} files still to move")
        
        if dry_run:
            print("🔍 **DRY RUN** - Files that would be moved:")
            for move_info in remaining_moves:
                print(f"  📄 {move_info['filename']} ({move_info['year']}/{move_info['file_type']})")
                print(f"      {move_info['old_path']} → {move_info['new_path']}")
            return True
        
        print("🚀 Starting retry process...")
        
        success_count = 0
        failed_files = []
        
        for i, move_info in enumerate(remaining_moves):
            progress = ((i + 1) / len(remaining_moves)) * 100
            print(f"\n📊 Progress: {progress:.1f}% ({i + 1}/{len(remaining_moves)})")
            
            if self.move_file_with_retry(move_info):
                success_count += 1
            else:
                failed_files.append(move_info)
            
            # Small delay between files to be respectful
            if i < len(remaining_moves) - 1:
                time.sleep(2)
        
        print(f"\n📊 **Retry Summary:**")
        print(f"✅ Successfully moved: {success_count}/{len(remaining_moves)} files")
        
        if failed_files:
            print(f"❌ Still failed: {len(failed_files)} files")
            for failure in failed_files:
                print(f"  - {failure['filename']} ({failure['year']}/{failure['file_type']})")
        
        return success_count == len(remaining_moves)
    
    def verify_final_structure(self) -> bool:
        """Verify the final structure is correct."""
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            new_structure_files = [f for f in files if not f.startswith('data/raw/') and '/' in f and not f.startswith('.')]
            old_structure_files = [f for f in files if f.startswith('data/raw/')]
            
            print(f"\n📊 **Final Structure Verification:**")
            print(f"✅ Files in new structure: {len(new_structure_files)}")
            print(f"📁 Files in old structure: {len(old_structure_files)}")
            
            if new_structure_files and not old_structure_files:
                print("🎉 **SUCCESS:** All files moved to new structure!")
                return True
            elif old_structure_files:
                print("⚠️  **INCOMPLETE:** Some files still in old structure")
                print("   Files still in data/raw/:")
                for f in old_structure_files[:10]:  # Show first 10
                    print(f"     {f}")
                if len(old_structure_files) > 10:
                    print(f"     ... and {len(old_structure_files) - 10} more")
                return False
            else:
                print("❌ **ERROR:** No files found in either structure")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Retry failed HuggingFace moves")
    parser.add_argument("--execute", action="store_true", help="Execute the retry operation")
    parser.add_argument("--verify-only", action="store_true", help="Only verify current structure")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--check-rate-limit", action="store_true", help="Check if API is still rate limited")
    
    args = parser.parse_args()
    
    mover = HFRetryMover()
    
    if args.verify_only:
        mover.verify_final_structure()
        return
    
    if args.status:
        remaining_moves = mover.get_remaining_moves()
        print(f"📊 **Status:** {len(remaining_moves)} files still need to be moved")
        return
    
    if args.check_rate_limit:
        is_rate_limited = mover.check_rate_limit_status()
        if is_rate_limited:
            print("⏳ **RATE LIMITED** - Please wait before retrying operations")
        else:
            print("✅ **READY** - API is accessible and ready for operations")
        return
    
    if args.execute:
        print("🚀 **EXECUTING RETRY OPERATION**")
        
        # Check rate limit status first
        if mover.check_rate_limit_status():
            print("❌ **RATE LIMIT STILL ACTIVE**")
            print("   Please wait before retrying. HuggingFace rate limits typically reset after 1 hour.")
            return
        
        success = mover.retry_all_moves(dry_run=False)
        
        if success:
            print("\n🔍 Verifying final structure...")
            verification_success = mover.verify_final_structure()
            
            if verification_success:
                print("\n🎉 **COMPLETE SUCCESS!**")
                print("   All files successfully moved to new structure!")
                print("   HuggingFace repo: {year}/{file_type}/")
                print("   Local downloads: data/raw/{year}/{file_type}/")
            else:
                print("\n⚠️  **PARTIAL SUCCESS**")
                print("   Some files may still need manual intervention")
        else:
            print("\n❌ **RETRY FAILED**")
            print("   Some files could not be moved due to persistent errors")
    else:
        print("🔍 **DRY RUN** - Checking remaining moves...")
        mover.retry_all_moves(dry_run=True)
        print("\n   Add --execute to perform actual retry operation")
        print("   Add --verify-only to check current structure")
        print("   Add --status to see quick status")
        print("   Add --check-rate-limit to test API rate limit status")


if __name__ == "__main__":
    main() 