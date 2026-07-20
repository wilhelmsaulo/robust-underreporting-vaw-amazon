from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_population_rates_v15 import percentile_ranks
from process_codec_microdata_v14 import classify, norm


def test_codec_normalization_preserves_meaning() -> None:
    assert norm("  Violência   Doméstica ") == "VIOLENCIA DOMESTICA"
    assert norm("Mojuí dos Campos") == "MOJUI DOS CAMPOS"


def test_codec_target_classification() -> None:
    assert classify("ESTUPRO", "", "F") == ("Estupro", True)
    assert classify("ESTUPRO DE VULNERÁVEL", "", "F") == ("Estupro de vulnerável", True)
    assert classify("LESÃO CORPORAL", "VIOLÊNCIA DOMÉSTICA", "F") == (
        "Lesão corporal - violência doméstica",
        True,
    )
    assert classify("HOMICÍDIO", "FEMINICÍDIO", "F") == ("Feminicídio", True)


def test_non_target_category_is_excluded() -> None:
    assert classify("FURTO", "", "F") == (None, True)


def test_percentile_ranks_use_average_ties() -> None:
    result = percentile_ranks([0.0, 10.0, 10.0, 20.0])
    assert result == [0.0, 0.5, 0.5, 1.0]
