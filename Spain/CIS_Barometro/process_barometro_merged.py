import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('filtered_barometros_files.csv')

# Create a dictionary to map Spanish month names to numbers
month_map = {
    'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
    'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
    'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
}

# Create a new column with the numeric month equivalent
df['Mes_numero'] = df['Mes de realización'].map(month_map)

# Create the date_of_study column
df['date_of_study'] = df['Mes_numero'] + '/' + df['Año de realización'].astype(str) + '/01'

# Convert date_of_study to datetime
df['date_of_study'] = pd.to_datetime(df['date_of_study'], format='%m/%Y/%d', errors='coerce')

# Create 'Principales Problemas' as a list of non-null problems
df['Principales Problemas'] = df.apply(lambda row: [prob for prob in [row['Primer problema'], row['Segundo problema'], row['Tercer problema']] if pd.notna(prob)], axis=1)

# Define the groups and their variables
groups = {
    "Estudio": [
        "Estudio", "Código del estudio", "Año de realización", 
        "Mes de realización", "Número de registro"
    ],
    "Demografía": [
        "Sexo de la persona entrevistada", "Edad de la persona entrevistada",
        "Nacionalidad de la persona entrevistada", "Religiosidad de la persona entrevistada",
        "Estado civil de la persona entrevistada", "Estudios de la persona entrevistada",
        "Situación laboral de la persona entrevistada", 
        "Clase social subjetiva de la persona entrevistada",
        "Nivel de ingresos netos del hogar", "Escala de autoubicación ideológica (1-10)",
        "Provincia", "Municipio", "Comunidad autónoma", "Tamaño de municipio"
    ],
    "Opiniones": [
        "Principales Problemas",
        "Primer problema", "Segundo problema", "Tercer problema",
        "Valoración de la situación económica personal actual",
        "Valoración de la situación económica general de España"
    ],
    "Voto": [
        "Intención de voto en unas supuestas elecciones generales [recodificada]",
        "Recuerdo de voto en las elecciones generales de 2023",
        "Partido político que considera más cercano a sus ideas",
        "Preferencia personal como presidente del Gobierno central"
    ]
}

# Function to check if a column exists and has null values
def check_column(column):
    return column in df.columns and df[column].isnull().any()

# Process each group
for group_name, variables in groups.items():
    print(f"\n{group_name}:")
    for variable in variables:
        if variable in df.columns:
            null_count = df[variable].isnull().sum()
            print(f"  {variable} - Null count: {null_count}")
        else:
            print(f"  {variable} - Not found in dataset")

# Flatten the list of variables from all groups
all_variables = [var for group in groups.values() for var in group]

# Get all columns from the DataFrame
all_columns = df.columns.tolist()

# Order the columns based on the groups, then add the remaining columns
ordered_columns = ['date_of_study', 'Mes_numero'] + [var for var in all_variables if var in all_columns]
remaining_columns = [col for col in all_columns if col not in ordered_columns]
ordered_columns.extend(remaining_columns)

# Reorder the DataFrame columns
df_ordered = df[ordered_columns]

# Clean and convert the "Edad de la persona entrevistada" column
if "Edad de la persona entrevistada" in df_ordered.columns:
    df_ordered["Edad de la persona entrevistada"] = pd.to_numeric(df_ordered["Edad de la persona entrevistada"].astype(str).str.replace(',', '.'), errors='coerce')

# Clean and convert the "Ponderación autonómica" column
if "Ponderación autonómica" in df_ordered.columns:
    df_ordered["Ponderación autonómica"] = pd.to_numeric(df_ordered["Ponderación autonómica"].astype(str).str.replace(',', '.'), errors='coerce')

# Convert all object columns to string type, except 'Principales Problemas'
object_columns = df_ordered.select_dtypes(include=['object']).columns
for col in object_columns:
    if col != 'Principales Problemas':
        df_ordered[col] = df_ordered[col].astype(str)

# Save the filtered and ordered DataFrame as a Parquet file
output_file = 'processed_barometros.parquet'
df_ordered.to_parquet(output_file, index=False)
print(f"\nProcessed data saved to {output_file}")

# Print missing columns from the defined groups
missing_columns = set(all_variables) - set(all_columns)
if missing_columns:
    print("\nMissing columns from defined groups:")
    for column in missing_columns:
        print(column)

# Find columns with no null values
columns_without_nulls = df_ordered.columns[df_ordered.notnull().all()].tolist()

# Find columns with null values
columns_with_nulls = df_ordered.columns[df_ordered.isnull().any()].tolist()

# Print the columns without null values
print("\nColumns without any null values:")
for column in columns_without_nulls:
    print(column)
# Print the total count of columns without null values
print(f"\nTotal number of columns without null values: {len(columns_without_nulls)}")

# Print the columns with null values
print("\nColumns with null values:")
for column in columns_with_nulls:
    print(column)

# Print the total count of columns with null values
print(f"\nTotal number of columns with null values: {len(columns_with_nulls)}")