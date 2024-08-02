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
        (0, 4), (4, 6), (6, 8), (8, 11), (11, 13), (13, 15), (15, 17),
        (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
        (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29),
        (29, 30), (30, 31), (31, 32), (32, 33), (33, 34), (34, 35),
        (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41),
        (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47),
        (47, 48), (48, 49), (49, 50), (50, 51), (51, 52), (52, 53),
        (53, 54), (54, 55), (55, 56), (56, 57), (57, 58), (58, 59),
        (59, 60), (60, 61), (61, 62), (62, 63), (63, 64), (64, 65),
        (65, 66), (66, 67), (67, 68), (68, 69), (69, 70), (70, 71),
        (71, 72), (72, 73), (73, 74), (74, 75), (75, 76), (76, 77),
        (77, 78), (78, 79), (79, 80), (80, 81), (81, 82), (82, 83),
        (83, 84), (84, 85), (85, 86), (86, 87), (87, 88), (88, 89),
        (89, 90), (90, 91), (91, 92), (92, 93), (93, 94), (94, 95),
        (95, 96), (96, 97), (97, 98), (98, 99), (99, 100), (100, 101),
        (101, 102), (102, 103), (103, 104), (104, 105), (105, 106),
        (106, 107), (107, 108), (108, 109), (109, 110), (110, 111),
        (111, 112), (112, 113), (113, 114), (114, 115), (115, 116),
        (116, 117), (117, 118), (118, 119), (119, 120), (120, 121),
        (121, 122), (122, 123), (123, 124), (124, 125), (125, 126),
        (126, 127), (127, 128), (128, 129), (129, 130), (130, 131),
        (131, 132), (132, 133), (133, 134), (134, 135), (135, 136),
        (136, 137), (137, 138), (138, 139), (139, 140), (140, 141),
        (141, 142), (142, 143), (143, 144), (144, 145), (145, 146),
        (146, 147), (147, 148), (148, 149), (149, 150), (150, 151),
        (151, 152), (152, 153), (153, 154), (154, 155), (155, 156),
        (156, 157), (157, 158), (158, 159), (159, 160), (160, 161),
        (161, 162), (162, 163), (163, 164), (164, 165), (165, 166),
        (166, 167), (167, 168), (168, 169), (169, 170), (170, 171),
        (171, 172), (172, 173), (173, 174), (174, 175), (175, 176),
        (176, 177), (177, 178), (178, 179), (179, 180)
    ]
    
    # Add more column specifications to match the number of col_names
    # You'll need to determine the correct column widths for these additional columns
    for i in range(len(col_specs), 185):
        last_end = col_specs[-1][1]
        col_specs.append((last_end, last_end + 1))  # Assuming 1-character width for each new column
    
    col_names = [
        'ANOENC', 'CCAA', 'PROV', 'MUNI', 'DISTR', 'SECCION', 'VIVI',
        'NIVEL', 'NORDEN', 'SEXO', 'EDAD', 'NACIONP', 'ESTCIVI',
        'PARESCO', 'ESTUDIO', 'OCUPA', 'SITUA', 'SECTOR', 'TIPOCONT',
        'TIPOCON2', 'JORNADA', 'HORASTR', 'INGRE1', 'INGRE2', 'INGRE3',
        'INGRE4', 'INGRE5', 'INGRE6', 'INGRE7', 'INGRE8', 'INGRE9',
        'INGRE10', 'INGRE11', 'INGRE12', 'INGRE13', 'INGRE14', 'INGRE15',
        'INGRE16', 'INGRE17', 'INGRE18', 'INGRE19', 'INGRE20', 'INGRE21',
        'INGRE22', 'INGRE23', 'INGRE24', 'INGRE25', 'INGRE26', 'INGRE27',
        'INGRE28', 'INGRE29', 'INGRE30', 'INGRE31', 'INGRE32', 'INGRE33',
        'INGRE34', 'INGRE35', 'INGRE36', 'INGRE37', 'INGRE38', 'INGRE39',
        'INGRE40', 'INGRE41', 'INGRE42', 'INGRE43', 'INGRE44', 'INGRE45',
        'INGRE46', 'INGRE47', 'INGRE48', 'INGRE49', 'INGRE50', 'INGRE51',
        'INGRE52', 'INGRE53', 'INGRE54', 'INGRE55', 'INGRE56', 'INGRE57',
        'INGRE58', 'INGRE59', 'INGRE60', 'INGRE61', 'INGRE62', 'INGRE63',
        'INGRE64', 'INGRE65', 'INGRE66', 'INGRE67', 'INGRE68', 'INGRE69',
        'INGRE70', 'INGRE71', 'INGRE72', 'INGRE73', 'INGRE74', 'INGRE75',
        'INGRE76', 'INGRE77', 'INGRE78', 'INGRE79', 'INGRE80', 'INGRE81',
        'INGRE82', 'INGRE83', 'INGRE84', 'INGRE85', 'INGRE86', 'INGRE87',
        'INGRE88', 'INGRE89', 'INGRE90', 'INGRE91', 'INGRE92', 'INGRE93',
        'INGRE94', 'INGRE95', 'INGRE96', 'INGRE97', 'INGRE98', 'INGRE99',
        'INGRE100', 'INGRE101', 'INGRE102', 'INGRE103', 'INGRE104',
        'INGRE105', 'INGRE106', 'INGRE107', 'INGRE108', 'INGRE109',
        'INGRE110', 'INGRE111', 'INGRE112', 'INGRE113', 'INGRE114',
        'INGRE115', 'INGRE116', 'INGRE117', 'INGRE118', 'INGRE119',
        'INGRE120', 'INGRE121', 'INGRE122', 'INGRE123', 'INGRE124',
        'INGRE125', 'INGRE126', 'INGRE127', 'INGRE128', 'INGRE129',
        'INGRE130', 'INGRE131', 'INGRE132', 'INGRE133', 'INGRE134',
        'INGRE135', 'INGRE136', 'INGRE137', 'INGRE138', 'INGRE139',
        'INGRE140', 'INGRE141', 'INGRE142', 'INGRE143', 'INGRE144',
        'INGRE145', 'INGRE146', 'INGRE147', 'INGRE148', 'INGRE149',
        'INGRE150', 'INGRE151', 'INGRE152', 'INGRE153', 'INGRE154',
        'INGRE155', 'INGRE156', 'INGRE157', 'INGRE158', 'INGRE159',
        'INGRE160', 'INGRE161', 'INGRE162', 'INGRE163'
    ]
    
    # Ensure that col_specs and col_names have the same length
    assert len(col_specs) == len(col_names), f"Length mismatch: col_specs ({len(col_specs)}) != col_names ({len(col_names)})"
    
    # Update the file name to include the correct extension
    file_name = 'Fichero de usuario de miembros a2023IMPAJUSTE.txt'
    
    df = read_fixed_width_file(file_name, col_specs, col_names)
    df.to_csv('miembros_2023.csv', index=False)

if __name__ == "__main__":
    convert_hogares()
    convert_gastos()
    convert_miembros()
    print("Conversión completada. Se han creado los archivos CSV correspondientes.")