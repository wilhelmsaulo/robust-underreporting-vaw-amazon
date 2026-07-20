# Reproducibility validation report — 20 July 2026

## Source package

Validated package: `Projeto_PLOS_v25_ELECTRE_TRI_B_Classico (1).zip`.

## Static and unit validation

- all Python files compiled successfully;
- the original test suite passed: **7/7 tests**;
- the integrated preprocessing core adds tests for CODEC normalization, target-category recoding and percentile ranking;
- no passwords, API tokens or personal absolute paths were found in the integrated files.

## Raw CODEC processing

The four complete annual XLSX exports were processed from the public CODEC/SEGUP-PA source.

- rows read: **643,281**;
- target-category rows before analytical filtering: **114,070**;
- municipalities in the reference frame: **144**;
- unmatched municipalities after documented aliases: **0**;
- Castelo dos Sonhos records aggregated to Altamira: **212**.

Final totals for 2022–2025:

| Category | Records |
|---|---:|
| Feminicide | 232 |
| Domestic-violence bodily injury involving female victims | 38,864 |
| Rape involving female victims | 3,236 |
| Rape of a vulnerable person involving female victims | 15,554 |

## Full downstream run

After regenerating the CODEC municipal panel, the following stages completed successfully:

1. population-denominator and rate construction;
2. 216-scenario robustness analysis;
3. territorial-accessibility analysis;
4. Pareto validation;
5. factor-level scenario sensitivity;
6. classical ELECTRE TRI-B v25.

## Reproduced dimensions

- municipalities in robustness output: **144**;
- robustness scenarios: **216**;
- robustness matrix: **144 × 216**;
- municipalities in ELECTRE output: **144**;
- ELECTRE specifications: **108**;
- ELECTRE class matrix: **144 × 108**.

## Baseline ELECTRE distribution

| Class | Municipalities |
|---|---:|
| Low | 91 |
| Moderate | 27 |
| High | 16 |
| Very high | 10 |

These values reproduce the archived v25 result.

## Portability issue identified

The legacy file `src/finalize_codec_v14.py` was not integrated because it contains an obsolete absolute path and depends on temporary `/tmp/codec_*` files. Its required functionality is consolidated in the portable `src/process_codec_microdata_v14.py` workflow.

## Interpretation

Successful software reproduction confirms that the code regenerates the documented analytical outputs from the supplied source files. It does not validate hidden incidence or prove municipal underreporting.
