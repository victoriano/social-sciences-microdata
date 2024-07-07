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

# Function to merge .sav files
def merge_sav_files(codes):
    merged_df = None
    common_columns = None
    label_dict = {}

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
                df.columns = pd.Series(df.columns).apply(lambda x: x if df.columns.tolist().count(x) == 1 else f"{x}_{df.columns.tolist().index(x)}")
                
                # Replace values with their labels
                for col in df.columns:
                    if col in meta.variable_value_labels:
                        df[col] = df[col].map(meta.variable_value_labels[col])
                
                if merged_df is None:
                    merged_df = df
                    common_columns = set(df.columns)
                else:
                    common_columns &= set(df.columns)
                    merged_df = pd.merge(merged_df, df, on=list(common_columns), how='outer')
    
    return merged_df[list(common_columns)]

# Main function to be called from another file
def main(start_month, end_month):
    filtered_df = filter_studies_by_date(start_month, end_month)
    merged_df = merge_sav_files(filtered_df['codigo'])
    
    # Save the merged dataframe to a CSV file
    merged_df.to_csv('merged_barometros.csv', index=False)
    print("Merged data saved to merged_barometros.csv")

# Example usage
if __name__ == "__main__":
    start_month = "04/24"  
    end_month = "07/24"
    main(start_month, end_month)