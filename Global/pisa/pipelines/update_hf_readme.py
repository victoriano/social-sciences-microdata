#!/usr/bin/env python3
"""
Update HuggingFace Repository README

This script creates and uploads a comprehensive README to the HuggingFace PISA repository
explaining the data source, structure, and usage.
"""

import os
import sys
import tempfile
from pathlib import Path

try:
    from huggingface_hub import upload_file
except ImportError:
    print("❌ huggingface_hub not found. Install with: uv add huggingface_hub")
    sys.exit(1)

# Configuration
RAW_REPO = "victoriano/pisa-raw"

def create_readme_content() -> str:
    """Create the README content."""
    
    readme_content = """---
license: other
task_categories:
- other
language:
- en
tags:
- education
- assessment
- international
- survey
- microdata
- student-achievement
- cross-national
- comparative-education
size_categories:
- 10M<n<100M
source_datasets:
- original
dataset_info:
  features:
  - name: student_questionnaire
    dtype: 
      - int64
      - float64
      - string
    description: Student background questionnaire responses
  - name: school_questionnaire  
    dtype:
      - int64
      - float64
      - string
    description: School background questionnaire responses
  - name: cognitive_item
    dtype:
      - int64
      - float64
      - string
    description: Cognitive assessment item responses
  configs:
  - config_name: default
    data_files:
    - split: train
      path: "*/student_questionnaire/*"
    - split: validation
      path: "*/school_questionnaire/*"
    - split: test
      path: "*/cognitive_item/*"
extra_gated_prompt: >
  This dataset contains PISA (Programme for International Student Assessment) raw data 
  from the OECD. By accessing this dataset, you agree to:
  
  1. Use the data for academic and research purposes only
  2. Properly attribute the OECD as the original data source
  3. Comply with OECD's terms of use for PISA data
  4. Not redistribute the raw data without proper attribution
  
  For commercial use, please contact the OECD directly.
extra_gated_fields:
  Name: text
  Email: text
  Affiliation: text
  Research Purpose: text
  I agree to use this data responsibly and cite the OECD appropriately: checkbox
pretty_name: PISA Raw Data Repository
---

# PISA Raw Data Repository

[![License: Custom](https://img.shields.io/badge/License-Custom-blue.svg)](https://www.oecd.org/pisa/data/)
[![Data Source: OECD](https://img.shields.io/badge/Data%20Source-OECD-green.svg)](https://www.oecd.org/pisa/)
[![Processing Tools](https://img.shields.io/badge/Processing-GitHub-orange.svg)](https://github.com/victoriano/social-sciences-microdata)

## 📊 Overview

This repository contains raw PISA (Programme for International Student Assessment) data files spanning from 2000 to 2022. PISA is a worldwide study by the Organisation for Economic Co-operation and Development (OECD) that evaluates education systems by testing the skills and knowledge of 15-year-old students.

## 🗂️ Repository Structure

The repository is organized by assessment year and file type:

```
{year}/
├── student_questionnaire/     # Student background questionnaire data
├── school_questionnaire/      # School background questionnaire data  
├── cognitive_item/           # Cognitive assessment item responses
├── parent_questionnaire/     # Parent questionnaire data (when available)
├── teacher_questionnaire/    # Teacher questionnaire data (when available)
├── documentation/           # README files, manuals, and guides
├── questionnaire_additional/ # Additional questionnaire data
└── other/                   # Converted files and supplementary data
```

## 📅 Available Years

| Year | Student Data | School Data | Cognitive Items | Documentation |
|------|-------------|-------------|-----------------|---------------|
| 2022 | ✅ | ✅ | ✅ | ✅ |
| 2018 | ✅ | ✅ | ✅ | ✅ |
| 2015 | ✅ | ✅ | ✅ | ✅ |
| 2012 | ✅ | ✅ | ✅ | ✅ |
| 2009 | ✅ | ✅ | ✅ | ✅ |
| 2006 | ✅ | ✅ | ✅ | ✅ |
| 2003 | ✅ | ✅ | ✅ | ✅ |
| 2000 | ✅ | ✅ | ✅ | ✅ |

## 📄 File Types

### Data Files
- **`.sav`** - SPSS data files (modern format)
- **`.SAV`** - SPSS data files (legacy format)
- **`.txt`** - Fixed-width text data files

### Control Files
- **`SPSS_*.txt`** - SPSS syntax files for reading data
- **`*.sps`** - SPSS syntax files
- **Control files** - Variable definitions and formatting instructions

### Documentation
- **`.pdf`** - Technical manuals and documentation
- **`README_*.txt`** - Dataset-specific instructions

## 🔄 Data Processing

For data processing, cleaning, and analysis tools, visit our main processing repository:

**🔗 [Social Sciences Microdata Processing Tools](https://github.com/victoriano/social-sciences-microdata)**

The processing repository includes:
- 🐍 **Python pipelines** for data harmonization
- 📊 **Analysis notebooks** with examples
- 🔧 **Utility functions** for PISA data handling
- 📈 **Visualization tools** for trends and comparisons
- 📚 **Documentation** for data usage

## 🚀 Quick Start

### Option 1: HuggingFace Hub (Recommended)
```python
from huggingface_hub import hf_hub_download

# Download a specific file
file_path = hf_hub_download(
    repo_id="victoriano/pisa-raw",
    filename="2022/student_questionnaire/CY08MSP_STU_QQQ.SAV",
    repo_type="dataset"
)
```

### Option 2: Using Processing Tools
```python
# Clone the processing repository
git clone https://github.com/victoriano/social-sciences-microdata.git
cd social-sciences-microdata/Global/pisa

# Use the download script
python scripts/download_from_hf.py --years 2022 --file-types student_questionnaire
```

## 📚 Data Content

### Student Questionnaire
- **Demographics**: Age, gender, immigration status
- **Socioeconomic background**: Family income, education, occupation
- **School experience**: Learning time, teaching quality, school climate
- **ICT usage**: Computer access and digital skills
- **Attitudes**: Motivation, self-efficacy, career aspirations

### School Questionnaire
- **School characteristics**: Size, location, resources
- **Student body**: Demographics, socioeconomic composition
- **Learning environment**: Facilities, staffing, policies
- **Curriculum**: Program offerings, assessment practices
- **Technology**: ICT resources and integration

### Cognitive Items
- **Mathematics**: Problem-solving, reasoning, modeling
- **Reading**: Comprehension, evaluation, reflection
- **Science**: Inquiry, knowledge, competency
- **Item responses**: Student answers to assessment questions
- **Timing data**: Response times and patterns

## 🏛️ Data Source

All data in this repository originates from the **OECD PISA Database**:

- **Official Source**: [OECD PISA Data](https://www.oecd.org/pisa/data/)
- **Original Publisher**: Organisation for Economic Co-operation and Development (OECD)
- **Data Collection**: Conducted every three years since 2000
- **Coverage**: 70+ countries and economies worldwide

## ⚖️ Terms of Use

This data is provided under the OECD's terms of use:

- **Academic Use**: ✅ Permitted for research and educational purposes
- **Commercial Use**: ⚠️ Requires permission from OECD
- **Attribution**: 📝 Required - cite OECD as the original source
- **Redistribution**: 🔄 Permitted with proper attribution

### Recommended Citation
```
OECD (2023), PISA Database. https://www.oecd.org/pisa/data/
```

## 🔍 Data Quality Notes

- **Missing Values**: Coded using PISA-specific conventions
- **Sampling Weights**: Available for population-level estimates  
- **Multiple Imputation**: Used for missing background data
- **Country Coverage**: Varies by assessment year
- **Technical Documentation**: Available in `/documentation/` folders

## 🛠️ Technical Information

### File Formats
- **SPSS Files**: Can be read with `pandas`, `pyreadstat`, or SPSS
- **Text Files**: Fixed-width format with accompanying syntax files
- **Encoding**: UTF-8 or Windows-1252 (varies by year)

### Data Structure
- **Hierarchical**: Students nested within schools within countries
- **Identifiers**: Country, school, and student ID variables
- **Plausible Values**: Multiple imputed values for achievement scores

## 🆘 Support

For issues with:
- **Data Access**: Check HuggingFace Hub documentation
- **Data Processing**: Visit our [GitHub Issues](https://github.com/victoriano/social-sciences-microdata/issues)
- **PISA Methodology**: Consult [OECD PISA Technical Reports](https://www.oecd.org/pisa/data/)

## 🏷️ Keywords

`PISA` `OECD` `Education` `Assessment` `International` `Student` `Achievement` `Reading` `Mathematics` `Science` `Microdata` `Survey` `Cross-national` `Comparative`

---

**Repository Maintained by**: [Victoriano](https://github.com/victoriano)  
**Last Updated**: 2024  
**Data License**: OECD Terms of Use  
**Processing Tools**: [GitHub Repository](https://github.com/victoriano/social-sciences-microdata)
"""
    
    return readme_content

def upload_readme(dry_run: bool = True) -> bool:
    """Upload the README to HuggingFace repository."""
    
    readme_content = create_readme_content()
    
    if dry_run:
        print("🔍 **README Preview:**")
        print("=" * 80)
        print(readme_content)
        print("=" * 80)
        print(f"📄 Total length: {len(readme_content)} characters")
        return True
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
            tmp_file.write(readme_content)
            tmp_file_path = tmp_file.name
        
        print("📤 Uploading README to HuggingFace repository...")
        
        # Upload to HuggingFace
        upload_file(
            path_or_fileobj=tmp_file_path,
            path_in_repo="README.md",
            repo_id=RAW_REPO,
            repo_type="dataset",
            commit_message="Update README with comprehensive data documentation"
        )
        
        # Clean up
        os.unlink(tmp_file_path)
        
        print("✅ README successfully uploaded!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload README: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update HuggingFace repository README")
    parser.add_argument("--upload", action="store_true", help="Upload README to repository")
    parser.add_argument("--preview", action="store_true", help="Preview README content only")
    
    args = parser.parse_args()
    
    if args.upload:
        print("📤 **UPLOADING README TO REPOSITORY**")
        success = upload_readme(dry_run=False)
        
        if success:
            print("\n🎉 **SUCCESS!**")
            print("   README has been uploaded to the HuggingFace repository")
            print("   Visit: https://huggingface.co/datasets/victoriano/pisa-raw")
        else:
            print("\n❌ **FAILED**")
            print("   README upload encountered errors")
    
    elif args.preview:
        print("👀 **PREVIEWING README CONTENT**")
        upload_readme(dry_run=True)
    
    else:
        print("📋 **HuggingFace README Updater**")
        print("   --preview    Show README content")
        print("   --upload     Upload README to repository")

if __name__ == "__main__":
    main() 