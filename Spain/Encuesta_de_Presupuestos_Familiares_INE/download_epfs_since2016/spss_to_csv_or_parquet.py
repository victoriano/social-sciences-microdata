import os
import pyreadstat
import pandas as pd
import argparse
from pathlib import Path

def convert_spss_files(year=None, output_format='csv'):
    input_dir = Path('SPSS_raw_files')
    output_dir = Path(f'{output_format}_raw_files')
    output_dir.mkdir(exist_ok=True)

    # Find all .sav files, or files for a specific year if provided
    if year:
        spss_files = list(input_dir.glob(f'*_{year}.sav'))
    else:
        spss_files = list(input_dir.glob('*.sav'))

    for spss_file in spss_files:
        print(f"Processing {spss_file.name}")
        try:
            df, meta = pyreadstat.read_sav(spss_file, encoding='latin1')
        except pyreadstat.ReadstatError as e:
            print(f"Error reading {spss_file.name}: {str(e)}")
            print("Trying with UTF-8 encoding...")
            try:
                df, meta = pyreadstat.read_sav(spss_file, encoding='utf-8')
            except pyreadstat.ReadstatError as e:
                print(f"Error reading {spss_file.name} with UTF-8: {str(e)}")
                print(f"Skipping {spss_file.name}")
                continue
        
        # Extract year from filename
        file_year = spss_file.stem.split('_')[-1]
        year_dir = output_dir / file_year
        year_dir.mkdir(exist_ok=True)
        
        output_file = year_dir / f"{spss_file.stem}.{output_format}"
        
        # Replace numeric codes with value labels
        for column in df.columns:
            if column in meta.variable_value_labels:
                df[column] = df[column].map(meta.variable_value_labels[column]).fillna(df[column])

        if output_format == 'csv':
            # Create a dictionary of variable labels
            labels = {col: meta.column_names_to_labels.get(col, col) for col in df.columns}
            
            # Save to CSV with labels as header
            df.to_csv(output_file, index=False, header=labels.values())
        
        elif output_format == 'parquet':
            # Save to Parquet
            df.to_parquet(output_file, index=False)
        
        print(f"Saved as {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Convert SPSS files to CSV or Parquet")
    parser.add_argument("--year", type=int, help="Specific year of SPSS files to convert (optional)")
    parser.add_argument("--format", choices=['csv', 'parquet'], default='csv', help="Output format (default: parquet)")
    
    args = parser.parse_args()
    
    convert_spss_files(args.year, args.format)

if __name__ == "__main__":
    main()