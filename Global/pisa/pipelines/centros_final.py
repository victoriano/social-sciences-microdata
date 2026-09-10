#!/usr/bin/env python3
"""Centros internacional final: centros_base dedup + agregados por centro desde finales."""
import pandas as pd, numpy as np, pyarrow.parquet as pq

c = pd.read_parquet('/tmp/pisa2/out/pisa_internacional_centros_base.parquet')
c['nn'] = c[[x for x in c.columns if x.startswith('cen_')]].notna().sum(axis=1)
c = c.sort_values('nn').drop_duplicates(subset=['pisa_year','pais','CNTSCHID'], keep='last').drop(columns='nn')
WIDTH = {2000:5,2003:5,2006:5,2009:5,2012:7,2015:7,2018:7,2022:7,2025:7}
aggs = []
for y in [2000,2003,2006,2012,2015,2018,2022,2025]:
    cols = ['pais','CNTSCHID','W_FSTUWT','ESCS','origen','repeticion']
    have = [f.name for f in pq.ParquetFile(f'/tmp/pisa2/out/final_{y}.parquet').schema_arrow]
    cols = [x for x in cols if x in have]
    t = pq.read_table(f'/tmp/pisa2/out/final_{y}.parquet', columns=cols).to_pandas()
    t['sch'] = pd.to_numeric(t['CNTSCHID'], errors='coerce').astype('Int64').astype(str).str.zfill(WIDTH[y])
    w = t['W_FSTUWT'] if 'W_FSTUWT' in t else pd.Series(float('nan'), index=t.index)
    if 'origen' in t:
        t['_imm'] = t['origen'].isin(['Primera generación','Segunda generación'])
        t['_immv'] = t['origen'].ne('Sin dato') & t['origen'].notna()
    else:
        t['_imm'] = False; t['_immv'] = False
    if 'repeticion' in t:
        t['_rep'] = t['repeticion'].eq('Repetidor'); t['_repv'] = t['repeticion'].ne('Sin dato') & t['repeticion'].notna()
    else:
        t['_rep'] = False; t['_repv'] = False
    if 'ESCS' not in t: t['ESCS'] = float('nan')
    t['_ew'] = t['ESCS']*w; t['_we'] = w.where(t['ESCS'].notna(), 0.0)
    t['_iw'] = w.where(t['_imm'], 0.0); t['_wi'] = w.where(t['_immv'], 0.0)
    t['_rw'] = w.where(t['_rep'], 0.0); t['_wr'] = w.where(t['_repv'], 0.0)
    g = t.groupby(['pais','sch']).agg(n=('ESCS','size'), ew=('_ew','sum'), we=('_we','sum'),
                               iw=('_iw','sum'), wi=('_wi','sum'), rw=('_rw','sum'), wr=('_wr','sum')).reset_index()
    g['cen_escs_media'] = g['ew']/g['we'].replace(0,np.nan)
    g['cen_pct_inmigrantes'] = 100*g['iw']/g['wi'].replace(0,np.nan)
    g['cen_pct_repetidores'] = 100*g['rw']/g['wr'].replace(0,np.nan)
    g['cen_alumnos_pisa'] = g['n']
    g['pisa_year'] = y
    aggs.append(g[['pisa_year','pais','sch','cen_escs_media','cen_pct_inmigrantes','cen_pct_repetidores','cen_alumnos_pisa']])
    print(y, len(g), flush=True)
    del t
a = pd.concat(aggs, ignore_index=True)
# pais para el join con agregados: los agregados no lo llevan; sch id solo unico por pais -> usar (pisa_year, pais) de centros
out = c.merge(a, left_on=['pisa_year','pais','CNTSCHID'], right_on=['pisa_year','pais','sch'], how='left').drop(columns='sch')
out.to_parquet('/tmp/pisa2/out/pisa_internacional_centros.parquet', index=False, compression='zstd')
print('centros final:', len(out))
