import os
import pandas as pd
from glob import glob

def merge_files(file_pattern):
    all_files = glob(f"../download_epfs_since2016/parquet_raw_files/**/{file_pattern}", recursive=True)
    print(f"Found {len(all_files)} files matching pattern: {file_pattern}")
    df_list = [pd.read_parquet(file) for file in all_files]
    merged_df = pd.concat(df_list, ignore_index=True)
    print(f"Merged dataframe shape: {merged_df.shape}")
    return merged_df

def main():
    print("Starting data merging process...")

    # Merge gastos files
    print("Merging gastos files...")
    gastos_df = merge_files("*_EPFgastos_*.parquet")
    
    # Merge hogar files
    print("Merging hogar files...")
    hogar_df = merge_files("*_EPFhogar_*.parquet")
    
    # Merge mhogar files
    print("Merging mhogar files...")
    mhogar_df = merge_files("*_EPFmhogar_*.parquet")
    
    print("Joining gastos and hogar dataframes...")
    # Join gastos and hogar dataframes
    columns_to_keep = [
        'CCAA', 'NUTS1', 'DENSIDAD', 'NMIEMB', 'TAMANO', 'TIPHOGAR1', 'EDADSP',
        'SEXOSP', 'PAISNACSP', 'NACIONASP', 'ECIVILLEGALSP', 'UNIONSP',
        'CONVIVENCIASP', 'ESTUDIOSSP', 'SITUACTSP', 'IMPEXACPSP', 'INTERINPSP',
        'OCUPA', 'OCUPARED', 'ACTESTB', 'ACTESTBRED', 'SITPROF', 'SECTOR',
        'CONTRATO', 'TIPOCONT', 'SITSOCI', 'SITSOCIRE', 'REGTEN', 'TIPOEDIF',
        'ZONARES', 'TIPOCASA', 'NHABIT', 'ANNOCON', 'SUPERF', 'AGUACALI',
        'FUENAGUA', 'CALEF', 'IMPEXAC', 'INTERIN', 'COMIMH'
    ]
    
    merged_df = pd.merge(
        gastos_df,
        hogar_df[['ANOENC', 'NUMERO'] + columns_to_keep],
        on=['ANOENC', 'NUMERO'],
        how='left'
    )
    
    print("Converting 'COMIMH' to float...")
    merged_df['COMIMH'] = pd.to_numeric(merged_df['COMIMH'], errors='coerce')

    print("Checking for other columns that might need conversion...")
    for col in merged_df.columns:
        if merged_df[col].dtype == 'object':
            try:
                merged_df[col] = pd.to_numeric(merged_df[col], errors='raise')
                print(f"Successfully converted column {col} to numeric.")
            except ValueError:
                print(f"Column {col} contains non-numeric data and will be left as is.")

    # Save the merged dataframe
    output_path = "../gastos_master.parquet"
    print(f"Saving merged data to {output_path}...")
    merged_df.to_parquet(output_path, index=False)
    print(f"Merged data saved successfully. Final dataframe shape: {merged_df.shape}")

if __name__ == "__main__":
    main()