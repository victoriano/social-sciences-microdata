#!/usr/bin/env python3
"""Centros PISA 2000-2012 (Espana): txt ancho fijo + control SAS / codebook PDF 2000."""
import re, zipfile, io
import pandas as pd

MISSING = {7,8,9,95,96,97,98,99,995,996,997,998,999,9995,9996,9997,9998,9999,
           99995,99996,99997,99998,99999,9999995,9999996,9999997,9999998,9999999}

def parse_sas(path):
    txt = open(path, encoding='latin-1').read().replace('\r','')
    tipos, pos, formatos, asig = {}, {}, {}, {}
    mlen = re.search(r'(?is)length\s+(.*?);', txt)
    if mlen:
        for ln in mlen.group(1).splitlines():
            m = re.match(r'\s*(\w+)\s+\$(\d+)', ln)
            if m: tipos[m.group(1).upper()] = 's'; continue
            m = re.match(r'\s*(\w+)\s+(\d+)', ln)
            if m: tipos[m.group(1).upper()] = 'n'
    minp = re.search(r'(?is)input\s+(.*?);', txt)
    for ln in minp.group(1).splitlines():
        m = re.match(r'\s*(\w+)\s+(\d+)\s*-\s*(\d+)', ln)
        if m: pos[m.group(1).upper()] = (int(m.group(2))-1, int(m.group(3)))
    for mf in re.finditer(r'(?is)value\s+(\$?\w+)\s+(.*?);', txt):
        cuerpo = mf.group(2)
        pares = re.findall(r'"?([^"=\n]+?)"?\s*=\s*"([^"]*)"', cuerpo)
        pares += re.findall(r"'?([^'=\n]+?)'?\s*=\s*'([^']*)'", cuerpo)
        formatos[mf.group(1).upper()] = {c.strip(): l.strip() for c, l in pares}
    for mf in re.finditer(r'(?ims)^\s*format\s+(.*?);', txt):
        for ln in mf.group(1).splitlines():
            toks = ln.replace(',',' ').split()
            fmt, vs = None, []
            for t in toks:
                if re.match(r'\$?\w+\.$', t): fmt = t[:-1].upper()
                else: vs.append(t.upper())
            if fmt:
                for v in vs: asig[v] = fmt
    return tipos, pos, formatos, asig

def leer_txt(zip_path, txt_name, pos, vars_out):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(txt_name) as f:
            rows = []
            for raw in io.TextIOWrapper(f, encoding='latin-1'):
                if len(raw.strip()) < 20: continue
                r = {}
                for v in vars_out:
                    if v not in pos: r[v]=None; continue
                    a,b = pos[v]
                    r[v] = raw[a:b].strip() or None
                rows.append(r)
    return pd.DataFrame(rows)

def norm_pub_priv(e):
    e = e.lower()
    if 'independent' in e: return 'Privado independiente'
    if 'government-dependent' in e: return 'Privado concertado'
    if 'government' in e or 'public' in e: return 'Público'
    if 'private' in e: return 'Privado'
    return None

def norm_comunidad(e):
    e = e.lower()
    if 'megacity' in e: return 'Megaciudad (más de 10M)'
    if 'large city' in e or ('city' in e and 'more' in e): return 'Ciudad grande (más de 1M)'
    if 'small town' in e: return 'Pueblo pequeño (3.000-15.000)'
    if 'town' in e: return 'Ciudad pequeña (15.000-100.000)'
    if 'city' in e: return 'Ciudad (100.000-1M)'
    if 'village' in e or 'rural' in e: return 'Zona rural (menos de 3.000 hab.)'
    return None

def norm_nunca(e):
    e = e.lower()
    if 'never' in e: return 'Nunca'
    if 'sometimes' in e: return 'A veces'
    if 'always' in e: return 'Siempre'
    return None

def norm_compete(e):
    e = e.lower()
    if 'two or more' in e: return 'Dos o más centros compiten por el alumnado'
    if 'one other' in e: return 'Un centro compite por el alumnado'
    if 'no other' in e: return 'Ningún centro compite por el alumnado'
    return None

ESP_OLD = {
 2003: dict(pub='SC03Q01', tipo='SCHLTYPE', alum1='SC02Q01', alum2='SC02Q02', fin_gob='SC04Q01',
            fin_cuota='SC04Q02', comun='SC01Q01', stratio='STRATIO', profcert='PROPCERT',
            admis=None, pais='COUNTRY', width=5),  # admision 2003 usa escala PRIORF no comparable
 2006: dict(pub='SC02Q01', tipo='SCHLTYPE', alum1='SC01Q01', alum2='SC01Q02', fin_gob='SC03Q01',
            fin_cuota='SC03Q02', comun='SC07Q01', stratio='STRATIO', profcert='PROPCERT',
            admis=None, pais='COUNTRY', width=5),
 2009: dict(pub='SC02Q01', tipo='SCHTYPE', alum1='SC06Q01', alum2='SC06Q02', fin_gob='SC03Q01',
            fin_cuota='SC03Q02', comun='SC04Q01', stratio='STRATIO', profcert='PROPCERT',
            admis='SC19Q02', pais='COUNTRY', width=5),
 2012: dict(pub='SC01Q01', tipo='SCHLTYPE', alum1='SC07Q01', alum2='SC07Q02', fin_gob='SC02Q01',
            fin_cuota='SC02Q02', comun='SC03Q01', stratio='STRATIO', profcert='PROPCERT',
            admis='SC32Q01', compet='SC04Q01', pais='CNT', width=7),
}
FILES = {
 2003: ('INT_schi_2003.zip','INT_schi_2003.txt','PISA2003_SAS_school.sas'),
 2006: ('INT_Sch06_Dec07.zip','INT_Sch06_Dec07.txt','PISA2006_SAS_school.sas'),
 2009: ('INT_SCQ09_Dec11.zip','INT_SCQ09_Dec11.txt','PISA2009_SAS_school.sas'),
 2012: ('INT_SCQ12_DEC03.zip','INT_SCQ12_DEC03.txt','PISA2012_SAS_school.sas'),
}

POS2000 = {'COUNTRY':(1,4),'SCHOOLID':(4,9),'SC01Q01':(13,14),'SC02Q01':(14,18),'SC02Q02':(18,22),
 'SC03Q01':(22,23),'SC04Q01':(23,26),'SC04Q02':(26,29),'SC07Q02':(57,58),'SCHLTYPE':(298,299),
 'STRATIO':(329,334),'PROPCERT':(338,342)}
LAB2000 = {'SC01Q01':{'1':'Village','2':'Small Town','3':'Town','4':'City','5':'Large City'},
 'SC03Q01':{'1':'Public','2':'Private'},
 'SC07Q02':{'1':'Never','2':'Sometimes','3':'Always'},
 'SCHLTYPE':{'1':'Private Independent','2':'Private government-dependent','3':'Public'}}

def construir(year, df, spec, labeler):
    """df crudo -> frame armonizado. labeler(var) -> {codigo: etiqueta_ingles}."""
    out = pd.DataFrame(index=df.index)
    out['pisa_year'] = year
    out['CNTSCHID'] = df['SCHOOLID'].astype(str).str.strip().str.replace(r'\.0$','',regex=True).str.zfill(spec['width'])
    def cat(var, norm):
        if not var: return pd.Series([None]*len(df), index=df.index, dtype=object)
        lb = labeler(var)
        s = pd.to_numeric(df[var], errors='coerce')
        s = s.where(~s.isin(MISSING))
        return s.astype('Int64').astype(str).map(lambda c: norm(lb[c]) if c in lb and norm(lb[c]) else None)
    def num(var, vmax=999999):
        if not var: return pd.Series([None]*len(df), index=df.index, dtype='float64')
        s = pd.to_numeric(df[var], errors='coerce')
        return s.where(~s.isin(MISSING) & (s.abs() < vmax))
    out['cen_publico'] = cat(spec['pub'], norm_pub_priv)
    out['cen_tipo'] = cat(spec['tipo'], norm_pub_priv)
    out['cen_comunidad'] = cat(spec['comun'], norm_comunidad)
    out['cen_admision_expediente'] = cat(spec.get('admis'), norm_nunca)
    out['cen_competencia'] = cat(spec.get('compet'), norm_compete)
    a1, a2 = num(spec['alum1'], 9000), num(spec['alum2'], 9000)
    out['cen_alumnos'] = (a1 + a2).where(~(a1.isna() & a2.isna()))
    out['cen_fin_gobierno_pct'] = num(spec['fin_gob'], 900)
    out['cen_fin_cuotas_pct'] = num(spec['fin_cuota'], 900)
    out['cen_stratio'] = num(spec['stratio'], 900)
    out['cen_profesorado_certificado'] = num(spec.get('profcert'), 90)
    return out

if __name__ == '__main__':
    out_all = []
    # 2000 desde codebook
    df = leer_txt('intscho.zip','intscho.txt', POS2000, list(POS2000))
    df = df[df['COUNTRY'].str.strip()=='724']
    out_all.append(construir(2000, df, dict(ESP2000w=1, **{k:v for k,v in
        dict(pub='SC03Q01', tipo='SCHLTYPE', alum1='SC02Q01', alum2='SC02Q02', fin_gob='SC04Q01',
             fin_cuota='SC04Q02', comun='SC01Q01', stratio='STRATIO', profcert='PROPCERT',
             admis='SC07Q02', compet=None, width=5).items()}), lambda v: LAB2000.get(v, {})))
    for year,(zf,tn,sasf) in FILES.items():
        tipos, pos, formatos, asig = parse_sas(sasf)
        spec = ESP_OLD[year]
        vars_need = sorted({v for v in spec.values() if isinstance(v,str)} | {'SCHOOLID', spec['pais']})
        df = leer_txt(zf, tn, pos, vars_need)
        pv = spec['pais']
        if pv == 'CNT':
            df = df[df[pv].str.strip().str.upper()=='ESP']
        else:
            df = df[pd.to_numeric(df[pv], errors='coerce')==724]
        def labeler(var, _f=formatos, _a=asig):
            fmt = _a.get(var.upper())
            return _f.get(fmt, {}) if fmt else {}
        out_all.append(construir(year, df, spec, labeler))
    res = pd.concat(out_all, ignore_index=True)
    res.to_parquet('centros_old.parquet', index=False)
    for y in (2000,2003,2006,2009,2012):
        r = res[res.pisa_year==y]
        print(y, len(r), {c:int(r[c].notna().sum()) for c in res.columns if c.startswith('cen_')})
