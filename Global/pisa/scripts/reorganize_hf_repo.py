#!/usr/bin/env python3
"""
Reorganize HuggingFace PISA Repository

This script reorganizes the HuggingFace PISA repository to match 
the new OECD download structure: data/raw/{year}/{file_type}/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import shutil

try:
    from huggingface_hub import HfApi, hf_hub_download, upload_file, create_repo, list_repo_files
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"

# File type mappings - map current files to standardized file types
FILE_MAPPINGS = {
    # Student questionnaire files
    'student_questionnaire': {
        'data_patterns': ['intstud_', 'INT_stui_', 'INT_STU', 'STU_QQQ', 'STU_COG'],
        'control_patterns': ['SPSS_student', 'SPSS_STU', 'student_mathematics', 'student_reading', 'student_science']
    },
    
    # School questionnaire files  
    'school_questionnaire': {
        'data_patterns': ['intscho', 'INT_schi_', 'INT_Sch', 'INT_SCQ', 'SCH_QQQ'],
        'control_patterns': ['SPSS_school', 'SPSS_SCH']
    },
    
    # Cognitive item files
    'cognitive_item': {
        'data_patterns': ['INT_cogn', 'INT_Cogn', 'INT_COG', 'COG', 'STU_COG'],
        'control_patterns': ['SPSS_cognitive', 'cognitive_item']
    },
    
    # Parent questionnaire files (when available)
    'parent_questionnaire': {
        'data_patterns': ['PAR_QQQ', 'parent'],
        'control_patterns': ['SPSS_parent']
    },
    
    # Additional questionnaire files
    'questionnaire_additional': {
        'data_patterns': ['STU_QQ2'],
        'control_patterns': []
    }
}

def classify_file(filename: str) -> Tuple[str, str]:
    """
    Classify a file into file_type and data_type (data/control).
    
    Returns: (file_type, data_type) where data_type is 'data' or 'control'
    """
    filename_lower = filename.lower()
    
    # Check if it's a control file (SPSS syntax)
    if any(pattern.lower() in filename_lower for pattern_list in FILE_MAPPINGS.values() 
           for pattern in pattern_list['control_patterns']):
        for file_type, patterns in FILE_MAPPINGS.items():
            if any(pattern.lower() in filename_lower for pattern in patterns['control_patterns']):
                return file_type, 'control'
    
    # Check if it's a data file
    for file_type, patterns in FILE_MAPPINGS.items():
        if any(pattern.lower() in filename_lower for pattern in patterns['data_patterns']):
            return file_type, 'data'
    
    # Default classification
    if 'readme' in filename_lower:
        return 'documentation', 'info'
    elif 'manual' in filename_lower or '.pdf' in filename_lower:
        return 'documentation', 'manual'
    
    return 'other', 'unknown'

class HFReorganizer:
    """Reorganize HuggingFace PISA repository."""
    
    def __init__(self):
        """Initialize reorganizer."""
        self.api = HfApi()
        self.temp_dir = None
        
    def analyze_current_structure(self) -> Dict[str, List[str]]:
        """Analyze current repository structure."""
        try:
            files = list_repo_files(RAW_REPO, repo_type="dataset")
            
            structure = {}
            for file_path in files:
                if '/' in file_path:  # Skip root level files like .gitattributes
                    year, filename = file_path.split('/', 1)
                    if year not in structure:
                        structure[year] = []
                    structure[year].append(filename)
            
            return structure
        except Exception as e:
            print(f"❌ Error analyzing repository: {e}")
            return {}
    
    def create_reorganization_plan(self, structure: Dict[str, List[str]]) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """Create reorganization plan mapping old paths to new paths."""
        plan = {}
        
        for year, files in structure.items():
            year_plan = {}
            
            for filename in files:
                file_type, data_type = classify_file(filename)
                
                # Create new path
                if file_type not in year_plan:
                    year_plan[file_type] = []
                
                year_plan[file_type].append({
                    'old_path': f"{year}/{filename}",
                    'new_path': f"data/raw/{year}/{file_type}/{filename}",
                    'data_type': data_type,
                    'filename': filename
                })
            
            plan[year] = year_plan
        
        return plan
    
    def preview_reorganization(self, plan: Dict[str, Dict[str, List[Dict[str, str]]]]):
        """Preview the reorganization plan."""
        print("📋 **Reorganization Plan Preview**\n")
        
        for year, year_plan in plan.items():
            print(f"📅 **PISA {year}:**")
            
            for file_type, files in year_plan.items():
                print(f"   📁 {file_type}:")
                
                for file_info in files:
                    icon = "📄" if file_info['data_type'] == 'data' else "📋" if file_info['data_type'] == 'control' else "📖"
                    print(f"     {icon} {file_info['filename']}")
                    print(f"        {file_info['old_path']} → {file_info['new_path']}")
            print()
    
    def execute_reorganization(self, plan: Dict[str, Dict[str, List[Dict[str, str]]]], dry_run: bool = True) -> bool:
        """Execute the reorganization plan."""
        if dry_run:
            print("🔍 **DRY RUN MODE** - No actual changes will be made\n")
            self.preview_reorganization(plan)
            return True
        
        try:
            print("🚀 **Executing Reorganization**\n")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                self.temp_dir = Path(temp_dir)
                
                total_files = sum(len(files) for year_plan in plan.values() for files in year_plan.values())
                processed = 0
                
                for year, year_plan in plan.items():
                    print(f"📅 Processing PISA {year}...")
                    
                    for file_type, files in year_plan.items():
                        print(f"   📁 Processing {file_type}...")
                        
                        for file_info in files:
                            try:
                                # Download file from HF
                                old_path = file_info['old_path']
                                local_file = hf_hub_download(
                                    repo_id=RAW_REPO,
                                    filename=old_path,
                                    repo_type="dataset",
                                    local_dir=self.temp_dir,
                                    local_dir_use_symlinks=False
                                )
                                
                                # Upload to new path
                                new_path = file_info['new_path']
                                upload_file(
                                    path_or_fileobj=local_file,
                                    path_in_repo=new_path,
                                    repo_id=RAW_REPO,
                                    repo_type="dataset"
                                )
                                
                                processed += 1
                                progress = (processed / total_files) * 100
                                print(f"     ✅ {file_info['filename']} ({progress:.1f}%)")
                                
                            except Exception as e:
                                print(f"     ❌ Failed to move {file_info['filename']}: {e}")
                
                print(f"\n✅ Reorganization complete! Processed {processed}/{total_files} files")
                return True
                
        except Exception as e:
            print(f"❌ Reorganization failed: {e}")
            return False
    
    def create_structure_summary(self, plan: Dict[str, Dict[str, List[Dict[str, str]]]]) -> str:
        """Create a summary of the new structure."""
        summary = "# PISA Data Repository Structure\n\n"
        summary += "Reorganized to match OECD download structure: `data/raw/{year}/{file_type}/`\n\n"
        
        for year in sorted(plan.keys()):
            year_plan = plan[year]
            summary += f"## PISA {year}\n\n"
            
            for file_type in sorted(year_plan.keys()):
                files = year_plan[file_type]
                summary += f"### {file_type}\n"
                
                data_files = [f for f in files if f['data_type'] == 'data']
                control_files = [f for f in files if f['data_type'] == 'control']
                
                if data_files:
                    summary += "**Data Files:**\n"
                    for f in data_files:
                        summary += f"- {f['filename']}\n"
                
                if control_files:
                    summary += "**Control Files:**\n"
                    for f in control_files:
                        summary += f"- {f['filename']}\n"
                
                summary += "\n"
        
        return summary


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reorganize HuggingFace PISA repository")
    parser.add_argument("--execute", action="store_true", help="Execute reorganization (default: dry run)")
    parser.add_argument("--preview-only", action="store_true", help="Only show preview")
    parser.add_argument("--skip-confirmation", action="store_true", help="Skip manual confirmation prompt")
    
    args = parser.parse_args()
    
    reorganizer = HFReorganizer()
    
    print("🔍 Analyzing current repository structure...")
    current_structure = reorganizer.analyze_current_structure()
    
    if not current_structure:
        print("❌ Failed to analyze repository")
        return
    
    print("📋 Creating reorganization plan...")
    plan = reorganizer.create_reorganization_plan(current_structure)
    
    if args.preview_only:
        reorganizer.preview_reorganization(plan)
        return
    
    # Show preview first
    reorganizer.preview_reorganization(plan)
    
    if not args.execute:
        print("\n🔍 **DRY RUN COMPLETE**")
        print("   Add --execute to perform actual reorganization")
        print("   Add --preview-only to skip this analysis")
        print("   Add --skip-confirmation to skip manual confirmation")
        return
    
    # Confirm execution (unless skipped)
    if not args.skip_confirmation:
        print("\n⚠️  **WARNING**: This will reorganize the entire HuggingFace repository!")
        confirm = input("   Type 'REORGANIZE' to confirm: ")
        
        if confirm != 'REORGANIZE':
            print("❌ Reorganization cancelled")
            return
    else:
        print("\n🚀 **PROCEEDING WITH REORGANIZATION** (confirmation skipped)")
    
    # Execute
    success = reorganizer.execute_reorganization(plan, dry_run=False)
    
    if success:
        print("\n📄 Creating structure summary...")
        summary = reorganizer.create_structure_summary(plan)
        
        # Save summary to temp file and upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(summary)
            temp_summary = f.name
        
        try:
            upload_file(
                path_or_fileobj=temp_summary,
                path_in_repo="STRUCTURE.md",
                repo_id=RAW_REPO,
                repo_type="dataset"
            )
            print("✅ Structure summary uploaded to repository")
        except Exception as e:
            print(f"⚠️  Failed to upload summary: {e}")
        finally:
            os.unlink(temp_summary)


if __name__ == "__main__":
    main() 