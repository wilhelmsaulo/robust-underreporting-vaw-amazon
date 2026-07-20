# MUNIC institutional indicators

## Purpose

This document consolidates the 14 MUNIC indicators used to calculate municipal institutional capacity and fragility. Exact analytical weights are taken from `config/cenarios_pesos_ici_v6.csv`.

Institutional capacity is a weighted combination of the coded indicators. Institutional fragility is defined as:

```text
institutional_fragility = 100 - institutional_capacity
```

## Metadata status

The repository currently contains the analytical indicator names and exact weights, but it does not yet contain the complete upstream MUNIC extraction dictionary. Therefore, original MUNIC variable codes, detailed recoding rules and missing-value handling are marked **PENDING CONFIRMATION** rather than inferred.

No pending field below should be completed by guessing. It must be verified against the original MUNIC 2023 questionnaire, extraction files and preprocessing script.

## Indicator table

| Analytical indicator | Original MUNIC variable | Dimension | Current analytical coding | Direction | Normalization | Missing-value treatment |
|---|---|---|---|---|---|---|
| organismo_executivo | PENDING CONFIRMATION | Governance | Expected coded presence/absence; verify exact positive categories | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| plano_municipal | PENDING CONFIRMATION | Governance | Expected coded presence/absence; verify validity/status conditions | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| conselho_mulher | PENDING CONFIRMATION | Governance | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| conselho_ativo | PENDING CONFIRMATION | Governance | Expected coded active/inactive status | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| conselho_infraestrutura | PENDING CONFIRMATION | Governance | Expected coded availability of infrastructure | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| conselho_orcamento_proprio | PENDING CONFIRMATION | Governance | Expected coded presence/absence of own budget | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| casa_abrigo | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| ceam_niam | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| servico_violencia_sexual | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| centro_integrado | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| unidade_movel | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| casa_passagem | PENDING CONFIRMATION | Services | Expected coded presence/absence | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| levantamento_atendimentos | PENDING CONFIRMATION | Monitoring | Expected coded existence of service/attendance survey or compilation | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |
| divulga_atendimentos | PENDING CONFIRMATION | Monitoring | Expected coded disclosure/publication of attendance information | Higher = greater capacity | Weighted contribution to 0–100 index | PENDING CONFIRMATION |

## Exact weights by scheme

| Indicator | Baseline | Equal indicators | Service emphasis | Governance emphasis |
|---|---:|---:|---:|---:|
| organismo_executivo | 8 | 7.142857142857143 | 4 | 12 |
| plano_municipal | 6 | 7.142857142857143 | 3 | 12 |
| conselho_mulher | 4 | 7.142857142857143 | 2 | 8 |
| conselho_ativo | 4 | 7.142857142857143 | 2 | 8 |
| conselho_infraestrutura | 4 | 7.142857142857143 | 2 | 6 |
| conselho_orcamento_proprio | 4 | 7.142857142857143 | 2 | 6 |
| casa_abrigo | 15 | 7.142857142857143 | 18 | 10 |
| ceam_niam | 15 | 7.142857142857143 | 18 | 10 |
| servico_violencia_sexual | 10 | 7.142857142857143 | 14 | 6 |
| centro_integrado | 10 | 7.142857142857143 | 14 | 6 |
| unidade_movel | 5 | 7.142857142857143 | 8 | 3 |
| casa_passagem | 5 | 7.142857142857143 | 8 | 3 |
| levantamento_atendimentos | 6 | 7.142857142857143 | 3 | 6 |
| divulga_atendimentos | 4 | 7.142857142857143 | 2 | 4 |

Each non-equal scheme sums to 100. The equal scheme uses fourteen equal raw weights and normalized percentages of `100/14`.

## Required verification before final public release

The following must be recovered from the original preprocessing materials:

1. exact MUNIC 2023 variable names or codes;
2. questionnaire wording and response categories;
3. recoding from original categories to analytical values;
4. whether nonresponse, “not applicable” and missing values were treated as zero, excluded, imputed or otherwise coded;
5. whether any indicators were constructed from more than one original variable;
6. confirmation that all indicators are oriented so that higher values mean greater institutional capacity;
7. formula used when one or more indicator values are missing;
8. source file name, extraction date and questionnaire edition.

## Potential overlap with territorial accessibility

Six service-existence indicators are also used to identify territorial service hubs. This creates a plausible conceptual overlap between institutional fragility and territorial accessibility. A sensitivity analysis excluding service-existence indicators from institutional fragility has been proposed, but it must be treated as an additional analysis because it could change classifications and manuscript results.
