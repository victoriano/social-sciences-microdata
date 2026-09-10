# Ampliación del dataset cocinado (v2, 2026-09-10)

## Qué se ha hecho

El dataset cocinado pasa de 80 a **228 columnas**: las 80 originales, 143
variables nuevas extraídas del fichero completo (alumnado) y 5 agregados de
composición del centro. Script: `pipelines/build_cooked_v2.py`.

### Bloques nuevos

- **03 Hogar y familia**: duración de ECEC, lengua en casa, estructura
  familiar, trabajo remunerado, riqueza (WEALTH), bienes culturales, etc.
- **04 Padres (cuestionario de padres PAQ 2015 + reporte del alumnado)**:
  índices PAQ reales solo en 2015 (PQSCHOOL, PRESUPP, CURSUPP, PQGENSCI,
  PQENPERC, PQENVOPT, ADDSCIIN; n ≈ 4.700, submuestra con cuestionario de
  padres). EMOSUPS (2015/2018) y SOCONPA (2018/2022) los reporta el alumnado.
  **Ojo**: los índices de padres 2022/2025 (PQMIMP, PQMCAR, PQFEED, PQSELFREG,
  PQDIGEFF, PQSCAR, FGENSUP, FSCISUP) aparecen en el fichero de alumnado pero
  **solo con códigos de falta** para España: no hay cuestionario de padres
  público para 2018-2025. Se han excluido del cocinado y así consta en la
  cobertura.
- **05-10**: tiempo y hábitos, TIC, bienestar, motivación/aspiraciones,
  trayectoria y resultados (GROSAGR, HISCED...).
- **11 Aula y aprendizaje**: clima disciplinario (DISCLIMA/DISCLIM), relación
  alumno-profesor, activación cognitiva, etc. Los nombres se conservan con el
  código PISA original porque las escalas no son comparables entre todos los
  ciclos; la descripción indica los ciclos con datos.
- **12-15**: convivencia y contexto global (2018), educación financiera
  (2018/2022), creatividad (2022), ciencia y ambiente (2006/2015/2025).
- **16 Composición del centro**: agregados ponderados por W_FSTUWT a nivel
  (pisa_year, CNTSCHID): `centro_escs_medio`, `centro_pct_inmigrantes`,
  `centro_pct_repetidores`, `centro_pct_ausentismo`, `centro_alumnos_muestra`.
  Base para análisis de segregación escolar.

### Accionabilidad para los padres

Todas las filas del diccionario (incluidas las 80 originales) llevan el campo
`accionabilidad_padres` (alta/media/baja/nula). Criterio documentado en
`site/metadata/AGENTS.md` y `site/metadata/README.md`.

### Garantías

- Ningún valor inventado: si una variable no existe o es todo faltante en un
  ciclo, queda vacía. Cobertura real (excluyendo códigos de falta 95-99,
  995-999, etc.) en `metadata/cooked_cobertura_por_ciclo.csv`.
- Alineación full↔cooked verificada fila a fila (0 desajustes en
  ANXMAT/BELONG/ESCS en todos los ciclos). Detalle: `fila_origen` de 2025
  continúa la numeración de 2022 (fichero CY09 conjunto: 30800-60765).
- Casos especiales documentados: `MISSSC` (2022) solo contiene códigos de
  falta para España; `EUDMO` solo tiene datos en 2018 (la columna 2022 viene
  vacía).

## Cuestionario de centro (SCQ) - en curso

Pipeline `pipelines/build_school_merge.py`: extrae el fichero de centro de la
OCDE, armoniza a español y une al cocinado por (pisa_year, CNTSCHID)
(normalizando el sufijo ".0" que arrastra CNTSCHID en 2000-2022 solo para el
join). 18 variables con prefijo `cen_`: entorno urbano/rural, competencia
entre centros, público/privado/concertado, tamaño, % financiación pública y
de cuotas, ratio alumno/profesor, escasez de material y de personal (WLE),
% profesorado certificado, ordenadores por alumno, autonomía, participación
docente, liderazgo educativo e instruccional, selectividad de admisión y
% de alumnado con padres inmigrantes.

Integrado y verificado para los **9 ciclos**: 2000-2012 desde los txt de
ancho fijo de la OCDE (control SAS parseado por `pipelines/parse_old_school.py`;
2000 desde el codebook PDF, que incluye el layout de columnas) y 2015-2025
desde SPSS (2015 vía Zenodo record 13383223; 2018/2022/2025 vía
webfs.oecd.org). Emparejamiento centro-cocinado: 100% de centros en
2000/2003/2006/2009/2012 y 96-99% del alumnado con datos de centro en
2015-2025. Salidas: `pisa_espana_2000_2025_centros.parquet` (6.257
centros-ciclo) y las columnas cen_* dentro del cocinado (246 columnas).

Cobertura cen_* por ciclo (resumen): público/tipo/comunidad/financiación/
tamaño/stratio en los 9 ciclos (salvo tamaño y financiación en 2025, no
preguntados); profesorado certificado en todos salvo 2006; escasez de
material/personal 2015-2025; autonomía, participación docente y liderazgos en
2022 (+EDULEAD 2025); admisión por expediente en todos salvo 2003/2006
(escala no comparable); competencia entre centros en 2012-2025.

## Pendiente

1. Subir los parquet (cocinado 246 cols + centros) al bucket R2 `pisa-data` y
   publicar la rama + PR.
2. Revisar si existe PUF del cuestionario de padres de 2025 (no localizado en
   el índice de la OCDE a fecha de hoy).
