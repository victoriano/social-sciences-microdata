# AGENTS.md — instrucciones para consumidores remotos

Estas reglas son obligatorias al usar los datos públicos de PISA España.

## Entrada y selección

- Empieza en `https://victoriano.me/pisa/manifest.json`. El manifest es la autoridad para
  resolver URLs, formatos, versiones, tamaños, hashes y enlaces de metadata.
  En la publicación web, los datos se encuentran bajo `files.cooked` y
  `files.full`; la documentación se resuelve desde `metadata.*`.
- Descarga la metadata antes de analizar. Inspecciona nombres, tipos, etiquetas,
  cobertura por ciclo y códigos de faltantes; no inventes columnas por analogía
  con otro ciclo o con documentación antigua.
- Usa primero el dataset `cooked` pequeño (191.254 filas, 80 columnas) para
  prototipos. Para inferencia, usa el dataset completo con los valores plausibles
  y pesos de réplica que declare el manifest.
- Proyecta columnas y procesa por lotes/streaming. No cargues un JSON o un PUF
  completo en memoria sin necesidad.

## Diseño de muestra y resultados

- Los ciclos son cortes transversales independientes: no son un panel de los
  mismos estudiantes. Las diferencias entre ciclos tienen además incertidumbre
  de enlace de escalas, cambios de población, cuestionario y administración.
- Matemáticas tiene tendencia comparable desde 2003; ciencias desde 2006;
  lectura desde 2000. No trates matemáticas 2000 ni ciencias 2000/2003 como una
  serie homogénea con las referencias posteriores.
- Hay cinco PV por materia hasta 2012 y diez desde 2015. Un PV es una imputación
  de la distribución de competencia, no una nota individual. Para inferencia,
  calcula la estadística en cada PV y cada réplica; no promedies PV por alumno y
  olvides su varianza.
- Un fichero apilado puede conservar diez columnas PV modernas aunque los ciclos
  antiguos tengan solo cinco PV no nulos. En 2000 algunos resultados usan
  prefijos históricos (`MATH__`/`SCIE__`): resuelve la correspondencia desde la
  metadata del ciclo.
- En 2000 existen submuestras específicas por materia: usa el peso de la
  materia (`peso_math`, `peso_read` o `peso_scie`, o el nombre que confirme la
  metadata), no un peso de lectura aplicado a todo. En los demás ciclos suele
  coincidir con `W_FSTUWT`, pero compruébalo.
- Para 2025, la variable `ST004D01T` española puede estar completamente ausente.
  El indicador disponible `MALE` codifica 1 = varón y 0 = femenino/otra
  categoría. `0` no debe etiquetarse como “niñas” sin esa salvedad; en 2022 el
  grupo no-varón sí corresponde a mujeres. No afirmes resultados separados de
  Cataluña: su alumnado permanece en el total español por la advertencia de la
  OCDE.
- España 2018 requiere cautela en las tres materias por incidencias de
  administración. Conserva el ciclo y el aviso; no corrijas ni elimines
  estudiantes arbitrariamente.

## Variables y comparabilidad

- `ESCS` es un índice de estatus económico, social y cultural; no es renta
  monetaria ni salario. Los cuartiles son posiciones ponderadas relativas dentro
  de cada ciclo, no tramos de euros comparables.
- Los índices originales (incluidos ESCS, HISEI y HOMEPOS) no se han reescalado.
  Una misma etiqueta no garantiza idéntica normalización, definición o unidad
  entre ciclos. `ICTSCH`/`ICTHOME` históricos pueden ser sumas de recursos,
  mientras que índices ICT recientes pueden ser WLE: no los unas por nombre.
- Región y sector históricos no están armonizados en el producto cocinado. Los
  códigos de región cambian entre ciclos; usa etiquetas de la metadata y no
  iguales numéricos. Un nulo significa falta de medición/correspondencia
  validada, no cero.
- IA 2025 solo tiene valores observados en 2025. Los nulos de IA en otros ciclos
  significan que no se midió o no se integró; nunca los conviertas en 0.
- Mantén los códigos y etiquetas originales además de cualquier variable
  armonizada. Documenta transformaciones y conserva la categoría “Sin dato”.

## Inferencia, privacidad y comunicación

- La receta mínima para una media es: estimar la media ponderada por separado
  para cada PV y cada peso; calcular la varianza BRR de Fay con las 80 réplicas
  (`sum((rep-full)^2)/20` cuando el factor de Fay es 0,5); combinarla con la
  varianza entre PV, usando el multiplicador Rubin `1 + 1/m`. Confirma `m` y el
  factor en la metadata antes de automatizar.
- Para cambios entre años, combina la varianza de ciclos independientes y
  declara si el intervalo omite el error de enlace. Para contrastes de brecha
  dentro de cada ciclo, conserva la covarianza calculando el contraste en cada
  PV/réplica antes de resumirlo.
- No utilices `ID`, `CNTSCHID`, `CNTSTUID`, `fila_origen`, pesos, réplicas,
  `numero_pv_*` ni `aviso_ciclo` como predictores. Evita también fuga de objetivo:
  un PV o un resumen de rendimiento no puede ser predictor de sí mismo.
- Una asociación PISA no demuestra causalidad. No atribuyas descensos a IA,
  SES, sexo, origen, centro o cualquier otra covariable sin diseño causal.
- Publica únicamente agregados que respeten las reglas de supresión de la
  metadata y la privacidad del PUF. No muestres filas individuales, hashes de
  identificadores combinados ni intentos de reidentificación.
