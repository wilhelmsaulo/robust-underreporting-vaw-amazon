#!/usr/bin/env python3
"""Classical ELECTRE TRI-B complementary validation (v25)."""
from __future__ import annotations
import json
from itertools import product
from pathlib import Path
import numpy as np
import pandas as pd
from electre_tri_b_core import pessimistic_assignment

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'outputs'
(OUT / 'tables_v25').mkdir(parents=True, exist_ok=True)


def percentile_priority(series: pd.Series, higher_is_priority: bool = True) -> pd.Series:
    values = pd.to_numeric(series, errors='coerce')
    ranks = values.rank(method='average', pct=True)
    if higher_is_priority:
        return ranks
    return 1.0 - ranks + (1.0 / len(values))


def profiles_from_levels(levels, number_of_criteria):
    return np.vstack([
        np.repeat(float(value), number_of_criteria) for value in levels
    ])


def main():
    cfg = json.loads((ROOT / 'config' / 'electre_tri_b_v25.json').read_text(encoding='utf-8'))
    df = pd.read_csv(
        PROC / 'prioridades_investigacao_consolidadas_v19.csv',
        dtype={'codigo_ibge': str},
    )
    pareto = pd.read_csv(
        PROC / 'validacao_pareto_v20.csv',
        dtype={'codigo_ibge': str},
    )[['codigo_ibge', 'fronteira_pareto', 'pareto_frente_1']]
    df = df.merge(pareto, on='codigo_ibge', how='left')

    df['institutional_fragility_percentile'] = percentile_priority(
        df['fragilidade_institucional_0_100'], True
    )
    df['low_reporting_visibility_percentile'] = percentile_priority(
        df['indice_visibilidade_recorrente_0_100'], False
    )
    df['territorial_barrier_percentile'] = percentile_priority(
        df['barreira_territorial_0_100'], True
    )

    criteria = cfg['criteria']
    performance_matrix = df[criteria].to_numpy(float)
    number_of_criteria = len(criteria)
    if not np.isfinite(performance_matrix).all():
        raise ValueError('Missing or non-finite criterion values.')

    profiles = {
        name: profiles_from_levels(values, number_of_criteria)
        for name, values in cfg['profile_schemes'].items()
    }
    baseline = cfg['baseline']
    thresholds = cfg['threshold_schemes'][baseline['threshold_scheme']]
    baseline_classes = pessimistic_assignment(
        performance_matrix,
        profiles[baseline['profile_scheme']],
        np.asarray(baseline['weights']),
        np.repeat(thresholds['q'], number_of_criteria),
        np.repeat(thresholds['p'], number_of_criteria),
        np.repeat(thresholds['v'], number_of_criteria),
        baseline['lambda'],
    )

    labels = {index: label for index, label in enumerate(cfg['class_labels'])}
    df['electre_baseline_class'] = baseline_classes
    df['electre_baseline_label'] = pd.Series(baseline_classes).map(labels).to_numpy()

    scenario_rows = []
    class_matrices = []
    scenario_id = 0
    for (weight_name, weights), (profile_name, _), (threshold_name, threshold), cut_level in product(
        cfg['weight_schemes'].items(),
        cfg['profile_schemes'].items(),
        cfg['threshold_schemes'].items(),
        cfg['lambda_values'],
    ):
        scenario_id += 1
        classes = pessimistic_assignment(
            performance_matrix,
            profiles[profile_name],
            np.asarray(weights),
            np.repeat(threshold['q'], number_of_criteria),
            np.repeat(threshold['p'], number_of_criteria),
            np.repeat(threshold['v'], number_of_criteria),
            cut_level,
        )
        class_matrices.append(classes)
        scenario_rows.append({
            'scenario_id': scenario_id,
            'weight_scheme': weight_name,
            'profile_scheme': profile_name,
            'threshold_scheme': threshold_name,
            'lambda': cut_level,
            'low': int((classes == 0).sum()),
            'moderate': int((classes == 1).sum()),
            'high': int((classes == 2).sum()),
            'very_high': int((classes == 3).sum()),
        })

    matrix = np.vstack(class_matrices).T
    df['electre_class_min'] = matrix.min(axis=1)
    df['electre_class_max'] = matrix.max(axis=1)
    df['electre_class_median'] = np.median(matrix, axis=1)
    df['electre_high_or_very_high_pct'] = ((matrix >= 2).mean(axis=1) * 100).round(6)
    df['electre_very_high_pct'] = ((matrix == 3).mean(axis=1) * 100).round(6)
    df['electre_stable_class'] = np.where(
        matrix.min(axis=1) == matrix.max(axis=1), 'Stable', 'Variable'
    )
    df['scenario_high_priority'] = df['classificacao_robustez'].isin(
        ['Sinal forte', 'Sinal moderado']
    )
    df['electre_high_priority'] = df['electre_baseline_class'] >= 2
    df['three_method_convergence'] = (
        df['scenario_high_priority']
        & df['electre_high_priority']
        & df['pareto_frente_1'].fillna(False)
    )
    df['two_or_more_method_convergence'] = (
        df[['scenario_high_priority', 'electre_high_priority', 'pareto_frente_1']]
        .fillna(False)
        .astype(int)
        .sum(axis=1)
        >= 2
    )

    output_columns = [
        'codigo_ibge', 'municipio', 'grupo_consolidado_v19',
        'frequencia_sinal_pct', 'classificacao_robustez',
        'fronteira_pareto', 'pareto_frente_1', *criteria,
        'electre_baseline_class', 'electre_baseline_label',
        'electre_class_min', 'electre_class_max', 'electre_class_median',
        'electre_high_or_very_high_pct', 'electre_very_high_pct',
        'electre_stable_class', 'scenario_high_priority',
        'electre_high_priority', 'three_method_convergence',
        'two_or_more_method_convergence',
    ]
    output = df[output_columns].sort_values(
        ['electre_baseline_class', 'electre_high_or_very_high_pct', 'frequencia_sinal_pct'],
        ascending=[False, False, False],
    )
    output.to_csv(
        PROC / 'electre_tri_b_v25_municipios.csv',
        index=False,
        encoding='utf-8-sig',
    )
    scenarios = pd.DataFrame(scenario_rows)
    scenarios.to_csv(
        PROC / 'electre_tri_b_v25_scenarios.csv', index=False, encoding='utf-8-sig'
    )
    np.save(PROC / 'electre_tri_b_v25_classes.npy', matrix)

    distribution = (
        df['electre_baseline_label']
        .value_counts()
        .reindex(cfg['class_labels'], fill_value=0)
        .rename_axis('priority_class')
        .reset_index(name='municipalities')
    )
    distribution.to_csv(
        OUT / 'tables_v25' / 'electre_baseline_distribution_v25.csv', index=False
    )
    output.head(30).to_csv(
        OUT / 'tables_v25' / 'electre_top_municipalities_v25.csv',
        index=False,
        encoding='utf-8-sig',
    )

    summary = {
        'method': cfg['method_name'],
        'municipalities': len(df),
        'criteria': criteria,
        'normalization': 'Empirical percentile ranks; higher values indicate greater investigation priority.',
        'temporal_persistence_handling': 'Retained in the 216-scenario analysis and excluded from ELECTRE to avoid double counting.',
        'baseline': baseline,
        'baseline_profiles': profiles[baseline['profile_scheme']].tolist(),
        'baseline_thresholds': thresholds,
        'sensitivity_scenarios': matrix.shape[1],
        'baseline_distribution': {
            str(key): int(value)
            for key, value in df['electre_baseline_label'].value_counts().items()
        },
        'stable_assignments': int((df['electre_stable_class'] == 'Stable').sum()),
        'interpretive_warning': 'Complementary sorting validation only; no confirmed underreporting ground truth was available.',
    }
    (PROC / 'resumo_electre_tri_b_v25.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
