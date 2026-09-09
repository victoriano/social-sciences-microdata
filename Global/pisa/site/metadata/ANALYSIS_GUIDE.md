# Guía estadística y de auditoría

## 1. Resolver la publicación sin suposiciones

Usa `https://victoriano.me/pisa/manifest.json` como índice. Un agente robusto debe registrar
el `dataset_id`, `version`, `generated_at`, `sha256` (si existen), formato y
las URLs de datos y metadata. En la publicación web, los ficheros están bajo
`files.cooked` y `files.full`; la documentación se enlaza bajo `metadata.*`.
Si el manifest ofrece varios ficheros, selecciona por `role`/`id` y explica por
qué. Si faltan campos, detente y pide una versión del manifest que los incluya;
no adivines una ruta.

Lee metadata y esquema de forma separada. El esquema dice qué columnas existen;
la metadata de variables dice qué significan, cuándo aparecen y qué valores son
missing. Diferencia “no administrado/no integrado” de cero. Para Parquet utiliza
lectura columnar y lotes; para CSV usa un `chunksize`; para JSON usa un lector
incremental o un formato de líneas, nunca `json.load` sobre un fichero masivo.

## 2. Producto pequeño frente a PUF completo

El cocinado `cooked191254students80colsall9cycles2000...2025` contiene 73
variables seleccionadas y siete controles de diseño. Es adecuado para explorar
cobertura, nombres armonizados y gráficos descriptivos. El PUF completo
`fullallstudentPUFcolumns...` conserva las columnas de estudiante que publique
el proyecto y debe usarse cuando se necesitan PV individuales, todas las
réplicas o una pregunta no incluida en el cocinado. La metadata JSON del PUF
completo se publica como `manifest-data.json`, `esquema_por_ciclo.json`,
`diccionario_variables_por_ciclo.csv`, un `pisa_YEAR_student_metadata.json` por
ciclo y `validacion_datos.json`; resuelve siempre sus URLs desde el manifest.
Ninguno de los dos implica
que estén publicados todos los ítems cognitivos ni datos de escuela.

El ejemplo Python se limita deliberadamente a 2022/2025 y exige `--year`,
porque un fichero apilado puede conservar diez columnas PV modernas aunque en
los ciclos antiguos solo haya cinco valores no nulos. En 2000, además, algunos
resultados de materia usan prefijos históricos (`MATH__`/`SCIE__`); consulta la
metadata del ciclo antes de mapearlos a nombres modernos.

La unión apila ciclos: una fila representa una persona en un ciclo. `fila_origen`
solo sirve para trazabilidad junto con el año y las fuentes; no es una clave
longitudinal ni un predictor. Los identificadores originales pueden estar
suprimidos o solo ser válidos dentro de ciclo/país.

## 3. Receta de PV y BRR

Para una materia y ciclo, con `m` PV y el peso final `w`, define para cada
`j = 0..80` (final y 80 réplicas) y cada PV `k`:

```text
theta[j,k] = sum_i(w[j,i] * PV[k,i]) / sum_i(w[j,i])
theta = mean_k(theta[0,k])
```

Con Fay 0,5 y 80 réplicas, la varianza de muestreo suele expresarse como:

```text
V_sampling = mean_k( sum_r (theta[r,k] - theta[0,k])² / (80 * 0,5²) )
V_imputation = (1 + 1/m) * sample_variance_k(theta[0,k])
SE = sqrt(V_sampling + V_imputation)
```

No asumas esos nombres, `m=10` o el factor sin comprobar la metadata. En 2000
selecciona el peso específico de la materia. Para una diferencia entre ciclos,
calcula cada ciclo por separado y suma sus varianzas bajo independencia de las
muestras. Declara expresamente que el intervalo no incluye automáticamente el
error de enlace entre escalas PISA.

Para un contraste grupo/resto que pueda cancelar un error aditivo común, calcula
grupo y resto en los mismos PV/réplicas y resta antes de resumir. Esto no elimina
cambios de cuestionario, cobertura, selección, compresión de escala o sesgo de
no respuesta. No presentes los contrastes como causalidad.

## 4. Comparaciones históricas seguras

Usa la siguiente ancla mínima de tendencia, sin rellenar ciclos ausentes:

| Dominio | Inicio de referencia | Precaución |
|---|---:|---|
| Lectura | 2000 | Cinco PV hasta 2012; diez desde 2015 |
| Matemáticas | 2003 | No unir directamente la submuestra de 2000 |
| Ciencias | 2006 | No unir directamente 2000/2003 con la serie posterior |

Los ciclos son encuestas repetidas, no observaciones longitudinales. Cambian
marcos, muestras, administración, población objetivo y codificaciones. Una
diferencia descriptiva no es una trayectoria individual.

Puntos de auditoría obligatorios:

- España 2018: incluir un aviso por las incidencias de administración en las
  tres materias.
- España 2025: si `ST004D01T` está ausente, usar solo el indicador `MALE` que
  confirme la metadata; 1 es varón y 0 es femenino/otra categoría. No llamarlo
  “chicas” sin matiz.
- Cataluña 2025: mantener estudiantes en el total español, no publicar un
  resultado separado si la metadata conserva la advertencia de exclusión.
- Región/sector: no igualar códigos numéricos de distintos años; los campos
  históricos no están armonizados en el cocinado.
- IA: ausencia antes de 2025 es no medición/no integración, nunca uso cero.
- ESCS: índice original, sin reescalado OCDE en esta publicación; cuartiles
  calculados dentro de cada ciclo son rangos relativos.

## 5. Modelos y fugas

Declara explícitamente el universo (estudiantes elegibles escolarizados en
España), los filtros válidos y los faltantes. Evita modelos con una variable de
resultado y sus PV/resúmenes como covariables simultáneos. Excluye IDs,
`fila_origen`, peso final, pesos replicados, número de PV y avisos de diseño de
las matrices de predictores. Si una pregunta solo se administra en un ciclo,
no la codifiques como ausencia conductual en los demás.

Si ajustas regresiones, repite la especificación por PV y réplica o usa un
método que respete el diseño; comunica que el resultado es asociacional. Para
subgrupos pequeños aplica los umbrales de publicación/supresión indicados por
la metadata. No infieras diferencias entre subgrupos solo porque sus rankings
se solapen o no se solapen.

## 6. Reproducibilidad y salida

Cada resultado debe guardar: manifest y metadata citados, hash/versión, URL,
columnas, filtros, ciclo, dominio, pesos/PV usados, tratamiento de faltantes,
fórmula de varianza y código. Los ficheros de salida deben ser agregados y
revisados para eliminar claves identificables. Si una cifra no puede
reproducirse desde el manifest público, márcala como no verificada.
