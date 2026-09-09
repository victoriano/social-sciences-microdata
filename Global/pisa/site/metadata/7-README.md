# PISA España: guía para agentes de IA

Este directorio acompaña la publicación pública de microdatos PUF anonimizados
de estudiantes de PISA para España. El punto de entrada es:

`https://victoriano.me/pisa/manifest.json`

El publicador informa de que cuenta con permiso para esta redistribución; aun
así, cada agente debe respetar el aviso de uso del manifest y la prohibición de
reidentificación.

No memorices nombres de ficheros ni columnas: descarga el manifest, elige un
dataset por su clave/`id` (en la publicación web son `files.cooked` y
`files.full`) y sigue su `url`, `format`, `columns` y hash. Consulta además
`metadata.*` para el diccionario, cobertura, guía y reglas de uso. Si una
versión del manifest añade `metadata_url` o `schema` dentro de la entrada,
úsalos también. La versión pequeña cocinada debe ser el primer dataset que se
inspeccione. El dataset completo está pensado para análisis que necesiten todas
las variables PUF y los pesos replicados.

## Prompt de arranque

```text
Trabaja únicamente con la publicación PISA España disponible en
https://victoriano.me/pisa/manifest.json. Descarga primero el manifest y la metadata asociada;
no inventes rutas ni nombres de columnas. Empieza con el dataset pequeño
`cooked` (o el id equivalente que indique el manifest) para comprobar el
esquema, años, etiquetas, tipos y faltantes. Solo después, si el análisis lo
requiere, cambia al dataset completo y usa los 10 valores plausibles y los 80
pesos replicados que describa su metadata.

Antes de calcular, cita el id/version/hash del dataset, la metadata y las
fuentes; selecciona solo las columnas necesarias y procesa por lotes. Trata
los ciclos como cortes transversales independientes, no como un panel. Usa
pesos y valores plausibles conforme a la guía; no uses IDs, pesos ni controles
de diseño como predictores. Presenta asociaciones como descriptivas: PISA no
identifica efectos causales. Devuelve código reproducible y deja claros los
filtros, faltantes, cobertura, unidad y límites.
```

## Flujo mínimo reproducible

1. `GET https://victoriano.me/pisa/manifest.json`; guarda la respuesta y verifica la versión,
   fecha, hashes y el aviso de uso/permiso declarado por quien publica el
   dataset. No infieras una licencia de redistribución distinta.
2. Para cada dataset elegido, resuelve la URL declarada por el manifest. Lee
   primero la metadata y el esquema; no cargues un JSON gigante completo.
3. Comienza con el dataset pequeño cocinado: sirve para exploración, columnas
   armonizadas y validación rápida, pero no sustituye al PUF completo para
   inferencia.
4. Para estimar medias o cambios, usa el completo con todos los PV de la
   materia y `W_FSTUWT` más los 80 pesos de réplica. Calcula cada PV y réplica,
   combina después la incertidumbre de imputación y muestreo.
5. Lee en streaming o por lotes y proyecta columnas. Conserva año/ciclo,
   etiquetas, faltantes y procedencia en la salida. Nunca publiques filas que
   permitan reidentificar a un estudiante, centro o familia.

El script [`../scripts/analysis_example.py`](../scripts/analysis_example.py)
implementa el arranque: obtiene el manifest, muestra el contrato, inspecciona
columnas sin adivinarlas y calcula una demostración ponderada solo si encuentra
PV y pesos compatibles.

Para la demostración reciente, pasa `--year 2022` o `--year 2025`. El error
Fay-BRR no se activa por contar columnas: añade `--fay-factor 0.5` únicamente
después de confirmar ese factor y las 80 réplicas en la metadata.

## Qué contiene y qué no contiene esta publicación

- Cubre los ciclos 2000, 2003, 2006, 2009, 2012, 2015, 2018, 2022 y 2025.
- Es una unión de muestras de cada ciclo. No sigue a las mismas personas y no
  debe llamarse panel longitudinal.
- El cocinado histórico tiene 191.254 estudiantes y 80 columnas (73 variables
  más 7 controles de diseño); sus columnas disponibles por año están en la
  metadata/cobertura, no necesariamente en todos los ciclos.
- El PUF completo contiene las columnas de estudiante publicadas para todos
  los ciclos que indique el manifest. No se debe describir como la totalidad
  de respuestas cognitivas de ítems ni como ficheros de escuelas.
- Son PUF anonimizados. Está prohibida la reidentificación o el intento de
  enlazar personas/centros fuera de las claves y del ciclo autorizado.

## Fuentes y citas

La respuesta de un agente debe citar el manifest, la metadata concreta y el
fichero de datos utilizado, incluyendo versión/hash cuando exista. Añade las
fuentes metodológicas de la OCDE que el manifest o la metadata indiquen. No
presentes una cifra local o una etiqueta armonizada como si fuera una cifra
oficial de la OCDE sin comprobar su definición.
