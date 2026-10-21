# CODEC/SEGUP data-quality audit — Reviewer B08

## Scope and provenance

Four complete-calendar-year CODEC exports downloaded through the public CODEC interface were examined: 2022 `17_06_26.xlsx`, 2023 `17_06_26 (1).xlsx`, 2024 `17_06_26 (2).xlsx`, and 2025 `17_06_26 (3).xlsx`. Source: https://codec.segup.pa.gov.br/. This report contains **aggregate audit statistics only** and does not redistribute occurrence-level data.

## Summary of observed counts

| Year | Export rows | Analytical selected records | Exact-row repeated extras (all exports) | Exact-row repeated extras (analytical subset) | Missing crime specification (analytical subset) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2022 | 170649 | 14041 | 195 | 14 | 464 |
| 2023 | 166749 | 15405 | 454 | 69 | 598 |
| 2024 | 156945 | 14017 | 318 | 30 | 504 |
| 2025 | 148938 | 14423 | 279 | 55 | 318 |
| **Total** | **643281** | **57886** | **1246** | **168** | **1884** |

The analytical subset follows the original four-category selection and the victim-sex handling in `src/process_codec_microdata_v14.py`: feminicide, domestic-violence bodily injury involving female victims, rape involving female victims, and rape of vulnerable persons involving female victims. The published counts by category are 232, 38864, 3236, and 15554 (sum 57886), respectively.

## Checks and findings

- **Temporal fields:** All 643281 records had nonblank occurrence-date fields, and the recorded occurrence year matched the assigned annual export. These checks establish temporal *internal consistency*, **not independent completeness relative to the source system**.
- **Municipal and victim-sex fields:** No blank values were found in either field within the 57886 analytically selected records. Municipality-label crosswalking is applied in the original preprocessing and is distinct from this field-completeness check.
- **Crime specification:** 1884 selected records had blank specification fields. Their consolidated crime classification still supported the classification rule; they were not discarded automatically.
- **Exact row equality:** 1246 repeated-extra lines across the full exports; 168 within the selected subset. These are repeated **attribute combinations**, not proven duplicate occurrences or victims. The exported 30 columns lack an unequivocal unique occurrence or victim identifier. The source methodology may count certain offenses by victim. Consequently, automatic deletion based on row equality is not justified.
- **Zero completion:** The municipal-year-category grid was filled with zero for unobserved combinations after processing the annual exports. This is conditional on the supplied exports being complete for the requested periods; internal date checks alone cannot establish source-system completeness.

## Reproduction and disclosure

The reproducible, aggregate-only auditing procedure is in `src/audit_codec_b08.py`. Place the original workbooks in a locally controlled folder excluded from version control; run `python src/audit_codec_b08.py /path/to/folder`. Do not commit the XLSX files, individual-record hashes, or any record-level derived material. See `data/README.md` for the repository's restricted-data policy.

## Scientific interpretation

The audit supports the descriptive figures and documents known ambiguities. It does not establish any erroneous double counting and does not warrant removal of the 168 coincident lines without an authoritative unique record key and validated deduplication rule. Institutional completeness of the CODEC export cannot be independently established solely from exported field values. No recalculation of model results is warranted on the current evidence.

**Execution provenance:** the per-year aggregate numbers above were obtained during the earlier audit of all four submitted files. A later re-execution of the new procedural script was verified for 2022 only before timing out; full execution of the newly committed script has not yet been independently verified in this session.
