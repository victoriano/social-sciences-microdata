import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import zipfile
import os
import shutil

# Load the CSV file
df = pd.read_csv('barometros_index.csv')

# Function to download and unzip files
def download_and_unzip_file(codigo):
    url = f"https://www.cis.es/documents/d/cis/MD{codigo}?download=true"
    response = requests.get(url)
    if response.status_code == 200:
        zip_path = f"barometros_raw/MD{codigo}.zip"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {zip_path}")
        
        try:
            # Attempt to unzip the file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(f"barometros_raw/MD{codigo}")
            print(f"Unzipped: {zip_path}")
            
            # Remove the zip file
            os.remove(zip_path)
            print(f"Removed: {zip_path}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_path} is not a valid zip file. Skipping extraction.")
            # Optionally, you can remove the invalid file
            os.remove(zip_path)
            print(f"Removed invalid file: {zip_path}")
    else:
        print(f"Failed to download: MD{codigo}")

# Function to filter studies by date range and download them
def download_studies(start_month, end_month):
    # Convert date columns to datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Parse the input date strings
    start_date = datetime.strptime(start_month, "%m/%Y")
    end_date = datetime.strptime(end_month, "%m/%Y") + relativedelta(months=1) - relativedelta(days=1)
    
    # Filter the dataframe by date range
    filtered_df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    
    # Download and unzip each file
    for codigo in filtered_df['codigo']:
        download_and_unzip_file(codigo)

# Function to remove all files in the barometros_raw folder
def clear_barometros_raw():
    folder = 'barometros_raw'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# Main function to be called from another file
def main(start_month, end_month, clear_folder=True):
    if clear_folder:
        clear_barometros_raw()
        print("Cleared barometros_raw folder.")
    
    # Download studies in the date range
    download_studies(start_month, end_month)

# Example usage
if __name__ == "__main__":
    start_month = "01/2008"
    end_month = "07/2024"
    main(start_month, end_month)