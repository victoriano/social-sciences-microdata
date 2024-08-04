import os
import requests
import zipfile
import shutil
from tqdm import tqdm

BASE_URL = "https://www.ine.es/ftp/microdatos/epf2006/datos_{}.zip"
SPSS_DIR = "SPSS_raw_files"

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def process_year(year):
    url = BASE_URL.format(year)
    zip_filename = f"datos_{year}.zip"
    
    # Download the zip file
    print(f"Downloading data for {year}...")
    download_file(url, zip_filename)
    
    # Unzip the main zip file
    print(f"Unzipping data for {year}...")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(f"temp_{year}")
    
    # Process the extracted files
    for root, dirs, files in os.walk(f"temp_{year}"):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(zip_path))
    
    # Move SPSS files to the output directory
    for root, dirs, files in os.walk(f"temp_{year}"):
        if "SPSS" in dirs:
            spss_dir = os.path.join(root, "SPSS")
            for file in os.listdir(spss_dir):
                if file.endswith(".sav"):
                    src = os.path.join(spss_dir, file)
                    dst = os.path.join(SPSS_DIR, f"{year}_{file}")
                    shutil.move(src, dst)
    
    # Clean up temporary files
    shutil.rmtree(f"temp_{year}")
    os.remove(zip_filename)

def main():
    os.makedirs(SPSS_DIR, exist_ok=True)
    
    for year in range(2016, 2023):
        process_year(year)
    
    print("Processing complete.")

if __name__ == "__main__":
    main()
