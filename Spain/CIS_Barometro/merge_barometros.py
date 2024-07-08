import pandas as pd
import os
import pyreadstat
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Load the CSV file
df = pd.read_csv('download_barometros/barometros_index.csv')

# Function to filter studies by date range
def filter_studies_by_date(start_month, end_month):
    # Convert date columns to datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Parse the input date strings
    start_date = datetime.strptime(start_month, "%m/%Y")
    end_date = datetime.strptime(end_month, "%m/%Y") + relativedelta(months=1) - relativedelta(days=1)
    
    # Filter the dataframe by date range
    filtered_df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    return filtered_df

def convert_sav_to_csv(sav_path, csv_path):
    # Read the .sav file
    df, meta = pyreadstat.read_sav(sav_path)
    
    # Create a copy of the DataFrame to store the labeled values
    df_labeled = df.copy()
    
    # Replace values with their labels for each variable
    for col in df.columns:
        if col in meta.variable_value_labels:
            value_labels = meta.variable_value_labels[col]
            df_labeled[col] = df[col].map(value_labels).fillna(df[col])
    
    # Replace variable names with their labels
    df_labeled.columns = [meta.column_names_to_labels.get(col, col) for col in df_labeled.columns]
    
    # Save the labeled DataFrame to a .csv file
    df_labeled.to_csv(csv_path, index=False)
    
    return df_labeled

def merge_sav_files(file_codes):
    merged_df = None
    common_columns = None
    
    for code in file_codes:
        sav_path = f'download_barometros/barometros_raw/MD{code}/{code}.sav'
        print(f"Processing file: {sav_path}")
        
        # Convert SAV to CSV
        df = convert_sav_to_csv(sav_path, None)
        
        # Rename duplicate columns
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        df.columns = [f'{col}_{i}' if df.columns.tolist().count(col) > 1 else col for i, col in enumerate(df.columns)]
        
        print(f"Columns: {df.columns.tolist()}")
        
        if merged_df is None:
            merged_df = df
            common_columns = set(df.columns)
        else:
            common_columns &= set(df.columns)
            
            # Ensure consistent data types for merge keys
            for col in common_columns:
                merged_df[col] = merged_df[col].astype(str)
                df[col] = df[col].astype(str)
            
            merged_df = pd.merge(merged_df, df, on=list(common_columns), how='outer', suffixes=('', f'_{code}'))
    
    print("Final merged DataFrame:")
    print(merged_df.head())
    
    return merged_df[list(common_columns)]

# Main function to be called from another file
def main(start_month, end_month):
    filtered_df = filter_studies_by_date(start_month, end_month)
    merged_df = merge_sav_files(filtered_df['codigo'])
    
    # Ensure all columns are converted to string to preserve value labels
    merged_df = merged_df.astype(str)
    
    # Save the merged dataframe to a CSV file
    merged_df.to_csv('merged_barometros.csv', index=False)
    print("Merged data saved to merged_barometros.csv")

# Example usage
if __name__ == "__main__":
    start_month = "01/2018"  
    end_month = "07/2024"
    main(start_month, end_month)