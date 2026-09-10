#!/usr/bin/env python3
"""PISA internacional ciclos txt (2003/2006/2009/2012): fixed-width + control SPSS."""
import argparse, json, re, sys, zipfile
from pathlib import Path
import pandas as pd, numpy as np
import pyarrow as pa, pyarrow.parquet as pq
import pycountry

sys.path.insert(0, '/tmp/pisa2/build')
from paises import pais_nombre


def _schema0_de(df):
    sc = pa.Table.from_pandas(df, preserve_index=False).schema
    return pa.schema([pa.field(f.name, pa.string()) if f.type == pa.null() else f for f in sc], metadata=sc.metadata)


MISSING = {7,8,9,95,96,97,98,99,995,996,997,998,999,9995,9996,9997,9998,9999,
           99995,99996,99997,99998,99999,9999995,9999996,9999997,9999998,9999999,99999999}

def parse_ctl(path):
    txt = open(path, encoding='latin-1', errors='replace').read().replace('\r','')
    pos, tipos, labels = {}, {}, {}
    m = re.search(r'(?is)data\s+list[^/]*?/(.*?)\.', txt)
    body = m.group(1) if m else txt
    for ln in body.splitlines():
        mm = re.match(r'\s*(\w+)\s+(\d+)\s*-\s*(\d+)\s*(\(\s*A\s*\)|\(F(?:\s*,\s*\d+)?\))?', ln)
        if mm:
            v = mm.group(1).upper()
            pos[v] = (int(mm.group(2))-1, int(mm.group(3)))
            tipos[v] = 's' if (mm.group(4) and 'A' in mm.group(4).upper()) else 'n'
    mvl = re.search(r'(?is)value\s+labels\s*\n(.*?)\n\s*\.', txt)
    if mvl:
        cur = None
        for ln in mvl.group(1).splitlines():
            mm = re.match(r'\s*/?(\w+)\s+(\S+)\s+"([^"]*)"', ln)
            if mm:
                cur = mm.group(1).upper()
                labels.setdefault(cur, {})[mm.group(2)] = mm.group(3)
                continue
            mm = re.match(r'\s+(\S+)\s+"([^"]*)"', ln)
            if mm and cur:
                labels[cur][mm.group(1)] = mm.group(2)
    return pos, tipos, labels

def limpia(s):
    v = pd.to_numeric(s, errors='coerce')
    return v.mask(v.isin(MISSING))

def labmap(labels, var):
    """{codigo: etiqueta minusculas}"""
    return {k: v.lower() for k, v in labels.get(var, {}).items()}

def map_origen(v, labs):
    def f(x):
        if pd.isna(x): return 'Sin dato'
        l = labs.get(str(int(x)), '')
        if 'native' in l: return 'Origen nativo'
        if 'first' in l: return 'Primera generación'
        if 'second' in l: return 'Segunda generación'
        if x==1: return 'Origen nativo'
        if x==2: return 'Segunda generación'
        if x==3: return 'Primera generación'
        return 'Sin dato'
    return v.map(f)

def map_sexo(v, labs):
    def f(x):
        if pd.isna(x): return None
        l = labs.get(str(int(x)), '')
        if 'female' in l or 'girl' in l: return 'No varón'
        if l and ('male' in l or 'boy' in l): return 'Varón'
        if x==1: return 'No varón'
        if x==2: return 'Varón'
        return None
    return v.map(f)

def map_hisced(v):
    return v.map(lambda x: 'Sin dato' if pd.isna(x) else
                 ('Hasta secundaria inferior' if x<=2 else
                  ('Secundaria superior/postsecundaria' if x<=4 else 'Terciaria')))

def pais_de_codigo(raw):
    s = str(raw).strip().replace('.0','')
    if re.fullmatch(r'\d{1,3}', s):
        try:
            c = pycountry.countries.get(numeric=s.zfill(3))
            if c: return pais_nombre(c.alpha_3) or c.name
        except Exception: pass
        return s
    if re.fullmatch(r'[A-Za-z]{3}', s):
        return pais_nombre(s.upper()) or s.upper()
    return s

def build(year, zip_path, ctl_path, out_path):
    pos, tipos, labels = parse_ctl(ctl_path)
    with zipfile.ZipFile(zip_path) as z:
        txt_name = [n for n in z.namelist() if n.lower().endswith('.txt')][0]
    # columnas
    has = lambda v: v and v in pos
    def pick(*names):
        for n in names:
            if has(n): return n
        return None
    id_c = pick('CNT','COUNTRY'); id_s = pick('SCHOOLID','CNTSCHID'); id_st = pick('STIDSTD','StIDStd')
    sx = pick('ST03Q01'); im = pick('IMMIG'); hs = pick('HISCED'); rp = pick('REPEAT')
    core_num = {d: pick(d) for d in ['AGE','GRADE','PARED','ESCS','HISEI','HOMEPOS','BELONG','BSMJ','ANXMAT','ICTRES','FAMSUP']}
    pvs = sorted([v for v in pos if re.fullmatch(r'PV\d(MATH|READ|SCIE)', v)])
    reps = sorted([v for v in pos if re.fullmatch(r'W_FSTR\d+', v)])
    wf = 'W_FSTUWT' if has('W_FSTUWT') else None
    keep = [id_c,id_s,id_st,wf,sx,im,hs,rp] + [v for v in core_num.values() if v] + pvs + reps
    keep = [k for k in dict.fromkeys(keep) if k]
    colspecs = [pos[k] for k in keep]
    print(f"[{year}] {len(keep)} cols, {len(pvs)} PVs, {len(reps)} reps, txt={txt_name}", flush=True)
    oimm, osex = labmap(labels, im or ''), labmap(labels, sx or '')
    agg, writer, nrows, schema0 = {}, None, 0, None

    def procesa(df):
        nonlocal writer, nrows, schema0
        out = {}
        out['pais'] = df[id_c].map(pais_de_codigo) if id_c else None
        out['CNTSCHID'] = limpia(df[id_s]) if id_s else None
        out['CNTSTUID'] = limpia(df[id_st]) if id_st else None
        if wf: out['W_FSTUWT'] = limpia(df[wf])
        for c in pvs: out[c] = limpia(df[c])
        for c in reps: out[c] = limpia(df[c])
        out['sexo'] = map_sexo(limpia(df[sx]), osex) if sx else None
        out['origen'] = map_origen(limpia(df[im]), oimm) if im else None
        out['educacion_familiar'] = map_hisced(limpia(df[hs])) if hs else None
        if rp:
            rv = limpia(df[rp])
            out['repeticion'] = rv.map(lambda x: 'Repetidor' if x==1 else ('No repetidor' if x==0 else 'Sin dato'))
        for d, srcn in core_num.items():
            if srcn: out[d] = limpia(df[srcn])
        for dom, dname in (('MATH','math_exploracion'),('READ','read_exploracion'),('SCIE','scie_exploracion')):
            cs = [c for c in pvs if dom in c]
            if cs:
                m = pd.concat([out[c] for c in cs], axis=1)
                out[dname] = m.mean(axis=1).where(m.notna().all(axis=1))
                out['numero_pv_'+dom.lower()] = len(cs)
        odf = pd.DataFrame({k:v for k,v in out.items() if v is not None})
        odf['fila_origen'] = range(nrows, nrows+len(odf)); odf['pisa_year'] = year
        nrows += len(odf)
        if writer is None:
            schema0 = _schema0_de(odf)
            writer = pq.ParquetWriter(out_path, schema0, compression='zstd', compression_level=10)
        odf = odf.reindex(columns=schema0.names)
        table = pa.Table.from_pandas(odf, schema=schema0, preserve_index=False)
        writer.write_table(table)
        print(f"  {nrows} filas...", flush=True)

    import io as _io
    cidx = {k: pos[k] for k in keep}
    with zipfile.ZipFile(zip_path) as z:
        with z.open(txt_name) as f:
            buf = []
            for raw in _io.TextIOWrapper(f, encoding='latin-1'):
                if len(raw.strip()) < 10: continue
                buf.append([raw[a:b].strip() or None for a,b in (cidx[k] for k in keep)])
                if len(buf) >= 80000:
                    procesa(pd.DataFrame(buf, columns=keep)); buf = []
            if buf: procesa(pd.DataFrame(buf, columns=keep))
    if writer: writer.close()
    json.dump(agg, open(str(out_path)+'.agg.json','w'))
    print(f"[{year}] OK {nrows} -> {out_path}", flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', type=int, required=True)
    ap.add_argument('--zip', required=True)
    ap.add_argument('--ctl', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    build(a.year, a.zip, a.ctl, a.out)
