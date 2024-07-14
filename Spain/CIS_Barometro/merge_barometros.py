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

def convert_sav_to_csv(sav_path):
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
    
    return df_labeled

def merge_sav_files(file_codes, output_file):
    first_file = True
    
    for code in file_codes:
        sav_path = f'download_barometros/barometros_raw/MD{code}/{code}.sav'
        print(f"Processing file: {sav_path}")
        
        # Convert SAV to DataFrame
        df = convert_sav_to_csv(sav_path)
        
        # Rename duplicate columns
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        df.columns = [f'{col}_{i}' if df.columns.tolist().count(col) > 1 else col for i, col in enumerate(df.columns)]
        
        # Ensure all columns are converted to string to preserve value labels
        df = df.astype(str)
        
        if first_file:
            df.to_csv(output_file, index=False, mode='w')
            first_file = False
        else:
            # Read existing CSV with dtype=object to treat all columns as strings
            existing_df = pd.read_csv(output_file, dtype=object, low_memory=False)
            
            # Merge DataFrames
            merged_df = pd.concat([existing_df, df], axis=0, ignore_index=True)
            
            # Write merged DataFrame back to CSV
            merged_df.to_csv(output_file, index=False, mode='w')
        
        print(f"Merged {code} into {output_file}")

# Update the filter_columns_with_nans function as well
def filter_columns_with_nans(input_file, output_file, threshold=0.5):
    df = pd.read_csv(input_file, dtype=object, low_memory=False)
    
    # Calculate the percentage of NaN values in each column
    nan_percentages = df.isnull().mean()
    
    # Filter columns based on the threshold
    columns_to_keep = nan_percentages[nan_percentages < threshold].index.tolist()
    
    # Create a new DataFrame with only the kept columns
    filtered_df = df[columns_to_keep]
    
    # Save the filtered DataFrame
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")

# Main function to be called from another file
def main(start_month, end_month, filter_nans=False, nan_threshold=0.5):
    filtered_df = filter_studies_by_date(start_month, end_month)
    
    output_file = 'merged_barometros_files.csv'
    merge_sav_files(filtered_df['codigo'], output_file)
    
    if filter_nans:
        filtered_output_file = 'filtered_barometros_files.csv'
        filter_columns_with_nans(output_file, filtered_output_file, nan_threshold)
    else:
        print(f"Merged data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    start_month = "01/2023"
    end_month = "07/2024"
    main(start_month, end_month, filter_nans=True, nan_threshold=0.5)