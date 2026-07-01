from pathlib import Path
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'outputs'
FIG = OUT / 'figures_v22'
TAB = OUT / 'tables_v22'
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

scenarios = pd.read_csv(PROC / 'cenarios_robustez_subnotificacao_v17.csv')
robustness = pd.read_csv(
    PROC / 'robustez_potencial_subnotificacao_v17.csv',
    dtype={'codigo_ibge': str},
)
matrix = np.load(PROC / 'matriz_sinais_subnotificacao_v17.npy')

if matrix.shape != (len(robustness), len(scenarios)):
    raise ValueError(
        f'Matrix shape {matrix.shape} does not match municipalities/scenarios '
        f'{(len(robustness), len(scenarios))}.'
    )

factor_specs = [
    ('cenario_ici', 'Institutional weighting scheme'),
    ('especificacao_visibilidade', 'Visibility composition'),
    ('quantil_fragilidade', 'Institutional-fragility threshold'),
    ('quantil_baixa_visibilidade', 'Low-visibility threshold'),
    ('min_anos_baixa_visibilidade', 'Persistence rule'),
]

level_rows = []
factor_rows = []
for factor, label in factor_specs:
    grouped = scenarios.groupby(factor, sort=False)
    municipal_conditional = []
    for level, indexes in grouped.groups.items():
        indexes = np.asarray(list(indexes), dtype=int)
        conditional_frequency = matrix[:, indexes].mean(axis=1) * 100
        municipal_conditional.append(conditional_frequency)
        counts = scenarios.loc[indexes, 'municipios_sinalizados']
        level_rows.append({
            'factor': factor,
            'factor_label': label,
            'level': str(level),
            'n_scenarios': int(len(indexes)),
            'mean_municipalities_flagged': float(counts.mean()),
            'median_municipalities_flagged': float(counts.median()),
            'min_municipalities_flagged': int(counts.min()),
            'max_municipalities_flagged': int(counts.max()),
            'mean_conditional_signal_frequency_pct': float(
                conditional_frequency.mean()
            ),
        })

    conditional_matrix = np.vstack(municipal_conditional).T
    municipal_range = conditional_matrix.max(axis=1) - conditional_matrix.min(axis=1)
    level_means = scenarios.groupby(factor)['municipios_sinalizados'].mean()
    factor_rows.append({
        'factor': factor,
        'factor_label': label,
        'n_levels': int(grouped.ngroups),
        'range_in_mean_number_flagged': float(level_means.max() - level_means.min()),
        'mean_municipal_conditional_range_pp': float(municipal_range.mean()),
        'median_municipal_conditional_range_pp': float(np.median(municipal_range)),
        'max_municipal_conditional_range_pp': float(municipal_range.max()),
        'municipalities_with_any_change': int((municipal_range > 0).sum()),
    })

levels = pd.DataFrame(level_rows)
factors = pd.DataFrame(factor_rows).sort_values(
    'mean_municipal_conditional_range_pp', ascending=False
)
levels.to_csv(
    PROC / 'sensibilidade_fatores_cenarios_v22_niveis.csv',
    index=False,
    encoding='utf-8-sig',
)
factors.to_csv(
    PROC / 'sensibilidade_fatores_cenarios_v22_resumo.csv',
    index=False,
    encoding='utf-8-sig',
)
levels.to_csv(
    TAB / 'sensibilidade_fatores_cenarios_v22_niveis.csv',
    index=False,
    encoding='utf-8-sig',
)
factors.to_csv(
    TAB / 'sensibilidade_fatores_cenarios_v22_resumo.csv',
    index=False,
    encoding='utf-8-sig',
)

geography = gpd.read_file(PROC / 'acessibilidade_rede_protecao_v18.geojson')
geography['codigo_ibge'] = geography['codigo_ibge'].astype(str).str.zfill(7)
robustness['codigo_ibge'] = robustness['codigo_ibge'].astype(str).str.zfill(7)
geography = geography.drop(
    columns=[
        column for column in ['frequencia_sinal_pct', 'classificacao_robustez']
        if column in geography.columns
    ]
)
geography = geography.merge(
    robustness[['codigo_ibge', 'municipio', 'frequencia_sinal_pct', 'classificacao_robustez']],
    on='codigo_ibge',
    how='left',
    suffixes=('', '_rob'),
)
if geography['frequencia_sinal_pct'].isna().any():
    raise ValueError('Some municipalities did not match robustness results.')

bins = [-0.001, 10, 30, 60, 100.001]
labels = [
    'No robust signal (0–10%)',
    'Weak (>10–30%)',
    'Moderate (>30–60%)',
    'Strong (>60–100%)',
]
colors = ['#f0f0f0', '#fee08b', '#f46d43', '#a50026']
geography['robustness_map_class'] = pd.cut(
    geography['frequencia_sinal_pct'],
    bins=bins,
    labels=labels,
    include_lowest=True,
)

figure, axis = plt.subplots(figsize=(8.2, 8.6))
for label, color in zip(labels, colors):
    subset = geography[geography['robustness_map_class'] == label]
    subset.plot(ax=axis, color=color, edgecolor='white', linewidth=0.28)
geography.boundary.plot(ax=axis, color='#666666', linewidth=0.18)
axis.set_axis_off()
legend_handles = [
    Patch(facecolor=color, edgecolor='#777777', label=label)
    for label, color in zip(labels, colors)
]
axis.legend(
    handles=legend_handles,
    loc='lower left',
    frameon=True,
    fontsize=8,
    title='Scenario frequency',
)
figure.tight_layout()
map_png = FIG / 'figura_5_mapa_robustez_municipal.png'
map_pdf = FIG / 'figura_5_mapa_robustez_municipal.pdf'
figure.savefig(map_png, dpi=350, bbox_inches='tight')
figure.savefig(map_pdf, bbox_inches='tight')
plt.close(figure)

summary = {
    'ranking_by_mean_municipal_conditional_range_pp': factors[[
        'factor_label',
        'mean_municipal_conditional_range_pp',
        'range_in_mean_number_flagged',
        'municipalities_with_any_change',
    ]].to_dict('records'),
    'map_png': str(map_png.relative_to(ROOT)),
    'map_pdf': str(map_pdf.relative_to(ROOT)),
}
with open(
    PROC / 'resumo_sensibilidade_fatores_v22.json',
    'w',
    encoding='utf-8',
) as file:
    json.dump(summary, file, ensure_ascii=False, indent=2)

print(factors.to_string(index=False))
print('\nLevel results:')
print(levels.to_string(index=False))
