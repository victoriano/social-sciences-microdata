#!/usr/bin/env python3
"""PISA internacional cocinado por ciclo (ficheros SAV 2015/2018/2022/2025).

Lee el SAV por chunks (pyreadstat usecols), limpia codigos de falta,
escribe parquet incremental (zstd) y acumula agregados por centro.
Esquema armonizado coherente con el cooked v2 de Espana.
"""
import argparse, json, sys, re
from pathlib import Path
import pyreadstat, pandas as pd, numpy as np
import pyarrow as pa, pyarrow.parquet as pq

sys.path.insert(0, '/tmp/ssm/Global/pisa/pipelines')
from build_cooked_v2 import ESPEC  # espec v2 (fuentes modernas, maps ES)
sys.path.insert(0, '/tmp/pisa2/build')
from paises import pais_nombre


def _schema0_de(df):
    sc = pa.Table.from_pandas(df, preserve_index=False).schema
    return pa.schema([pa.field(f.name, pa.string()) if f.type == pa.null() else f for f in sc], metadata=sc.metadata)


MISSING = {7,8,9,95,96,97,98,99,995,996,997,998,999,9995,9996,9997,9998,9999,
           99995,99996,99997,99998,99999,9999995,9999996,9999997,9999998,9999999,99999999}

# nucleo: fuentes por ciclo (modernas; 2022 = 2018, 2025 = CY09)
CORE_SRC = {
 2015: dict(id_c='CNTRYID', cnt='CNT', sch='CNTSCHID', stu='CNTSTUID', sexo='ST004D01T',
            age='AGE', grade='GRADE', immigr='IMMIG', hisced='HISCED', pared='PARED',
            escs='ESCS', hisei='HISEI', homepos='HOMEPOS', belong='BELONG', bsmj='BSMJ',
            anxmat='ANXMAT', repeat='REPEAT', famsup='FAMSUP', ictres='ICTRES'),
 2018: dict(id_c='CNTRYID', cnt='CNT', sch='CNTSCHID', stu='CNTSTUID', sexo='ST004D01T',
            age='AGE', grade='GRADE', immigr='IMMIG', hisced='HISCED', pared='PARED',
            escs='ESCS', hisei='HISEI', homepos='HOMEPOS', belong='BELONG', bsmj='BSMJ',
            anxmat='ANXMAT', repeat='REPEAT', famsup='FAMSUP', ictres='ICTRES'),
 2022: dict(id_c='CNTRYID', cnt='CNT', sch='CNTSCHID', stu='CNTSTUID', sexo='ST004D01T',
            age='AGE', grade='GRADE', immigr='IMMIG', hisced='HISCED', pared='PARED',
            escs='ESCS', hisei='HISEI', homepos='HOMEPOS', belong='BELONG', bsmj='BSMJ',
            anxmat='ANXMAT', repeat='REPEAT', famsup='FAMSUP', ictres='ICTRES'),
 2025: dict(id_c='CNTRYID', cnt='CNT', sch='CNTSCHID', stu='CNTSTUID', sexo='ST004D01T',
            age='AGE', grade='GRADE', immigr='IMMIG', hisced='HISCED', pared='PARED',
            escs='ESCS', hisei='HISEI', homepos='HOMEPOS', belong='BELONG', bsmj='BSMJ',
            anxmat='ANXMAT', repeat='REPEAT', famsup='FAMSUP', ictres='ICTRES'),
}
# candidatos alternativos si el nombre moderno no existe en un ciclo
ALT = {'sexo': ['ST004D01T','MALE'], 'anxmat': ['ANXMAT'], 'famsup':['FAMSUP']}

ORIGEN = {1:'Origen nativo', 2:'Segunda generación', 3:'Primera generación'}

def limpia(s, thr=None):
    v = pd.to_numeric(s, errors='coerce')
    m = v.isin(MISSING)
    if thr: m |= v.abs() >= thr
    return v.mask(m)

def hisced_map(v):
    # esquema antiguo 0-6 (<=2018): 0-2 bajo, 3-4 medio, 5-6 terciario
    return v.map(lambda x: 'Sin dato' if pd.isna(x) else
                 ('Hasta secundaria inferior' if x<=2 else
                  ('Secundaria superior/postsecundaria' if x<=4 else 'Terciaria')))

def build(year, sav, out_path, cyc_filter=None):
    meta_cols = pyreadstat.read_sav(sav, metadataonly=True)[1].column_names
    cols_up = {c.upper(): c for c in meta_cols}
    def has(c): return c and c.upper() in cols_up
    src = CORE_SRC[year]

    # plan de columnas
    plan_num, plan_cat = {}, {}  # destino -> (fuente, thr)
    def add(dst, fuente, thr=None, tipo='num'):
        if has(fuente):
            (plan_cat if tipo=='cat' else plan_num)[dst] = (cols_up[fuente.upper()], thr)
    # ids + peso
    ids = {k: cols_up[v.upper()] for k,v in src.items() if has(v)}
    # PVs
    pvs = [c for c in meta_cols if re.fullmatch(r'PV\d+(MATH|READ|SCIE)', c.upper())]
    # pesos replica
    reps = [c for c in meta_cols if re.fullmatch(r'W_FST[A-Z]*\d+', c.upper())]
    wf = 'W_FSTUWT' if has('W_FSTUWT') else None
    # core
    core_num = ['age','grade','pared','escs','hisei','homepos','belong','bsmj','anxmat','ictres']
    for k in core_num:
        add(k.upper() if k in ('age','grade','escs','hisei','homepos','belong','bsmj','anxmat','ictres') else 'PAREDINT',
            src.get(k), thr=90 if k in ('belong','bsmj','anxmat') else None)
    # v2 ESPEC
    for e in ESPEC:
        if has(e['fuente']):
            if e['tipo']=='categorica':
                plan_cat[e['nombre']] = (cols_up[e['fuente'].upper()], e['thr'])
            else:
                plan_num[e['nombre']] = (cols_up[e['fuente'].upper()], e['thr'])

    usecols = sorted({ids.get('cnt'), ids.get('sch'), ids.get('stu'), wf, *pvs, *reps,
                      src.get('sexo'), src.get('immigr'), src.get('hisced'), src.get('repeat'),
                      *[v[0] for v in plan_num.values()], *[v[0] for v in plan_cat.values()]} - {None})
    if cyc_filter and 'CYC' in cols_up: usecols.append(cols_up['CYC'])
    print(f"[{year}] {len(usecols)} columnas fuente, {len(pvs)} PVs, {len(reps)} pesos réplica", flush=True)

    # agregados por centro (streaming)
    agg = {}
    writer = None
    nrows = 0
    off = 0
    while True:
        df, _ = pyreadstat.read_sav(sav, row_limit=50000, row_offset=off, usecols=usecols)
        if df is None or len(df)==0: break
        off += len(df)
        df.columns = [c.upper() for c in df.columns]
        if cyc_filter and 'CYC' in df.columns:
            df = df[df['CYC']==cyc_filter]
            if len(df)==0: continue
        out = {}
        if ids.get('cnt'): out['pais'] = df[ids['cnt'].upper()].astype(str).str.strip()
        if ids.get('sch'): out['CNTSCHID'] = limpia(df[ids['sch'].upper()])
        if ids.get('stu'): out['CNTSTUID'] = limpia(df[ids['stu'].upper()])
        if wf: out['W_FSTUWT'] = limpia(df[wf])
        for c in pvs: out[c.upper()] = limpia(df[c.upper()])
        for c in reps: out[c.upper()] = limpia(df[c.upper()])
        # core derivados
        sx = limpia(df[src['sexo'].upper()]) if has(src.get('sexo')) else pd.Series(np.nan, index=df.index)
        if src['sexo']=='MALE':
            out['sexo'] = sx.map(lambda x: 'Varón' if x==1 else ('No varón' if x==0 else None))
        else:
            out['sexo'] = sx.map(lambda x: 'Varón' if x==2 else ('No varón' if x==1 else None))
        im = limpia(df[src['immigr'].upper()]) if has(src.get('immigr')) else pd.Series(np.nan, index=df.index)
        out['origen'] = im.map(lambda x: ORIGEN.get(int(x)) if pd.notna(x) else 'Sin dato')
        rp = limpia(df[src['repeat'].upper()]) if has(src.get('repeat')) else pd.Series(np.nan, index=df.index)
        out['repeticion'] = rp.map(lambda x: 'Repetidor' if x==1 else ('No repetidor' if x==0 else 'Sin dato'))
        hs = limpia(df[src['hisced'].upper()]) if has(src.get('hisced')) else pd.Series(np.nan, index=df.index)
        out['educacion_familiar'] = hisced_map(hs)
        for dst,(fuente,thr) in plan_num.items():
            out[dst] = limpia(df[fuente.upper()], thr)
        for dst,(fuente,thr) in plan_cat.items():
            espec = next(e for e in ESPEC if e['nombre']==dst)
            v = limpia(df[fuente.upper()], thr)
            out[dst] = v.map(lambda x: espec['cat'].get(str(int(x))) if pd.notna(x) else None)
        # exploracion (media PVs)
        for dom, dname in (('MATH','math_exploracion'),('READ','read_exploracion'),('SCIE','scie_exploracion')):
            cs = [c.upper() for c in pvs if dom in c.upper()]
            if cs:
                m = pd.concat([out[c] for c in cs], axis=1)
                out[dname] = m.mean(axis=1).where(m.notna().all(axis=1))
                out['numero_pv_'+dom.lower()] = len(cs)
        odf = pd.DataFrame(out)
        odf['fila_origen'] = range(nrows, nrows+len(odf))
        odf['pisa_year'] = year
        nrows += len(odf)
        # agregados streaming
        if 'CNTSCHID' in odf:
            t = pd.DataFrame({'sch': odf['CNTSCHID'], 'w': odf.get('W_FSTUWT'),
                              'escs': odf.get('ESCS'),
                              'imm': odf['origen'].isin(['Primera generación','Segunda generación']),
                              'imm_v': odf['origen']!='Sin dato',
                              'rep': odf['repeticion'].eq('Repetidor'), 'rep_v': odf['repeticion']!='Sin dato'})
            t = t[t['sch'].notna() & t['w'].notna()]
            for schv, g in t.groupby('sch'):
                a = agg.setdefault(int(schv), [0]*9)
                a[0]+=float((g['escs']*g['w']).sum()); a[1]+=float(g.loc[g['escs'].notna(),'w'].sum())
                a[2]+=float(g.loc[g['imm'],'w'].sum()); a[3]+=float(g.loc[g['imm_v'],'w'].sum())
                a[4]+=float(g.loc[g['rep'],'w'].sum()); a[5]+=float(g.loc[g['rep_v'],'w'].sum())
                a[6]+=len(g)
        if writer is None:
            schema0 = _schema0_de(odf)
            writer = pq.ParquetWriter(out_path, schema0, compression='zstd', compression_level=10)
        odf = odf.reindex(columns=schema0.names)
        table = pa.Table.from_pandas(odf, schema=schema0, preserve_index=False)
        writer.write_table(table)
        print(f"  {nrows} filas...", flush=True)
    if writer: writer.close()
    json.dump({str(k): v for k,v in agg.items()}, open(str(out_path)+'.agg.json','w'))
    print(f"[{year}] OK {nrows} filas -> {out_path}", flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', type=int, required=True)
    ap.add_argument('--sav', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--cyc', type=int, default=None)
    a = ap.parse_args()
    build(a.year, a.sav, a.out, a.cyc)
