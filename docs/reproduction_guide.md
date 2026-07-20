# Reproduction guide

## 1. Reproducibility scope

The repository currently reproduces the final analytical stages from authorized processed municipal files. It does not yet contain a complete public upstream pipeline from raw police exports and original MUNIC files.

A fully clean run from raw restricted data therefore requires:

- authorized source files;
- the original preprocessing scripts or an equivalent verified reconstruction;
- exact source schemas and crosswalks;
- extraction-completeness records.

The limitation should remain explicit until those materials are added.

## 2. Environment

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Restricted local data

Place authorized source files only in local directories excluded from version control:

```text
data/raw/
data/external/
private/
```

Never commit raw police microdata.

## 4. Required processed inputs

The final scripts currently expect processed files in `data/processed/`. Important dependencies visible in the final-stage code include:

- `ici_mulheres_robustez_cenarios.csv`;
- `codec_resumo_taxas_municipio_natureza_2022_2025.csv`;
- `codec_taxas_100mil_mulheres_2022_2025.csv`;
- `base_mestre_com_munic_2023.csv`;
- `indice_visibilidade_exploratorio_v15.csv`;
- `prioridades_investigacao_consolidadas_v19.csv`;
- geographic input `data/raw/munics.geojson`.

This list should be verified against every script before release because additional intermediate dependencies may exist.

## 5. Exact final-stage execution order

The authoritative current order is the order encoded in `src/run_final_pipeline.py`:

```bash
python src/robust_underreporting_v17.py
python src/spatial_access_services_v18.py
python src/pareto_validation_v20.py
python src/sensitivity_scenario_factors_v22.py
python src/electre_tri_b_v25.py
```

Or run:

```bash
python src/run_final_pipeline.py
```

This guide now follows the executor. No analytical script was reordered or modified as part of the documentation audit.

## 6. Expected analytical dimensions

A successful run should reproduce:

- 144 municipalities;
- 216 scenario specifications;
- one 144 × 216 municipal flag matrix;
- robustness frequencies and classes;
- territorial-barrier outputs;
- Pareto fronts;
- factor-level sensitivity outputs;
- 108 ELECTRE TRI-B specifications;
- one 144 × 108 ELECTRE class matrix;
- aggregated tables used by the manuscript.

The current guide previously listed a baseline ELECTRE distribution of 91 Low, 27 Moderate, 16 High and 10 Very high municipalities. This distribution must be checked in a clean run before being treated as a frozen expected result.

## 7. Suggested clean-run protocol

When all required inputs are available:

1. create a new environment;
2. install only `requirements.txt`;
3. record Python and package versions;
4. remove or archive generated outputs from a previous run;
5. preserve restricted inputs unchanged;
6. run `python src/run_final_pipeline.py`;
7. capture stdout and stderr in a dated log;
8. verify row counts, scenario counts and missing values;
9. compare regenerated CSV, JSON, NPY and figure outputs with the archived manuscript version;
10. record hashes for files expected to be exactly deterministic;
11. document numerical or formatting differences separately.

## 8. Determinism and random seeds

The inspected final-stage scripts use deterministic ranking, quantiles, Cartesian products and multicriteria assignments. They do not appear to use random sampling, so no random seed is presently required.

A seed must be introduced and documented if synthetic data generation, resampling, stochastic optimization or simulation is added later.

## 9. Required validation checks

### Scenario analysis

- exactly 216 scenarios;
- municipality count equals 144;
- all flag values are binary;
- frequency equals flagged scenarios divided by 216 times 100;
- robustness bins match the documented boundaries;
- annual persistence uses year-specific visibility cuts.

### Territorial barrier

- all 144 municipalities have valid representative points;
- both service-hub sets are nonempty;
- self-service municipalities have zero distance to the applicable set;
- all distances are finite and nonnegative;
- final score equals `0.45 × any-service percentile + 0.55 × high-complexity percentile`.

### Pareto

- all 144 municipalities are assigned a valid front;
- front-1 membership agrees with the dominance implementation;
- criterion direction is consistent with greater investigation priority.

### ELECTRE TRI-B

- exactly 108 configurations;
- all weights sum to one within numerical tolerance;
- `q <= p <= v` for each threshold scheme;
- class values are integers from 0 to 3;
- baseline labels agree with numeric classes;
- minimum class never exceeds maximum class;
- stability equals equality of minimum and maximum assignments.

## 10. Output comparison report

A clean-run report should contain:

| Item | Archived value/hash | Regenerated value/hash | Status | Explanation |
|---|---|---|---|---|
| Municipality count | 144 | PENDING RUN | PENDING | |
| Scenario count | 216 | PENDING RUN | PENDING | |
| ELECTRE configurations | 108 | PENDING RUN | PENDING | |
| Robustness distribution | manuscript value | PENDING RUN | PENDING | |
| Baseline ELECTRE distribution | archived output | PENDING RUN | PENDING | |
| Consolidated groups | manuscript value | PENDING RUN | PENDING | |
| Figures | archived hashes | PENDING RUN | PENDING | |

## 11. Interpretation

Outputs are screening and decision-support results. They do not prove underreporting, estimate hidden incidence or constitute field validation. ELECTRE TRI-B and Pareto are complementary assessments using related municipal data, not independent external validation.
