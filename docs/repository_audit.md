# Repository reproducibility audit

## Audit scope

This audit was initiated to improve documentation and organization without changing analytical results, municipal classifications, figures or methodological decisions.

Branch used for the documentation work:

```text
docs/reproducibility-audit
```

## Preserved analytical components

The following existing components were retained without modification:

- `src/robust_underreporting_v17.py`;
- `src/sensitivity_scenario_factors_v22.py`;
- `src/spatial_access_services_v18.py`;
- `src/pareto_validation_v20.py`;
- `src/electre_tri_b_v25.py`;
- `src/electre_tri_b_core.py`;
- existing analytical configuration values;
- existing generated results and figures;
- the `outputs/` directory name and script dependencies.

## Documentation changes completed

- expanded root README;
- added MIT license for code and documentation;
- documented the full 216-scenario factorial design;
- documented the 108 ELECTRE TRI-B configurations;
- documented the territorial-barrier formula and service sets;
- created a consolidated MUNIC indicator metadata table with exact weights;
- documented police-record preprocessing requirements and restrictions;
- strengthened the restricted-data policy;
- aligned the reproduction guide with the actual pipeline executor;
- clarified that ELECTRE TRI-B and Pareto are complementary triangulation, not external validation;
- clarified the fixed 2022 female-population denominator;
- clarified that geodesic distance is not travel time.

## Confirmed repository strengths

- final analytical scripts are modular;
- dependencies are pinned by version;
- restricted directories are excluded through `.gitignore`;
- exact scenario and ELECTRE parameter files exist;
- final scripts use deterministic operations and do not currently require a random seed;
- the repository already warns that the framework does not estimate hidden incidence;
- a data-availability statement and `CITATION.cff` already exist.

## Information still required from the authors

- exact police-data extraction or delivery date;
- complete source-file inventory and checksums;
- exact police-record filters and exclusion counts;
- duplicate definition and treatment;
- annual extraction-completeness confirmation;
- original MUNIC variable codes and questionnaire mappings;
- exact MUNIC missing-value treatment;
- source year and download metadata for municipal geometries;
- complete author list and ORCIDs for `CITATION.cff`;
- confirmation that each aggregate municipal output may be publicly released.

## Technical work still pending

### Full clean run

A complete raw-to-results run cannot yet be performed from the public repository because upstream preprocessing scripts and restricted source schemas are incomplete or absent.

When the authorized processed inputs are available, run:

```bash
python src/run_final_pipeline.py
```

Then compare all regenerated outputs with the archived manuscript results.

### Consolidated 144-municipality table

A single public table should be assembled, where permitted, with:

- institutional capacity and fragility;
- annual category rates;
- visibility percentiles;
- persistence;
- frequency across 216 scenarios;
- robustness class;
- territorial barrier;
- reference ELECTRE class;
- stability across 108 specifications;
- Pareto front;
- consolidated group.

This should be assembled from existing outputs without changing classifications.

### Institutional-index saturation diagnostic

The following diagnostic remains pending because it requires the processed municipal index files:

- distribution of each institutional index;
- number of unique values;
- number of municipalities with fragility equal to 100;
- size and position of ties;
- explanation of why weights and institutional thresholds did or did not change classifications.

This diagnostic is descriptive and should not alter the model.

## Analyses requiring separate approval and result review

The following were not implemented in this documentation branch:

1. alternative territorial-barrier cut points for principal and expanded groups;
2. institutional fragility recalculated without service-existence indicators.

Both may change groups, tables, figures or interpretation. They should be run on a separate analysis branch and compared with the main results before any manuscript revision.

## Manuscript alignment

The article should state explicitly that:

- the 216-scenario signal is produced by institutional fragility and persistently low reporting visibility;
- territorial barriers are applied afterward to qualify priority and form the principal and expanded groups;
- ELECTRE TRI-B and Pareto are complementary assessments or methodological triangulation;
- these methods use related municipal data and are not independent evidence sources;
- no field validation was conducted;
- 2022 female population is the fixed denominator for 2022–2025;
- geodesic distance is not actual travel time.

## Limitations that should remain declared

- no confirmed ground truth of municipal underreporting;
- no field validation;
- dependence on administrative-record quality and extraction completeness;
- possible overlap between service indicators and territorial accessibility;
- fixed population denominator;
- geodesic rather than network or travel-time accessibility;
- municipal aggregation and within-municipality heterogeneity;
- related criteria across complementary methods.
