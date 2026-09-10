# CNT ISO3 -> nombre en espanol (codigos PISA, incl. no-ISO historicos)
PAISES = {
"ALB":"Albania","ARE":"Emiratos Árabes Unidos","ARG":"Argentina","ARM":"Armenia","AUS":"Australia","AUT":"Austria",
"AZE":"Azerbaiyán","BEL":"Bélgica","BGR":"Bulgaria","BHR":"Baréin","BIH":"Bosnia y Herzegovina","BLR":"Bielorrusia",
"BRA":"Brasil","BRN":"Brunéi","CAN":"Canadá","CHE":"Suiza","CHL":"Chile","CHN":"China","COL":"Colombia",
"CRI":"Costa Rica","CYP":"Chipre","CZE":"Chequia","DEU":"Alemania","DNK":"Dinamarca","DOM":"República Dominicana",
"DZA":"Argelia","ECU":"Ecuador","EGY":"Egipto","ESP":"España","EST":"Estonia","FIN":"Finlandia","FRA":"Francia",
"GBR":"Reino Unido","GEO":"Georgia","GHA":"Ghana","GRC":"Grecia","GTM":"Guatemala","HKG":"Hong Kong (China)",
"HND":"Honduras","HRV":"Croacia","HUN":"Hungría","IDN":"Indonesia","IND":"India","IRL":"Irlanda","IRN":"Irán",
"IRQ":"Irak","ISL":"Islandia","ISR":"Israel","ITA":"Italia","JAM":"Jamaica","JOR":"Jordania","JPN":"Japón",
"KAZ":"Kazajistán","KGZ":"Kirguistán","KHM":"Camboya","KOR":"Corea del Sur","KWT":"Kuwait","LAO":"Laos",
"LBN":"Líbano","LIE":"Liechtenstein","LTU":"Lituania","LUX":"Luxemburgo","LVA":"Letonia","MAC":"Macao (China)",
"MAR":"Marruecos","MDA":"Moldavia","MEX":"México","MKD":"Macedonia del Norte","MLT":"Malta","MNE":"Montenegro",
"MNG":"Mongolia","MYS":"Malasia","NIC":"Nicaragua","NLD":"Países Bajos","NOR":"Noruega","NZL":"Nueva Zelanda",
"OMN":"Omán","PAK":"Pakistán","PAN":"Panamá","PER":"Perú","PHL":"Filipinas","POL":"Polonia","PRT":"Portugal",
"PRY":"Paraguay","PSE":"Palestina","QAT":"Catar","ROU":"Rumanía","RUS":"Rusia","SAU":"Arabia Saudí",
"SGP":"Singapur","SLV":"El Salvador","SRB":"Serbia","SVK":"Eslovaquia","SVN":"Eslovenia","SWE":"Suecia",
"TAP":"Taipéi China","THA":"Tailandia","TTO":"Trinidad y Tobago","TUN":"Túnez","TUR":"Turquía","UKR":"Ucrania",
"URY":"Uruguay","USA":"Estados Unidos","UZB":"Uzbekistán","VNM":"Vietnam","ZAF":"Sudáfrica",
"QCH":"China (B-S-J-G)","QCY":"Chipre","QES":"España","QIN":"India","QRS":"Rusia","QUK":"Reino Unido",
"QUV":"Eslovenia","QVE":"Venezuela","XKX":"Kosovo","YUG":"Yugoslavia","SCG":"Serbia y Montenegro",
}
def pais_nombre(cnt):
    return PAISES.get((cnt or '').strip().upper())
