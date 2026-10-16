# Institutional-fragility ablation

## Purpose

This analysis separates the contribution of institutional fragility from the
low-visibility and temporal-persistence conditions in the 216-scenario
factorial design.

Two models are compared for every municipality and scenario:

1. **Joint model:** institutional fragility, low reporting visibility and
   temporal persistence must all be satisfied.
2. **Visibility-only ablation:** only low reporting visibility and temporal
   persistence must be satisfied.

The comparison quantifies municipalities and municipality-scenario
observations removed by the institutional condition. It also reports how many
flag vectors are empirically distinct among the 216 parameter combinations.

## Public diagnostic already available

The public consolidated municipal output contains the baseline institutional
fragility measure for all 144 municipalities. Its distribution shows:

- minimum: 19.3571;
- mean: 82.6520;
- maximum: 100;
- 47 distinct values;
- 48 municipalities with fragility equal to 100.

For this baseline measure, the 0.67, 0.70 and 0.75 quantile cutoffs select the
same 48 municipalities. This explains why nearby fragility thresholds can
show zero classification effect. It does **not** mean that all municipalities
pass the institutional condition.

The reproducible figures are stored in
`outputs/tables/fragility_threshold_diagnostic_v26.csv`.

## Exact execution

Run from the repository root:

```bash
python src/ablation_fragility_v26.py
```

The script requires the same authorized processed inputs used by
`src/robust_underreporting_v17.py`:

- `data/processed/ici_mulheres_robustez_cenarios.csv`;
- `data/processed/codec_resumo_taxas_municipio_natureza_2022_2025.csv`;
- `data/processed/codec_taxas_100mil_mulheres_2022_2025.csv`.

These files are intentionally absent from the public repository. Raw police
microdata must not be committed.

## Outputs

The script creates new files and does not overwrite manuscript results:

- `ablation_fragility_v26_scenarios.csv`;
- `ablation_fragility_v26_municipal.csv`;
- `ablation_fragility_v26_effective_configurations.csv`;
- `ablation_fragility_v26_joint_matrix.npy`;
- `ablation_fragility_v26_visibility_only_matrix.npy`;
- `ablation_fragility_v26_summary.json`.

## Interpretation

The factorial design still contains 216 declared parameter combinations.
The number of unique municipal flag vectors measures their empirical
redundancy. The 18 combinations formed by visibility composition, visibility
threshold and persistence rule are also summarized separately. The ablation
determines whether institutional fragility acts as a substantive filter even
when its alternative weights and thresholds do not change the final flags.
