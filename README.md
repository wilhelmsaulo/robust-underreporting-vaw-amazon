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
- SEGUP/CODEC police records covering 2022–2025;
- 2022 Census female population, used as a fixed denominator for all annual rates;
- IBGE municipal geographic data;
- municipal locations of services for women.

Raw police microdata are not redistributed. See [`data/README.md`](data/README.md) and [`docs/data_availability.md`](docs/data_availability.md).

## Repository structure

```text
.
├── config/          # Parameter files and analytical configurations
├── data/
│   ├── raw/         # Restricted/local inputs; excluded from version control
│   ├── processed/   # Derived municipal files used by the analytical scripts
│   └── README.md
├── docs/            # Methodological and reproducibility documentation
├── outputs/         # Aggregated tables and manuscript-oriented outputs
├── src/             # Analysis scripts
├── CITATION.cff
├── LICENSE
├── requirements.txt
└── README.md
```

The existing `outputs/` directory is preserved because current scripts depend on it. Renaming it to `results/` would require code changes and is not necessary for reproducibility.

## Requirements

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Exact execution order

The public repository currently reproduces the final analytical stages from authorized processed municipal files. Place the required local inputs in `data/processed/` and then run:

```bash
python src/robust_underreporting_v17.py
python src/spatial_access_services_v18.py
python src/pareto_validation_v20.py
python src/sensitivity_scenario_factors_v22.py
python src/electre_tri_b_v25.py
```

Alternatively:

```bash
python src/run_final_pipeline.py
```

The order above follows the current pipeline executor and preserves existing dependencies. The upstream police and MUNIC preprocessing stages are not yet fully reconstructible from the public repository; this limitation is documented in [`docs/reproduction_guide.md`](docs/reproduction_guide.md).

## Analytical components

### 216 robustness scenarios

The scenario design combines:

- four institutional weighting schemes;
- three visibility compositions;
- three institutional-fragility thresholds;
- three low-visibility thresholds;
- two persistence rules.

The complete specification, formulas, thresholds and category weights are documented in [`docs/scenario_design.md`](docs/scenario_design.md).

### MUNIC indicators

The exact weights used for the 14 institutional indicators are stored in [`config/cenarios_pesos_ici_v6.csv`](config/cenarios_pesos_ici_v6.csv). A consolidated metadata table is provided in [`docs/municipal_indicators.md`](docs/municipal_indicators.md). Fields that require confirmation from the original preprocessing dictionary are explicitly marked as pending rather than inferred.

### Territorial barrier

The territorial score uses WGS84 geodesic distances between representative municipal points and the nearest municipalities containing two service sets. Distances are expressed in kilometres, converted to empirical percentile ranks, and combined as 45% for any specialized service and 55% for high-complexity services. Geodesic distance is not equivalent to road or river travel time. See [`docs/territorial_barrier.md`](docs/territorial_barrier.md).

### ELECTRE TRI-B

The complementary ELECTRE TRI-B assessment evaluates 108 specifications generated from four weighting schemes, three profile schemes, three threshold configurations, and three lambda values. The implementation uses a local classical pessimistic assignment procedure. See [`docs/electre_tri_b.md`](docs/electre_tri_b.md).

### Pareto analysis

Pareto fronts are used as a non-compensatory complementary assessment. They are not external validation and do not provide independent confirmation of underreporting.

## Reproducibility scope

The repository is intended to provide:

- source code;
- exact parameter configurations;
- methodological documentation;
- variable dictionaries;
- aggregated municipal results suitable for public release;
- instructions for authorized reconstruction of the analysis.

It does not provide protected police microdata. A complete clean run from raw restricted records cannot be performed from the public repository alone until the upstream preprocessing scripts and source-file specifications are finalized.

## Reproducibility safeguards

- dependency versions are fixed in `requirements.txt`;
- restricted directories are excluded by `.gitignore`;
- current analytical scripts are deterministic unless a future stage introduces random sampling;
- no random seed is presently required by the final analytical chain;
- changes that may alter classifications, figures or manuscript results must be evaluated separately before implementation.

## Interpretation and limitations

- the signal from the 216 scenarios is generated by institutional fragility and persistently low reporting visibility;
- the territorial barrier is used subsequently to qualify priority and form consolidated groups;
- ELECTRE TRI-B and Pareto provide complementary triangulation, not external validation;
- the methods use related municipal data and are not independent evidence sources;
- no field validation was conducted;
- the 2022 female population was used as a fixed denominator for 2022–2025 rates;
- geodesic distance does not represent actual travel time;
- administrative records may reflect both underlying violence and reporting, access, recording and institutional processes.

## License

Source code and documentation are released under the MIT License. Data remain subject to the terms, legal restrictions and attribution requirements of their original providers.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Article DOI and complete author identifiers should be added after confirmation.

## Contact

Saulo William da Silva Costa  
Federal Institute of Education, Science and Technology of Pará, Campus Óbidos  
Email: saulo.costa@ifpa.edu.br
