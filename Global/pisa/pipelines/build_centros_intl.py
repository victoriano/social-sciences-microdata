#!/usr/bin/env python3
"""Centros PISA internacional 2000-2025 -> parquet unificado (cen_* armonizadas)."""
import re, sys, zipfile, io
import pandas as pd, numpy as np
import pyreadstat
sys.path.insert(0, '/tmp/pisa2/build')
from build_intl_txt import parse_ctl, pais_de_codigo, MISSING

COMUNIDAD = {"1":"Zona rural (menos de 3.000 hab.)","2":"Pueblo pequeño (3.000-15.000)","3":"Ciudad pequeña (15.000-100.000)","4":"Ciudad (100.000-1M)","5":"Ciudad grande (1M-10M)","6":"Megaciudad (más de 10M)"}
COMPETENCIA = {"1":"Dos o más centros compiten por el alumnado","2":"Un centro compite por el alumnado","3":"Ningún centro compite por el alumnado"}
PUBLICO = {"1":"Público","2":"Privado"}
TIPO = {"1":"Privado independiente","2":"Privado concertado","3":"Público"}
SIEMPRE = {"1":"Nunca","2":"A veces","3":"Siempre"}

# ciclo -> (fichero, tipo, mapa cen_->fuente, ancho id)
SPEC = {
 2015: dict(tipo='sav', path='/tmp/pisa2/raw/2015_SCH.sav', width=7, cnt='CNT', sch='CNTSCHID', m={
   'cen_comunidad':'SC001Q01TA','cen_publico':'SC013Q01TA','cen_tipo':'SCHLTYPE',
   'cen_alumnos':'SC002Q01TA+SC002Q02TA','cen_fin_gobierno_pct':'SC016Q01TA','cen_fin_cuotas_pct':'SC016Q02TA',
   'cen_stratio':'STRATIO','cen_escasez_material':'EDUSHORT','cen_escasez_personal':'STAFFSHORT',
   'cen_profesorado_certificado':'PROATCE','cen_ordenadores_alumno':'RATCMP1','cen_admision_expediente':'SC012Q01TA'}),
 2018: dict(tipo='sav', path='/tmp/pisa2/raw/sch_2018/CY07_MSU_SCH_QQQ.sav', width=7, cnt='CNT', sch='CNTSCHID', m={
   'cen_comunidad':'SC001Q01TA','cen_competencia':'SC011Q01TA','cen_publico':'SC013Q01TA','cen_tipo':'SCHLTYPE',
   'cen_alumnos':'SC002Q01TA+SC002Q02TA','cen_fin_gobierno_pct':'SC016Q01TA','cen_fin_cuotas_pct':'SC016Q02TA',
   'cen_stratio':'STRATIO','cen_escasez_material':'EDUSHORT','cen_escasez_personal':'STAFFSHORT',
   'cen_profesorado_certificado':'PROATCE','cen_ordenadores_alumno':'RATCMP1','cen_admision_expediente':'SC012Q01TA'}),
 2022: dict(tipo='sav', path='/tmp/pisa2/raw/sch_2022/CY08MSP_SCH_QQQ.SAV', width=7, cnt='CNT', sch='CNTSCHID', m={
   'cen_comunidad':'SC001Q01TA','cen_competencia':'SC011Q01TA','cen_publico':'SC013Q01TA','cen_tipo':'SCHLTYPE',
   'cen_alumnos':'SC002Q01TA+SC002Q02TA','cen_fin_gobierno_pct':'SC016Q01TA','cen_fin_cuotas_pct':'SC016Q02TA',
   'cen_stratio':'STRATIO','cen_escasez_material':'EDUSHORT','cen_escasez_personal':'STAFFSHORT',
   'cen_profesorado_certificado':'PROATCE','cen_ordenadores_alumno':'RATCMP1','cen_autonomia':'SCHAUTO',
   'cen_participacion_prof':'TCHPART','cen_liderazgo_educativo':'EDULEAD','cen_liderazgo_instruccional':'INSTLEAD',
   'cen_admision_expediente':'SC012Q01TA','cen_padres_inmigrantes_pct':'SC211Q05JA'}),
 2025: dict(tipo='sav', path='/tmp/pisa2/raw/sch_2025/CY09_MS_SCH_PUF.sav', width=7, cnt='CNT', sch='CNTSCHID', m={
   'cen_comunidad':'SC001Q01TA','cen_competencia':'SC011Q01TA','cen_publico':'SC013Q01TA','cen_tipo':'SCHLTYPE',
   'cen_stratio':'STRATIO_Q','cen_escasez_material':'EDUSHORT','cen_escasez_personal':'STAFFSHORT',
   'cen_profesorado_certificado':'PROATCE','cen_liderazgo_educativo':'EDULEAD','cen_liderazgo_instruccional':'INSTLEAD',
   'cen_admision_expediente':'SC012Q01TA'}),
 2003: dict(tipo='txt', zip='/tmp/pisa2/raw/2003_SCH.zip', txt='INT_schi_2003.txt', ctl='/tmp/pisa2/raw/ctl/PISA2003_SPSS_school.txt', width=5, cnt='COUNTRY', sch='SCHOOLID', m={
   'cen_comunidad':'SC01Q01','cen_publico':'SC03Q01','cen_tipo':'SCHLTYPE','cen_alumnos':'SC02Q01+SC02Q02',
   'cen_fin_gobierno_pct':'SC04Q01','cen_fin_cuotas_pct':'SC04Q02','cen_stratio':'STRATIO','cen_profesorado_certificado':'PROPCERT'}),
 2006: dict(tipo='txt', zip='/tmp/pisa2/raw/2006_SCH.zip', txt='INT_Sch06_Dec07.txt', ctl='/tmp/pisa2/raw/ctl/PISA2006_SPSS_school.txt', width=5, cnt='COUNTRY', sch='SCHOOLID', m={
   'cen_comunidad':'SC07Q01','cen_publico':'SC02Q01','cen_tipo':'SCHLTYPE','cen_alumnos':'SC01Q01+SC01Q02',
   'cen_fin_gobierno_pct':'SC03Q01','cen_fin_cuotas_pct':'SC03Q02','cen_stratio':'STRATIO','cen_profesorado_certificado':'PROPCERT'}),
 2009: dict(tipo='txt', zip='/tmp/pisa2/raw/2009_SCH.zip', txt='INT_SCQ09_Dec11.txt', ctl='/tmp/pisa2/raw/ctl/PISA2009_SPSS_school.txt', width=5, cnt='COUNTRY', sch='SCHOOLID', m={
   'cen_comunidad':'SC04Q01','cen_publico':'SC02Q01','cen_tipo':'SCHTYPE','cen_alumnos':'SC06Q01+SC06Q02',
   'cen_fin_gobierno_pct':'SC03Q01','cen_fin_cuotas_pct':'SC03Q02','cen_stratio':'STRATIO','cen_profesorado_certificado':'PROPCERT',
   'cen_admision_expediente':'SC19Q02'}),
 2012: dict(tipo='txt', zip='/tmp/pisa2/raw/2012_SCH.zip', txt='INT_SCQ12_DEC03.txt', ctl='/tmp/pisa2/raw/ctl/PISA2012_SPSS_school.txt', width=7, cnt='CNT', sch='SCHOOLID', m={
   'cen_comunidad':'SC03Q01','cen_publico':'SC01Q01','cen_tipo':'SCHLTYPE','cen_alumnos':'SC07Q01+SC07Q02',
   'cen_fin_gobierno_pct':'SC02Q01','cen_fin_cuotas_pct':'SC02Q02','cen_stratio':'STRATIO','cen_profesorado_certificado':'PROPCERT',
   'cen_admision_expediente':'SC32Q01','cen_competencia':'SC04Q01'}),
}
POS2000 = {'COUNTRY':(1,4),'SCHOOLID':(4,9),'SC01Q01':(13,14),'SC02Q01':(14,18),'SC02Q02':(18,22),
 'SC03Q01':(22,23),'SC04Q01':(23,26),'SC04Q02':(26,29),'SC07Q02':(57,58),'SCHLTYPE':(298,299),
 'STRATIO':(329,334),'PROPCERT':(338,342)}
M2000 = {'cen_comunidad':'SC01Q01','cen_publico':'SC03Q01','cen_tipo':'SCHLTYPE','cen_alumnos':'SC02Q01+SC02Q02',
 'cen_fin_gobierno_pct':'SC04Q01','cen_fin_cuotas_pct':'SC04Q02','cen_stratio':'STRATIO',
 'cen_profesorado_certificado':'PROPCERT','cen_admision_expediente':'SC07Q02'}

def limp(s, vmax=None):
    v = pd.to_numeric(s, errors='coerce')
    v = v.mask(v.isin(MISSING))
    if vmax: v = v.mask(v.abs()>=vmax)
    return v

def catmap(v, mapa):
    return v.map(lambda x: mapa.get(str(int(x))) if pd.notna(x) else None)

def construye(df, year, width, cntcol, schcol, m):
    out = pd.DataFrame(index=df.index)
    out['pisa_year'] = year
    out['pais'] = df[cntcol].map(pais_de_codigo)
    out['CNTSCHID'] = df[schcol].astype(str).str.strip().str.replace(r'\.0$','',regex=True).str.zfill(width)
    for dst, src in m.items():
        if '+' in src:
            a,b = src.split('+')
            if a in df.columns and b in df.columns:
                v1, v2 = limp(df[a],9000), limp(df[b],9000)
                out[dst] = (v1+v2).where(~(v1.isna()&v2.isna()))
            continue
        if src not in df.columns: continue
        v = limp(df[src], 900 if dst in ('cen_fin_gobierno_pct','cen_fin_cuotas_pct','cen_stratio') else (90 if dst.startswith('cen_escasez') or dst in ('cen_profesorado_certificado',) else None))
        if dst in ('cen_comunidad',): out[dst] = catmap(v, COMUNIDAD)
        elif dst == 'cen_competencia': out[dst] = catmap(v, COMPETENCIA)
        elif dst in ('cen_publico',): out[dst] = catmap(v, PUBLICO)
        elif dst == 'cen_tipo': out[dst] = catmap(v, TIPO)
        elif dst == 'cen_admision_expediente': out[dst] = catmap(v, SIEMPRE)
        else: out[dst] = v
    return out

frames = []
for year, s in SPEC.items():
    if s['tipo']=='sav':
        need = {s['cnt'], s['sch']} | {x for v in s['m'].values() for x in v.split('+')}
        meta = pyreadstat.read_sav(s['path'], metadataonly=True)[1]
        use = [c for c in meta.column_names if c.upper() in {n.upper() for n in need}]
        df, _ = pyreadstat.read_sav(s['path'], usecols=use)
        df.columns = [c.upper() for c in df.columns]
    else:
        pos, tipos, labels = parse_ctl(s['ctl'])
        need = {s['cnt'], s['sch']} | {x for v in s['m'].values() for x in v.split('+')}
        need = {n for n in need if n in pos}
        with zipfile.ZipFile(s['zip']) as z:
            with z.open(s['txt']) as f:
                df = pd.read_fwf(f, colspecs=[pos[k] for k in sorted(need)], names=sorted(need), dtype=str, encoding='latin-1')
    r = construye(df, year, s['width'], s['cnt'].upper(), s['sch'].upper(), s['m'])
    frames.append(r)
    print(year, len(r), flush=True)

# 2000
with zipfile.ZipFile('/tmp/pisa2/raw/2000_SCH.zip') as z:
    with z.open('intscho.txt') as f:
        rows = []
        for raw in io.TextIOWrapper(f, encoding='latin-1'):
            if len(raw.strip())<20: continue
            rows.append({v:(raw[a-1:b].strip() or None) for v,(a,b) in POS2000.items()})
df0 = pd.DataFrame(rows)
r0 = construye(df0, 2000, 5, 'COUNTRY', 'SCHOOLID', M2000)
frames.append(r0); print(2000, len(r0), flush=True)

res = pd.concat(frames, ignore_index=True)
res.to_parquet('/tmp/pisa2/out/pisa_internacional_centros_base.parquet', index=False, compression='zstd')
print("TOTAL centros:", len(res))
for y in sorted(res.pisa_year.unique()):
    r = res[res.pisa_year==y]
    print(y, len(r), {c:int(r[c].notna().sum()) for c in res.columns if c.startswith('cen_')})
