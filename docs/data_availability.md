# Data availability and restricted-data statement

The study combines public institutional, demographic and geographic sources with police-record exports supplied for research purposes.

## Public sources

The following sources are public, subject to their original terms and attribution requirements:

- MUNIC 2023 institutional information;
- 2022 Census female population;
- IBGE municipal geographic reference data.

The exact source editions, download dates and file identifiers should be recorded in the final provenance table.

## Police records

The 2022–2025 police microdata used in the study are not redistributed in this repository. Access may be subject to institutional authorization and conditions established by the Public Security Secretariat of Pará, including SEGUP/CODEC.

The repository must not be interpreted as granting permission to access, use or redistribute those records.

## Materials made available

The intended public reproducibility package includes:

- final source code;
- parameter and configuration files;
- methodological documentation;
- variable and category dictionaries;
- non-identifying aggregate audit summaries;
- aggregated municipal results approved for release;
- optional synthetic data for software tests;
- instructions for authorized reconstruction of the analysis.

## Materials not made available

The package excludes:

- raw or row-level police records;
- personal identifiers;
- addresses, exact incident coordinates and free-text narratives;
- confidential operational variables;
- restricted credentials and source links;
- any intermediate file that could expose protected information.

## Reproducibility boundary

The public repository currently documents and executes the final analytical stages when the required processed municipal files are available locally. It does not yet permit a complete independent reconstruction from raw police exports because the full upstream preprocessing code, original schemas, extraction date and audit trail remain to be consolidated.

## Analytical cautions

- absence may be transformed into zero only after confirming that the annual extraction is complete;
- the 2022 female population is used as a fixed denominator for rates from 2022 through 2025;
- aggregated results do not validate the completeness of the original police-record system;
- the model identifies municipalities for investigation and does not estimate hidden incidence.

## Contact and access requests

Researchers seeking access to restricted source records should contact the original data provider and follow the applicable institutional and ethical procedures. The article authors cannot redistribute data when authorization does not permit it.
