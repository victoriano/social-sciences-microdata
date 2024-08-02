import pandas as pd
import numpy as np

def read_fixed_width_file(file_path, col_specs, col_names):
    return pd.read_fwf(file_path, colspecs=col_specs, names=col_names, encoding='latin-1')

def convert_hogares():
    col_specs = [
        (0, 4), (4, 6), (6, 8), (8, 10), (10, 11), (11, 13), (13, 14), (14, 15),
        (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22),
        (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29),
        (29, 37), (37, 45), (45, 53), (53, 61), (61, 69), (69, 77), (77, 85),
        (85, 93), (93, 101), (101, 109), (109, 117), (117, 125), (125, 133)
    ]
    col_names = [
        'ANOENC', 'CCAA', 'PROV', 'MUNI', 'DISTR', 'SECCION', 'VIVI', 'NIVEL',
        'NHOGARES', 'NMIEMB', 'NMIEMB614', 'NMIEMB1415', 'FACTOREH', 'TIPHOGAR',
        'NMESENC', 'SUSTENT', 'IMPEXAC', 'FACTORHA', 'FACTORHM', 'FACTORT',
        'NPERIODO', 'NMES', 'GASTMON', 'GASTNOMON', 'GASTOT', 'IMPUTALQ',
        'GASTMON_NM', 'GASTNOMON_NM', 'GASTOT_NM', 'GASTMON_R', 'GASTNOMON_R',
        'GASTOT_R', 'GASTMON_NM_R', 'GASTNOMON_NM_R', 'GASTOT_NM_R'
    ]
    
    df = read_fixed_width_file('Fichero de usuario de hogar a2023IMPAJUSTE.txt', col_specs, col_names)
    df.to_csv('hogares_2023.csv', index=False)

def convert_gastos():
    col_specs = [
        (0, 4), (4, 6), (6, 8), (8, 10), (10, 11), (11, 13), (13, 14), (14, 15),
        (15, 16), (16, 24), (24, 30), (30, 38), (38, 46), (46, 54), (54, 62),
        (62, 70), (70, 78)
    ]
    col_names = [
        'ANOENC', 'CCAA', 'PROV', 'MUNI', 'DISTR', 'SECCION', 'VIVI', 'NIVEL',
        'NHOGARES', 'CODIGO', 'CANTIDAD', 'VALORGASTO', 'FACTORGC', 'FACTORGA',
        'FACTORGM', 'VALORGASTO_R', 'FACTORGC_R'
    ]
    
    df = read_fixed_width_file('Fichero de usuario de gastos a2023AJUSTE.txt', col_specs, col_names)
    df.to_csv('gastos_2023.csv', index=False)

def convert_miembros():
    col_specs = [
        (0, 4), (4, 6), (6, 8), (8, 10), (10, 11), (11, 13), (13, 14), (14, 15),
        (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22),
        (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29),
        (29, 30), (30, 31), (31, 32), (32, 33), (33, 34), (34, 35), (35, 36),
        (36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43),
        (43, 44)
    ]
    col_names = [
        'ANOENC', 'CCAA', 'PROV', 'MUNI', 'DISTR', 'SECCION', 'VIVI', 'NIVEL',
        'NHOGARES', 'NORDEN', 'FACTORPM', 'FACTORPA', 'FACTORP', 'EDAD', 'SEXO',
        'NACI', 'ESTUD', 'RELA', 'OCUPA', 'SITUA', 'SECTOR', 'TIPOCONT',
        'TIPOCON2', 'TASAOCU', 'ESTUDIOS', 'IMPEXAC', 'FACTORPMA', 'FACTORPAA',
        'FACTORPA2', 'NPERIODO', 'NMES', 'NMESENC', 'FACTORPT', 'FACTORPMT',
        'FACTORPAT'
    ]
    
    df = read_fixed_width_file('Fichero de usuario de miembros a2023IMPAJUSTE', col_specs, col_names)
    df.to_csv('miembros_2023.csv', index=False)

if __name__ == "__main__":
    convert_hogares()
    convert_gastos()
    convert_miembros()
    print("Conversión completada. Se han creado los archivos CSV correspondientes.")