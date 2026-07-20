# Design of the 216 robustness scenarios

## Purpose

The scenario analysis identifies municipalities that repeatedly satisfy a conjunctive screening rule under plausible analytical choices. It does not estimate the number of unreported cases and does not confirm underreporting.

The signal is generated only from:

1. institutional fragility;
2. low reporting visibility;
3. persistence of low visibility over time.

The territorial barrier is not part of the 216-scenario flag. It is applied afterward to qualify priority and support the principal and expanded municipal groups.

## Factorial design

The full design is:

```text
4 institutional weighting schemes
× 3 visibility compositions
× 3 institutional-fragility thresholds
× 3 low-visibility thresholds
× 2 persistence rules
= 216 scenarios
```

## Institutional weighting schemes

The institutional capacity index contains 14 binary or coded MUNIC indicators. Institutional fragility is calculated as:

```text
fragility = 100 - institutional_capacity
```

Exact indicator-level weights are stored in `config/cenarios_pesos_ici_v6.csv`.

### Baseline (`base_v4`)

| Indicator | Weight (%) |
|---|---:|
| organismo_executivo | 8 |
| plano_municipal | 6 |
| conselho_mulher | 4 |
| conselho_ativo | 4 |
| conselho_infraestrutura | 4 |
| conselho_orcamento_proprio | 4 |
| casa_abrigo | 15 |
| ceam_niam | 15 |
| servico_violencia_sexual | 10 |
| centro_integrado | 10 |
| unidade_movel | 5 |
| casa_passagem | 5 |
| levantamento_atendimentos | 6 |
| divulga_atendimentos | 4 |

### Equal indicators (`pesos_iguais`)

All 14 indicators receive equal weight:

```text
100 / 14 = 7.142857142857143% per indicator
```

### Service emphasis (`prioridade_servicos`)

| Indicator | Weight (%) |
|---|---:|
| organismo_executivo | 4 |
| plano_municipal | 3 |
| conselho_mulher | 2 |
| conselho_ativo | 2 |
| conselho_infraestrutura | 2 |
| conselho_orcamento_proprio | 2 |
| casa_abrigo | 18 |
| ceam_niam | 18 |
| servico_violencia_sexual | 14 |
| centro_integrado | 14 |
| unidade_movel | 8 |
| casa_passagem | 8 |
| levantamento_atendimentos | 3 |
| divulga_atendimentos | 2 |

### Governance emphasis (`prioridade_governanca`)

| Indicator | Weight (%) |
|---|---:|
| organismo_executivo | 12 |
| plano_municipal | 12 |
| conselho_mulher | 8 |
| conselho_ativo | 8 |
| conselho_infraestrutura | 6 |
| conselho_orcamento_proprio | 6 |
| casa_abrigo | 10 |
| ceam_niam | 10 |
| servico_violencia_sexual | 6 |
| centro_integrado | 6 |
| unidade_movel | 3 |
| casa_passagem | 3 |
| levantamento_atendimentos | 6 |
| divulga_atendimentos | 4 |

## Visibility compositions

Municipal annual rates are converted into empirical state percentiles by year and police-record category. For each composition, the visibility score is the arithmetic mean of the included category percentiles.

### Recurrent three-category composition (`recorrentes_3`)

| Category | Weight |
|---|---:|
| Domestic-violence bodily injury | 1/3 |
| Rape | 1/3 |
| Rape of a vulnerable person | 1/3 |

### Sexual-violence composition (`sexuais_2`)

| Category | Weight |
|---|---:|
| Rape | 1/2 |
| Rape of a vulnerable person | 1/2 |

### Four-category composition (`quatro_naturezas`)

| Category | Weight |
|---|---:|
| Feminicide | 1/4 |
| Domestic-violence bodily injury | 1/4 |
| Rape | 1/4 |
| Rape of a vulnerable person | 1/4 |

The municipal cross-period visibility value used in the scenario rule is also the arithmetic mean of the corresponding category percentiles in the processed summary file.

## Thresholds

### Institutional fragility

For each weighting scheme, the following empirical quantiles of municipal fragility are used:

- 0.67;
- 0.70;
- 0.75.

A municipality satisfies the fragility condition when:

```text
fragility_i >= quantile(fragility, q_f)
```

### Low reporting visibility

For each visibility composition, the following empirical quantiles are used:

- 0.25;
- 0.33;
- 0.40.

The municipal cross-period visibility condition is:

```text
visibility_i <= quantile(visibility, q_v)
```

For persistence, the annual cut is calculated separately within each year using the same visibility quantile.

## Persistence rules

Two minimum-persistence requirements are evaluated:

- low visibility in at least 2 of the 4 years;
- low visibility in at least 3 of the 4 years.

For municipality `i`, year `t`, visibility composition `c`, and quantile `q_v`:

```text
low_i,t = 1 if visibility_i,t <= annual_quantile_t(visibility_c, q_v), otherwise 0
low_years_i = sum_t low_i,t
```

## Scenario flag

For municipality `i` and scenario `s`:

```text
flag_i,s = 1
```

only when all three conditions are satisfied:

```text
institutional_fragility_i >= scenario fragility cut
AND municipal_visibility_i <= scenario visibility cut
AND low_years_i >= scenario persistence requirement
```

Otherwise:

```text
flag_i,s = 0
```

## Municipal frequency

The robustness frequency is:

```text
frequency_i = (sum_s flag_i,s / 216) × 100
```

## Robustness classes

| Frequency | Class |
|---|---|
| 0% to 10%, inclusive at 10 | No robust signal |
| above 10% to 30% | Weak signal |
| above 30% to 60% | Moderate signal |
| above 60% to 100% | Strong signal |

The implementation uses the bins `[-0.01, 10, 30, 60, 100]`.

## Interpretation

A high frequency means that the municipality satisfies the screening conditions under many plausible combinations of weights, thresholds, visibility definitions and persistence requirements. It does not measure the probability that underreporting exists.
