# CODEC/SEGUP-PA data source

## Official source

The police-record exports used in the study were obtained from the **Consulta de Dados Estatísticos Criminais (CODEC)**, the official criminal-statistics consultation system of the Secretaria de Estado de Segurança Pública e Defesa Social do Pará (SEGUP-PA).

- Portal: `https://codec.segup.pa.gov.br/`
- Download date: **2 February 2026**
- Coverage used in the study: **2022–2025**
- Data from 2026 were not used because the corresponding reports were not consolidated at the time of download.

## Annual filters

A separate complete-calendar-year export was produced for each analytical year:

- 1 January 2022 through 31 December 2022;
- 1 January 2023 through 31 December 2023;
- 1 January 2024 through 31 December 2024;
- 1 January 2025 through 31 December 2025.

All four annual files were confirmed as complete exports for their respective periods. Consequently, after category and municipality standardization, absent municipality-year-category combinations were represented as zero in the complete analytical grid.

## Fields included in the exports

The downloaded files contained the following fields:

1. `CONSOLIDADO(S)`;
2. `ESPECIFICAÇÃO CRIME`;
3. `MEIO EMPREGADO DEAC`;
4. `MUNICÍPIO(S)`;
5. `BAIRRO(S)`;
6. `ANO DO FATO`;
7. `MÊS DO FATO`;
8. `RISP`;
9. `AISP`;
10. `DATA DO FATO`;
11. `DIA DA SEMANA`;
12. `HORA DO FATO`;
13. `FAIXA 4 HORAS`;
14. `FAIXA 12 HORAS`;
15. `LATITUDE`;
16. `LONGITUDE`;
17. `DISTRITO`;
18. `REGIÃO DE INTEGRAÇÃO`;
19. `LOCAL DA OCORRÊNCIA`;
20. `SEXO VÍTIMA`;
21. `IDADE VÍTIMA`;
22. `FAIXA ETÁRIA VÍTIMA`;
23. `TIPO DE VÍTIMA`;
24. `COR VÍTIMA`;
25. `GRAU DE INSTRUÇÃO VÍTIMA`;
26. `ESTADO CIVÍL VÍTIMA`;
27. `SEXO AUTOR`;
28. `IDADE AUTOR`;
29. `COR AUTOR`;
30. `GRAU DE RELACIONAMENTO`.

The analytical pipeline uses only the fields required for category definition, municipality standardization, year attribution, victim-sex filtering and aggregation. Coordinates and person-level descriptive fields are not included in public derived outputs.

## Analytical categories

The principal panel contains:

- feminicide;
- domestic-violence bodily injury involving female victims;
- rape involving female victims;
- rape of a vulnerable person involving female victims.

The exact recoding rules are implemented in `src/process_codec_microdata_v14.py`.

## Municipality standardization

Municipal names are matched to the 144-municipality IBGE reference frame. Documented exceptions include:

- `ALTAMIRA/CASTELO DOS SONHOS` aggregated to Altamira;
- `ELDORADO DOS CARAJAS` mapped to Eldorado do Carajás;
- `PAU D ARCO` mapped to Pau D'Arco;
- accent and spelling normalization for other official names.

## Public-release policy

The original annual XLSX exports are not stored in the repository. The repository provides:

- processing code;
- category and municipality rules;
- non-identifying municipal aggregates;
- rates and analytical outputs.

This avoids redistributing large source files and permits users to obtain a current copy from the official portal when it is available.
