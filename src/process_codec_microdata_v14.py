from __future__ import annotations

import csv
import json
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'external' / 'codec_segup_2022_2025'
OUT = ROOT / 'data' / 'processed'
OUT.mkdir(parents=True, exist_ok=True)

# Annual exports downloaded from the public CODEC/SEGUP-PA platform on
# 2026-02-02. Each file covers a complete calendar year.
FILES = {
    2022: '17_06_26.xlsx',
    2023: '17_06_26 (1).xlsx',
    2024: '17_06_26 (2).xlsx',
    2025: '17_06_26 (3).xlsx',
}


def norm(value: object) -> str:
    text = '' if value is None else str(value)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().upper().strip()
    return re.sub(r'\s+', ' ', text)


def read_reference() -> dict[str, tuple[str, str]]:
    path = OUT / 'base_referencia_original.csv'
    with path.open(encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    name_cols = [column for column in rows[0] if 'MUNIC' in norm(column)]
    code_cols = [column for column in rows[0] if 'CODIGO' in norm(column) or 'COD_IBGE' in norm(column)]
    name_col = name_cols[0]
    code_col = code_cols[0]
    mapping = {norm(row[name_col]): (row[code_col], row[name_col]) for row in rows}
    aliases = {
        'PAU D ARCO': "PAU D'ARCO",
        'PAU DARCO': "PAU D'ARCO",
        'MOJUI DOS CAMPOS': 'MOJUÍ DOS CAMPOS',
        'ELDORADO DOS CARAJAS': 'ELDORADO DO CARAJÁS',
    }
    for alias, official in aliases.items():
        if norm(official) in mapping:
            mapping[alias] = mapping[norm(official)]
    return mapping


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    strings: list[str] = []
    for _, element in ET.iterparse(archive.open('xl/sharedStrings.xml'), events=('end',)):
        if element.tag == NS + 'si':
            strings.append(''.join((node.text or '') for node in element.iter() if node.tag == NS + 't'))
            element.clear()
    return strings


def iter_rows(path: Path):
    """Stream only the columns used by the analysis from a CODEC XLSX export."""
    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        selected = {'A', 'B', 'C', 'D', 'F', 'T', 'U', 'V', 'AD'}
        row_values: dict[str, str] = {}
        first = True
        for _, element in ET.iterparse(archive.open('xl/worksheets/sheet1.xml'), events=('end',)):
            if element.tag == NS + 'c':
                reference = element.attrib.get('r', '')
                column = ''.join(character for character in reference if character.isalpha())
                if column in selected:
                    value_node = element.find(NS + 'v')
                    value = '' if value_node is None else (value_node.text or '')
                    if element.attrib.get('t') == 's' and value:
                        value = strings[int(value)]
                    row_values[column] = value
                element.clear()
            elif element.tag == NS + 'row':
                if first:
                    first = False
                else:
                    yield row_values
                row_values = {}
                element.clear()


def classify(consolidated: object, specification: object, victim_sex: object) -> tuple[str | None, bool]:
    consolidated_norm = norm(consolidated)
    specification_norm = norm(specification)
    sex_norm = norm(victim_sex)
    female = sex_norm == 'F'
    if consolidated_norm == 'FEMINICIDIO' or (
        consolidated_norm == 'HOMICIDIO' and 'FEMINICIDIO' in specification_norm
    ):
        return 'Feminicídio', female
    if consolidated_norm == 'LESAO CORPORAL':
        if specification_norm == 'VIOLENCIA DOMESTICA':
            return 'Lesão corporal - violência doméstica', female
        return 'Lesão corporal - outras especificações', female
    if consolidated_norm == 'ESTUPRO DE VULNERAVEL':
        return 'Estupro de vulnerável', female
    if consolidated_norm == 'ESTUPRO':
        return 'Estupro', female
    return None, female


def main() -> None:
    mapping = read_reference()
    detail: defaultdict[tuple[str, str, int, str, str], int] = defaultdict(int)
    audits: Counter[str] = Counter()
    unmatched: Counter[str] = Counter()
    raw_categories: Counter[tuple[int, str, str, str], int] = Counter()

    for year, filename in FILES.items():
        path = RAW / filename
        if not path.exists():
            raise FileNotFoundError(
                f'{path} not found. Download the complete {year} export from '
                'https://codec.segup.pa.gov.br/ and place it in data/external/codec_segup_2022_2025/.'
            )
        for row in iter_rows(path):
            audits['linhas_totais'] += 1
            consolidated = row.get('A', '')
            specification = row.get('B', '')
            municipality_raw = row.get('D', '')
            victim_sex = row.get('T', '')
            category, female = classify(consolidated, specification, victim_sex)
            if category is None:
                continue
            audits['linhas_naturezas_alvo'] += 1
            raw_categories[(year, norm(consolidated), norm(specification), norm(victim_sex))] += 1
            municipality = norm(municipality_raw)
            if municipality == 'ALTAMIRA/CASTELO DOS SONHOS':
                municipality = 'ALTAMIRA'
                audits['castelo_agregado_altamira'] += 1
            if municipality not in mapping:
                unmatched[municipality] += 1
                continue
            code, name = mapping[municipality]
            sex_status = (
                'Feminina'
                if female
                else ('Sexo não informado' if norm(victim_sex) in ('', 'PREJUDICADO') else 'Não feminina')
            )
            detail[(code, name, year, category, sex_status)] += 1

    detail_path = OUT / 'codec_registros_2022_2025_por_municipio_ano_natureza_sexo.csv'
    with detail_path.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['codigo_ibge', 'municipio', 'ano', 'natureza_padronizada', 'status_sexo_vitima', 'quantidade'])
        for key, quantity in sorted(detail.items(), key=lambda item: (item[0][2], item[0][1], item[0][3], item[0][4])):
            writer.writerow([*key, quantity])

    main_categories = {
        'Feminicídio',
        'Lesão corporal - violência doméstica',
        'Estupro',
        'Estupro de vulnerável',
    }
    panel: defaultdict[tuple[str, str, int, str], int] = defaultdict(int)
    for (code, name, year, category, sex_status), quantity in detail.items():
        if category in main_categories and (sex_status == 'Feminina' or category == 'Feminicídio'):
            panel[(code, name, year, category)] += quantity

    municipalities = sorted(set(mapping.values()), key=lambda item: item[1])
    panel_path = OUT / 'codec_painel_principal_2022_2025.csv'
    with panel_path.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['codigo_ibge', 'municipio', 'ano', 'natureza', 'quantidade'])
        for code, name in municipalities:
            for year in sorted(FILES):
                for category in [
                    'Feminicídio',
                    'Lesão corporal - violência doméstica',
                    'Estupro',
                    'Estupro de vulnerável',
                ]:
                    writer.writerow([code, name, year, category, panel.get((code, name, year, category), 0)])

    by_year: Counter[tuple[int, str]] = Counter()
    by_nature: Counter[str] = Counter()
    by_municipality: Counter[tuple[str, str, str]] = Counter()
    for (code, name, year, category), quantity in panel.items():
        by_year[(year, category)] += quantity
        by_nature[category] += quantity
        by_municipality[(code, name, category)] += quantity

    with (OUT / 'codec_resumo_ano_natureza_2022_2025.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['ano', 'natureza', 'quantidade'])
        for key, quantity in sorted(by_year.items()):
            writer.writerow([*key, quantity])

    with (OUT / 'codec_resumo_municipio_natureza_2022_2025.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['codigo_ibge', 'municipio', 'natureza', 'quantidade_2022_2025'])
        for key, quantity in sorted(by_municipality.items(), key=lambda item: (item[0][1], item[0][2])):
            writer.writerow([*key, quantity])

    report = {
        'source': 'Consulta de Dados Estatísticos Criminais (CODEC), SEGUP-PA',
        'source_url': 'https://codec.segup.pa.gov.br/',
        'download_date': '2026-02-02',
        'anos': [2022, 2023, 2024, 2025],
        'periodos_completos': True,
        'municipios_referencia': len(municipalities),
        'linhas_totais_lidas': audits['linhas_totais'],
        'linhas_naturezas_alvo': audits['linhas_naturezas_alvo'],
        'castelo_dos_sonhos_agregado_altamira': audits['castelo_agregado_altamira'],
        'municipios_nao_associados': dict(unmatched),
        'totais_natureza_principal': dict(by_nature),
        'totais_ano_natureza': {f'{year}|{category}': quantity for (year, category), quantity in sorted(by_year.items())},
        'regras': {
            'feminicidio': 'Consolidado ou especificação contém FEMINICIDIO; sexo auditado, sem excluir por definição legal.',
            'lesao_corporal': 'Consolidado LESAO CORPORAL + especificação VIOLENCIA DOMESTICA + vítima feminina.',
            'estupro': 'Consolidado ESTUPRO + vítima feminina.',
            'estupro_vulneravel': 'Consolidado ESTUPRO DE VULNERAVEL + vítima feminina.',
            'zeros_grade': 'Ausência de registro na exportação anual completa foi representada como zero após criação da grade completa.',
        },
    }
    (OUT / 'resumo_codec_v14.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    with (OUT / 'auditoria_categorias_codec_v14.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['ano', 'consolidado', 'especificacao', 'sexo_vitima', 'quantidade'])
        for key, quantity in sorted(raw_categories.items()):
            writer.writerow([*key, quantity])

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
