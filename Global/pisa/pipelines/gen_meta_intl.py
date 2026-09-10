#!/usr/bin/env python3
"""Genera metadata internacional: diccionario + cobertura + manifest v5 (lee finales + cooked ES)."""
import json, hashlib, os, sys
from pathlib import Path
import pandas as pd, pyarrow.parquet as pq

OUT = Path('/tmp/pisa2/out'); YEARS = [2000,2003,2006,2009,2012,2015,2018,2022,2025]
ES_DIC = '/tmp/ssm/Global/pisa/site/metadata/cooked_diccionario.csv'

DESC_EXTRA = {
 'pais': ('País o economía participante (nombre en español).', 'string'),
 'pais_codigo': ('Código CNT de 3 letras del país.', 'string'),
 'CNTSCHID': ('ID del centro (único dentro de país y ciclo).', 'int'),
 'CNTSTUID': ('ID del alumno (único dentro de país y ciclo).', 'int'),
 'W_FSTUWT': ('Peso final del alumno (pondera a la población de 15 años del país).', 'float'),
 'fila_origen': ('Fila base cero en el extracto original del ciclo.', 'int'),
 'pisa_year': ('Ciclo PISA (2000-2025).', 'int'),
 'math_exploracion': ('Media de los valores plausibles de matemáticas (exploración; nula si falta alguno). Para inferencia usa los PV individuales.', 'float'),
 'read_exploracion': ('Media de los valores plausibles de lectura (exploración).', 'float'),
 'scie_exploracion': ('Media de los valores plausibles de ciencias (exploración).', 'float'),
 'numero_pv_math': ('Número de PV de matemáticas por diseño (5 antes de 2015, 10 después).', 'int'),
 'numero_pv_read': ('Número de PV de lectura por diseño.', 'int'),
 'numero_pv_scie': ('Número de PV de ciencias por diseño.', 'int'),
 'sexo': ('Sexo del alumnado: Varón / No varón. En 2025 (MALE) "No varón" no equivale exactamente a niña.', 'string'),
 'origen': ('Estatus migratorio: Origen nativo / Primera generación / Segunda generación / Sin dato.', 'string'),
 'repeticion': ('Ha repetido algún curso alguna vez: Repetidor / No repetidor / Sin dato.', 'string'),
 'educacion_familiar': ('Nivel educativo más alto de los progenitores (HISCED armonizado).', 'string'),
 'nivel_socioeconomico': ('Cuartil de ESCS ponderado dentro de su país y ciclo (Q1 menor - Q4 mayor).', 'string'),
 'PESO_MATH': ('Peso del fichero de matemáticas de 2000 (peso por materia; en el resto de ciclos usar W_FSTUWT).', 'float'),
 'PESO_SCIE': ('Peso del fichero de ciencias de 2000.', 'float'),
 'cen_alumnos_pisa': ('Número de alumnado PISA muestreado en el centro (composición, no tamaño oficial).', 'int'),
 'cen_escs_media': ('ESCS medio ponderado del alumnado del centro en ese ciclo.', 'float'),
 'cen_pct_inmigrantes': ('% ponderado del alumnado del centro de primera o segunda generación.', 'float'),
 'cen_pct_repetidores': ('% ponderado del alumnado del centro que ha repetido.', 'float'),
}

def sha256(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''): h.update(chunk)
    return h.hexdigest()

def main():
    es = {}
    if os.path.exists(ES_DIC):
        d = pd.read_csv(ES_DIC)
        for _, r in d.iterrows():
            es[str(r.iloc[0])] = str(r.iloc[2]) if len(r)>2 else ''
    schemas = {}
    files_meta = {}
    for y in YEARS:
        p = OUT / f'final_{y}.parquet'
        if not p.exists(): continue
        pf = pq.ParquetFile(p)
        schemas[y] = [(f.name, str(f.type)) for f in pf.schema_arrow]
        files_meta[y] = dict(rows=pf.metadata.num_rows, bytes=p.stat().st_size,
                             sha256=sha256(p), cols=len(pf.schema_arrow.names))
    # diccionario union
    cols = {}
    for y, sc in schemas.items():
        for name, typ in sc:
            cols.setdefault(name, {'tipo': typ, 'ciclos': []})['ciclos'].append(y)
    rows = []
    for name, info in sorted(cols.items()):
        if name in DESC_EXTRA: desc = DESC_EXTRA[name][0]
        elif name in es: desc = es[name]
        elif name.startswith('PV') : desc = 'Valor plausible (uso inferencial con pesos; nunca tratar como nota individual).'
        elif name.startswith('W_FSTR'): desc = 'Peso replicado BRR/Fay para errores estándar según diseño PISA.'
        elif name.startswith('cen_'): desc = es.get(name, 'Variable del cuestionario de centro (ver AGENTS internacional).')
        else: desc = ''
        rows.append({'columna': name, 'tipo': info['tipo'], 'descripcion': desc,
                     'ciclos': ','.join(map(str, info['ciclos']))})
    pd.DataFrame(rows).to_csv(OUT/'diccionario_internacional.csv', index=False)
    json.dump(files_meta, open(OUT/'files_meta.json','w'), indent=1)
    print(json.dumps({y: {'rows': m['rows'], 'MB': round(m['bytes']/1e6,1), 'cols': m['cols']} for y,m in files_meta.items()}, indent=0))
    print("diccionario:", len(rows), "columnas")
if __name__ == '__main__':
    main()
