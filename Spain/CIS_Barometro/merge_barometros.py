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
    start_date = datetime.strptime(start_month, "%m/%y")
    end_date = datetime.strptime(end_month, "%m/%y") + relativedelta(months=1) - relativedelta(days=1)
    
    # Filter the dataframe by date range
    filtered_df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    return filtered_df
# ... existing code ...

# Function to merge .sav files
def merge_sav_files(codes):
    merged_df = None
    common_columns = None

    for codigo in codes:
        folder_path = f'download_barometros/barometros_raw/MD{codigo}'
        for file in os.listdir(folder_path):
            if file.endswith('.sav'):
                file_path = os.path.join(folder_path, file)
                df, meta = pyreadstat.read_sav(file_path)
                
                # Check if meta.column_labels is a dictionary or a list
                if isinstance(meta.column_labels, dict):
                    df.columns = [meta.column_labels.get(col, col) for col in df.columns]
                elif isinstance(meta.column_labels, list):
                    df.columns = meta.column_labels
                
                # Ensure unique column names
                original_columns = df.columns.tolist()
                df.columns = pd.Series(df.columns).apply(lambda x: x if df.columns.tolist().count(x) == 1 else f"{x}_{df.columns.tolist().index(x)}")
                
                # Debug print to check column names and value labels
                print(f"Processing file: {file_path}")
                print(f"Original columns: {original_columns}")
                print(f"New columns: {df.columns.tolist()}")
                print(f"Variable value labels keys: {list(meta.variable_value_labels.keys())}")
                
                # Temporarily replace original column names with short ones
                short_to_long_col_map = {short: long for short, long in zip(meta.variable_value_labels.keys(), original_columns)}
                df.rename(columns={v: k for k, v in short_to_long_col_map.items()}, inplace=True)
                
                # Replace values with their labels using short column names
                for short_col in meta.variable_value_labels.keys():
                    if short_col in df.columns:
                        print(f"Applying mapping to column: {short_col}")
                        df[short_col] = df[short_col].map(meta.variable_value_labels[short_col])
                        # Debug print to check the mapping
                        print(f"Mapping applied to column: {short_col}")
                        print(df[short_col].head())
                    else:
                        print(f"No mapping found for column: {short_col}")
                
                # Revert to original long column names
                df.rename(columns=short_to_long_col_map, inplace=True)
                
                # Convert all columns to string to avoid type mismatch during merge
                df = df.astype(str)
                
                if merged_df is None:
                    merged_df = df
                    common_columns = set(df.columns)
                else:
                    common_columns &= set(df.columns)
                    merged_df = pd.merge(merged_df, df, on=list(common_columns), how='outer')
    
    # Debug print to check the final merged DataFrame
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
    start_month = "04/24"  
    end_month = "07/24"
    main(start_month, end_month)