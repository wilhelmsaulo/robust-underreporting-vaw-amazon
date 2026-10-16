#!/usr/bin/env python3
"""Ablate the institutional-fragility condition from the 216-scenario model.

The script reproduces the scenario construction in ``robust_underreporting_v17.py``
and compares two specifications:

1. joint: institutional fragility AND low reporting visibility AND persistence;
2. visibility-only: low reporting visibility AND persistence.

It never overwrites the manuscript outputs. All files are written with the
``ablation_fragility_v26`` suffix in ``data/processed/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

REQUIRED = {
    "ici": PROC / "ici_mulheres_robustez_cenarios.csv",
    "rates": PROC / "codec_resumo_taxas_municipio_natureza_2022_2025.csv",
    "annual": PROC / "codec_taxas_100mil_mulheres_2022_2025.csv",
}

ICI_COLS = {
    "base_v4": "ici_base_v4",
    "pesos_iguais": "ici_pesos_iguais",
    "prioridade_servicos": "ici_prioridade_servicos",
    "prioridade_governanca": "ici_prioridade_governanca",
}

SPECS = {
    "recorrentes_3": [
        "Lesão corporal - violência doméstica",
        "Estupro",
        "Estupro de vulnerável",
    ],
    "sexuais_2": ["Estupro", "Estupro de vulnerável"],
    "quatro_naturezas": [
        "Feminicídio",
        "Lesão corporal - violência doméstica",
        "Estupro",
        "Estupro de vulnerável",
    ],
}

FRAG_QS = [0.67, 0.70, 0.75]
VIS_QS = [0.25, 0.33, 0.40]
PERSISTENCE_REQS = [2, 3]


def robustness_class(values: pd.Series) -> pd.Series:
    return pd.cut(
        values,
        bins=[-0.01, 10, 30, 60, 100],
        labels=["Sem sinal robusto", "Sinal fraco", "Sinal moderado", "Sinal forte"],
        include_lowest=True,
    )


def require_inputs() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED.values() if not path.exists()]
    if missing:
        formatted = "\n - ".join(missing)
        raise FileNotFoundError(
            "The ablation requires the authorized processed municipal inputs:\n"
            f" - {formatted}\n"
            "These files are intentionally absent from the public repository."
        )


def main() -> None:
    require_inputs()

    ici = pd.read_csv(REQUIRED["ici"], dtype={"codigo_ibge": str})
    rates = pd.read_csv(REQUIRED["rates"], dtype={"codigo_ibge": str})
    annual_raw = pd.read_csv(REQUIRED["annual"], dtype={"codigo_ibge": str})

    pivot_pct = rates.pivot(
        index=["codigo_ibge", "municipio"],
        columns="natureza",
        values="percentil_estadual_taxa",
    ).reset_index()

    annual_raw["percentil_anual_natureza"] = (
        annual_raw.groupby(["ano", "natureza"])["taxa_100mil_mulheres"]
        .rank(pct=True, method="average")
        .mul(100)
    )
    annual = annual_raw.pivot_table(
        index=["codigo_ibge", "municipio", "ano"],
        columns="natureza",
        values="percentil_anual_natureza",
        aggfunc="mean",
    ).reset_index()

    base = ici[["codigo_ibge", "municipio", *ICI_COLS.values()]].copy()
    base = base.merge(pivot_pct, on=["codigo_ibge", "municipio"], how="left", validate="one_to_one")

    for spec, natures in SPECS.items():
        base[f"vis_{spec}"] = base[natures].mean(axis=1)
        annual[f"vis_{spec}"] = annual[natures].mean(axis=1)

    scenario_rows: list[dict] = []
    joint_columns: list[np.ndarray] = []
    visibility_columns: list[np.ndarray] = []
    scenario_id = 0

    for ici_name, ici_col in ICI_COLS.items():
        fragility = 100 - base[ici_col]
        for spec in SPECS:
            vis_col = f"vis_{spec}"
            for frag_q in FRAG_QS:
                frag_cut = float(fragility.quantile(frag_q))
                fragility_pass = fragility >= frag_cut
                for vis_q in VIS_QS:
                    vis_cut = float(base[vis_col].quantile(vis_q))
                    annual_cut = annual.groupby("ano")[vis_col].transform(lambda s: s.quantile(vis_q))
                    low_years = (
                        annual.assign(low=annual[vis_col] <= annual_cut)
                        .groupby("codigo_ibge")["low"]
                        .sum()
                    )
                    for persistence in PERSISTENCE_REQS:
                        scenario_id += 1
                        persistent_low = (
                            (base[vis_col] <= vis_cut)
                            & (base["codigo_ibge"].map(low_years).fillna(0) >= persistence)
                        )
                        joint = fragility_pass & persistent_low
                        removed = persistent_low & ~fragility_pass

                        joint_columns.append(joint.to_numpy(dtype=np.uint8))
                        visibility_columns.append(persistent_low.to_numpy(dtype=np.uint8))
                        scenario_rows.append(
                            {
                                "cenario_id": scenario_id,
                                "cenario_ici": ici_name,
                                "especificacao_visibilidade": spec,
                                "quantil_fragilidade": frag_q,
                                "corte_fragilidade": frag_cut,
                                "municipios_que_passam_fragilidade": int(fragility_pass.sum()),
                                "quantil_baixa_visibilidade": vis_q,
                                "corte_visibilidade": vis_cut,
                                "min_anos_baixa_visibilidade": persistence,
                                "sinalizados_modelo_conjunto": int(joint.sum()),
                                "sinalizados_sem_fragilidade": int(persistent_low.sum()),
                                "removidos_pela_fragilidade": int(removed.sum()),
                            }
                        )

    joint_matrix = np.vstack(joint_columns).T
    visibility_matrix = np.vstack(visibility_columns).T
    if joint_matrix.shape != (len(base), 216):
        raise AssertionError(f"Unexpected joint matrix shape: {joint_matrix.shape}")

    municipal = base[["codigo_ibge", "municipio"]].copy()
    municipal["cenarios_conjuntos"] = joint_matrix.sum(axis=1)
    municipal["frequencia_conjunta_pct"] = municipal["cenarios_conjuntos"] / 216 * 100
    municipal["classe_conjunta"] = robustness_class(municipal["frequencia_conjunta_pct"])
    municipal["cenarios_sem_fragilidade"] = visibility_matrix.sum(axis=1)
    municipal["frequencia_sem_fragilidade_pct"] = municipal["cenarios_sem_fragilidade"] / 216 * 100
    municipal["classe_sem_fragilidade"] = robustness_class(municipal["frequencia_sem_fragilidade_pct"])
    municipal["cenarios_removidos_pela_fragilidade"] = (
        municipal["cenarios_sem_fragilidade"] - municipal["cenarios_conjuntos"]
    )
    municipal["diferenca_frequencia_pontos_pct"] = (
        municipal["frequencia_sem_fragilidade_pct"] - municipal["frequencia_conjunta_pct"]
    )
    municipal["mudanca_de_classe"] = (
        municipal["classe_conjunta"].astype(str) != municipal["classe_sem_fragilidade"].astype(str)
    )
    municipal = municipal.sort_values(
        ["diferenca_frequencia_pontos_pct", "frequencia_sem_fragilidade_pct", "municipio"],
        ascending=[False, False, True],
    )

    scenarios = pd.DataFrame(scenario_rows)
    effective = (
        scenarios.groupby(
            ["especificacao_visibilidade", "quantil_baixa_visibilidade", "min_anos_baixa_visibilidade"],
            as_index=False,
        )
        .agg(
            repeticoes_no_fatorial=("cenario_id", "size"),
            min_sinalizados_conjunto=("sinalizados_modelo_conjunto", "min"),
            max_sinalizados_conjunto=("sinalizados_modelo_conjunto", "max"),
            min_sinalizados_sem_fragilidade=("sinalizados_sem_fragilidade", "min"),
            max_sinalizados_sem_fragilidade=("sinalizados_sem_fragilidade", "max"),
            min_removidos_pela_fragilidade=("removidos_pela_fragilidade", "min"),
            max_removidos_pela_fragilidade=("removidos_pela_fragilidade", "max"),
        )
    )
    effective["resultado_conjunto_invariante_nas_12_repeticoes"] = (
        effective["min_sinalizados_conjunto"] == effective["max_sinalizados_conjunto"]
    )

    unique_joint = int(np.unique(joint_matrix, axis=1).shape[1])
    unique_visibility = int(np.unique(visibility_matrix, axis=1).shape[1])
    pearson = float(municipal["frequencia_conjunta_pct"].corr(municipal["frequencia_sem_fragilidade_pct"]))
    spearman = float(
        municipal["frequencia_conjunta_pct"].corr(
            municipal["frequencia_sem_fragilidade_pct"], method="spearman"
        )
    )

    summary = {
        "municipios": int(len(base)),
        "cenarios_parametricos": 216,
        "configuracoes_visibility_persistence": 18,
        "vetores_conjuntos_distintos": unique_joint,
        "vetores_sem_fragilidade_distintos": unique_visibility,
        "correlacao_pearson_frequencias": pearson,
        "correlacao_spearman_frequencias": spearman,
        "municipios_com_mudanca_de_classe": int(municipal["mudanca_de_classe"].sum()),
        "municipios_alguma_vez_removidos_pela_fragilidade": int(
            (municipal["cenarios_removidos_pela_fragilidade"] > 0).sum()
        ),
        "remocoes_municipio_cenario_pela_fragilidade": int(
            (visibility_matrix - joint_matrix).sum()
        ),
        "interpretacao": (
            "The 216 parameter combinations remain the declared factorial design. "
            "The number of distinct flag vectors quantifies empirical redundancy. "
            "The comparison with the visibility-only model measures the filtering "
            "contribution of institutional fragility."
        ),
    }

    prefix = PROC / "ablation_fragility_v26"
    scenarios.to_csv(f"{prefix}_scenarios.csv", index=False, encoding="utf-8-sig")
    municipal.to_csv(f"{prefix}_municipal.csv", index=False, encoding="utf-8-sig")
    effective.to_csv(f"{prefix}_effective_configurations.csv", index=False, encoding="utf-8-sig")
    np.save(f"{prefix}_joint_matrix.npy", joint_matrix)
    np.save(f"{prefix}_visibility_only_matrix.npy", visibility_matrix)
    Path(f"{prefix}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
