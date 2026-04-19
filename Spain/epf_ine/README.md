# Encuesta de Presupuestos Familiares (EPF) 🇪🇸

Pipelines to download and process INE's **Encuesta de Presupuestos Familiares**
(household budget survey) for every year since 2016.

## 📁 Folder layout

```
Spain/epf_ine/
├── config.py                            ← URLs, paths, household columns
├── pipelines/
│   ├── download_raw.py                  ← Download + extract SPSS files for a year range
│   ├── spss_to_parquet.py               ← Convert .sav files to labeled Parquet/CSV
│   ├── process_fixed_width_2023.py      ← Parse the 2023 fixed-width files
│   ├── enrich_2023.py                   ← Add label columns to 2023 CSVs
│   └── build_gastos_master.py           ← Build the joined gastos master Parquet
├── utils/
│   ├── fixed_width_specs.py             ← Column specs for the 2023 text files
│   └── label_mappings.py                ← Code → label mappings (miembros, gastos, hogares)
├── analysis/                            ← Ad-hoc analysis scripts (TBD)
└── docs/
    └── data_sources.md                  ← Endpoints, format history, design registers
```

## 🚀 Quick start

Run the pipelines from the repository root:

```bash
# 1. Download + extract SPSS files for every year from 2016 onward
uv run python -m Spain.epf_ine.pipelines.download_raw --years 2016 2017 2018 2019 2020 2021 2022

# 2. Convert each .sav file to Parquet (per-year sub-folder)
uv run python -m Spain.epf_ine.pipelines.spss_to_parquet --format parquet

# 3. Handle 2023 separately (fixed-width files)
uv run python -m Spain.epf_ine.pipelines.process_fixed_width_2023
uv run python -m Spain.epf_ine.pipelines.enrich_2023

# 4. Build the gastos master file
uv run python -m Spain.epf_ine.pipelines.build_gastos_master
```

Artifacts land under ``data/Spain/epf_ine/`` (see ``config.DATA_DIR``), which
is git-ignored.

## 📦 Dependencies

``pandas``, ``pyreadstat``, ``pyarrow``, ``requests``, ``tqdm``.
