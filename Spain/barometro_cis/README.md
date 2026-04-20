# Barómetro del CIS 🇪🇸

Pipelines to download and harmonise the monthly microdata from the
**Centro de Investigaciones Sociológicas (CIS)** Barómetros.

Each Barómetro is a public-opinion survey with 100+ questions on politics,
economy and society. The pipeline covers everything from catalogue discovery
to a clean Parquet dataset ready for analysis.

## 📁 Folder layout

```
Spain/barometro_cis/
├── config.py                    ← URLs, paths, variable groupings
├── pipelines/
│   ├── fetch_index.py           ← Fetch the catalogue of all Barómetros
│   ├── download_raw.py          ← Download + unzip SAV files for a date range
│   ├── merge_sav.py             ← Merge SAV files into one labeled parquet
│   ├── preprocess.py            ← Reorder, type, and write final Parquet
│   ├── upload_hf.py             ← Publish processed + raw to HuggingFace
│   └── update.py                ← One-command orchestrator (idempotent)
├── utils/
│   └── spss_reader.py           ← Helpers to read .sav files with labels
├── analysis/                    ← Ad-hoc analysis scripts (TBD)
└── docs/
    └── data_sources.md          ← Endpoints and raw-data layout
```

## 📥 Consume directly from HuggingFace

The processed parquet is published on the public
[`victoriano/social-sciences-microdata`](https://huggingface.co/datasets/victoriano/social-sciences-microdata)
dataset under `spain/barometro_cis/`:

```python
from huggingface_hub import hf_hub_download
import pandas as pd

path = hf_hub_download(
    repo_id="victoriano/social-sciences-microdata",
    filename="spain/barometro_cis/processed_barometros.parquet",
    repo_type="dataset",
)
df = pd.read_parquet(path)
```

Raw `MD{codigo}` archives live in the private
`victoriano/barometro-cis-raw` mirror.

## 🚀 Quick start

Run every step from the repository root so the ``Spain.barometro_cis`` imports
resolve (or use ``uv run -m`` as shown below).

For a monthly refresh, one command is enough:

```bash
uv run python -m Spain.barometro_cis.pipelines.update --since 2020
# add --upload all to also publish to HuggingFace after the refresh
```

Each sub-step can still be run individually:

```bash
# 1. Catalogue of all Barómetros ever published
uv run python -m Spain.barometro_cis.pipelines.fetch_index

# 2. Download raw SAV packages for the months you need
uv run python -m Spain.barometro_cis.pipelines.download_raw \
    --start 01/2023 --end 07/2024

# 3. Merge into a labeled parquet (optionally drop sparse columns)
uv run python -m Spain.barometro_cis.pipelines.merge_sav \
    --start 01/2023 --end 07/2024 --filter-nans

# 4. Final preprocessing → Parquet
uv run python -m Spain.barometro_cis.pipelines.preprocess

# 5. Publish to HuggingFace (requires HF_TOKEN or huggingface-cli login)
uv run python -m Spain.barometro_cis.pipelines.upload_hf --processed
```

Artifacts land under ``data/Spain/barometro_cis/`` (see
``config.DATA_DIR``), which is git-ignored.

## 📦 Dependencies

``pandas``, ``requests``, ``python-dateutil``, ``pyreadstat``, ``pyarrow``.
