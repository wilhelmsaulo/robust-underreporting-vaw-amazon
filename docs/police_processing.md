# Processing of police records

## Scope

The study uses municipal police-record data supplied by SEGUP/CODEC for the years 2022, 2023, 2024 and 2025. Raw microdata are protected and are not redistributed through this repository.

This document separates confirmed study rules from information that is still absent from the public repository. Missing details are marked **PENDING CONFIRMATION** and must be recovered from the original preprocessing code or extraction records.

## Confirmed analytical coverage

- geographic unit: municipalities in Pará;
- analytical period: 2022–2025;
- principal categories used in the scenario analysis:
  - domestic-violence bodily injury;
  - rape;
  - rape of a vulnerable person;
  - feminicide, in the four-category composition;
- annual rates calculated per 100,000 women;
- fixed denominator: female population from the 2022 Census for all four years;
- Castelo dos Sonhos must be aggregated to Altamira because it is not an independent municipality in the municipal analytical frame.

## Required processing sequence

The complete reproducible preprocessing stage should implement and record the following order.

### 1. Source inventory and integrity checks

For every annual export, record:

- original filename;
- file checksum;
- extraction or delivery date;
- period covered;
- number of rows received;
- expected start and end dates;
- confirmation that the extraction represents the full requested year;
- responsible source unit and authorization conditions.

**Extraction date:** PENDING CONFIRMATION.

A missing municipality-category-year combination may be converted to zero only after the annual export has been confirmed as complete. Otherwise, absence can reflect incomplete extraction rather than zero recorded events.

### 2. Filters

The exact filters used on occurrence status, victim sex, age, date field, jurisdiction, municipality and record validity are **PENDING CONFIRMATION**.

The final documentation must state:

- which date field defines the analytical year;
- whether attempted and completed events are combined;
- how cancelled, invalidated or duplicate records are handled;
- whether only female victims are retained and how sex/gender values are coded;
- whether records outside Pará are excluded;
- whether records without a valid municipality are excluded or reassigned;
- exact nature/category inclusion rules.

### 3. Municipality standardization

The preprocessing should:

- strip whitespace and harmonize capitalization and accents;
- map spelling variants and legacy names to official IBGE municipality names;
- attach seven-digit IBGE municipality codes;
- aggregate Castelo dos Sonhos to Altamira;
- generate an exception log for unmatched or ambiguous localities;
- avoid fuzzy reassignment without a documented review table.

The complete municipality crosswalk is **PENDING CONFIRMATION**.

### 4. Category standardization

Original police nature labels must be mapped to the analytical categories using an explicit lookup table. The table should contain:

- original code;
- original label;
- standardized category;
- inclusion/exclusion status;
- notes on legal or coding changes across years.

The exact original codes and labels are **PENDING CONFIRMATION**.

### 5. Duplicate treatment

The repository does not currently document the unique record key or deduplication rule.

The final pipeline must identify:

- candidate identifier fields;
- exact duplicate definition;
- whether multiple victims or multiple categories within one occurrence generate multiple analytical rows;
- priority rule for conflicting duplicates;
- number of rows removed by year and reason.

Current rule and counts: **PENDING CONFIRMATION**.

### 6. Missing fields

The final pipeline must distinguish:

- missing victim sex;
- missing occurrence date;
- missing municipality;
- missing nature/category;
- malformed identifiers;
- incomplete annual municipality-category combinations.

For each field, document whether records are excluded, corrected through a crosswalk, retained in an unknown category or otherwise treated.

Current treatment and counts: **PENDING CONFIRMATION**.

### 7. Exclusion log

A non-identifying aggregate exclusion table should be generated with at least:

| Year | Exclusion reason | Records excluded |
|---|---|---:|
| 2022 | PENDING | PENDING |
| 2023 | PENDING | PENDING |
| 2024 | PENDING | PENDING |
| 2025 | PENDING | PENDING |

No personal identifiers should appear in this log.

### 8. Aggregation and zero completion

After cleaning and standardization:

1. aggregate event counts by IBGE municipality code, year and standardized category;
2. create the complete Cartesian frame of 144 municipalities × 4 years × analytical categories;
3. join observed counts to the complete frame;
4. replace missing counts with zero only for years whose extraction completeness has been confirmed;
5. retain a completeness flag in the processed data.

### 9. Rate calculation

For municipality `i`, category `c` and year `t`:

```text
rate_i,c,t = events_i,c,t / female_population_2022_i × 100,000
```

The denominator remains fixed at the 2022 female population for all years. This supports comparability of recorded-event rates across 2022–2025 but does not account for subsequent population change.

### 10. Percentile transformation

Within each year and category, annual rates are converted to empirical state percentile ranks using average ranks for ties.

These percentiles are then combined into the visibility compositions documented in `docs/scenario_design.md`.

## Public-release outputs

Permitted public materials include:

- preprocessing code without embedded protected records;
- variable and category dictionaries;
- municipality crosswalks that contain no personal data;
- aggregate exclusion counts;
- completeness flags;
- municipal annual counts or rates only if release is institutionally permitted;
- final non-identifying municipal results;
- synthetic test data.

## Prohibited materials

Do not publish:

- row-level police records;
- personal identifiers;
- precise addresses or coordinates of incidents;
- free-text narratives;
- confidential operational fields;
- credentials or direct restricted-download links;
- any aggregate that violates an applicable disclosure-control requirement.

## Reproducibility limitation

At present, the repository documents the downstream analytical stages but does not contain a complete upstream preprocessing script and audit trail. Therefore, a clean reproduction from restricted raw police exports cannot yet be independently completed from the repository alone.
