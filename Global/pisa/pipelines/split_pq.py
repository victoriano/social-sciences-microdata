import sys, pyarrow.parquet as pq
src, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
pf = pq.ParquetFile(src)
total = pf.metadata.num_rows
half = total // 2
print(f"{src}: {total} rows, {pf.metadata.num_row_groups} row groups -> split at {half}")
wa = pq.ParquetWriter(a, pf.schema_arrow, compression='zstd')
wb = None
na = nb = 0
for i in range(pf.metadata.num_row_groups):
    rg = pf.read_row_group(i)
    if na < half:
        if na + rg.num_rows <= half:
            wa.write_table(rg); na += rg.num_rows
        else:
            cut = half - na
            wa.write_table(rg.slice(0, cut)); na += cut
            wb = wb or pq.ParquetWriter(b, pf.schema_arrow, compression='zstd')
            wb.write_table(rg.slice(cut)); nb += rg.num_rows - cut
    else:
        wb = wb or pq.ParquetWriter(b, pf.schema_arrow, compression='zstd')
        wb.write_table(rg); nb += rg.num_rows
wa.close()
if wb: wb.close()
print(f"a={na} b={nb}")
