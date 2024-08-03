import pandas as pd
import numpy as np

def read_fixed_width_file(file_path, col_specs, col_names):
    return pd.read_fwf(file_path, colspecs=col_specs, names=col_names, encoding='latin-1')

def convert_hogares():
    col_specs = [
        (0, 4),    # ANOENC
        (4, 9),    # NUMERO
        (9, 11),   # CCAA
        (11, 12),  # NUTS1
        (12, 13),  # CAPROV
        (13, 14),  # TAMAMU
        (14, 15),  # DENSIDAD
        (15, 16),  # CLAVE
        (16, 17),  # CLATEO
        (17, 28),  # FACTOR
        (28, 30),  # NMIEMB
        (30, 32),  # TAMANO
        (32, 34),  # NMIEMSD
        (34, 36),  # NMIEMHU
        (36, 38),  # NMIEMIN
        (38, 40),  # NMIEM1
        (40, 42),  # NMIEM2
        (42, 44),  # NMIEM3
        (44, 46),  # NMIEM4
        (46, 48),  # NMIEM5
        (48, 50),  # NMIEM6
        (50, 52),  # NMIEM7
        (52, 54),  # NMIEM8
        (54, 56),  # NMIEM9
        (56, 58),  # NMIEM10
        (58, 60),  # NMIEM11
        (60, 62),  # NMIEM12
        (62, 64),  # NMIEM13
        (64, 66),  # NUMACTI
        (66, 68),  # NUMINACTI
        (68, 70),  # NUMOCU
        (70, 72),  # NUMNOCU
        (72, 74),  # NUMESTU
        (74, 76),  # NUMNOESTU
        (76, 78),  # NNINOSD
        (78, 80),  # NHIJOSD
        (80, 83),  # UC1
        (83, 86),  # UC2
        (86, 88),  # PF2TEO
        (88, 90),  # PF2RECO
        (90, 92),  # TIPHOGAR1
        (92, 94),  # TIPHOGAR2
        (94, 96),  # TIPHOGAR3
        (96, 98),  # TIPHOGAR4
        (98, 100), # TIPHOGAR5
        (100, 102), # TIPHOGAR6
        (102, 104), # TIPHOGAR7
        (104, 106), # TIPHOGAR8
        (106, 108), # TIPHOGAR9
        (108, 110), # TIPHOGAR10
        (110, 112), # TIPHOGAR11
        (112, 114), # SITUOCUHOG
        (114, 116), # SITUACTHOG
        (116, 118), # NORDENSP
        (118, 120), # EDADSP
        (120, 122), # SEXOSP
        (122, 124), # PAISNACSP
        (124, 126), # NACIONASP
        (126, 128), # PAISSP
        (128, 130), # SITURESSP
        (130, 132), # ECIVILLEGALSP
        (132, 134), # NORDENCOSP
        (134, 136), # UNIONSP
        (136, 138), # CONVIVENCIASP
        (138, 140), # NORDENPASP
        (140, 142), # PAISPADRESP
        (142, 144), # NORDENMASP
        (144, 146), # PAISMADRESP
        (146, 148), # ESTUDIOSSP
        (148, 150), # ESTUDREDSP
        (150, 152), # SITUACTSP
        (152, 154), # SITUREDSP
        (154, 156), # OCUSP
        (156, 158), # JORNADASP
        (158, 160), # PERCEPSP
        (160, 165), # IMPEXACPSP
        (165, 167), # INTERINPSP
        (167, 169), # TRABAJO
        (169, 171), # OCUPA
        (171, 173), # OCUPARED
        (173, 175), # ACTESTB
        (175, 177), # ACTESTBRED
        (177, 179), # SITPROF
        (179, 181), # SECTOR
        (181, 183), # CONTRATO
        (183, 185), # TIPOCONT
        (185, 187), # SITSOCI
        (187, 189), # SITSOCIRE
        (189, 190), # REGTEN
        (190, 192), # TIPOEDIF
        (192, 194), # ZONARES
        (194, 196), # TIPOCASA
        (196, 198), # NHABIT
        (198, 200), # ANNOCON
        (200, 203), # SUPERF
        (203, 205), # AGUACALI
        (205, 207), # FUENAGUA
        (207, 209), # CALEF
        (209, 211), # FUENCALE
        (211, 212), # DISPOSIOV
        (212, 213), # NUMOVD
        (213, 215), # REGTENV1
        (215, 217), # MESESV1
        (217, 219), # DIASV1
        (219, 221), # AGUACV1
        (221, 223), # FUENACV1
        (223, 225), # CALEFV1
        (225, 227), # FUENCAV1
        (227, 229), # REGTENV2
        (229, 231), # MESESV2
        (231, 233), # DIASV2
        (233, 235), # AGUACV2
        (235, 237), # FUENACV2
        (237, 239), # CALEFV2
        (239, 241), # FUENCAV2
        (241, 243), # REGTENV3
        (243, 245), # MESESV3
        (245, 247), # DIASV3
        (247, 249), # AGUACV3
        (249, 251), # FUENACV3
        (251, 253), # CALEFV3
        (253, 255), # FUENCAV3
        (255, 257), # REGTENV4
        (257, 259), # MESESV4
        (259, 261), # DIASV4
        (261, 263), # AGUACV4
        (263, 265), # FUENACV4
        (265, 267), # CALEFV4
        (267, 269), # FUENCAV4
        (269, 271), # REGTENV5
        (271, 273), # MESESV5
        (273, 275), # DIASV5
        (275, 277), # AGUACV5
        (277, 279), # FUENACV5
        (279, 281), # CALEFV5
        (281, 283), # FUENCAV5
        (283, 285), # REGTENV6
        (285, 287), # MESESV6
        (287, 289), # DIASV6
        (289, 291), # AGUACV6
        (291, 293), # FUENACV6
        (293, 295), # CALEFV6
        (295, 297), # FUENCAV6
        (297, 299), # REGTENV7
        (299, 301), # MESESV7
        (301, 303), # DIASV7
        (303, 305), # AGUACV7
        (305, 307), # FUENACV7
        (307, 309), # CALEFV7
        (309, 311), # FUENCAV7
        (311, 313), # REGTENV8
        (313, 315), # MESESV8
        (315, 317), # DIASV8
        (317, 319), # AGUACV8
        (319, 321), # FUENACV8
        (321, 323), # CALEFV8
        (323, 325), # FUENCAV8
        (325, 327), # REGTENV9
        (327, 329), # MESESV9
        (329, 331), # DIASV9
        (331, 333), # AGUACV9
        (333, 335), # FUENACV9
        (335, 337), # CALEFV9
        (337, 339), # FUENCAV9
        (339, 355), # GASTOT
        (355, 360), # IMPUTGAS
        (360, 376), # GASTMON
        (376, 389), # GASTNOM1
        (389, 402), # GASTNOM2
        (402, 415), # GASTNOM3
        (415, 428), # GASTNOM4
        (428, 430), # CAPROP
        (430, 432), # CAJENA
        (432, 434), # PENSIO
        (434, 436), # DESEM
        (436, 438), # OTRSUB
        (438, 440), # RENTAS
        (440, 442), # OTROIN
        (442, 444), # FUENPRIN
        (444, 446), # FUENPRINRED
        (446, 451), # IMPEXAC
        (451, 453), # INTERIN
        (453, 455), # NUMPERI
        (455, 458), # COMIMH
        (458, 461), # COMISD
        (461, 464), # COMIHU
        (464, 467), # COMIINV
        (467, 470)  # COMITOT
    ]
    
    col_names = [
        'ANOENC', 'NUMERO', 'CCAA', 'NUTS1', 'CAPROV', 'TAMAMU', 'DENSIDAD', 'CLAVE',
        'CLATEO', 'FACTOR', 'NMIEMB', 'TAMANO', 'NMIEMSD', 'NMIEMHU', 'NMIEMIN',
        'NMIEM1', 'NMIEM2', 'NMIEM3', 'NMIEM4', 'NMIEM5', 'NMIEM6', 'NMIEM7',
        'NMIEM8', 'NMIEM9', 'NMIEM10', 'NMIEM11', 'NMIEM12', 'NMIEM13', 'NUMACTI',
        'NUMINACTI', 'NUMOCU', 'NUMNOCU', 'NUMESTU', 'NUMNOESTU', 'NNINOSD', 'NHIJOSD',
        'UC1', 'UC2', 'PF2TEO', 'PF2RECO', 'TIPHOGAR1', 'TIPHOGAR2', 'TIPHOGAR3',
        'TIPHOGAR4', 'TIPHOGAR5', 'TIPHOGAR6', 'TIPHOGAR7', 'TIPHOGAR8', 'TIPHOGAR9',
        'TIPHOGAR10', 'TIPHOGAR11', 'SITUOCUHOG', 'SITUACTHOG', 'NORDENSP', 'EDADSP',
        'SEXOSP', 'PAISNACSP', 'NACIONASP', 'PAISSP', 'SITURESSP', 'ECIVILLEGALSP',
        'NORDENCOSP', 'UNIONSP', 'CONVIVENCIASP', 'NORDENPASP', 'PAISPADRESP',
        'NORDENMASP', 'PAISMADRESP', 'ESTUDIOSSP', 'ESTUDREDSP', 'SITUACTSP',
        'SITUREDSP', 'OCUSP', 'JORNADASP', 'PERCEPSP', 'IMPEXACPSP', 'INTERINPSP',
        'TRABAJO', 'OCUPA', 'OCUPARED', 'ACTESTB', 'ACTESTBRED', 'SITPROF', 'SECTOR',
        'CONTRATO', 'TIPOCONT', 'SITSOCI', 'SITSOCIRE', 'REGTEN', 'TIPOEDIF',
        'ZONARES', 'TIPOCASA', 'NHABIT', 'ANNOCON', 'SUPERF', 'AGUACALI', 'FUENAGUA',
        'CALEF', 'FUENCALE', 'DISPOSIOV', 'NUMOVD', 'REGTENV1', 'MESESV1', 'DIASV1',
        'AGUACV1', 'FUENACV1', 'CALEFV1', 'FUENCAV1', 'REGTENV2', 'MESESV2', 'DIASV2',
        'AGUACV2', 'FUENACV2', 'CALEFV2', 'FUENCAV2', 'REGTENV3', 'MESESV3', 'DIASV3',
        'AGUACV3', 'FUENACV3', 'CALEFV3', 'FUENCAV3', 'REGTENV4', 'MESESV4', 'DIASV4',
        'AGUACV4', 'FUENACV4', 'CALEFV4', 'FUENCAV4', 'REGTENV5', 'MESESV5', 'DIASV5',
        'AGUACV5', 'FUENACV5', 'CALEFV5', 'FUENCAV5', 'REGTENV6', 'MESESV6', 'DIASV6',
        'AGUACV6', 'FUENACV6', 'CALEFV6', 'FUENCAV6', 'REGTENV7', 'MESESV7', 'DIASV7',
        'AGUACV7', 'FUENACV7', 'CALEFV7', 'FUENCAV7', 'REGTENV8', 'MESESV8', 'DIASV8',
        'AGUACV8', 'FUENACV8', 'CALEFV8', 'FUENCAV8', 'REGTENV9', 'MESESV9', 'DIASV9',
        'AGUACV9', 'FUENACV9', 'CALEFV9', 'FUENCAV9', 'GASTOT', 'IMPUTGAS', 'GASTMON',
        'GASTNOM1', 'GASTNOM2', 'GASTNOM3', 'GASTNOM4', 'CAPROP', 'CAJENA', 'PENSIO',
        'DESEM', 'OTRSUB', 'RENTAS', 'OTROIN', 'FUENPRIN', 'FUENPRINRED', 'IMPEXAC',
        'INTERIN', 'NUMPERI', 'COMIMH', 'COMISD', 'COMIHU', 'COMIINV', 'COMITOT'
    ]
    
    df = read_fixed_width_file('Fichero de usuario de hogar a2023IMPAJUSTE.txt', col_specs, col_names)
    df.to_csv('hogares_2023.csv', index=False)

def convert_gastos():
    col_specs = [
        (0, 4),   # ANOENC
        (4, 9),   # NUMERO
        (9, 14),  # CODIGO
        (14, 29), # GASTO
        (29, 34), # PORCENDES
        (34, 39), # PORCENIMP
        (39, 51), # CANTIDAD
        (51, 66), # GASTOMON
        (66, 79), # GASTNOM1
        (79, 92), # GASTNOM2
        (92, 105),# GASTNOM3
        (105, 118),# GASTNOM4
        (118, 131),# GASTNOM5
        (131, 142) # FACTOR
    ]
    
    col_names = [
        'ANOENC', 'NUMERO', 'CODIGO', 'GASTO', 'PORCENDES', 'PORCENIMP',
        'CANTIDAD', 'GASTOMON', 'GASTNOM1', 'GASTNOM2', 'GASTNOM3',
        'GASTNOM4', 'GASTNOM5', 'FACTOR'
    ]
    
    df = read_fixed_width_file('Fichero de usuario de gastos a2023AJUSTE.txt', col_specs, col_names)
    df.to_csv('gastos_2023.csv', index=False)

def convert_miembros():
    col_specs = [
        (0, 4),   # ANOENC
        (4, 9),   # NUMERO
        (9, 11),  # NORDEN
        (11, 13), # CATEGMH
        (13, 14), # SUSPRIN
        (14, 16), # RELASP
        (16, 18), # EDAD
        (18, 20), # SEXO
        (20, 22), # PAISNACIM
        (22, 24), # NACIONA
        (24, 26), # PAISNACION
        (26, 28), # SITURES
        (28, 30), # ECIVILLEGAL
        (30, 32), # NORDENCO
        (32, 34), # UNION
        (34, 36), # CONVIVENCIA
        (36, 38), # NORDENPA
        (38, 40), # PAISPADRE
        (40, 42), # NORDENMA
        (42, 44), # PAISMADRE
        (44, 46), # ESTUDIOS
        (46, 48), # ESTUDIORED
        (48, 50), # SITUACT
        (50, 52), # SITURED
        (52, 54), # OCU
        (54, 56), # JORNADA
        (56, 58), # PERCEP
        (58, 63), # IMPEXACP
        (63, 65), # INTERINP
        (65, 67), # NINODEP
        (67, 69), # HIJODEP
        (69, 71), # ADULTO
        (71, 82)  # FACTOR
    ]
    
    col_names = [
        'ANOENC', 'NUMERO', 'NORDEN', 'CATEGMH', 'SUSPRIN', 'RELASP', 'EDAD', 'SEXO',
        'PAISNACIM', 'NACIONA', 'PAISNACION', 'SITURES', 'ECIVILLEGAL', 'NORDENCO', 'UNION',
        'CONVIVENCIA', 'NORDENPA', 'PAISPADRE', 'NORDENMA', 'PAISMADRE', 'ESTUDIOS',
        'ESTUDIORED', 'SITUACT', 'SITURED', 'OCU', 'JORNADA', 'PERCEP', 'IMPEXACP',
        'INTERINP', 'NINODEP', 'HIJODEP', 'ADULTO', 'FACTOR'
    ]
    
    # Update the file name to include the correct extension
    file_name = 'Fichero de usuario de miembros a2023IMPAJUSTE.txt'
    
    df = read_fixed_width_file(file_name, col_specs, col_names)
    df.to_csv('miembros_2023.csv', index=False)

if __name__ == "__main__":
    #convert_hogares()
    #convert_gastos()
    convert_miembros()
    print("Conversión completada. Se han creado los archivos CSV correspondientes.")