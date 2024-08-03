import subprocess
import sys
import pandas as pd
import numpy as np
import os
import time
import platform

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"{script_name} executed successfully.")
        print(result.stdout)
    else:
        print(f"Error executing {script_name}:")
        print(result.stderr)

def generate_summary(file_name):
    df = pd.read_csv(file_name)
    total_columns = len(df.columns)
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
    null_percentages = (df.isnull().sum() / len(df) * 100).round(2)

    print(f"\nSummary for {file_name}:")
    print(f"Total columns: {total_columns}")
    print(f"Numeric columns: {len(numeric_columns)}")
    print(f"Categorical columns: {len(categorical_columns)}")
    print(f"Percentage of null values:")
    for column, percentage in null_percentages.items():
        if percentage > 0:
            print(f"  {column}: {percentage}%")

def wait_for_file(file_name, timeout=60):
    start_time = time.time()
    while not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        if time.time() - start_time > timeout:
            print(f"Timeout: File {file_name} was not created or is empty after {timeout} seconds.")
            return False
        time.sleep(1)
    return True

def open_file(file_name):
    if wait_for_file(file_name):
        print(f"Opening {file_name} with the default program...")
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.run(('open', file_name))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(file_name)
            else:                                   # linux variants
                subprocess.run(('xdg-open', file_name))
        except Exception as e:
            print(f"Error: Failed to open {file_name}. {str(e)}")
    else:
        print(f"Skipping opening {file_name} due to file creation issues.")

def main():
    # Step 1: Run convert_epf_to_csv.py
    run_script("convert_epf_to_csv.py")

    # Step 2: Run enrich_csv.py
    run_script("enrich_csv.py")

    # Step 3: Generate summaries for enriched datasets and open files
    enriched_files = [
        #"hogares_2023_enriched.csv",
        #"gastos_2023_enriched.csv",
        "miembros_2023_enriched.csv"
    ]

    for file in enriched_files:
        generate_summary(file)
        open_file(file)

    print("Data processing, summary generation, and file opening completed.")

if __name__ == "__main__":
    main()