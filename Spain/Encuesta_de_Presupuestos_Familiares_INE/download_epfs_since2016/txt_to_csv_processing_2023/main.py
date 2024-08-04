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

    print(f"\nSummary for {file_name}:")
    print(f"Total columns: {total_columns}")
    print(f"Numeric columns: {len(numeric_columns)}")
    print(f"Categorical columns: {len(categorical_columns)}")
    
    print("\nColumn details:")
    for column in df.columns:
        null_percentage = (df[column].isnull().sum() / len(df) * 100).round(2)
        non_null_values = df[column].dropna()
        
        # Check if the column contains mixed types
        numeric_count = non_null_values.apply(lambda x: pd.api.types.is_numeric_dtype(type(x)) or (isinstance(x, str) and x.replace('.', '').isdigit())).sum()
        numeric_percentage = (numeric_count / len(non_null_values) * 100).round(2)
        string_percentage = (100 - numeric_percentage).round(2)
        
        # Calculate cardinality for numeric columns
        cardinality = non_null_values.nunique() if numeric_percentage == 100 else None
        
        # Determine column name color
        if 0 < numeric_percentage < 100:
            column_name = f"\033[91m{column}\033[0m"  # Red color for mixed types
        elif cardinality is not None and 1 < cardinality < 20 and "NORDEN" not in column:
            column_name = f"\033[94m{column}\033[0m"  # Electric blue for specified condition
        else:
            column_name = column

        print(f"  {column_name}:")
        print(f"    Null: {null_percentage}%")
        print(f"    Non-null: {100 - null_percentage}% ({numeric_percentage}% numeric, {string_percentage}% string)")
        
        # Add cardinality for 100% numeric columns
        if cardinality is not None:
            print(f"    Cardinality: {cardinality}")

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

def summarize_enriched_files(generate_summaries=True, open_files=True):
    enriched_files = [
        "final_outputs_enriched/hogares_2023.csv",
        "final_outputs_enriched/gastos_2023.csv",
        "final_outputs_enriched/miembros_2023.csv"
    ]

    for file in enriched_files:
        if generate_summaries:
            generate_summary(file)
        if open_files:
            open_file(file)

def main():
    # Step 1: Run convert_epf_to_csv.py
    run_script("convert_epf_to_csv.py")

    # Step 2: Run enrich_csv.py
    run_script("enrich_csv.py")

    # Step 3: Generate summaries for enriched datasets and open files
    # Uncomment the following line to disable summary generation and file opening
    # process_enriched_files(generate_summaries=False, open_files=False)
    #summarize_enriched_files()

    print("Data processing, summary generation, and file opening completed.")

if __name__ == "__main__":
    main()