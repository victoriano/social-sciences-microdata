#!/usr/bin/env python3
"""
Remove data/raw/ Prefix from HuggingFace PISA Repository

This script moves files from data/raw/{year}/{file_type}/ to {year}/{file_type}/
using the HuggingFace API for efficient server-side operations.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from huggingface_hub import HfApi, list_repo_files, hf_hub_download, upload_file, delete_file
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"

class HFPrefixRemover:
    """Remove data/raw/ prefix from HuggingFace PISA repository."""
    
    def __init__(self):
        """Initialize the prefix remover."""
        self.api = HfApi()
        
    def analyze_current_structure(self) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """Analyze current repository structure and find files to move."""
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            # Find files in data/raw/ structure
            files_to_move = []
            for file_path in files:
                if file_path.startswith('data/raw/'):
                    files_to_move.append(file_path)
            
            print(f"📊 Found {len(files_to_move)} files to move")
            
            # Organize by year and file type
            structure = {}
            for file_path in files_to_move:
                # data/raw/2000/cognitive_item/file.txt
                parts = file_path.split('/')
                if len(parts) >= 5:
                    year = parts[2]
                    file_type = parts[3]
                    filename = '/'.join(parts[4:])  # Handle nested paths
                    
                    if year not in structure:
                        structure[year] = {}
                    if file_type not in structure[year]:
                        structure[year][file_type] = []
                    
                    structure[year][file_type].append({
                        'old_path': file_path,
                        'new_path': f"{year}/{file_type}/{filename}",
                        'filename': filename
                    })
            
            return structure
            
        except Exception as e:
            print(f"❌ Error analyzing repository: {e}")
            return {}
    
    def create_move_plan(self, structure: Dict[str, Dict[str, List[Dict[str, str]]]]) -> List[Dict[str, str]]:
        """Create a flat list of file moves."""
        move_plan = []
        
        for year, year_data in structure.items():
            for file_type, files in year_data.items():
                for file_info in files:
                    move_plan.append({
                        'old_path': file_info['old_path'],
                        'new_path': file_info['new_path'],
                        'filename': file_info['filename'],
                        'year': year,
                        'file_type': file_type
                    })
        
        return move_plan
    
    def preview_move_plan(self, structure: Dict[str, Dict[str, List[Dict[str, str]]]]):
        """Preview the move plan."""
        print("📋 **Move Plan Preview**\n")
        
        total_files = 0
        for year, year_data in structure.items():
            print(f"📅 **PISA {year}:**")
            
            for file_type, files in year_data.items():
                print(f"   📁 {file_type} ({len(files)} files):")
                
                for file_info in files:
                    icon = "📄" if file_info['filename'].endswith(('.txt', '.sav', '.SAV')) else "📋"
                    print(f"     {icon} {file_info['filename']}")
                    print(f"        {file_info['old_path']} → {file_info['new_path']}")
                    total_files += 1
            print()
        
        print(f"📊 **Total files to move:** {total_files}")
    
    def execute_move(self, move_plan: List[Dict[str, str]], dry_run: bool = True) -> bool:
        """Execute the file move operations."""
        if dry_run:
            print("🔍 **DRY RUN MODE** - No actual changes will be made")
            return True
        
        try:
            print("🚀 **Executing File Moves**\n")
            
            total_files = len(move_plan)
            success_count = 0
            failed_moves = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                for i, move_info in enumerate(move_plan):
                    try:
                        old_path = move_info['old_path']
                        new_path = move_info['new_path']
                        filename = move_info['filename']
                        year = move_info['year']
                        file_type = move_info['file_type']
                        
                        progress = ((i + 1) / total_files) * 100
                        print(f"📄 Moving {filename} ({year}/{file_type}) - {progress:.1f}%")
                        
                        # Download file to temp location
                        local_file = hf_hub_download(
                            repo_id=RAW_REPO,
                            filename=old_path,
                            repo_type="dataset",
                            local_dir=temp_path,
                            local_dir_use_symlinks=False
                        )
                        
                        # Upload to new path
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
                        
                        success_count += 1
                        print(f"  ✅ Moved successfully")
                        
                    except Exception as e:
                        print(f"  ❌ Failed to move {filename}: {e}")
                        failed_moves.append({
                            'file': filename,
                            'old_path': old_path,
                            'new_path': new_path,
                            'error': str(e)
                        })
            
            print(f"\n📊 **Move Summary:**")
            print(f"✅ Successfully moved: {success_count}/{total_files} files")
            
            if failed_moves:
                print(f"❌ Failed moves: {len(failed_moves)}")
                for failure in failed_moves:
                    print(f"  - {failure['file']}: {failure['error']}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Move operation failed: {e}")
            return False
    
    def cleanup_empty_directories(self, dry_run: bool = True) -> bool:
        """Clean up empty data/raw/ structure (Note: HF doesn't have empty dirs)."""
        if dry_run:
            print("🔍 **DRY RUN:** Would clean up empty data/raw/ structure")
            return True
        
        print("🧹 **Cleanup:** HuggingFace automatically removes empty directories")
        return True
    
    def verify_new_structure(self) -> bool:
        """Verify the new structure is correct."""
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            # Check for new structure
            new_structure_files = [f for f in files if not f.startswith('data/raw/') and '/' in f and not f.startswith('.')]
            old_structure_files = [f for f in files if f.startswith('data/raw/')]
            
            print(f"📊 **Structure Verification:**")
            print(f"✅ Files in new structure: {len(new_structure_files)}")
            print(f"📁 Files in old structure: {len(old_structure_files)}")
            
            if new_structure_files and not old_structure_files:
                print("🎉 **Success:** All files moved to new structure!")
                return True
            elif new_structure_files and old_structure_files:
                print("⚠️  **Warning:** Files exist in both structures")
                return False
            else:
                print("❌ **Error:** No files found in new structure")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Remove data/raw/ prefix from HuggingFace PISA repository")
    parser.add_argument("--execute", action="store_true", help="Execute the move operation")
    parser.add_argument("--preview-only", action="store_true", help="Only show preview")
    parser.add_argument("--skip-confirmation", action="store_true", help="Skip manual confirmation")
    parser.add_argument("--verify-only", action="store_true", help="Only verify current structure")
    
    args = parser.parse_args()
    
    remover = HFPrefixRemover()
    
    # Verify only
    if args.verify_only:
        remover.verify_new_structure()
        return
    
    print("🔍 Analyzing current repository structure...")
    structure = remover.analyze_current_structure()
    
    if not structure:
        print("❌ No files found to move or analysis failed")
        return
    
    # Create move plan
    move_plan = remover.create_move_plan(structure)
    
    if args.preview_only:
        remover.preview_move_plan(structure)
        return
    
    # Show preview
    remover.preview_move_plan(structure)
    
    if not args.execute:
        print("\n🔍 **DRY RUN COMPLETE**")
        print("   Add --execute to perform actual move operation")
        print("   Add --preview-only to skip analysis")
        print("   Add --skip-confirmation to skip manual confirmation")
        return
    
    # Confirm execution
    if not args.skip_confirmation:
        print("\n⚠️  **WARNING**: This will move all files in the HuggingFace repository!")
        print("   This operation will:")
        print("   - Download each file temporarily")
        print("   - Upload to new location")
        print("   - Delete old location")
        confirm = input("   Type 'MOVE' to confirm: ")
        
        if confirm != 'MOVE':
            print("❌ Move operation cancelled")
            return
    else:
        print("\n🚀 **PROCEEDING WITH MOVE** (confirmation skipped)")
    
    # Execute move
    success = remover.execute_move(move_plan, dry_run=False)
    
    if success:
        print("\n🧹 Cleaning up empty directories...")
        remover.cleanup_empty_directories(dry_run=False)
        
        print("\n🔍 Verifying new structure...")
        verification_success = remover.verify_new_structure()
        
        if verification_success:
            print("\n🎉 **Repository reorganization complete!**")
            print("   HuggingFace repository now uses: {year}/{file_type}/")
            print("   Local downloads will still go to: data/raw/{year}/{file_type}/")
        else:
            print("\n⚠️  **Reorganization completed with warnings**")
            print("   Please check the repository structure manually")
    else:
        print("\n❌ **Reorganization failed**")


if __name__ == "__main__":
    main() 