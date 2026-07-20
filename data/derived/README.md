# Public derived results

This directory contains the compact, municipal-level aggregate outputs intended for public use and manuscript verification. These files do not contain row-level police records, victim or author attributes, coordinates of individual occurrences, or the original MUNIC and CODEC spreadsheets.

## Main files

- `statewide_rates_2022_2025.csv`: annual statewide counts and rates per 100,000 women for the four crime categories used in the study.
- `municipal_robustness_summary.csv`: number and percentage of the 216 robustness scenarios in which each municipality was flagged, with its robustness class and rank.
- `municipal_priority_groups.csv`: consolidated municipal groups and the institutional, visibility, persistence, and territorial-barrier indicators used to interpret them.
- `electre_tri_b_summary.csv`: baseline ELECTRE TRI-B class, sensitivity range, high-priority stability, and convergence indicators for all 144 municipalities.
- `pareto_summary.csv`: Pareto-front assignment and the three oriented criteria used in the non-compensatory validation.

## Supplementary audit files

The complete scenario definitions and matrices remain reproducible through the scripts and configuration files. Larger intermediate outputs are retained under `data/processed/` when needed by the pipeline; they are not duplicated here.

## Interpretation

These outputs are screening and decision-support results. They do not estimate hidden incidence, prove underreporting, or rank municipalities by violence prevalence. Low administrative visibility is interpreted only together with institutional fragility, temporal persistence, and territorial access conditions.

## Provenance

Police-record exports were downloaded from the public Consulta de Dados Estatísticos Criminais platform maintained by SEGUP-PA on 2026-02-02. The annual exports cover the complete calendar years 2022–2025. Original detailed exports are not redistributed in this repository.
