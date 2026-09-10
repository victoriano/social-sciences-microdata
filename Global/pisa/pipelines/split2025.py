import os, re, pyarrow.parquet as pq
p = 'out/final_2025.parquet'
pf = pq.ParquetFile(p)
names = pf.schema_arrow.names
reps = [n for n in names if re.fullmatch(r'W_FST[A-Z]*[0-9]+', n)]
main_cols = [n for n in names if n not in reps]
pesos_cols = ['pais','CNTSCHID','CNTSTUID','W_FSTUWT'] + reps
wm = wp = None
for b in pf.iter_batches(batch_size=80000):
    t = __import__("pyarrow").Table.from_batches([b])
    tm = t.select(main_cols); tp = t.select(pesos_cols)
    if wm is None:
        wm = pq.ParquetWriter('out/final_2025_main.parquet', tm.schema, compression='zstd', compression_level=10)
        wp = pq.ParquetWriter('out/final_2025_pesos.parquet', tp.schema, compression='zstd', compression_level=10)
    wm.write_table(tm); wp.write_table(tp)
wm.close(); wp.close()
print('main', round(os.path.getsize('out/final_2025_main.parquet')/1e6,1), len(main_cols))
print('pesos', round(os.path.getsize('out/final_2025_pesos.parquet')/1e6,1), len(pesos_cols))
