#!/usr/bin/env python3
"""Merge del cuestionario de centro PISA (España) -> dataset cocinado.

Entrada: ficheros de centro descargados de la OCDE (SPSS .sav o txt),
ya filtrados a España o completos (el script filtra CNT == 'ESP').

Salida:
- pisa_espana_centros_2000_2025.parquet  (una fila por centro y ciclo)
- columnas cen_* listas para unir al cocinado por (pisa_year, CNTSCHID)

Reglas:
- Códigos de falta PISA (95-99, 995-999, 9995-9999...) a nulo.
- Categóricas a etiquetas en español; índices WLE pasan tal cual.
- Si una variable no existe en un ciclo, queda vacía (documentado en cobertura).
"""
import argparse
from pathlib import Path
import duckdb
import pandas as pd

COMUNIDAD = {"1": "Zona rural (menos de 3.000 hab.)", "2": "Pueblo pequeño (3.000-15.000)", "3": "Ciudad pequeña (15.000-100.000)", "4": "Ciudad (100.000-1M)", "5": "Ciudad grande (1M-10M)", "6": "Megaciudad (más de 10M)"}
COMPETENCIA = {"1": "Dos o más centros compiten por el alumnado", "2": "Un centro compite por el alumnado", "3": "Ningún centro compite por el alumnado"}
PUBLICO = {"1": "Público", "2": "Privado"}
TIPO = {"1": "Privado independiente", "2": "Privado concertado", "3": "Público"}
SIEMPRE = {"1": "Nunca", "2": "A veces", "3": "Siempre"}

# nombre, fuentes por ciclo (2018/2022/2025), tipo, umbral falta, mapa, descripcion, accionabilidad
ESP = [
 ("cen_comunidad", {"2015":"SC001Q01TA","2018":"SC001Q01TA","2022":"SC001Q01TA","2025":"SC001Q01TA"}, "cat", 90, COMUNIDAD,
  "Entorno del centro según tamaño del municipio (director/a).", "baja"),
 ("cen_competencia", {"2015":None,"2018":"SC011Q01TA","2022":"SC011Q01TA","2025":"SC011Q01TA"}, "cat", 90, COMPETENCIA,
  "Competencia con otros centros por el alumnado de la zona (director/a).", "baja"),
 ("cen_publico", {"2015":"SC013Q01TA","2018":"SC013Q01TA","2022":"SC013Q01TA","2025":"SC013Q01TA"}, "cat", 90, PUBLICO,
  "Centro público o privado según el director/a.", "media"),
 ("cen_tipo", {"2015":"SCHLTYPE","2018":"SCHLTYPE","2022":"SCHLTYPE","2025":"SCHLTYPE"}, "cat", 90, TIPO,
  "Tipo de centro: público, privado concertado (depende de fondos públicos) o privado independiente.", "media"),
 ("cen_alumnos", {"2015":"SC002Q01TA+SC002Q02TA","2018":"SC002Q01TA+SC002Q02TA","2022":"SC002Q01TA+SC002Q02TA","2025":None}, "suma2", 9000, None,
  "Tamaño del centro: alumnado total matriculado (chicos + chicas). Sin dato en 2025.", "baja"),
 ("cen_fin_gobierno_pct", {"2015":"SC016Q01TA","2018":"SC016Q01TA","2022":"SC016Q01TA","2025":None}, "num", 900, None,
  "% de la financiación anual del centro que viene de fondos públicos. Sin dato en 2025.", "baja"),
 ("cen_fin_cuotas_pct", {"2015":"SC016Q02TA","2018":"SC016Q02TA","2022":"SC016Q02TA","2025":None}, "num", 900, None,
  "% de la financiación anual que viene de cuotas pagadas por las familias. Sin dato en 2025.", "baja"),
 ("cen_stratio", {"2015":"STRATIO","2018":"STRATIO","2022":"STRATIO","2025":"STRATIO_Q"}, "num", 900, None,
  "Ratio alumnos por profesor del centro.", "baja"),
 ("cen_escasez_material", {"2015":"EDUSHORT","2018":"EDUSHORT","2022":"EDUSHORT","2025":"EDUSHORT"}, "num", 90, None,
  "Escasez de material educativo (WLE; valores altos = más escasez).", "baja"),
 ("cen_escasez_personal", {"2015":"STAFFSHORT","2018":"STAFFSHORT","2022":"STAFFSHORT","2025":"STAFFSHORT"}, "num", 90, None,
  "Escasez de personal docente (WLE; valores altos = más escasez).", "baja"),
 ("cen_profesorado_certificado", {"2015":"PROATCE","2018":"PROATCE","2022":"PROATCE","2025":"PROATCE"}, "num", 90, None,
  "Proporción de profesorado con certificación completa (0-1).", "baja"),
 ("cen_ordenadores_alumno", {"2015":"RATCMP1","2018":"RATCMP1","2022":"RATCMP1","2025":None}, "num", 900, None,
  "Ordenadores disponibles por alumno (ratio). Sin dato en 2025.", "baja"),
 ("cen_autonomia", {"2015":None,"2018":None,"2022":"SCHAUTO","2025":None}, "num", 90, None,
  "Autonomía del centro (WLE 2022).", "baja"),
 ("cen_participacion_prof", {"2015":None,"2018":None,"2022":"TCHPART","2025":None}, "num", 90, None,
  "Participación del profesorado en decisiones (WLE 2022).", "baja"),
 ("cen_liderazgo_educativo", {"2015":None,"2018":None,"2022":"EDULEAD","2025":"EDULEAD"}, "num", 90, None,
  "Liderazgo educativo del equipo directivo (WLE 2022/2025).", "baja"),
 ("cen_liderazgo_instruccional", {"2015":None,"2018":None,"2022":"INSTLEAD","2025":None}, "num", 90, None,
  "Liderazgo instruccional (WLE 2022).", "baja"),
 ("cen_admision_expediente", {"2015":"SC012Q01TA","2018":"SC012Q01TA","2022":"SC012Q01TA","2025":"SC012Q01TA"}, "cat", 90, SIEMPRE,
  "Frecuencia con que el centro considera el expediente académico al admitir alumnado (selectividad).", "media"),
 ("cen_padres_inmigrantes_pct", {"2015":None,"2018":None,"2022":"SC211Q05JA","2025":None}, "num", 900, None,
  "% de alumnado del curso modal con padres inmigrantes según el director/a (2022).", "baja"),
]


def cargar(path, year):
    df = pd.read_parquet(path)
    df["pisa_year"] = year
    df["CNTSCHID"] = df["CNTSCHID"].apply(lambda v: str(int(v)) if pd.notna(v) else None)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sch2015"), ap.add_argument("--sch2018"), ap.add_argument("--sch2022"), ap.add_argument("--sch2025")
    ap.add_argument("--cooked", help="cooked v2 para producir el merge a nivel alumno")
    args = ap.parse_args()
    rutas = {"2015": args.sch2015, "2018": args.sch2018, "2022": args.sch2022, "2025": args.sch2025}
    frames = []
    for year, ruta in rutas.items():
        if not ruta:
            continue
        df = cargar(ruta, year)
        out = pd.DataFrame({"pisa_year": df["pisa_year"], "CNTSCHID": df["CNTSCHID"]})
        for nombre, src, tipo, thr, mapa, desc, acc in ESP:
            s = src.get(year)
            if s is None:
                out[nombre] = None
                continue
            if tipo == "suma2":
                a, b = s.split("+")
                v = df[a] + df[b]
                out[nombre] = v.where(v.abs() < thr)
            elif tipo == "cat":
                v = pd.to_numeric(df[s], errors="coerce")
                v = v.where(v.abs() < thr)
                out[nombre] = v.astype("Int64").astype(str).map(mapa)
            else:
                v = pd.to_numeric(df[s], errors="coerce")
                out[nombre] = v.where(v.abs() < thr)
        frames.append(out)
        print(year, "centros:", len(df))
    centros = pd.concat(frames, ignore_index=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    centros.to_parquet(args.out, index=False)
    print("escrito", args.out, len(centros), "filas,", len(centros.columns), "cols")

    if args.cooked:
        con = duckdb.connect()
        tmp = args.out + ".tmp.parquet"
        centros.to_parquet(tmp, index=False)
        out_merged = str(Path(args.out).parent / "pisa_espana_2000_2025_cocinado_con_centro.parquet")
        cen_cols = [e[0] for e in ESP]
        sel = ", ".join(f's."{c}"' for c in cen_cols)
        # CNTSCHID del cocinado lleva ".0" flotante en 2000-2022; se normaliza solo para el join
        con.execute(f"""
            copy (
              select c.*, {sel}
              from read_parquet('{args.cooked}') c
              left join read_parquet('{tmp}') s
                on s.pisa_year = c.pisa_year
               and s.CNTSCHID = regexp_replace(c.CNTSCHID, '\\.0$', '')
            ) to '{out_merged}' (format parquet, compression zstd)
        """)
        import os
        os.remove(tmp)
        n = con.execute(f"select count(*) from read_parquet('{out_merged}')").fetchone()[0]
        print("cooked+centro:", out_merged, n, "filas")
    # cobertura
    for nombre, *_ in ESP:
        nn = centros.groupby("pisa_year")[nombre].apply(lambda s: s.notna().sum())
        if nn.sum() > 0:
            print(f"  {nombre}: {dict(nn)}")


if __name__ == "__main__":
    main()
