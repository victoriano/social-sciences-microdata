#!/usr/bin/env python3
"""Small, schema-first example for the public PISA Spain publication.

The script deliberately does not contain a dataset URL or a list of assumed
columns. It reads those from a manifest, inspects the advertised schema, and
only computes a demonstration when it can discover plausible-value and weight
columns in the selected file.  Parquet is read in batches and only selected
columns are projected; CSV is read with a chunksize.  A cooked file normally
has no individual PVs, so the script will print the schema and explain why the
full PUF is needed for the weighted example.

Examples:
    python analysis_example.py --manifest 'https://victoriano.me/pisa/manifest.json' --year 2025
    python analysis_example.py --manifest 'https://victoriano.me/pisa/manifest.json' \
        --dataset cooked --year 2025 --show-metadata

Dependencies for the optional calculation: pandas and numpy.  Parquet input
also needs pyarrow (and fsspec for a remote Parquet URL).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


PV_RE = re.compile(r"^PV(\d+)(MATH|READ|SCIE)$", re.I)
PV_ALT_RE = re.compile(r"^PV(MATH|READ|SCIE)(\d+)$", re.I)
REPLICATE_RE = re.compile(r"^W_FSTURWT(\d+)$", re.I)
YEAR_NAMES = ("pisa_year", "year", "YEAR", "cycle", "CYCLE")


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def fetch_json(location: str) -> Any:
    """Read a JSON URL/path without exposing credentials or redirect fragments."""
    if is_url(location):
        request = Request(location, headers={"User-Agent": "pisa-public-analysis-example/1"})
        with urlopen(request, timeout=60) as response:  # nosec B310: caller supplies public URL
            return json.load(response)
    return json.loads(Path(location).read_text(encoding="utf-8"))


def relative_location(value: str, manifest_location: str) -> str:
    if is_url(value) or Path(value).is_absolute():
        return value
    if is_url(manifest_location):
        return urljoin(manifest_location, value)
    return str((Path(manifest_location).parent / value).resolve())


def _candidate_entries(value: Any, key: str = "") -> Iterator[dict[str, Any]]:
    """Yield resource-like dicts from common manifest layouts.

    The canonical publication uses ``datasets`` entries. The small amount of
    fallback handling makes the example useful if a static host wraps those
    entries in ``resources`` or ``files`` without changing the data contract.
    """
    if isinstance(value, dict):
        looks_like_resource = any(
            k in value for k in ("url", "href", "download_url", "path", "location")
        ) and any(k in value for k in ("id", "name", "format", "role", "type", "metadata_url", "schema"))
        if looks_like_resource:
            entry = dict(value)
            if key and "id" not in entry:
                entry["id"] = key
            yield entry
        for nested_key, nested in value.items():
            if nested_key in {"datasets", "resources", "files", "artifacts", "data"} or isinstance(nested, (dict, list)):
                yield from _candidate_entries(nested, nested_key)
    elif isinstance(value, list):
        for item in value:
            yield from _candidate_entries(item, key)


def entries_from_manifest(manifest: Any) -> list[dict[str, Any]]:
    entries = list(_candidate_entries(manifest))
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        identity = (str(entry.get("id", entry.get("name", ""))), str(entry.get("url", entry.get("path", ""))))
        if identity not in seen:
            unique.append(entry)
            seen.add(identity)
    return unique


def entry_location(entry: dict[str, Any], manifest_location: str) -> str | None:
    for key in ("url", "href", "download_url", "path", "location"):
        value = entry.get(key)
        if isinstance(value, str) and value:
            return relative_location(value, manifest_location)
    return None


def entry_format(entry: dict[str, Any], location: str) -> str:
    declared = entry.get("format") or entry.get("type")
    if isinstance(declared, str):
        declared = declared.lower().split(";")[0].strip()
        if declared in {"parquet", "csv", "json", "jsonl", "ndjson"}:
            return declared
    suffix = Path(urlparse(location).path).suffix.lower()
    return {".parquet": "parquet", ".csv": "csv", ".json": "json", ".jsonl": "jsonl", ".ndjson": "ndjson"}.get(suffix, "unknown")


def choose_entry(entries: list[dict[str, Any]], requested: str | None) -> dict[str, Any]:
    if not entries:
        raise ValueError("El manifest no contiene entradas de dataset con URL/ruta y esquema.")
    if requested:
        exact = [e for e in entries if str(e.get("id", e.get("name", ""))).casefold() == requested.casefold()]
        if exact:
            return exact[0]
        matching = [e for e in entries if requested.casefold() in json.dumps(e, ensure_ascii=False).casefold()]
        if matching:
            return matching[0]
        available = ", ".join(str(e.get("id", e.get("name", "(sin id)"))) for e in entries)
        raise ValueError(f"No se encontró dataset {requested!r}. Disponibles: {available}")
    cooked = [e for e in entries if any(token in json.dumps(e, ensure_ascii=False).casefold() for token in ("cooked", "small", "explor"))]
    return cooked[0] if cooked else entries[0]


def schema_from_entry(entry: dict[str, Any]) -> list[str]:
    schema = entry.get("schema")
    if isinstance(schema, list):
        names: list[str] = []
        for item in schema:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("column")
                if name:
                    names.append(str(name))
        return names
    if isinstance(schema, dict):
        columns = schema.get("columns") or schema.get("fields")
        if isinstance(columns, (list, dict)):
            return schema_from_entry({"schema": columns})
        return [str(k) for k in schema if k not in {"types", "dtypes"}]
    columns = entry.get("columns")
    if isinstance(columns, list):
        return [str(c.get("name", c) if isinstance(c, dict) else c) for c in columns]
    return []


def inspect_file(location: str, fmt: str, advertised: list[str]) -> list[str]:
    """Inspect physical columns, falling back to manifest schema when needed."""
    if fmt == "parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError:
            return advertised
        if is_url(location):
            try:
                import fsspec
            except ImportError:
                return advertised
            with fsspec.open(location, "rb") as handle:
                return list(pq.ParquetFile(handle).schema.names)
        return list(pq.ParquetFile(location).schema.names)
    if fmt == "csv":
        if is_url(location):
            with urlopen(location, timeout=60) as handle:  # nosec B310: caller supplies public URL
                line = handle.readline().decode("utf-8-sig")
        else:
            with Path(location).open("r", encoding="utf-8-sig", newline="") as handle:
                line = handle.readline()
        return [str(name) for name in next(csv.reader([line]))] if line else advertised
    return advertised


def metadata_location(entry: dict[str, Any], manifest_location: str) -> str | None:
    for key in ("metadata_url", "metadataUrl", "metadata_href", "metadata"):
        value = entry.get(key)
        if isinstance(value, str):
            return relative_location(value, manifest_location)
    return None


def metadata_from_manifest(manifest: Any, entry: dict[str, Any], manifest_location: str) -> dict[str, str]:
    """Return public metadata links, including the site's files/metadata layout."""
    links: dict[str, str] = {}
    direct = metadata_location(entry, manifest_location)
    if direct:
        links["dataset"] = direct
    if isinstance(manifest, dict) and isinstance(manifest.get("metadata"), dict):
        for key, value in manifest["metadata"].items():
            if isinstance(value, str):
                links[str(key)] = relative_location(value, manifest_location)
    return links


def discover_pvs(columns: Iterable[str]) -> dict[str, list[str]]:
    found: dict[str, list[tuple[int, str]]] = {domain: [] for domain in ("MATH", "READ", "SCIE")}
    for column in columns:
        match = PV_RE.match(column) or PV_ALT_RE.match(column)
        if not match:
            continue
        if PV_RE.match(column):
            number, domain = int(match.group(1)), match.group(2).upper()
        else:
            domain, number = match.group(1).upper(), int(match.group(2))
        found[domain].append((number, column))
    return {domain: [column for _, column in sorted(values)] for domain, values in found.items() if values}


def discover_weights(columns: Iterable[str]) -> list[str]:
    final = next((c for c in columns if c.upper() == "W_FSTUWT"), None)
    reps = sorted(
        ((int(match.group(1)), column) for column in columns if (match := REPLICATE_RE.match(column))),
        key=lambda item: item[0],
    )
    return ([final] if final else []) + [column for _, column in reps]


def iter_batches(location: str, fmt: str, columns: list[str], batch_size: int = 10_000,
                 year_column: str | None = None, year: int | None = None) -> Iterator[Any]:
    if fmt == "parquet":
        import pyarrow.parquet as pq
        def read_selected(parquet):
            groups = list(range(parquet.num_row_groups))
            if year_column and year is not None:
                column_index = parquet.schema.names.index(year_column)
                selected_groups = []
                for group in groups:
                    stats = parquet.metadata.row_group(group).column(column_index).statistics
                    # Missing statistics cannot safely exclude a row group.
                    if stats is None or not stats.has_min_max or stats.min <= year <= stats.max:
                        selected_groups.append(group)
                groups = selected_groups
            yield from parquet.iter_batches(batch_size=batch_size, columns=columns, row_groups=groups)
        if is_url(location):
            import fsspec
            with fsspec.open(location, "rb") as handle:
                yield from read_selected(pq.ParquetFile(handle))
        else:
            yield from read_selected(pq.ParquetFile(location))
        return
    if fmt == "csv":
        import pandas as pd
        yield from pd.read_csv(location, usecols=columns, chunksize=batch_size)
        return
    raise ValueError(f"El ejemplo no transmite formato {fmt!r}; usa Parquet o CSV según el manifest.")


def weighted_demo(
    location: str,
    fmt: str,
    columns: list[str],
    year_column: str | None,
    year: int | None,
    fay_factor: float | None,
) -> dict[str, Any]:
    if year is None:
        return {"status": "schema_only", "reason": "Pasa --year 2022 o --year 2025; no se permite mezclar ciclos en este ejemplo."}
    if year not in {2022, 2025}:
        return {"status": "schema_only", "reason": "Este ejemplo de inferencia está limitado a 2022/2025; consulta ANALYSIS_GUIDE.md para ciclos históricos."}
    pvs = discover_pvs(columns)
    weights = discover_weights(columns)
    if not pvs or len(weights) < 2:
        return {"status": "schema_only", "reason": "Se requieren PV individuales y peso final más réplicas; cambia al PUF completo."}
    try:
        import numpy as np
    except ImportError:
        return {"status": "schema_only", "reason": "La inspección funcionó, pero el cálculo requiere numpy."}
    if not year_column and year is not None:
        return {"status": "schema_only", "reason": "Se pidió un año, pero el esquema no tiene columna de ciclo."}
    selected = ([year_column] if year_column else []) + sorted(set(sum(pvs.values(), []) + weights))
    domains: dict[str, dict[str, np.ndarray]] = {}
    counts = 0
    for batch in iter_batches(location, fmt, selected, year_column=year_column, year=year):
        if hasattr(batch, "to_pandas"):
            frame = batch.to_pandas()
        else:
            frame = batch
        if year is not None:
            frame = frame[frame[year_column].astype("Int64") == year]
        if frame.empty:
            continue
        counts += len(frame)
        w = frame[weights].to_numpy(dtype=float)
        for domain, score_columns in pvs.items():
            y = frame[score_columns].to_numpy(dtype=float)
            numerator = domains.setdefault(domain, {"num": np.zeros((len(weights), len(score_columns))), "den": np.zeros((len(weights), len(score_columns)))})
            valid = np.isfinite(y[:, None, :]) & np.isfinite(w[:, :, None]) & (w[:, :, None] >= 0)
            numerator["num"] += np.where(valid, w[:, :, None] * y[:, None, :], 0).sum(axis=0)
            numerator["den"] += np.where(valid, w[:, :, None], 0).sum(axis=0)
    result: dict[str, Any] = {"status": "ok", "rows_used": counts, "weights": len(weights), "plausible_values": {k: len(v) for k, v in pvs.items()}}
    for domain, arrays in domains.items():
        draws = arrays["num"] / np.where(arrays["den"] > 0, arrays["den"], np.nan)
        m = draws.shape[1]
        point = float(np.nanmean(draws[0]))
        # Do not infer Fay-BRR from a column count. The caller must confirm the
        # factor in the published design metadata and pass it explicitly.
        if fay_factor is not None and len(weights) == 81 and 0 <= fay_factor < 1:
            denominator = len(weights[1:]) * (1 - fay_factor) ** 2
            sampling = float(np.nanmean(np.nansum((draws[1:] - draws[0]) ** 2, axis=0) / denominator))
            imputation = float((1 + 1 / m) * np.nanvar(draws[0], ddof=1)) if m > 1 else 0.0
            result[domain] = {"weighted_mean": point, "se_fay_brr_plus_pv": float(np.sqrt(sampling + imputation)), "pv_means": [float(x) for x in draws[0]]}
        else:
            result[domain] = {"weighted_mean": point, "pv_means": [float(x) for x in draws[0]], "se": None, "note": "No se calculó Fay-BRR: confirma el factor en metadata y pásalo con --fay-factor."}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="URL o ruta local de manifest.json")
    parser.add_argument("--dataset", help="id (o texto distintivo) del dataset; por defecto se prefiere cooked/small")
    parser.add_argument("--year", type=int, help="ciclo a filtrar; solo si el esquema declara columna de ciclo")
    parser.add_argument("--fay-factor", type=float, help="factor Fay confirmado en la metadata (p. ej. 0.5); sin él solo se muestran medias")
    parser.add_argument("--show-metadata", action="store_true", help="mostrar las claves principales de metadata")
    parser.add_argument("--all-columns", action="store_true", help="imprimir todos los nombres (por defecto solo una vista previa)")
    args = parser.parse_args()

    try:
        manifest = fetch_json(args.manifest)
        entries = entries_from_manifest(manifest)
        entry = choose_entry(entries, args.dataset)
        location = entry_location(entry, args.manifest)
        if not location:
            raise ValueError("La entrada elegida no declara url/path.")
        fmt = entry_format(entry, location)
        advertised = schema_from_entry(entry)
        columns = inspect_file(location, fmt, advertised)
        print(json.dumps({"dataset_id": entry.get("id", entry.get("name")), "format": fmt, "url": location, "columns": len(columns), "schema_source": "physical_file" if fmt in {"parquet", "csv"} and columns else "manifest"}, ensure_ascii=False, indent=2))
        if args.all_columns or len(columns) <= 120:
            print("Columnas:", ", ".join(columns))
        else:
            print("Columnas (vista previa):", ", ".join(columns[:60]), "...", ", ".join(columns[-20:]))
            print(f"(Se omiten {len(columns) - 80}; usa --all-columns para verlas todas.)")
        metadata_links = metadata_from_manifest(manifest, entry, args.manifest)
        if args.show_metadata and metadata_links:
            print("Enlaces de metadata:", json.dumps(metadata_links, ensure_ascii=False, indent=2))
        year_column = next((name for name in YEAR_NAMES if name in columns), None)
        print(json.dumps(weighted_demo(location, fmt, columns, year_column, args.year, args.fay_factor), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, ImportError, KeyError, TypeError) as error:
        print(f"Error controlado: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
