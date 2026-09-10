# Ampliación internacional (10 sept 2026, manifest v5)

## Qué se añade
Dataset internacional PISA: todo el alumnado de todos los países participantes, un Parquet por ciclo, coherente con el cocinado de España v2. 3.884.676 alumnos en 8 ciclos (2000, 2003, 2006, 2012, 2015, 2018, 2022, 2025) + `pisa_internacional_centros.parquet` (156.389 centros-ciclo, 9 ciclos incl. centros de 2009).

## Fuentes (descarga automatizada)
- 2015: Zenodo (réplica oficial OCDE, record 13383223), SAV.
- 2018/2022/2025: webfs.oecd.org (zips SPSS oficiales).
- 2000/2003/2006/2012 + cuestionarios de centro 2000-2012: snapshots de oecd.org/pisa/pisaproducts en web.archive.org (la OCDE retiró los txt históricos de su CDN entre las 18:00 y 19:15 del 10-sep-2026; wayback quedó como fuente de verdad).
- 2009 alumnado: PENDIENTE. La OCDE retiró el zip y no existe snapshot público bajo ningún nombre conocido. Vías abiertas: IHSN/Banco Mundial y mirror privado.

## Pipeline (scripts en /pipelines del repo... pendiente de subir; versionados también en la carpeta 'pisa' de Drive)
1. `build_intl_sav.py` (2015-2025): lectura SAV por chunks con pyreadstat, limpieza de códigos de falta (7-9, 95-99, ...), etiquetas en español coherentes con el cocinado ES, exploraciones = media de PVs, parquet zstd incremental con esquema fijo.
2. `build_intl_txt.py` (2003-2012): txt de ancho fijo con colspecs de los controles SPSS (slicing manual por líneas; read_fwf se cortaba en 2012). Etiquetas de VALUE LABELS del control (p. ej. ST03Q01 1=Female→No varón); país desde código ISO numérico (pycountry) o CNT.
3. `build2000.py`: 3 ficheros por materia unidos por COUNTRY+SCHOOLID+STIDSTD (base lectura); AGE meses→años; pesos por materia.
4. `build_centros_intl.py`: cen_* de cuestionarios de centro (SAV 2015-2025, txt+controles 2000-2012), spec = la de España generalizada sin filtro ESP.
5. `merge_final.py`: por ciclo añade pais (nombre ES), nivel_socioeconomico (cuartiles ponderados de ESCS por país), cen_* (join pais+CNTSCHID con normalización zfill 5/7, dedup por fila más completa) y agregados de centro (ESCS medio, % inmigrantes, % repetidores, n PISA) calculados en streaming.
6. `split2025.py`: 2025 queda >300MB; pesos replicados W_FSTURWT1-80 a fichero compañero.

## Verificación
- Filas por ciclo contra el fichero fuente completo; cuartiles ESCS ~uniformes por país; sexo ~50/50; Albania 2015 sin cuestionario de contexto en la fuente oficial (faltas reales, no bug); sha256 publicado en el manifest y verificado por URL pública tras subir a R2.

## Lecciones
- RAM del entorno 1,9GB: builds/merges estrictamente secuenciales; verificar num_rows tras cada paso (un parquet sin footer parece válido en ls).
- ParquetWriter: fijar esquema en el primer chunk y promover columnas todo-nulas a string, o un chunk posterior con valores rompe la escritura.
- webfs.oecd.org acepta rangos (206): descarga paralela por chunks ~10x más rápida que curl simple tras los primeros ~250MB.


## Publicación: ciclos grandes divididos en dos partes

Los ciclos 2018, 2022 y 2025 superan el límite práctico de subida del
dashboard de R2 en navegador (~160-200 MB por objeto; el proceso de render
del navegador se queda sin memoria por encima). Se publican divididos por
filas en `_a`/`_b` (misma estructura, mitad de alumnado cada una), con
sha256 por parte en el manifest (`dividido_en_partes: true`). Para unirlas:
`pyarrow.concat_tables([pq.read_table(a), pq.read_table(b)])`. Los demás
ciclos y el fichero de pesos replicados de 2025 van en objeto único. Los 13
objetos están verificados byte a byte contra su URL pública (sha256).
