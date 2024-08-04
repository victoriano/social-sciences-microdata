# Encuesta de Presupuestos Familiares

Los microdatos disponibles de [la encuesta de Presupuestos Familiares](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176806&menu=resultados&idp=1254735976608#_tabs-1254736195147) que realiza el INE en España cada año, dispone de 2 periodos con codificaciones diferentes: 2006-2015 y desde 2016 al presente. 

Los datos de la encuesta se componen cada año de 3 tablas: 

- Una tabla que representa **los gastos** anuales de un hogar para cada categoría de producto y servicios. Hay 354 categorías de granulares de gasto que se pueden agrupar a su vez en 12 grandes categorías. Estos ficheros suelen contener unas 1.5M de observaciones cada año. 

- Un fichero donde se describe **características del hogar**. Suele contener unos 20K observaciones de hogares. 

- Un fichero otro archivo que detalla características de cada miembro del hogar. Suele contener unos 50K observaciones de miembros de hogares.

## 2016 - Presente

- Desde 2016, la EPF incorpora la nueva clasificación europea de consumo (ECOICOP).
- En la carpeta **/download_and_merge_spss_files_since2016** se pueden encontrar scripts para automticamente descargar los ficheros, descomprimir los zips, extraer los ficheros de SPSS, convertirlos a CSV/Parquet y mergearlos en uno solo. 

- En la carpeta **/datamarts** se pueden encontrar scripts para crear joins entre tablas de gasto, el hogar y sus miembros para poder fácilmente hacer queries análisis con Graphext, Duckdb o un Notebook que permitan entender diferencias de gastos por tipos de hogares por ejemplo. Además se generan columnas nuevas como computar el gasto real y cantidades dividiendo por el factor de cada observación, o creando un índice para hogar mezclando la variable del año de la encuesta con el número de hogar.

- Por alguna razón para el 2023 los microdatos sólo vienen en formato de ancho fijo, txts, por lo que he tenido que hacer un script sólo para ese año, que se puede encontrar en la carpeta **/txt_to_csv_processing_2023** para convertirlos a csv con los mappings de las columnas y conseguir el mismo formato que se puede sacar fácilmente a partir de los ficheros de SPSS de años anteriores.


## Acceso a los datos

Los microdatos y resultados detallados de la EPF están disponibles en la [página oficial del INE](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176806&menu=resultados&idp=1254735976608#_tabs-1254736195147).