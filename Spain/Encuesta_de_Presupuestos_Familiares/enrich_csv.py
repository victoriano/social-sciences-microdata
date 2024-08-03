import pandas as pd
import os

# Define the mappings based on the image
mappings = {
    'SUSPRIN': {1: 'Sí', 6: 'No'},
    'NINODEP': {1: 'Sí', 6: 'No'},
    'HIJODEP': {1: 'Sí', 6: 'No'},
    'ADULTO': {1: 'Sí', 6: 'No'},
    'PERCEP': {1: 'Sí', 6: 'No', 9: 'No Consta' },
    'INTERINP': {
        1.00: 'Menos de 500 euros',
        2.00: 'De 500 a menos de 1000 euros',
        3.00: 'De 1000 a menos de 1500 euros',
        4.00: 'De 1500 a menos de 2000 euros',
        5.00: 'De 2000 a menos de 2500 euros',
        6.00: 'De 2500 a menos de 3000 euros',
        7.00: '3000 euros o más',
        9: 'No consta'
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
    'JORNADA': {1: 'Completa', 2: 'Parcial', 9: 'No Consta'},
    'IMPEXACP': {-9.0: ''},
    'INTERINP': {-9.0: ''},
    'NORDENCO': {99: ''},
    'NORDENPA': {99: ''},
    'NORDENMA': {99: ''},
    'ESTUDIOS': {
        1: 'No sabe leer o escribir o fue menos de 5 años a la escuela',
        2: 'Educación primaria completa o fue a la escuela 5 o más años',
        3: 'ESO, EGB o Bachiller Elemental (con título o sin título)',
        4: 'Bachiller, BUP, COU, Bachiller Superior, FP de Grado Medio',
        5: 'FP de Grado Superior, FPII y equivalentes',
        6: 'Grado de 240 ECTS, Diplomatura, Arquitectura o Ingeniería Técnica',
        7: 'Grado de más de 240 ECTS, Licenciatura, Arquitectura o Ingeniería',
        8: 'Doctorado universitario',
        -9: 'No consta'
    },
    'ESTUDRED': {
        1: 'Inferior a la primera etapa de Educación Secundaria',
        2: 'Primera etapa de Educación secundaria',
        3: 'Segunda etapa de Educación secundaria',
        4: 'Educación superior',
        -9: 'No consta'
    },
    'SITUACT': {
        1: 'Trabajando al menos una hora',
        2: 'Con trabajo del que está ausente (por enfermedad, vacaciones, etc.)',
        3: 'Parado/a',
        4: 'Jubilado/a, retirado/a anticipadamente',
        5: 'Estudiante',
        6: 'Dedicado/a a las labores del hogar',
        7: 'Con incapacidad laboral permanente',
        8: 'Otra situación de inactividad económica',
        -9: 'No consta'
    }
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