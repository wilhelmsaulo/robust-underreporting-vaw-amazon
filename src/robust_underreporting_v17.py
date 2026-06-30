from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'

ici = pd.read_csv(PROC / 'ici_mulheres_robustez_cenarios.csv', dtype={'codigo_ibge': str})
rates = pd.read_csv(PROC / 'codec_resumo_taxas_municipio_natureza_2022_2025.csv', dtype={'codigo_ibge': str})
annual_raw = pd.read_csv(PROC / 'codec_taxas_100mil_mulheres_2022_2025.csv', dtype={'codigo_ibge': str})

ici_cols = {
    'base_v4': 'ici_base_v4',
    'pesos_iguais': 'ici_pesos_iguais',
    'prioridade_servicos': 'ici_prioridade_servicos',
    'prioridade_governanca': 'ici_prioridade_governanca',
}

specs = {
    'recorrentes_3': ['Lesão corporal - violência doméstica', 'Estupro', 'Estupro de vulnerável'],
    'sexuais_2': ['Estupro', 'Estupro de vulnerável'],
    'quatro_naturezas': ['Feminicídio', 'Lesão corporal - violência doméstica', 'Estupro', 'Estupro de vulnerável'],
}

pivot_pct = rates.pivot(index=['codigo_ibge','municipio'], columns='natureza', values='percentil_estadual_taxa').reset_index()
annual_raw['percentil_anual_natureza'] = annual_raw.groupby(['ano','natureza'])['taxa_100mil_mulheres'].rank(pct=True, method='average') * 100
annual = annual_raw.pivot_table(index=['codigo_ibge','municipio','ano'], columns='natureza', values='percentil_anual_natureza', aggfunc='mean').reset_index()

base = ici[['codigo_ibge','municipio'] + list(ici_cols.values())].copy()
base = base.merge(pivot_pct, on=['codigo_ibge','municipio'], how='left')

for spec, natures in specs.items():
    base[f'vis_{spec}'] = base[natures].mean(axis=1)
    annual[f'vis_{spec}'] = annual[natures].mean(axis=1)

frag_qs = [0.67, 0.70, 0.75]
vis_qs = [0.25, 0.33, 0.40]
persistence_reqs = [2, 3]
scenario_rows = []
flag_matrix = []
scenario_id = 0

for ici_name, ici_col in ici_cols.items():
    frag = 100 - base[ici_col]
    for spec in specs:
        vis_col = f'vis_{spec}'
        for fq in frag_qs:
            frag_cut = float(frag.quantile(fq))
            for vq in vis_qs:
                vis_cut = float(base[vis_col].quantile(vq))
                annual_cut = annual.groupby('ano')[vis_col].transform(lambda s: s.quantile(vq))
                annual_low = annual[vis_col] <= annual_cut
                low_years = annual.assign(low=annual_low).groupby('codigo_ibge')['low'].sum()
                for req in persistence_reqs:
                    scenario_id += 1
                    flags = (frag >= frag_cut) & (base[vis_col] <= vis_cut) & (base['codigo_ibge'].map(low_years).fillna(0) >= req)
                    flag_matrix.append(flags.to_numpy(dtype=np.uint8))
                    scenario_rows.append({
                        'cenario_id': scenario_id,
                        'cenario_ici': ici_name,
                        'especificacao_visibilidade': spec,
                        'quantil_fragilidade': fq,
                        'corte_fragilidade': frag_cut,
                        'quantil_baixa_visibilidade': vq,
                        'corte_visibilidade': vis_cut,
                        'min_anos_baixa_visibilidade': req,
                        'municipios_sinalizados': int(flags.sum()),
                    })

M = np.vstack(flag_matrix).T
out = base[['codigo_ibge','municipio']].copy()
out['cenarios_sinalizados'] = M.sum(axis=1)
out['total_cenarios'] = M.shape[1]
out['frequencia_sinal_pct'] = out['cenarios_sinalizados'] / out['total_cenarios'] * 100
out['classificacao_robustez'] = pd.cut(
    out['frequencia_sinal_pct'],
    bins=[-0.01, 10, 30, 60, 100],
    labels=['Sem sinal robusto', 'Sinal fraco', 'Sinal moderado', 'Sinal forte'],
    include_lowest=True,
)

out = out.merge(ici[['codigo_ibge','ici_media_cenarios','ici_min_cenarios','ici_max_cenarios','amplitude_rank','estabilidade_rank']], on='codigo_ibge', how='left')
for spec in specs:
    out = out.merge(base[['codigo_ibge',f'vis_{spec}']], on='codigo_ibge', how='left')

central_col = 'vis_recorrentes_3'
central_cut = annual.groupby('ano')[central_col].transform(lambda s: s.quantile(0.33))
central_years = annual.assign(low=annual[central_col] <= central_cut).groupby('codigo_ibge')['low'].sum()
out['anos_baixa_visibilidade_central'] = out['codigo_ibge'].map(central_years).fillna(0).astype(int)
out = out.sort_values(['frequencia_sinal_pct','cenarios_sinalizados','municipio'], ascending=[False,False,True]).reset_index(drop=True)
out['ranking_robustez'] = np.arange(1, len(out)+1)

scenarios = pd.DataFrame(scenario_rows)
out.to_csv(PROC / 'robustez_potencial_subnotificacao_v17.csv', index=False, encoding='utf-8-sig')
scenarios.to_csv(PROC / 'cenarios_robustez_subnotificacao_v17.csv', index=False, encoding='utf-8-sig')
np.save(PROC / 'matriz_sinais_subnotificacao_v17.npy', M)

summary = {
    'total_municipios': int(len(out)),
    'total_cenarios': int(M.shape[1]),
    'distribuicao_robustez': {str(k): int(v) for k,v in out['classificacao_robustez'].value_counts(dropna=False).items()},
    'frequencia_media_sinal_pct': float(out['frequencia_sinal_pct'].mean()),
    'municipios_sinal_forte': out.loc[out['classificacao_robustez']=='Sinal forte', ['municipio','frequencia_sinal_pct']].to_dict('records'),
    'municipios_sinal_moderado': out.loc[out['classificacao_robustez']=='Sinal moderado', ['municipio','frequencia_sinal_pct']].to_dict('records'),
    'variacao_num_municipios_por_cenario': {
        'min': int(scenarios['municipios_sinalizados'].min()),
        'mediana': float(scenarios['municipios_sinalizados'].median()),
        'max': int(scenarios['municipios_sinalizados'].max()),
    },
    'nota': 'Triagem exploratória baseada apenas em capacidade institucional e registros. Não comprova subnotificação.'
}
with open(PROC / 'resumo_robustez_subnotificacao_v17.json','w',encoding='utf-8') as f:
    json.dump(summary,f,ensure_ascii=False,indent=2)

print(json.dumps(summary, ensure_ascii=False, indent=2))
