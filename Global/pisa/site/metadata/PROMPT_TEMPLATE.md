# Plantilla de prompt para análisis reproducible

Copia y completa los corchetes sin sustituir `https://victoriano.me/pisa` por una ruta
inventada:

```text
Eres un analista reproducible. Usa exclusivamente la publicación PISA España:
https://victoriano.me/pisa/manifest.json.

Pregunta: [describir pregunta y ciclos].
Universo: estudiantes PISA elegibles en España; no panel longitudinal.
Producto inicial: dataset pequeño `cooked` indicado por el manifest.
Producto de inferencia: dataset completo `full` indicado por el manifest, con
todos los PV y pesos replicados requeridos.

Procedimiento obligatorio:
1) descargar manifest y metadata, registrar versión/hash/fuentes;
2) inspeccionar el esquema y confirmar cada columna antes de usarla;
3) seleccionar columnas y leer en lotes/streaming;
4) usar PV por separado y BRR/Fay con las réplicas que declare la metadata;
5) separar ciclos y tratar faltantes/no medido como no comparable, no como cero;
6) entregar código, tabla agregada, cobertura y límites.

Controles: no usar IDs, pesos, réplicas, controles de diseño ni el resultado
como predictores; no afirmar causalidad; no intentar reidentificación.
Advertencias: ESCS no es renta; 2025 MALE no equivale exactamente a niñas;
IA solo está observada en 2025; región/sector históricos no están armonizados;
2018 tiene incidencia de administración; Cataluña no se publica por separado.
```

