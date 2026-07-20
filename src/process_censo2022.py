#!/usr/bin/env python3
"""Trata os indicadores Censo 2022 e integra-os à base mestre MUNIC 2023.

O parser é baseado nos rótulos do SIDRA, pois os nomes das colunas C1..Cn
podem variar entre tabelas. Preserva valores ausentes como NaN.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_api"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def norm(text: object) -> str:
    s = "" if text is None else str(text)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())


def read_sidra(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    header = payload[0]
    rows = payload[1:]
    df = pd.DataFrame(rows).rename(columns=header)
    return df


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"-": np.nan, "..": np.nan, "...": np.nan, "X": np.nan}),
        errors="coerce",
    )


def find_col(df: pd.DataFrame, *needles: str) -> str:
    for col in df.columns:
        n = norm(col)
        if all(norm(x) in n for x in needles):
            return col
    raise KeyError(f"Coluna não encontrada: {needles}. Colunas: {list(df.columns)}")


def municipality_columns(df: pd.DataFrame) -> tuple[str, str]:
    code = find_col(df, "municipio", "codigo")
    name = find_col(df, "municipio")
    if code == name:
        candidates = [c for c in df.columns if "municipio" in norm(c)]
        code_candidates = [c for c in candidates if "codigo" in norm(c)]
        name_candidates = [c for c in candidates if "codigo" not in norm(c)]
        code = code_candidates[0]
        name = name_candidates[0]
    return code, name


def choose_total_rows(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    dimensions = [
        c for c in result.columns
        if any(k in norm(c) for k in ["sexo", "cor ou raca", "grupo de idade", "situacao do domicilio"])
    ]
    for col in dimensions:
        vals = result[col].map(norm)
        if (vals == "total").any():
            result = result[vals == "total"]
    return result


def process_income(path: Path) -> pd.DataFrame:
    df = choose_total_rows(read_sidra(path))
    code_col, name_col = municipality_columns(df)
    value_col = find_col(df, "valor")
    variable_col = next((c for c in df.columns if "variavel" in norm(c)), None)
    unit_col = next((c for c in df.columns if "unidade" in norm(c)), None)
    out = df[[code_col, name_col, value_col] + ([variable_col] if variable_col else []) + ([unit_col] if unit_col else [])].copy()
    out["codigo_ibge"] = out[code_col].astype(str).str.extract(r"(\d{7})", expand=False)
    out["municipio"] = out[name_col]
    out["valor_num"] = numeric(out[value_col])
    descriptor = out[variable_col].map(norm) if variable_col else pd.Series("", index=out.index)
    mean_mask = descriptor.str.contains("medio") & ~descriptor.str.contains("mediano")
    median_mask = descriptor.str.contains("mediano")
    result = out[["codigo_ibge", "municipio"]].drop_duplicates()
    if mean_mask.any():
        mean = out.loc[mean_mask, ["codigo_ibge", "valor_num"]].drop_duplicates("codigo_ibge")
        result = result.merge(mean.rename(columns={"valor_num": "renda_domiciliar_pc_media_2022"}), on="codigo_ibge", how="left")
    if median_mask.any():
        med = out.loc[median_mask, ["codigo_ibge", "valor_num"]].drop_duplicates("codigo_ibge")
        result = result.merge(med.rename(columns={"valor_num": "renda_domiciliar_pc_mediana_2022"}), on="codigo_ibge", how="left")
    return result


def process_rurality(path: Path) -> pd.DataFrame:
    df = read_sidra(path)
    code_col, name_col = municipality_columns(df)
    value_col = find_col(df, "valor")
    sit_col = next(c for c in df.columns if "situacao do domicilio" in norm(c))
    variable_col = next((c for c in df.columns if "variavel" in norm(c)), None)
    if variable_col:
        mask = df[variable_col].map(norm).str.contains("populacao residente")
        if mask.any():
            df = df[mask]
    df["codigo_ibge"] = df[code_col].astype(str).str.extract(r"(\d{7})", expand=False)
    df["municipio"] = df[name_col]
    df["valor_num"] = numeric(df[value_col])
    df["situacao_norm"] = df[sit_col].map(norm)
    pivot = df.pivot_table(index=["codigo_ibge", "municipio"], columns="situacao_norm", values="valor_num", aggfunc="first").reset_index()
    total_col = next((c for c in pivot.columns if c == "total"), None)
    rural_col = next((c for c in pivot.columns if "rural" in str(c)), None)
    urban_col = next((c for c in pivot.columns if "urbana" in str(c)), None)
    out = pivot[["codigo_ibge", "municipio"]].copy()
    out["populacao_total_2022"] = pivot[total_col] if total_col else np.nan
    out["populacao_rural_2022"] = pivot[rural_col] if rural_col else np.nan
    out["populacao_urbana_2022"] = pivot[urban_col] if urban_col else np.nan
    out["percentual_rural_2022"] = np.where(out["populacao_total_2022"] > 0, 100*out["populacao_rural_2022"]/out["populacao_total_2022"], np.nan)
    return out


def process_literacy(path: Path) -> pd.DataFrame:
    df = choose_total_rows(read_sidra(path))
    code_col, name_col = municipality_columns(df)
    value_col = find_col(df, "valor")
    df["codigo_ibge"] = df[code_col].astype(str).str.extract(r"(\d{7})", expand=False)
    df["municipio"] = df[name_col]
    df["taxa_alfabetizacao_15mais_2022"] = numeric(df[value_col])
    out = df[["codigo_ibge", "municipio", "taxa_alfabetizacao_15mais_2022"]].drop_duplicates("codigo_ibge")
    out["taxa_analfabetismo_15mais_2022"] = 100 - out["taxa_alfabetizacao_15mais_2022"]
    return out


def main() -> None:
    required = {
        "income": RAW / "sidra_10295_rendimento_2022.json",
        "rurality": RAW / "sidra_9923_urbano_rural_2022.json",
        "literacy": RAW / "sidra_9543_alfabetizacao_2022.json",
    }
    missing = [str(p) for p in required.values() if not p.exists()]
    if missing:
        raise SystemExit("Arquivos SIDRA ausentes:\n- " + "\n- ".join(missing) + "\nExecute src/fetch_censo2022_sidra.py.")
    income = process_income(required["income"])
    rurality = process_rurality(required["rurality"])
    literacy = process_literacy(required["literacy"])
    socio = income.merge(rurality, on=["codigo_ibge", "municipio"], how="outer").merge(literacy, on=["codigo_ibge", "municipio"], how="outer")
    socio.to_csv(PROCESSED / "censo2022_socioeconomico_pa.csv", index=False)
    master = pd.read_csv(PROCESSED / "base_mestre_com_munic_2023.csv", dtype={"codigo_ibge": str})
    master["codigo_ibge"] = master["codigo_ibge"].str.zfill(7)
    socio["codigo_ibge"] = socio["codigo_ibge"].astype(str).str.zfill(7)
    merged = master.merge(socio.drop(columns=["municipio"], errors="ignore"), on="codigo_ibge", how="left", validate="one_to_one")
    merged.to_csv(PROCESSED / "base_mestre_munic_censo2022.csv", index=False)
    coverage = {c: int(merged[c].notna().sum()) for c in socio.columns if c not in {"codigo_ibge", "municipio"}}
    summary = {"municipios_base": int(len(merged)), "cobertura_por_variavel": coverage, "observacao": "Valores ausentes foram preservados; nenhum zero foi imputado."}
    (PROCESSED / "resumo_censo2022.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
