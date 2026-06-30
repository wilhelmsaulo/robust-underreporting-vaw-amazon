# Robust Multicriteria Decision Support for Identifying Potential Underreporting of Violence Against Women

This repository contains the reproducibility materials for the study **“Robust Multicriteria Decision Support for Identifying Potential Underreporting of Violence Against Women: A Municipal-Level Study in the Brazilian Amazon.”**

## Overview

The analytical framework integrates municipal institutional capacity, police records from 2022–2025, female-population denominators, temporal persistence of low reporting visibility, and territorial accessibility to specialized services. The final workflow combines:

- 216 analytical scenarios;
- robustness and factor-level sensitivity analysis;
- classical ELECTRE TRI-B sorting under 108 sensitivity specifications;
- Pareto-based non-compensatory validation;
- municipal priority groups for complementary investigation.

The framework is designed for screening and decision support. It does **not** estimate hidden incidence directly and does **not** confirm underreporting.

## Repository structure

```text
.
├── config/       # Analytical parameters and model configurations
├── data/         # Data documentation and permitted derived files
├── docs/         # Methodology, data availability, and reproduction guide
├── outputs/      # Aggregated tables and final analytical outputs
├── src/          # Final analysis scripts
├── CITATION.cff
├── LICENSE
├── requirements.txt
└── README.md
```

## Data availability

Raw police microdata are not included in this repository because they may be subject to institutional and privacy restrictions. The repository provides code, configurations, data dictionaries, and non-identifying derived outputs needed to document and reproduce the analytical procedures when authorized source files are available.

See [`data/README.md`](data/README.md) and [`docs/data_availability.md`](docs/data_availability.md).

## Reproduction

The recommended execution order is documented in [`docs/reproduction_guide.md`](docs/reproduction_guide.md).

Main analytical scripts:

1. `src/robust_underreporting_v17.py`
2. `src/sensitivity_scenario_factors_v22.py`
3. `src/spatial_access_services_v18.py`
4. `src/pareto_validation_v20.py`
5. `src/electre_tri_b_v25.py`

## Software

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## License

The source code is released under the MIT License. Data remain subject to the terms and restrictions of their original providers.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). The article DOI will be added after publication.

## Contact

Saulo William da Silva Costa  
Federal Institute of Education, Science and Technology of Pará, Campus Óbidos  
Email: saulo.costa@ifpa.edu.br
