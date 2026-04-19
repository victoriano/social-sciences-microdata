# EPF INE — data sources

The INE publishes the **Encuesta de Presupuestos Familiares** every year with
three tables:

- ``EPFhogar`` — ~20k households, describing household-level attributes.
- ``EPFmhogar`` — ~50k household members.
- ``EPFgastos`` — ~1.5M rows with annual expenditure per ECOICOP category
  (354 granular categories that roll up to 12 top-level groups).

## Format history

- **2006–2015:** legacy codification. Not yet covered by this pipeline.
- **2016–2022:** new ECOICOP codification, shipped as SPSS (+ CSV + TXT).
- **2023:** shipped only as fixed-width text files. Needs the dedicated
  fixed-width parser in ``pipelines/process_fixed_width_2023.py`` plus the
  enrichment step in ``pipelines/enrich_2023.py``.

## Endpoints

- Official page: <https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176806>
- Download template: ``https://www.ine.es/ftp/microdatos/epf2006/datos_{year}.zip``

## Design registers (diseño de registro)

The Excel files `dr_EPFgastos_2016.xlsx`, `dr_EPFhogar_2016.xlsx`,
`dr_EPFmhogar_2016.xlsx` and the PDF `t2530p45822.pdf` contain the exact
variable definitions. They are not committed to this repo (see the root
``.gitignore``); download them from the INE microdata portal if you need to
cross-check variables.
