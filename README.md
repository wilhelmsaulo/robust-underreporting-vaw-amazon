# Robust Multicriteria Decision Support for Identifying Potential Underreporting of Violence Against Women in the Brazilian Amazon

This repository contains the reproducibility materials for the study **“Robust Multicriteria Decision Support for Identifying Potential Underreporting of Violence Against Women in the Brazilian Amazon.”**

## Study objective

The study develops a municipal-level decision-support framework for identifying places where police records may provide a comparatively weak representation of violence against women. The framework does not estimate hidden incidence and does not confirm underreporting. It identifies municipalities that warrant closer investigation because institutional fragility coincides with persistently low reporting visibility.

The analytical sequence is intentionally staged:

1. the 216-scenario analysis produces a robustness signal from institutional fragility and persistently low reporting visibility;
2. the territorial barrier is applied later to qualify investigation priority and support the principal and expanded groups;
3. ELECTRE TRI-B and Pareto analysis provide complementary multicriteria assessment and methodological triangulation.

These methods use related municipal information and are therefore not independent sources of evidence. No field validation or confirmed ground truth of underreporting was available.

## Data sources

- MUNIC 2023 institutional indicators;
- SEGUP/CODEC police records covering the complete calendar years 2022–2025;
- 2022 Census female population, used as a fixed denominator for all annual rates;
- IBGE municipal geographic data;
- municipal locations of services for women.

The annual CODEC exports were downloaded from the public SEGUP-PA platform on 2026-02-02. Detailed police-record exports and original MUNIC spreadsheets are not redistributed. See [`data/README.md`](data/README.md), [`data/derived/README.md`](data/derived/README.md), and [`docs/codec_data_source.md`](docs/codec_data_source.md).

## Repository structure

```text
.
├── config/          # Parameter files and analytical configurations
├── data/
│   ├── raw/         # Local source inputs; excluded from version control
│   ├── processed/   # Pipeline intermediate files
│   ├── derived/     # Compact public municipal-level results
│   └── README.md
├── docs/            # Methodological and reproducibility documentation
├── outputs/         # Aggregated manuscript-oriented tables and figures
├── src/             # Preprocessing and analysis scripts
├── tests/           # Automated tests
├── CITATION.cff
├── LICENSE
├── requirements.txt
└── README.md
```

The existing `outputs/` directory is preserved because current scripts depend on it. The `data/derived/` directory is the preferred entry point for readers interested in the public results rather than pipeline internals.

## Public derived results

The following compact files cover all 144 municipalities where applicable:

- [`statewide_rates_2022_2025.csv`](data/derived/statewide_rates_2022_2025.csv);
- [`municipal_robustness_summary.csv`](data/derived/municipal_robustness_summary.csv);
- [`municipal_priority_groups.csv`](data/derived/municipal_priority_groups.csv);
- [`electre_tri_b_summary.csv`](data/derived/electre_tri_b_summary.csv);
- [`pareto_summary.csv`](data/derived/pareto_summary.csv).

Definitions, provenance, and interpretation limits are documented in [`data/derived/README.md`](data/derived/README.md).

## Requirements

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Reproduction workflow

Place the original local inputs in the ignored directories described in the data documentation. The preprocessing chain includes MUNIC 2023, Censo 2022 female population, CODEC/SEGUP-PA annual exports, population-rate construction, robustness analysis, territorial accessibility, Pareto validation, factor sensitivity, and ELECTRE TRI-B.

The main analytical stages are:

```bash
python src/process_munic_2023.py
python src/fetch_censo2022_sidra.py
python src/process_censo2022.py
python src/process_codec_microdata_v14.py
python src/build_population_rates_v15.py
python src/robust_underreporting_v17.py
python src/spatial_access_services_v18.py
python src/pareto_validation_v20.py
python src/sensitivity_scenario_factors_v22.py
python src/electre_tri_b_v25.py
```

The complete validation performed on the consolidated project reproduced 144 municipalities, 216 robustness scenarios, 108 ELECTRE configurations, the manuscript priority groups, and the reported statewide totals. See [`docs/validation_report_2026-07-20.md`](docs/validation_report_2026-07-20.md).

## Analytical components

### 216 robustness scenarios

The scenario design combines four institutional weighting schemes, three visibility compositions, three institutional-fragility thresholds, three low-visibility thresholds, and two persistence rules. The complete specification is documented in [`docs/scenario_design.md`](docs/scenario_design.md).

### MUNIC indicators

The exact weights used for the 14 institutional indicators are stored in [`config/cenarios_pesos_ici_v6.csv`](config/cenarios_pesos_ici_v6.csv). A consolidated metadata table is provided in [`docs/municipal_indicators.md`](docs/municipal_indicators.md).

### Territorial barrier

The territorial score uses WGS84 geodesic distances between representative municipal points and the nearest municipalities containing two service sets. Distances are expressed in kilometres, converted to empirical percentile ranks, and combined as 45% for any specialized service and 55% for high-complexity services. Geodesic distance is not equivalent to road or river travel time. See [`docs/territorial_barrier.md`](docs/territorial_barrier.md).

### ELECTRE TRI-B

The complementary ELECTRE TRI-B assessment evaluates 108 specifications generated from four weighting schemes, three profile schemes, three threshold configurations, and three lambda values. The implementation uses a local classical pessimistic assignment procedure. See [`docs/electre_tri_b.md`](docs/electre_tri_b.md).

### Pareto analysis

Pareto fronts are used as a non-compensatory complementary assessment. They are not external validation and do not provide independent confirmation of underreporting.

## Reproducibility safeguards

- dependency versions are fixed in `requirements.txt`;
- raw/external source directories, caches, backups, office files, and common secret files are excluded by `.gitignore`;
- current analytical scripts are deterministic;
- automated tests cover core preprocessing behavior;
- changes that may alter classifications, figures, or manuscript results must be evaluated separately before implementation.

## Interpretation and limitations

- the signal from the 216 scenarios is generated by institutional fragility and persistently low reporting visibility;
- the territorial barrier is used subsequently to qualify priority and form consolidated groups;
- ELECTRE TRI-B and Pareto provide complementary triangulation, not external validation;
- no field validation was conducted;
- the 2022 female population was used as a fixed denominator for 2022–2025 rates;
- geodesic distance does not represent actual travel time;
- administrative records may reflect both underlying violence and reporting, access, recording, and institutional processes.

## License

Source code and documentation are released under the MIT License. Data remain subject to the terms, legal restrictions, and attribution requirements of their original providers.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Article DOI and complete author identifiers will be added after confirmation.

## Contact

Saulo William da Silva Costa  
Federal Institute of Education, Science and Technology of Pará, Campus Óbidos  
Email: saulo.costa@ifpa.edu.br
