#!/usr/bin/env python3
"""Merge final por ciclo: +pais_nombre, nivel_socioeconomico (cuartiles ESCS ponderados por pais),
cen_* por (pais, CNTSCHID), agregados de centro. Esquema union entre ciclos."""
import argparse, json, re, sys
import pandas as pd, numpy as np
import pyarrow as pa, pyarrow.parquet as pq
sys.path.insert(0, '/tmp/pisa2/build')
from paises import pais_nombre


def _schema0_de(df):
    sc = pa.Table.from_pandas(df, preserve_index=False).schema
    return pa.schema([pa.field(f.name, pa.string()) if f.type == pa.null() else f for f in sc], metadata=sc.metadata)


WIDTH = {2000:5, 2003:5, 2006:5, 2009:5, 2012:7, 2015:7, 2018:7, 2022:7, 2025:7}

def norm_sch(s, w):
    return pd.to_numeric(s, errors='coerce').astype('Int64').astype(str).str.zfill(w)

def cuartiles_ponderados(v, w):
    m = v.notna() & w.notna()
    if m.sum() < 50: return None
    vv, ww = v[m].to_numpy(), w[m].to_numpy()
    o = np.argsort(vv); vv, ww = vv[o], ww[o]
    cw = np.cumsum(ww) / ww.sum()
    return [float(vv[min(np.searchsorted(cw, q), len(vv)-1)]) for q in (0.25, 0.5, 0.75)]

def merge_cycle(year, in_path, centros, out_path):
    pf = pq.ParquetFile(in_path)
    w = WIDTH[year]
    # pase A: slim
    slim = []
    for b in pf.iter_batches(batch_size=120000, columns=['pais','CNTSCHID','W_FSTUWT','ESCS','origen','repeticion']):
        d = b.to_pandas()
        slim.append(d)
    s = pd.concat(slim, ignore_index=True)
    for col, default in (('origen','Sin dato'), ('repeticion','Sin dato')):
        if col not in s.columns: s[col] = default
    if 'ESCS' not in s.columns: s['ESCS'] = float('nan')
    if 'W_FSTUWT' not in s.columns: s['W_FSTUWT'] = float('nan')
    if s['pais'].astype(str).str.fullmatch(r'[A-Z]{3}').all():
        s['pais'] = s['pais'].map(lambda c: pais_nombre(c) or c)
    s['sch'] = norm_sch(s['CNTSCHID'], w)
    # cuartiles por pais
    qs = {}
    for p, g in s.groupby('pais'):
        q = cuartiles_ponderados(g['ESCS'], g['W_FSTUWT'])
        if q: qs[p] = q
    # agregados por (pais, sch)
    wp = s['W_FSTUWT']
    s['imm'] = s['origen'].isin(['Primera generación','Segunda generación'])
    s['imm_v'] = s['origen'].ne('Sin dato') & s['origen'].notna()
    s['rep'] = s['repeticion'].eq('Repetidor')
    s['rep_v'] = s['repeticion'].ne('Sin dato') & s['repeticion'].notna()
    s['_escs_w'] = s['ESCS'] * wp
    s['_w_escs'] = wp.where(s['ESCS'].notna(), 0.0)
    s['_imm_w'] = wp.where(s['imm'], 0.0)
    s['_w_imm'] = wp.where(s['imm_v'], 0.0)
    s['_rep_w'] = wp.where(s['rep'], 0.0)
    s['_w_rep'] = wp.where(s['rep_v'], 0.0)
    g = s.groupby(['pais','sch'])
    agg = g.agg(n=('W_FSTUWT','size'), escs_w=('_escs_w','sum'), w_escs=('_w_escs','sum'),
                imm_w=('_imm_w','sum'), w_imm=('_w_imm','sum'),
                rep_w=('_rep_w','sum'), w_rep=('_w_rep','sum')).reset_index()
    agg['cen_escs_media'] = agg['escs_w']/agg['w_escs'].replace(0, float('nan'))
    agg['cen_pct_inmigrantes'] = 100*agg['imm_w']/agg['w_imm'].replace(0, float('nan'))
    agg['cen_pct_repetidores'] = 100*agg['rep_w']/agg['w_rep'].replace(0, float('nan'))
    agg['cen_alumnos_pisa'] = agg['n']
    agg = agg[['pais','sch','cen_escs_media','cen_pct_inmigrantes','cen_pct_repetidores','cen_alumnos_pisa']]
    cz = centros[centros['pisa_year']==year].copy()
    cz['nn'] = cz[[c for c in cz.columns if c.startswith('cen_')]].notna().sum(axis=1)
    cz = cz.sort_values('nn').drop_duplicates(subset=['pais','CNTSCHID'], keep='last').drop(columns='nn')
    del s
    # pase B: transformar + escribir
    writer, n = None, 0
    cen_cols = [c for c in cz.columns if c.startswith('cen_')]
    for b in pf.iter_batches(batch_size=50000):
        d = b.to_pandas()
        if d['pais'].astype(str).str.fullmatch(r'[A-Z]{3}').all():
            d['pais'] = d['pais'].map(lambda c: pais_nombre(c) or c)
        d['sch'] = norm_sch(d['CNTSCHID'], w)
        if 'ESCS' not in d.columns: d['ESCS'] = float('nan')
        for col in ('sexo','origen','repeticion','educacion_familiar'):
            if col not in d.columns: d[col] = None
        niv = pd.Series('Sin dato', index=d.index, dtype=object)
        for pais, q in qs.items():
            msk = (d['pais']==pais) & d['ESCS'].notna()
            if msk.any():
                idx = np.searchsorted(q, d.loc[msk,'ESCS'].to_numpy(), side='right')
                niv.loc[msk] = np.take(['Q1','Q2','Q3','Q4'], np.clip(idx,0,3))
        d['nivel_socioeconomico'] = niv
        if len(cz):
            d = d.merge(cz[['pais','CNTSCHID']+cen_cols].rename(columns={'CNTSCHID':'sch'}),
                        on=['pais','sch'], how='left')
        d = d.merge(agg, on=['pais','sch'], how='left')
        d = d.drop(columns=['sch'])
        n += len(d)
        if writer is None:
            schema0 = _schema0_de(d)
            writer = pq.ParquetWriter(out_path, schema0, compression='zstd', compression_level=10)
        d = d.reindex(columns=schema0.names)
        t = pa.Table.from_pandas(d, schema=schema0, preserve_index=False)
        writer.write_table(t)
    if writer: writer.close()
    print(f"[{year}] merge OK {n} filas -> {out_path}", flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', type=int, required=True)
    ap.add_argument('--inp', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    centros = pd.read_parquet('/tmp/pisa2/out/pisa_internacional_centros_base.parquet')
    merge_cycle(a.year, a.inp, centros, a.out)
