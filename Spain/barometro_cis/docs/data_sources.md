# CIS Barómetro — data sources

The CIS (Centro de Investigaciones Sociológicas) publishes monthly "barómetros"
— surveys of public opinion in Spain with 100+ questions. The first published
study is from October 1986 (código 1552); most variables of interest start
from ~2013 onwards.

## Endpoints used by this pipeline

- **Catalogue (all studies):** `POST https://www.cis.es/o/cis/estudios` with
  `cndColeccion=Barómetros CIS` and `registrosPorPagina=-1`.
- **Download by código:** `https://www.cis.es/documents/d/cis/MD{codigo}?download=true`.
- **Human catalogue page:** <https://www.cis.es/catalogo-estudios/resultados-definidos/barometros>

## File layout delivered by CIS

Each `MD{codigo}.zip` contains an SPSS file (`{codigo}.sav`) plus documentation
(PDF with the questionnaire and a disreg Excel with variable definitions). The
pipeline only consumes the `.sav` file and relies on the embedded value labels
to produce human-readable columns.

## Related links

- Example study page: <https://www.cis.es/descarga-fichero-datos?codEstudio=3463>
- ODS terms of use for CIS microdata: <https://www.cis.es/condiciones-de-uso>
