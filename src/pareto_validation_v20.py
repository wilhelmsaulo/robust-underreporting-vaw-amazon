#!/usr/bin/env python3
"""Non-compensatory validation using Pareto fronts.

Dimensions are oriented so that larger values indicate greater investigation
priority: institutional fragility, low reporting visibility, and territorial
barrier. No criterion weights are used.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / 'data' / 'processed' / 'prioridades_investigacao_consolidadas_v19.csv'
OUTPUT_DIR = ROOT / 'data' / 'processed'


def as_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def dominates(a: dict, b: dict, columns: list[str]) -> bool:
    at_least_as_good = all(a[column] >= b[column] - 1e-12 for column in columns)
    strictly_better = any(a[column] > b[column] + 1e-12 for column in columns)
    return at_least_as_good and strictly_better


def pareto_fronts(rows: list[dict], columns: list[str]) -> list[list[int]]:
    remaining = set(range(len(rows)))
    fronts: list[list[int]] = []
    while remaining:
        front = []
        for index in sorted(remaining):
            if not any(
                dominates(rows[other], rows[index], columns)
                for other in remaining
                if other != index
            ):
                front.append(index)
        if not front:
            raise RuntimeError('Unable to construct Pareto front.')
        fronts.append(front)
        remaining -= set(front)
    return fronts


def main() -> None:
    with INPUT_FILE.open(encoding='utf-8-sig', newline='') as file:
        raw_rows = list(csv.DictReader(file))

    rows = []
    for row in raw_rows:
        fragility = as_float(row['fragilidade_institucional_0_100'])
        visibility = as_float(row['indice_visibilidade_recorrente_0_100'])
        barrier = as_float(row['barreira_territorial_0_100'])
        rows.append({
            **row,
            'fragilidade_institucional': fragility,
            'baixa_visibilidade': 100.0 - visibility,
            'barreira_territorial': barrier,
            'frequencia_sinal': as_float(row['frequencia_sinal_pct']),
        })

    columns = ['fragilidade_institucional', 'baixa_visibilidade', 'barreira_territorial']
    fronts = pareto_fronts(rows, columns)
    front_number = {}
    for number, front in enumerate(fronts, start=1):
        for index in front:
            front_number[index] = number

    for index, row in enumerate(rows):
        row['fronteira_pareto'] = front_number[index]
        row['qtd_dominados'] = sum(
            dominates(row, rows[other], columns)
            for other in range(len(rows))
            if other != index
        )
        row['qtd_dominadores'] = sum(
            dominates(rows[other], row, columns)
            for other in range(len(rows))
            if other != index
        )
        row['pareto_frente_1'] = front_number[index] == 1
        row['validacao_pareto'] = (
            'Prioridade não dominada' if front_number[index] == 1
            else 'Prioridade próxima' if front_number[index] == 2
            else 'Demais níveis'
        )

    rows.sort(
        key=lambda row: (
            row['fronteira_pareto'],
            -row['qtd_dominados'],
            -row['frequencia_sinal'],
            row['municipio'],
        )
    )

    fields = [
        'codigo_ibge', 'municipio', 'grupo_consolidado_v19',
        'fragilidade_institucional', 'baixa_visibilidade', 'barreira_territorial',
        'frequencia_sinal', 'fronteira_pareto', 'qtd_dominados',
        'qtd_dominadores', 'pareto_frente_1', 'validacao_pareto',
    ]
    output_file = OUTPUT_DIR / 'validacao_pareto_v20.csv'
    with output_file.open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})

    front_one = [row for row in rows if row['fronteira_pareto'] == 1]
    summary = {
        'municipios': len(rows),
        'numero_fronteiras': len(fronts),
        'frente_1_nao_dominada': len(front_one),
        'municipios_frente_1': [row['municipio'] for row in front_one],
        'metodo': 'Pareto não compensatório em três dimensões, sem pesos',
    }
    (OUTPUT_DIR / 'resumo_validacao_pareto_v20.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
