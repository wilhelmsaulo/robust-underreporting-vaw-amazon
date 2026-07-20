"""Build municipal rates per 100,000 women and exploratory visibility metrics.

Inputs
------
data/processed/populacao_feminina_2022_pa.csv
data/processed/codec_painel_principal_2022_2025.csv

Outputs
-------
data/processed/codec_taxas_100mil_mulheres_2022_2025.csv
data/processed/codec_resumo_taxas_municipio_natureza_2022_2025.csv
data/processed/codec_taxas_estaduais_2022_2025.csv
data/processed/indice_visibilidade_exploratorio_v15.csv
data/processed/resumo_taxas_visibilidade_v15.json
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def percentile_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        percentile = ((i + j) / 2) / (len(indexed) - 1) if len(indexed) > 1 else 0.0
        for position in range(i, j + 1):
            ranks[indexed[position][0]] = percentile
        i = j + 1
    return ranks


def main() -> None:
    population = read_csv(PROCESSED / "populacao_feminina_2022_pa.csv")
    panel = read_csv(PROCESSED / "codec_painel_principal_2022_2025.csv")

    pop_by_code = {row["codigo_ibge"]: int(row["populacao_feminina"]) for row in population}
    missing = sorted({row["codigo_ibge"] for row in panel} - set(pop_by_code))
    if missing:
        raise ValueError(f"Municipalities without female population: {missing}")

    rate_rows: list[dict] = []
    for row in panel:
        pop = pop_by_code[row["codigo_ibge"]]
        quantity = int(float(row["quantidade"]))
        rate_rows.append({**row, "populacao_feminina_2022": pop, "taxa_100mil_mulheres": round(quantity / pop * 100_000, 6)})
    write_csv(PROCESSED / "codec_taxas_100mil_mulheres_2022_2025.csv", rate_rows)

    groups: defaultdict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rate_rows:
        groups[(row["codigo_ibge"], row["municipio"], row["natureza"])].append(row)

    summary: list[dict] = []
    for (code, municipality, nature), items in sorted(groups.items()):
        items = sorted(items, key=lambda row: int(row["ano"]))
        quantities = [int(row["quantidade"]) for row in items]
        rates = [float(row["taxa_100mil_mulheres"]) for row in items]
        mean_rate = sum(rates) / 4
        coefficient_variation = statistics.pstdev(rates) / mean_rate if mean_rate > 0 else 0.0
        summary.append({
            "codigo_ibge": code,
            "municipio": municipality,
            "natureza": nature,
            "populacao_feminina_2022": items[0]["populacao_feminina_2022"],
            "total_2022_2025": sum(quantities),
            "media_anual_registros": round(sum(quantities) / 4, 4),
            "taxa_media_anual_100mil": round(mean_rate, 6),
            "taxa_acumulada_4anos_100mil": round(sum(rates), 6),
            "anos_com_registro": sum(value > 0 for value in quantities),
            "persistencia_pct": round(sum(value > 0 for value in quantities) / 4 * 100, 2),
            "cv_taxa_anual": round(coefficient_variation, 6),
            "taxa_2022": round(rates[0], 6),
            "taxa_2023": round(rates[1], 6),
            "taxa_2024": round(rates[2], 6),
            "taxa_2025": round(rates[3], 6),
        })

    for nature in sorted({row["natureza"] for row in summary}):
        positions = [index for index, row in enumerate(summary) if row["natureza"] == nature]
        percentiles = percentile_ranks([summary[index]["taxa_media_anual_100mil"] for index in positions])
        for index, percentile in zip(positions, percentiles):
            summary[index]["percentil_estadual_taxa"] = round(percentile * 100, 2)
    write_csv(PROCESSED / "codec_resumo_taxas_municipio_natureza_2022_2025.csv", summary)

    by_municipality: defaultdict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in summary:
        by_municipality[(row["codigo_ibge"], row["municipio"])].append(row)

    visibility: list[dict] = []
    for (code, municipality), rows in sorted(by_municipality.items()):
        visibility.append({
            "codigo_ibge": code,
            "municipio": municipality,
            "populacao_feminina_2022": rows[0]["populacao_feminina_2022"],
            "indice_visibilidade_percentil_0_100": round(sum(float(row["percentil_estadual_taxa"]) for row in rows) / 4, 2),
            "persistencia_media_pct": round(sum(float(row["persistencia_pct"]) for row in rows) / 4, 2),
            "observacao": "Índice exploratório: média dos percentis estaduais das taxas médias anuais das quatro naturezas. Não representa risco nem prevalência real.",
        })
    visibility.sort(key=lambda row: row["indice_visibilidade_percentil_0_100"], reverse=True)
    for rank, row in enumerate(visibility, start=1):
        row["ranking_visibilidade"] = rank
    write_csv(PROCESSED / "indice_visibilidade_exploratorio_v15.csv", visibility)

    state_population = sum(int(row["populacao_feminina"]) for row in population)
    state_rates: list[dict] = []
    for year in range(2022, 2026):
        for nature in sorted({row["natureza"] for row in rate_rows}):
            quantity = sum(int(row["quantidade"]) for row in rate_rows if int(row["ano"]) == year and row["natureza"] == nature)
            state_rates.append({
                "ano": year,
                "natureza": nature,
                "registros": quantity,
                "populacao_feminina_2022_pa": state_population,
                "taxa_100mil_mulheres": round(quantity / state_population * 100_000, 4),
            })
    write_csv(PROCESSED / "codec_taxas_estaduais_2022_2025.csv", state_rates)

    report = {
        "municipios": len(population),
        "populacao_feminina_pa_2022": state_population,
        "linhas_taxas_municipio_ano_natureza": len(rate_rows),
        "linhas_resumo_municipio_natureza": len(summary),
        "denominador": "População feminina municipal do Censo 2022, fixa para taxas de 2022 a 2025.",
        "fonte_populacao": "IBGE Censo 2022 tabela 9514, compilada pela FAPESPA.",
        "top_10_visibilidade": visibility[:10],
    }
    (PROCESSED / "resumo_taxas_visibilidade_v15.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
