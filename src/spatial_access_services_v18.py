#!/usr/bin/env python3
"""Calculate geographic accessibility to the municipal protection network."""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'outputs'
DOCS = ROOT / 'docs'
PROC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

GEOD = Geod(ellps='WGS84')


def geodesic_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    _, _, distance_m = GEOD.inv(lon1, lat1, lon2, lat2)
    return float(distance_m / 1000.0)


def min_distance_to_hubs(points: pd.DataFrame, hubs: pd.DataFrame, prefix: str) -> pd.DataFrame:
    hub_coordinates = hubs[['codigo_ibge', 'municipio', 'lon', 'lat']].to_records(index=False)
    rows = []
    for row in points.itertuples(index=False):
        if len(hub_coordinates) == 0:
            rows.append({
                'codigo_ibge': row.codigo_ibge,
                f'dist_{prefix}_km': np.nan,
                f'hub_{prefix}_codigo': None,
                f'hub_{prefix}_municipio': None,
            })
            continue
        best = None
        for hub in hub_coordinates:
            distance = geodesic_km(row.lon, row.lat, hub.lon, hub.lat)
            if best is None or distance < best[0]:
                best = (distance, str(hub.codigo_ibge), str(hub.municipio))
        rows.append({
            'codigo_ibge': row.codigo_ibge,
            f'dist_{prefix}_km': best[0],
            f'hub_{prefix}_codigo': best[1],
            f'hub_{prefix}_municipio': best[2],
        })
    return pd.DataFrame(rows)


def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(method='average', pct=True) * 100


def main() -> None:
    geometry_path = RAW / 'munics.geojson'
    institutional_path = PROC / 'base_mestre_com_munic_2023.csv'
    visibility_path = PROC / 'indice_visibilidade_exploratorio_v15.csv'
    robustness_path = PROC / 'robustez_potencial_subnotificacao_v17.csv'

    for path in [geometry_path, institutional_path, visibility_path, robustness_path]:
        if not path.exists():
            raise SystemExit(f'Missing file: {path}')

    geography = gpd.read_file(geometry_path)[['codarea', 'geometry']].copy()
    geography['codigo_ibge'] = geography['codarea'].astype(str).str.zfill(7)
    representative_points = geography.geometry.representative_point()
    geography['lon'] = representative_points.x
    geography['lat'] = representative_points.y

    institutional = pd.read_csv(institutional_path, dtype={'codigo_ibge': str})
    institutional['codigo_ibge'] = institutional['codigo_ibge'].str.zfill(7)
    institutional['municipio'] = institutional['municipio_original']

    service_columns = [
        'casa_abrigo', 'ceam_niam', 'servico_violencia_sexual',
        'centro_integrado', 'unidade_movel', 'casa_passagem',
    ]
    high_complexity_columns = [
        'casa_abrigo', 'ceam_niam', 'centro_integrado', 'casa_passagem'
    ]
    institutional['qtd_tipos_servicos_especializados'] = (
        institutional[service_columns].fillna(0).astype(float).sum(axis=1)
    )
    institutional['possui_servico_especializado'] = (
        institutional['qtd_tipos_servicos_especializados'] > 0
    ).astype(int)
    institutional['possui_servico_alta_complexidade'] = (
        institutional[high_complexity_columns].fillna(0).astype(float).sum(axis=1) > 0
    ).astype(int)

    points = institutional.merge(
        geography[['codigo_ibge', 'lon', 'lat', 'geometry']],
        on='codigo_ibge',
        how='left',
        validate='one_to_one',
    )
    if points[['lon', 'lat']].isna().any().any():
        raise ValueError('Municipalities without associated geometry were found.')

    hubs_any = points.loc[
        points['possui_servico_especializado'] == 1,
        ['codigo_ibge', 'municipio', 'lon', 'lat'],
    ]
    hubs_high = points.loc[
        points['possui_servico_alta_complexidade'] == 1,
        ['codigo_ibge', 'municipio', 'lon', 'lat'],
    ]

    distance_any = min_distance_to_hubs(
        points[['codigo_ibge', 'municipio', 'lon', 'lat']],
        hubs_any,
        'servico_especializado',
    )
    distance_high = min_distance_to_hubs(
        points[['codigo_ibge', 'municipio', 'lon', 'lat']],
        hubs_high,
        'alta_complexidade',
    )

    output = (
        points.drop(columns='geometry')
        .merge(distance_any, on='codigo_ibge', how='left')
        .merge(distance_high, on='codigo_ibge', how='left')
    )
    output['percentil_dist_servico'] = percentile_rank(
        output['dist_servico_especializado_km']
    )
    output['percentil_dist_alta_complexidade'] = percentile_rank(
        output['dist_alta_complexidade_km']
    )
    output['barreira_territorial_0_100'] = (
        0.45 * output['percentil_dist_servico']
        + 0.55 * output['percentil_dist_alta_complexidade']
    )
    output['classe_barreira_territorial'] = pd.cut(
        output['barreira_territorial_0_100'],
        bins=[-np.inf, 20, 40, 60, 80, np.inf],
        labels=['Muito baixa', 'Baixa', 'Média', 'Alta', 'Muito alta'],
        include_lowest=True,
    ).astype(str)

    visibility = pd.read_csv(visibility_path, dtype={'codigo_ibge': str})
    visibility['codigo_ibge'] = visibility['codigo_ibge'].str.zfill(7)
    robustness = pd.read_csv(robustness_path, dtype={'codigo_ibge': str})
    robustness['codigo_ibge'] = robustness['codigo_ibge'].str.zfill(7)

    visibility_columns = [column for column in visibility.columns if column in {
        'codigo_ibge', 'municipio', 'indice_visibilidade_3_naturezas_0_100',
        'indice_visibilidade_4_naturezas_0_100',
        'indice_visibilidade_exploratorio_0_100',
        'indice_visibilidade_percentil_0_100', 'persistencia_media_pct',
    }]
    robustness_columns = [column for column in robustness.columns if column in {
        'codigo_ibge', 'municipio', 'percentual_cenarios_sinalizado',
        'frequencia_sinal', 'frequencia_sinal_pct', 'robustez_sinal',
        'classificacao_robustez',
    }]
    output = output.merge(
        visibility[visibility_columns].drop(columns=['municipio'], errors='ignore'),
        on='codigo_ibge',
        how='left',
    )
    output = output.merge(
        robustness[robustness_columns].drop(columns=['municipio'], errors='ignore'),
        on='codigo_ibge',
        how='left',
    )

    robustness_column = next((
        column for column in [
            'percentual_cenarios_sinalizado', 'frequencia_sinal_pct', 'frequencia_sinal'
        ] if column in output.columns
    ), None)
    if robustness_column:
        robustness_scale = output[robustness_column].astype(float)
        if robustness_scale.max(skipna=True) <= 1.0:
            robustness_scale = robustness_scale * 100
        output['robustez_sinal_percentual'] = robustness_scale
        output['prioridade_territorial_suplementar'] = np.select(
            [
                (robustness_scale >= 60) & (output['barreira_territorial_0_100'] >= 80),
                (robustness_scale >= 60) & (output['barreira_territorial_0_100'] >= 60),
                (robustness_scale >= 33) & (output['barreira_territorial_0_100'] >= 80),
            ],
            ['Muito alta', 'Alta', 'Moderada'],
            default='Sem prioridade suplementar',
        )

    output = output.sort_values(
        ['barreira_territorial_0_100', 'municipio'], ascending=[False, True]
    )
    output.to_csv(PROC / 'acessibilidade_rede_protecao_v18.csv', index=False)

    hubs = pd.concat([
        hubs_any.assign(tipo_polo='Algum serviço especializado'),
        hubs_high.assign(tipo_polo='Serviço de alta complexidade'),
    ], ignore_index=True)
    hubs.to_csv(PROC / 'polos_servicos_mulheres_v18.csv', index=False)

    summary = {
        'municipios': int(len(output)),
        'polos_algum_servico': int(len(hubs_any)),
        'polos_alta_complexidade': int(len(hubs_high)),
        'distancia_mediana_algum_servico_km': round(float(output['dist_servico_especializado_km'].median()), 2),
        'distancia_maxima_algum_servico_km': round(float(output['dist_servico_especializado_km'].max()), 2),
        'distancia_mediana_alta_complexidade_km': round(float(output['dist_alta_complexidade_km'].median()), 2),
        'distancia_maxima_alta_complexidade_km': round(float(output['dist_alta_complexidade_km'].max()), 2),
        'nota': 'Geodesic distances between representative municipal points; they are not equivalent to real road or river travel time.',
    }
    (PROC / 'resumo_acessibilidade_v18.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    geography_output = geography.merge(
        output.drop(columns=['lon', 'lat'], errors='ignore'),
        on='codigo_ibge',
        how='left',
    )
    geography_output.to_file(
        PROC / 'acessibilidade_rede_protecao_v18.geojson', driver='GeoJSON'
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
