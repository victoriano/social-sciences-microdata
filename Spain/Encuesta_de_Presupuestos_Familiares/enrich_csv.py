import pandas as pd
import os

# Define the mappings based on the image
mappings = {
    'SUSPRIN': {1: 'Sí', 6: 'No'},
    'PERCEP': {1: 'Sí', 6: 'No', 9: 'No Consta' },
    'INTERINP': {
        1: 'Menos de 500 euros',
        2: 'De 500 a menos de 1000 euros',
        3: 'De 1000 a menos de 1500 euros',
        4: 'De 1500 a menos de 2000 euros',
        5: 'De 2000 a menos de 2500 euros',
        6: 'De 2500 a menos de 3000 euros',
        7: '3000 euros o más',
        9: 'No Consta'
    },
    'CATEGMH': {
        1: 'Miembro del hogar',
        2: 'Servicio doméstico',
        3: 'Huésped',
        4: 'Invitado',
        9: 'No Consta'
    },
    'RELASP': {
        1: 'Sustentador principal',
        2: 'Cónyuge o pareja',
        3: 'Hijo del sustentador principal y/o pareja',
        4: 'Padre o madre del sustentador principal',
        5: 'Padre o madre del cónyuge o pareja',
        6: 'Otra situación (con parentesco distinto de los anteriores y sin ningún parentesco)'
    },
    'SEXO': {1: 'Hombre', 6: 'Mujer', -9: 'No Consta'},

    'NACIONA': {
        1: 'Solo española',
        2: 'Solo extranjera',
        3: 'Española y extranjera',
        9: 'No Consta'
    },

    'PAISNACIM': {
        1: 'España',
        2: 'Resto de la Unión Europea (27 países)',
        3: 'Resto de Europa',
        4: 'Resto del mundo',
        9: 'No Consta'
    },

    'PAISNACION': {
        1: 'España',
        2: 'Resto de la Unión Europea (27 países)',
        3: 'Resto de Europa',
        4: 'Resto del mundo',
        9: 'No Consta'
    },

    'PAISPADRE': {
        1: 'España',
        2: 'Resto de la Unión Europea (27 países)',
        3: 'Resto de Europa',
        4: 'Resto del mundo',
        9: 'No Consta'
    },

    'PAISMADRE': {
        1: 'España',
        2: 'Resto de la Unión Europea (27 países)',
        3: 'Resto de Europa',
        4: 'Resto del mundo',
        9: 'No Consta'
    },

    'UNION': {
        1: 'Casado',
        2: 'Unión de hecho registrada',
        3: 'Pareja de hecho sin registrar',
        9: 'No Consta'
    },
    'CONVIVENCIA': {
        1: 'Conviviendo con su cónyuge',
        2: 'Conviviendo con una pareja de hecho',
        3: 'No conviviendo en pareja',
        9: 'No Consta'
    },
    'ECIVILLEGAL': {
        1: 'Soltero',
        2: 'Casado',
        3: 'Viudo',
        4: 'Separado',
        5: 'Divorciado',
        9: 'No Consta'
    },
    'SITURES': {1: 'Presente', 6: 'Ausente'},

    'SITURED': {1: 'Activo', 2: 'Inactivo', 9: 'No Consta'},
    'OCU': {1: 'Ocupado', 2: 'No ocupado', 9: 'No Consta'},
    'JORNADA': {1: 'Completa', 6: 'Parcial', 9: 'No Consta'},
    'IMPEXACP': {-9.0: ''},
    'INTERINP': {-9.0: ''},
    'NORDENCO': {99: ''},
    'NORDENPA': {99: ''},
    'NORDENMA': {99: ''}

}

def enrich_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Apply mappings to each column
    for column, mapping in mappings.items():
        if column in df.columns:
            df[column] = df[column].map(mapping).fillna(df[column])
    
    # Write the enriched DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Enriched file saved as {output_file}")

# Directory containing the CSV files
directory = '.'

# Process hogares_2023.csv
input_file = os.path.join(directory, 'miembros_2023.csv')
output_file = os.path.join(directory, 'miembros_2023_enriched.csv')

if os.path.exists(input_file):
    enrich_csv(input_file, output_file)
else:
    print(f"File {input_file} not found.")

print("Enrichment process completed.")