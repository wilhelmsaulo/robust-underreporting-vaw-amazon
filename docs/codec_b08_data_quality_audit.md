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

**Execution provenance (21 October 2026):** A complete independent re-execution of all four original CODEC XLSX workbooks with a column-reference-aware streaming XML reader reproduced the reported counts for every year. The original published audit script uses openpyxl and was not the implementation used in this successful re-run; equivalence of its output remains untested. No individual-level records were published.

## Confirmed independent full re-execution (21 October 2026)

All four annual workbooks were scanned from first to last row. The audit verified 643281 rows, 57886 analytically selected records, 1884 blank selected crime-specification entries, and 168 extra exact-attribute matches in the analytical subset. Every row had a filled occurrence-date field, with zero mismatches of the occurrence-year field against its annual export. This re-execution used an optimized streaming XML implementation that respects Excel column references, including omitted blank cells; it is separate from the openpyxl implementation in the published `src/audit_codec_b08.py`. By category, reproduced four-year totals were: feminicide 232; domestic-violence bodily injury 38864; rape 3236; and rape of vulnerable persons 15554. These exactly match the manuscript.
