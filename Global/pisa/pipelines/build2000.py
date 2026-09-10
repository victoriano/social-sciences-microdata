#!/usr/bin/env python3
"""PISA 2000 internacional chunked: base READ + MATH/SCIE left-join por claves."""
import sys, zipfile, re
import pandas as pd, numpy as np
import pyarrow as pa, pyarrow.parquet as pq
sys.path.insert(0, '/tmp/pisa2/build')
from build_intl_txt import parse_ctl, pais_de_codigo, MISSING

RAW='/tmp/pisa2/raw'
DOM = {'READ': ('2000_READ.zip','intstud_read_v3.txt','PISA2000_SPSS_student_reading.txt'),
       'MATH': ('2000_MATH.zip','intstud_math_v3.txt','PISA2000_SPSS_student_mathematics.txt'),
       'SCIE': ('2000_SCIE.zip','intstud_scie_v3.txt','PISA2000_SPSS_student_science.txt')}
KEYS = ['COUNTRY','SCHOOLID','STIDSTD']

def limp(s):
    return pd.to_numeric(s, errors='coerce').mask(lambda v: v.isin(MISSING))

def carga_lateral(dom):
    zf, tn, ctl = DOM[dom]
    pos, _, _ = parse_ctl(f'{RAW}/ctl/{ctl}')
    pvs = sorted([v for v in pos if re.fullmatch(rf'PV[1-5]{dom}', v)])
    keep = KEYS + pvs + ['W_FSTUWT']
    with zipfile.ZipFile(f'{RAW}/{zf}') as z:
        with z.open(tn) as f:
            df = pd.read_fwf(f, colspecs=[pos[k] for k in keep], names=keep, dtype=str, encoding='latin-1')
    for k in KEYS: df[k] = df[k].astype(str).str.strip()
    df = df.rename(columns={'W_FSTUWT': f'PESO_{dom}'})
    print(dom, len(df), flush=True)
    return df.set_index(KEYS), pvs

math_df, pvs_m = carga_lateral('MATH')
scie_df, pvs_s = carga_lateral('SCIE')

zf, tn, ctl = DOM['READ']
pos, _, _ = parse_ctl(f'{RAW}/ctl/{ctl}')
pvs_r = sorted([v for v in pos if re.fullmatch(r'PV[1-5]READ', v)])
reps = [f'W_FSTR{i}' for i in range(1,81) if f'W_FSTR{i}' in pos]
core = [c for c in ['ST03Q01','AGE','HISEI','BELONG'] if c in pos]
keep = KEYS + pvs_r + ['W_FSTUWT'] + reps + core
writer, n = None, 0
with zipfile.ZipFile(f'{RAW}/{zf}') as z:
    with z.open(tn) as f:
        for df in pd.read_fwf(f, colspecs=[pos[k] for k in keep], names=keep, dtype=str,
                              encoding='latin-1', chunksize=60000):
            for k in KEYS: df[k] = df[k].astype(str).str.strip()
            df = df.set_index(KEYS)
            df = df.join(math_df, how='left').join(scie_df, how='left').reset_index()
            out = {}
            out['pais'] = df['COUNTRY'].map(pais_de_codigo)
            out['CNTSCHID'] = pd.to_numeric(df['SCHOOLID'], errors='coerce')
            out['CNTSTUID'] = pd.to_numeric(df['STIDSTD'], errors='coerce')
            out['W_FSTUWT'] = limp(df['W_FSTUWT'])
            out['PESO_MATH'] = limp(df['PESO_MATH']); out['PESO_SCIE'] = limp(df['PESO_SCIE'])
            for dd, pvs in (('READ',pvs_r),('MATH',pvs_m),('SCIE',pvs_s)):
                for c in pvs: out[c] = limp(df[c])
                mm = pd.concat([out[c] for c in pvs], axis=1)
                out[dd.lower()+'_exploracion'] = mm.mean(axis=1).where(mm.notna().all(axis=1))
                out['numero_pv_'+dd.lower()] = len(pvs)
            for c in reps: out[c] = limp(df[c])
            sx = limp(df['ST03Q01'])
            out['sexo'] = sx.map(lambda x: 'No varón' if x==1 else ('Varón' if x==2 else None))
            out['AGE'] = (limp(df['AGE'])/12).round(2)
            out['HISEI'] = limp(df['HISEI']); out['BELONG'] = limp(df['BELONG'])
            odf = pd.DataFrame(out)
            odf['fila_origen'] = range(n, n+len(odf)); odf['pisa_year'] = 2000
            n += len(odf)
            t = pa.Table.from_pandas(odf, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter('/tmp/pisa2/out/pisa_internacional_2000.parquet', t.schema, compression='zstd', compression_level=10)
            writer.write_table(t)
            print(f"  {n} filas...", flush=True)
if writer: writer.close()
print("[2000] OK", n, flush=True)
