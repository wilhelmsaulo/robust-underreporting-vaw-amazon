#!/usr/bin/env python3
"""Baixa indicadores municipais do Censo 2022 via API SIDRA.

Tabelas:
- 10295: rendimento domiciliar mensal per capita, médio e mediano.
- 9923: população residente por situação urbana/rural.
- 9543: taxa de alfabetização das pessoas de 15 anos ou mais.

A consulta usa todos os municípios do Pará (UF 15) e preserva as respostas
JSON em data/raw_api. Em caso de indisponibilidade da API, o script termina
com mensagem objetiva e mantém URLs prontas para nova tentativa.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final

import requests

ROOT: Final = Path(__file__).resolve().parents[1]
OUT: Final = ROOT / "data" / "raw_api"
OUT.mkdir(parents=True, exist_ok=True)

# As dimensões são mantidas amplas; o tratamento seleciona os totais relevantes
# com base nos rótulos devolvidos pelo SIDRA, evitando depender de IDs frágeis.
URLS: dict[str, str] = {
    "sidra_10295_rendimento_2022.json": (
        "https://apisidra.ibge.gov.br/values/t/10295/n6/in%20n3%2015/v/all/p/2022/all?formato=json"
    ),
    "sidra_9923_urbano_rural_2022.json": (
        "https://apisidra.ibge.gov.br/values/t/9923/n6/in%20n3%2015/v/all/p/2022/all?formato=json"
    ),
    "sidra_9543_alfabetizacao_2022.json": (
        "https://apisidra.ibge.gov.br/values/t/9543/n6/in%20n3%2015/v/all/p/2022/all?formato=json"
    ),
}


def fetch(name: str, url: str) -> None:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Resposta inesperada para {name}")
    path = OUT / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {name} ({len(payload)-1} registros)")


def main() -> int:
    failures: list[str] = []
    for name, url in URLS.items():
        try:
            fetch(name, url)
        except Exception as exc:  # rede/HTTP/formato
            failures.append(f"{name}: {exc}")
            print(f"FALHA: {name}: {exc}", file=sys.stderr)

    (ROOT / "config" / "urls_sidra_censo2022.json").write_text(
        json.dumps(URLS, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if failures:
        print("\nA API não respondeu para todas as tabelas. URLs preservadas em config/urls_sidra_censo2022.json.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
