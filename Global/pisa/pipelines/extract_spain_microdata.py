"""Extract Spain with every original variable, value label, weight and PV intact."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/Global/pisa'


def extract(source, year, output=None):
    output = output or DATA / 'processed/analysis_ready'
    output.mkdir(parents=True, exist_ok=True)
    country, meta = pyreadstat.read_sav(str(source), usecols=['CNT'])
    indices = np.flatnonzero(country.CNT.eq('ESP').to_numpy())
    if not len(indices):
        raise ValueError('Spain absent from source')
    runs = np.split(indices, np.flatnonzero(np.diff(indices) != 1) + 1)
    frames = []
    for run in runs:
        frame, meta = pyreadstat.read_sav(str(source), row_offset=int(run[0]), row_limit=len(run))
        assert frame.CNT.eq('ESP').all()
        frames.append(frame)
    frame = pd.concat(frames, ignore_index=True)
    keys = ['CNT', 'CNTSCHID', 'CNTSTUID']
    if frame.duplicated(keys).any() or frame[keys].isna().any().any():
        raise ValueError('Missing or duplicate respondent identity')
    required = ['W_FSTUWT'] + [f'W_FSTURWT{i}' for i in range(1,81)]
    required += [f'PV{i}{domain}' for domain in ['MATH','READ','SCIE'] for i in range(1,11)]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f'Missing statistical design columns: {missing}')
    frame['pisa_year'] = year
    target = output / f'spain_{year}_full.parquet'
    frame.to_parquet(target, index=False)
    with source.open('rb') as handle:
        checksum = hashlib.file_digest(handle, 'sha256').hexdigest()
    metadata = {'year':year, 'source':str(source), 'sha256':checksum,
                'rows':len(frame), 'columns':len(frame.columns),
                'labels':meta.column_names_to_labels,
                'value_labels':meta.variable_value_labels,
                'missing_ranges':meta.missing_ranges,
                'note':'Original codes; SPSS user-missing values converted to null by pyreadstat.'}
    (output/f'spain_{year}_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{year}: {len(frame)} students, {len(frame.columns)} columns -> {target}', flush=True)
    return frame


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('--year',type=int,required=True)
    args = p.parse_args()
    extract(args.source,args.year)
