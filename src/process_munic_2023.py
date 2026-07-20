from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'external' / 'Base_MUNIC_2023.xlsx'
OUT_DIR = ROOT / 'data' / 'processed'
DOCS_DIR = ROOT / 'docs'

YES = {'Sim', 'SIM', 'sim', 1, '1', True}


def yes_flag(series: pd.Series) -> pd.Series:
    return series.map(lambda x: 1 if x in YES else 0).astype('int8')


def to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace({'-': np.nan, 'Não sabe informar': np.nan}), errors='coerce')


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_excel(INPUT, sheet_name='Política para Mulheres', dtype={'CodMun': str})
    pa = raw.loc[raw['UF'].eq('PA')].copy()
    pa['codigo_ibge'] = pa['CodMun'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(7)
    pa['municipio'] = pa['Mun'].astype(str).str.strip()
    pa['populacao_munic_2023'] = to_num(pa['PopMun'])

    mapping = {
        'organismo_executivo': 'MPPM01',
        'plano_municipal': 'MPPM11',
        'conselho_mulher': 'MPPM13',
        'conselho_infraestrutura': 'MPPM17',
        'conselho_orcamento_proprio': 'MPPM1718',
        'casa_abrigo': 'MPPM20',
        'ceam_niam': 'MPPM24a1',
        'servico_violencia_sexual': 'MPPM24a2',
        'centro_integrado': 'MPPM24a3',
        'unidade_movel': 'MPPM24a4',
        'casa_passagem': 'MPPM24a5',
        'levantamento_atendimentos': 'MPPM25',
        'divulga_atendimentos': 'MPPM251',
    }
    for new, old in mapping.items():
        if new == 'levantamento_atendimentos':
            pa[new] = pa[old].map(lambda x: 1 if x == 'Sim' else 0).astype('int8')
        else:
            pa[new] = yes_flag(pa[old])

    pa['reunioes_conselho_12m'] = to_num(pa['MPPM14']).fillna(0)
    pa['conselho_ativo'] = ((pa['conselho_mulher'] == 1) & (pa['reunioes_conselho_12m'] > 0)).astype('int8')

    quantity_map = {
        'qtd_casas_abrigo': 'MPPM201',
        'qtd_ceam_niam': 'MPPM24a11',
        'qtd_servicos_violencia_sexual': 'MPPM24a21',
        'qtd_centros_integrados': 'MPPM24a31',
        'qtd_unidades_moveis': 'MPPM24a41',
        'qtd_casas_passagem': 'MPPM24a51',
    }
    for new, old in quantity_map.items():
        pa[new] = to_num(pa[old]).fillna(0)

    governance_weights = {
        'organismo_executivo': 8,
        'plano_municipal': 6,
        'conselho_mulher': 4,
        'conselho_ativo': 4,
        'conselho_infraestrutura': 3,
        'conselho_orcamento_proprio': 5,
    }
    service_weights = {
        'casa_abrigo': 15,
        'ceam_niam': 15,
        'servico_violencia_sexual': 10,
        'centro_integrado': 10,
        'unidade_movel': 4,
        'casa_passagem': 6,
    }
    monitoring_weights = {
        'levantamento_atendimentos': 6,
        'divulga_atendimentos': 4,
    }

    pa['ici_governanca_0_30'] = sum(pa[col] * weight for col, weight in governance_weights.items())
    pa['ici_servicos_0_60'] = sum(pa[col] * weight for col, weight in service_weights.items())
    pa['ici_monitoramento_0_10'] = sum(pa[col] * weight for col, weight in monitoring_weights.items())
    pa['ici_mulheres_0_100'] = pa['ici_governanca_0_30'] + pa['ici_servicos_0_60'] + pa['ici_monitoramento_0_10']

    bins = [-0.01, 10, 25, 45, 65, 100]
    labels = ['Muito baixa', 'Baixa', 'Média', 'Alta', 'Muito alta']
    pa['classe_ici_descritiva'] = pd.cut(pa['ici_mulheres_0_100'], bins=bins, labels=labels, include_lowest=True)

    selected = [
        'codigo_ibge', 'municipio', 'populacao_munic_2023',
        *governance_weights.keys(), *service_weights.keys(), *monitoring_weights.keys(),
        'reunioes_conselho_12m', *quantity_map.keys(),
        'ici_governanca_0_30', 'ici_servicos_0_60', 'ici_monitoramento_0_10',
        'ici_mulheres_0_100', 'classe_ici_descritiva'
    ]
    out = pa[selected].sort_values('codigo_ibge').reset_index(drop=True)

    assert len(out) == 144, f'Esperados 144 municípios do Pará, obtidos {len(out)}'
    assert out['codigo_ibge'].is_unique, 'Código IBGE duplicado na MUNIC 2023'

    out.to_csv(OUT_DIR / 'munic_2023_politicas_mulheres_pa.csv', index=False, encoding='utf-8-sig')

    ref_path = OUT_DIR / 'base_referencia_original.csv'
    if ref_path.exists():
        ref = pd.read_csv(ref_path, dtype={'codigo_ibge': str})
        ref['codigo_ibge'] = ref['codigo_ibge'].astype(str).str.zfill(7)
        merged = ref.merge(out, on='codigo_ibge', how='left', validate='one_to_one', suffixes=('_original', '_munic2023'))
        merged.to_csv(OUT_DIR / 'base_mestre_com_munic_2023.csv', index=False, encoding='utf-8-sig')

    weights_doc = {
        'versao': 'candidata_v1',
        'pontuacao_maxima': 100,
        'governanca': governance_weights,
        'servicos': service_weights,
        'monitoramento': monitoring_weights,
        'observacao': 'Pesos normativos iniciais para análise e sensibilidade; não são definitivos.'
    }
    (ROOT / 'config' / 'pesos_ici_mulheres_v1.json').write_text(json.dumps(weights_doc, ensure_ascii=False, indent=2), encoding='utf-8')

    counts = {col: int(out[col].sum()) for col in [*governance_weights.keys(), *service_weights.keys(), *monitoring_weights.keys()]}
    summary = {
        'municipios': int(len(out)),
        'media_ici': round(float(out['ici_mulheres_0_100'].mean()), 2),
        'mediana_ici': round(float(out['ici_mulheres_0_100'].median()), 2),
        'min_ici': int(out['ici_mulheres_0_100'].min()),
        'max_ici': int(out['ici_mulheres_0_100'].max()),
        'contagens': counts,
        'classes_descritivas': {str(k): int(v) for k, v in out['classe_ici_descritiva'].value_counts(sort=False).items()},
        'top_10': out.nlargest(10, 'ici_mulheres_0_100')[['municipio', 'ici_mulheres_0_100']].to_dict('records'),
    }
    (OUT_DIR / 'resumo_munic_2023.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    report = f'''# Tratamento da MUNIC 2023 — políticas para as mulheres no Pará

## Resultado da extração

- Municípios do Pará: **{len(out)}**.
- Chave de integração: código IBGE de 7 dígitos.
- Planilha de origem: `Política para Mulheres` da Base MUNIC 2023.
- Valores ausentes ou marcados com `-` foram preservados conceitualmente e convertidos em zero apenas quando significavam ausência/não aplicabilidade do serviço.

## Índice candidato ICI-Mulheres v1

O índice foi construído em escala de 0 a 100 e separado em três blocos:

- Governança: 30 pontos.
- Serviços especializados: 60 pontos.
- Monitoramento/transparência: 10 pontos.

Os pesos são **iniciais e normativos**, destinados à análise de sensibilidade. Eles não serão tratados como definitivos antes da comparação com pesos iguais, pesos por especialistas e cenários alternativos.

## Estatísticas iniciais

- Média: **{summary['media_ici']}**.
- Mediana: **{summary['mediana_ici']}**.
- Mínimo: **{summary['min_ici']}**.
- Máximo: **{summary['max_ici']}**.

## Observação metodológica

A classificação descritiva do índice não substitui o ELECTRE Tri-B. Ela serve apenas para auditoria, exploração e comparação preliminar da capacidade institucional municipal.
'''
    (DOCS_DIR / 'TRATAMENTO_MUNIC_2023_V4.md').write_text(report, encoding='utf-8')

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
