# PISA Data Upload Guide

## 📤 Intelligent Upload System

The PISA project includes an intelligent upload system that efficiently manages data uploads to HuggingFace repositories with smart change detection and proper organization.

## 🎯 Repository Structure

### **Private Repository** (Raw Data)
- **Repository**: `victoriano/pisa-raw`
- **Content**: Raw PISA data files (SPSS, text, documentation)
- **Access**: Private (requires authentication)
- **Structure**: Maintains original directory structure by year

### **Public Repository** (Processed Data)
- **Repository**: `victoriano/social-sciences-microdata`
- **Content**: Processed, harmonized PISA data files
- **Access**: Public (no authentication required for downloads)
- **Structure**: Files stored under `global/pisa/` prefix

## 🧠 Intelligent Features

### **Change Detection**
- ✅ **File size comparison** - Only uploads files that have changed
- ✅ **Timestamp checking** - Skips files that haven't been modified
- ✅ **Existence detection** - Automatically uploads new files
- ✅ **Hash verification** - Ensures data integrity

### **Upload Optimization**
- 📁 **Individual file uploads** - No wasteful archive creation
- 🔄 **Retry logic** - Handles rate limits and network issues
- ⏳ **Exponential backoff** - Smart retry timing
- 📊 **Progress tracking** - Detailed statistics and reporting

## 🚀 Usage

### **1. Check Status**
```bash
# Show current file detection and statistics
uv run python pipelines/upload_raw_data.py --status
```

### **2. Upload Raw Data Only**
```bash
# Upload to private repository (victoriano/pisa-raw)
uv run python pipelines/upload_raw_data.py --raw
```

### **3. Upload Processed Data Only**
```bash
# Upload to public repository (victoriano/social-sciences-microdata)
uv run python pipelines/upload_raw_data.py --processed
```

### **4. Upload Everything**
```bash
# Upload both raw and processed data
uv run python pipelines/upload_raw_data.py --all
```

## 📊 Expected File Counts

### **Raw Data** (59 files total)
- **2000**: 10 files (txt, pdf)
- **2003**: 6 files (sav, txt, pdf)
- **2006**: 9 files (sav, txt, pdf)
- **2009**: 10 files (sav, txt, pdf)
- **2012**: 10 files (sav, txt, pdf)
- **2015**: 6 files (sav, pdf)
- **2018**: 4 files (sav, pdf)
- **2022**: 4 files (sav, pdf)

### **Processed Data** (10 files total)
- **Harmonized datasets**: `pisa_YYYY_harmonized.parquet`
- **Combined trends**: `pisa_combined_2006_2022.parquet`
- **Spain analysis**: `spain_trends_2006_2022.parquet`
- **Metadata**: `processing_metadata_2006_2022.json`
- **Summaries**: Various CSV files

## 🔧 Configuration

### **Default Settings**
```python
# Repository configuration
raw_repo = "victoriano/pisa-raw"           # Private repository
processed_repo = "victoriano/social-sciences-microdata"  # Public repository
processed_prefix = "global/pisa"           # Path prefix for processed data

# Upload settings
max_retries = 3                            # Maximum retry attempts
retry_delay = 1.0                          # Base retry delay (seconds)
chunk_size = 8192                          # File reading chunk size
```

## 🛡️ Authentication

### **HuggingFace Hub Setup**
1. **Install HuggingFace Hub**:
   ```bash
   uv add huggingface_hub
   ```

2. **Login to HuggingFace**:
   ```bash
   huggingface-cli login
   ```

3. **Verify Access**:
   ```bash
   # Test with status command
   uv run python pipelines/upload_raw_data.py --status
   ```

## 📈 Upload Process

### **Smart Upload Flow**
1. **Repository Check** - Verify repository exists (create if needed)
2. **Remote Scan** - List existing files in repository
3. **Local Scan** - Find all eligible files locally
4. **Change Detection** - Compare file sizes and timestamps
5. **Selective Upload** - Upload only new/modified files
6. **Progress Tracking** - Report statistics and results

### **File Type Filtering**
- **Raw Data**: `.sav`, `.txt`, `.pdf`, `.sps`
- **Processed Data**: `.parquet`, `.csv`, `.json`, `.md`

## 🔄 Error Handling

### **Rate Limiting**
- ⏳ **Automatic detection** of 429 (Too Many Requests) errors
- 🔄 **Exponential backoff** with 1s, 2s, 4s delays
- 📊 **Progress reporting** during wait periods

### **Network Issues**
- 🔄 **Retry mechanism** for temporary failures
- 📝 **Detailed error logging** for debugging
- ✅ **Graceful degradation** - continues with other files

### **Authentication Errors**
- 🔐 **Clear error messages** for missing credentials
- 📋 **Setup instructions** for HuggingFace authentication
- 🛡️ **Private repository handling** for raw data

## 📊 Output Example

### **Status Command**
```
📊 **UPLOAD STATUS**
Raw data directory: True (.../data/raw)
Processed data directory: True (.../data/processed)
Raw files found: 59
  2000: 10 files
  2003: 6 files
  2006: 9 files
  2009: 10 files
  2012: 10 files
  2015: 6 files
  2018: 4 files
  2022: 4 files
Processed files found: 10

Statistics:
  Uploaded: 0
  Skipped: 0
  Failed: 0
  Total size: 0.0 MB
```

### **Upload Summary**
```
🎯 **UPLOAD SUMMARY**
✅ Uploaded: 15 files
⏩ Skipped: 44 files (unchanged)
❌ Failed: 0 files
📊 Total uploaded: 145.2 MB

🔗 **Repository Links:**
Raw data: https://huggingface.co/datasets/victoriano/pisa-raw
Processed data: https://huggingface.co/datasets/victoriano/social-sciences-microdata
```

## 🎯 Best Practices

### **Before Upload**
1. ✅ **Run harmonize_trends.py** to ensure processed data is up-to-date
2. ✅ **Check status** to verify file detection
3. ✅ **Verify HuggingFace authentication** is working

### **During Upload**
1. 🔄 **Monitor progress** - uploads will show real-time status
2. ⏳ **Be patient** - large files may take time
3. 📊 **Check statistics** - verify expected file counts

### **After Upload**
1. 🔗 **Verify repositories** - check HuggingFace links in summary
2. 📊 **Review statistics** - ensure no unexpected failures
3. 📝 **Document changes** - update README if needed

## 🔗 Repository Links

- **Raw Data**: https://huggingface.co/datasets/victoriano/pisa-raw
- **Processed Data**: https://huggingface.co/datasets/victoriano/social-sciences-microdata
- **GitHub Source**: https://github.com/victoriano/social-sciences-microdata/tree/main/Global/pisa

## 🆘 Troubleshooting

### **Common Issues**

1. **Authentication Error**
   ```bash
   # Solution: Login to HuggingFace
   huggingface-cli login
   ```

2. **Repository Not Found**
   ```bash
   # Solution: Script will create repository automatically
   # Or create manually at https://huggingface.co/new-dataset
   ```

3. **Rate Limiting**
   ```bash
   # Solution: Script handles automatically with exponential backoff
   # Wait for completion, don't interrupt
   ```

4. **File Not Found**
   ```bash
   # Solution: Check file paths and run from correct directory
   cd Global/pisa/pipelines
   uv run python upload_raw_data.py --status
   ```

### **Support**
- 📚 **Documentation**: This guide and inline help
- 🐛 **Issues**: GitHub repository issues section
- 📝 **Logs**: Script provides detailed error information 