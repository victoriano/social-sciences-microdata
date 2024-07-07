import pandas as pd
import pyreadstat

# Define the path to the folder containing the .sav files
barometro_path = 'download_barometros/barometros_raw/MD3450/3450.sav'

# Read the .sav file and print the dictionary values of the first variable
df, meta = pyreadstat.read_sav(barometro_path)
# Get the first variable name
first_variable_name = df.columns[0]

# Print the name of the column
print("First variable name:", first_variable_name)

# Get the value labels for the first variable
value_labels = meta.variable_value_labels.get(first_variable_name, {})

print(value_labels)

# Map the values to their labels
#first_variable_values = df[first_variable_name].map(value_labels).fillna(df[first_variable_name])
# Get unique labels
#unique_labels = set(first_variable_values)

#print(list(unique_labels))