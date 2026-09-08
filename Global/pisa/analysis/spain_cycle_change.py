"""Reproducible Spain 2022-2025 subgroup changes, BRR/PVs and decomposition.

Inputs are local authorised PUF extracts; outputs contain aggregate statistics.
All means are computed independently for each PV and final/80 replicate weights.
Fay BRR factor = 1/(80*(1-.5)**2); Rubin imputation variance = 1.1*Var(PV).
Cross-cycle intervals exclude linking error; subgroup-vs-rest trend contrasts
cancel the common additive linking error. Subgroup discovery uses BH FDR.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'data/Global/pisa/processed/analysis_ready'
DOMAINS = ['MATH','READ','SCIE']
WEIGHTS = ['W_FSTUWT']+[f'W_FSTURWT{i}' for i in range(1,81)]
FAMILY = ['ST300Q01JA','ST300Q05JA','ST300Q08JA','ST300Q09JA','ST300Q10JA']


def summarize(draws):
    """draws shape (81 weights, M plausible values)."""
    point = draws[0].mean()
    sampling = ((draws[1:] - draws[0])**2).sum(axis=0).mean()/20
    imputation = (1+1/draws.shape[1])*draws[0].var(ddof=1) if draws.shape[1]>1 else 0
    se = np.sqrt(sampling+imputation)
    return float(point), float(se)


def mean_draws(y,w):
    if y.ndim==1:
        y=y[:,None]
    if not np.isfinite(y).all() or not np.isfinite(w).all() or (w<0).any():
        raise ValueError('Invalid outcomes/weights')
    denom=w.sum(axis=0)
    if (denom<=0).any():
        raise ValueError('Empty replicate')
    return (w.T@y)/denom[:,None]


def difference(a,b):
    pa,sa=summarize(a); pb,sb=summarize(b)
    d=pb-pa; se=np.hypot(sa,sb)
    return d,se,d-1.96*se,d+1.96*se


def prepare(frame,year,meta):
    f=frame.copy()
    if year==2025 and f.ST004D01T.isna().all() and 'MALE' in f:
        # Spain suppresses Female/Male ST004D01T in 2025; MALE is Male/Other.
        f['sexo']=f.MALE.map({0:'No varón',1:'Varón'}).fillna('Sin dato')
    else:
        f['sexo']=f.ST004D01T.map({1:'No varón',2:'Varón'}).fillna('Sin dato')
    f['origen']=f.IMMIG.map({1:'Origen nativo',2:'Segunda generación',3:'Primera generación'}).fillna('Sin dato')
    # HISCED changed codes: 2022 has separate categories below ISCED 2.
    e=f.HISCED; low,medium,high=(3,6,10) if year==2022 else (2,5,9)
    f['educacion_familiar']=np.select([e.between(1,low),e.between(low+1,medium),e.between(medium+1,high)],['Hasta secundaria inferior','Secundaria superior/postsecundaria','Terciaria'],default='Sin dato')
    f['repeticion']=f.REPEAT.map({0:'No repetidor',1:'Repetidor'}).fillna('Sin dato') if 'REPEAT' in f else 'Sin dato'
    # REGION was recoded in 2025: harmonize LABELS, never equate numeric codes.
    region_labels={str(int(float(k))):v.removeprefix('Spain: ').replace('Castile - La Mancha','Castile-La Mancha') for k,v in meta['value_labels'].get('REGION',{}).items()}
    codes=pd.to_numeric(f.REGION,errors='coerce').fillna(-1).astype(int).astype(str)
    f['region']=codes.map(region_labels).fillna('Sin dato')
    labels=meta['value_labels'].get('STRATUM',{})
    stratum=f.STRATUM.map(labels).fillna('')
    f['sector']=np.select([stratum.str.contains('Public',case=False),stratum.str.contains('Private',case=False)],['Público','Privado/concertado'],default='Sin dato')
    escs=f.ESCS; valid=escs.between(-10,10)&f.W_FSTUWT.gt(0)
    order=np.argsort(escs[valid]); values=escs[valid].to_numpy()[order]
    w=f.W_FSTUWT[valid].to_numpy()[order]
    cuts=np.interp([.25,.5,.75],np.cumsum(w)/w.sum(),values)
    f['nivel_socioeconomico']='Sin dato'
    f.loc[valid,'nivel_socioeconomico']=['Q'+str(x+1) for x in np.searchsorted(cuts,escs[valid],side='right')]
    for c in FAMILY:
        if c in f:
            f['apoyo_'+c]=np.select([f[c].between(4,5),f[c].between(1,3)],['Semanal o diario','Menos de semanal'],default='Sin dato')
    return f


def subgroup_tables(frames, specifications=None):
    dimensions=['sexo','origen','educacion_familiar','nivel_socioeconomico','region','sector','repeticion']
    combinations=[('sexo','origen'),('sexo','educacion_familiar'),('origen','educacion_familiar'),('sexo','nivel_socioeconomico'),('origen','nivel_socioeconomico'),('sexo','origen','educacion_familiar')]
    if specifications is None:
        specifications=[(d,) for d in dimensions]+combinations+[('region','nivel_socioeconomico')]
        for col in FAMILY:
            derived='apoyo_'+col
            if all(derived in f for f in frames.values()):
                specifications.extend([(derived,),('educacion_familiar',derived)])
    results=[]; suppressed=[]
    for dims in specifications:
        keys={yr:f[list(dims)].astype(str).agg(' | '.join,axis=1) for yr,f in frames.items()}
        for key in sorted(set(keys[2022])|set(keys[2025])):
            if 'region' in dims and key.split(' | ')[dims.index('region')]=='Catalonia':
                suppressed.append({'dimensions':'region','group':key,'reason':'OECD: Catalonia not reported separately due to exclusions'})
                continue
            masks={yr:k.eq(key).to_numpy() for yr,k in keys.items()}
            counts={yr:int(m.sum()) for yr,m in masks.items()}
            schools={yr:int(frames[yr].loc[m,'CNTSCHID'].nunique()) for yr,m in masks.items()}
            if min(counts.values())<100 or min(schools.values())<10 or any(m.all() for m in masks.values()):
                suppressed.append({'dimensions':' + '.join(dims),'group':key,'n2022':counts[2022],'n2025':counts[2025]}); continue
            for domain in DOMAINS:
                samples={}; contrasts={}; shares={}; neff={}
                for yr,f in frames.items():
                    mask=masks[yr]; y=f[[f'PV{i}{domain}' for i in range(1,11)]].to_numpy(float)
                    w=f[WEIGHTS].to_numpy(float)
                    samples[yr]=mean_draws(y[mask],w[mask])
                    contrasts[yr]=samples[yr]-mean_draws(y[~mask],w[~mask])
                    shares[yr]=w[mask,0].sum()/w[:,0].sum()
                    neff[yr]=w[mask,0].sum()**2/(w[mask,0]**2).sum()
                change,se,lo,hi=difference(samples[2022],samples[2025])
                interaction,ise,ilo,ihi=difference(contrasts[2022],contrasts[2025])
                results.append({'dimensions':' + '.join(dims),'group':key,'domain':domain,
                    'n2022':counts[2022],'n2025':counts[2025],'schools2022':schools[2022],'schools2025':schools[2025],
                    'effective_n2022':neff[2022],'effective_n2025':neff[2025],
                    'share2022':shares[2022],'share2025':shares[2025],
                    'mean2022':summarize(samples[2022])[0],'mean2025':summarize(samples[2025])[0],
                    'change':change,'se_change':se,'ci_low':lo,'ci_high':hi,
                    'change_vs_rest':interaction,'se_vs_rest':ise,'p_vs_rest':2*norm.sf(abs(interaction/ise)) if ise>0 else 1,
                    'within_contribution':.5*(shares[2022]+shares[2025])*change})
    result=pd.DataFrame(results)
    if result.empty: return result,pd.DataFrame(suppressed)
    result['q_vs_rest']=multipletests(result.p_vs_rest,method='fdr_bh')[1]
    result['interval_scope']='sampling_and_PV_only_excludes_linking_error'
    return result,pd.DataFrame(suppressed)


def decomposition(frames,dims,domain):
    """Symmetric Kitagawa decomposition, including missing and pooled sparse cells."""
    keys={yr:f[list(dims)].astype(str).agg(' | '.join,axis=1) for yr,f in frames.items()}
    counts={yr:k.value_counts() for yr,k in keys.items()}
    retain={k for k in set(keys[2022])|set(keys[2025]) if min(counts[2022].get(k,0),counts[2025].get(k,0))>=100}
    keys={yr:k.where(k.isin(retain),'Otros grupos (celdas pequeñas)') for yr,k in keys.items()}
    cells=sorted(set(keys[2022])|set(keys[2025]))
    mu={}; shares={}
    for yr,f in frames.items():
        w=f[WEIGHTS].to_numpy(float); y=f[[f'PV{i}{domain}' for i in range(1,11)]].to_numpy(float)
        mu[yr]=[]; shares[yr]=[]
        for cell in cells:
            mask=keys[yr].eq(cell).to_numpy()
            if not mask.any(): raise ValueError('No common support for decomposition')
            mu[yr].append(mean_draws(y[mask],w[mask]))
            shares[yr].append((w[mask].sum(axis=0)/w.sum(axis=0))[:,None])
        mu[yr]=np.array(mu[yr]); shares[yr]=np.array(shares[yr])
    comp=(shares[2025]-shares[2022])*(mu[2025]+mu[2022])/2
    within=(shares[2025]+shares[2022])*(mu[2025]-mu[2022])/2
    # Point estimates only for decomposition; no SE from pairing independent cycles.
    total_comp=comp[:,0,:].mean(axis=1)
    total_within=within[:,0,:].mean(axis=1)
    direct=summarize(mean_draws(frames[2025][[f'PV{i}{domain}' for i in range(1,11)]].to_numpy(),frames[2025][WEIGHTS].to_numpy()))[0]-summarize(mean_draws(frames[2022][[f'PV{i}{domain}' for i in range(1,11)]].to_numpy(),frames[2022][WEIGHTS].to_numpy()))[0]
    assert np.isclose(total_comp.sum()+total_within.sum(),direct,atol=1e-7)
    return [{'dimensions':' + '.join(dims),'domain':domain,'group':c,'composition':float(a),'within':float(b)} for c,a,b in zip(cells,total_comp,total_within)]


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    frames={}; metadata={}
    for yr in [2022,2025]:
        metadata[yr]=json.loads((DATA/f'spain_{yr}_metadata.json').read_text())
        frames[yr]=prepare(pd.read_parquet(DATA/f'spain_{yr}_full.parquet'),yr,metadata[yr])
        assert (frames[yr].W_FSTUWT>0).all()
        for dimension in ['sexo','region','educacion_familiar','origen']:
            if frames[yr][dimension].eq('Sin dato').all():
                raise ValueError(f'{yr}: no usable {dimension}; check schema/labels')
    # Union is a repeated cross-section; original variables and missingness retained.
    pl.concat([pl.from_pandas(f) for f in frames.values()],how='diagonal_relaxed').write_parquet(DATA/'spain_2022_2025_full.parquet')
    overall=[]
    for domain in DOMAINS:
        draws={yr:mean_draws(f[[f'PV{i}{domain}' for i in range(1,11)]].to_numpy(),f[WEIGHTS].to_numpy()) for yr,f in frames.items()}
        change,se,lo,hi=difference(draws[2022],draws[2025])
        overall.append({'domain':domain,'mean2022':summarize(draws[2022])[0],'mean2025':summarize(draws[2025])[0],'change':change,'se_change':se,'ci_low':lo,'ci_high':hi,'interval_scope':'sampling_and_PV_only_excludes_linking_error'})
    pd.DataFrame(overall).to_csv(output/'national_changes.csv',index=False)
    print(pd.DataFrame(overall).to_string(index=False),flush=True)
    groups,suppressed=subgroup_tables(frames)
    groups.to_csv(output/'subgroup_changes.csv',index=False)
    suppressed.to_csv(output/'suppressed_groups.csv',index=False)
    print(f'{len(groups)} subgroup/domain comparisons',flush=True)
    decompositions=[]
    specs=[('sexo','origen','educacion_familiar'),('sexo','origen'),('sexo','origen','nivel_socioeconomico'),('sector',),('origen',),('educacion_familiar',)]
    # Do not decompose by family-item response status: administration coverage
    # differs sharply across cycles, and missing is not a comparable behavior.
    for dims in specs:
        for domain in DOMAINS:
            decompositions.extend(decomposition(frames,dims,domain))
    pd.DataFrame(decompositions).to_csv(output/'composition_decomposition.csv',index=False)
    family=[]
    for col in FAMILY:
        if not all(col in f for f in frames.values()): continue
        for yr,f in frames.items():
            valid=f[col].between(1,5)
            if not valid.any(): continue
            draws=mean_draws(f.loc[valid,col].ge(4).to_numpy(float),f.loc[valid,WEIGHTS].to_numpy())
            point,se=summarize(draws)
            family.append({'year':yr,'variable':col,'question':metadata[yr]['labels'].get(col),
                           'weekly_share':point,'se':se,'valid_n':int(valid.sum()),
                           'weighted_missing_share':float(f.loc[~valid,'W_FSTUWT'].sum()/f.W_FSTUWT.sum())})
    pd.DataFrame(family).to_csv(output/'family_support.csv',index=False)
    coverage=[]
    for yr,f in frames.items():
        for col in ['IMMIG','HISCED','ESCS','FAMSUP','REPEAT']+FAMILY:
            coverage.append({'year':yr,'column':col,'present':col in f,'non_null':int(f[col].notna().sum()) if col in f else 0})
    pd.DataFrame(coverage).to_csv(output/'variable_coverage.csv',index=False)
    print('Finished:',output,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/Global/pisa/analysis/2025')
    args=parser.parse_args()
    run(args.output_dir)
