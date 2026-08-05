# Oncology Clinical Registry Analytics

## 1. Project overview

This project reproduces, for educational and portfolio purposes,
a clinical oncology registry data-management pipeline.

It demonstrates:

- reproducible data preparation;
- technical data quality validation;
- SQL-based analytical indicators;
- descriptive and survival analyses;
- automated reporting;
- testing and traceability.

The project uses public data and is not intended for clinical
decision-making or individual patient prediction.

## 2. Public health and clinical context

Reliable oncology data are essential for monitoring clinical
activity, describing patient populations, supporting research and
improving the quality of care.

Clinical registry data may originate from several sources, including
electronic health records, multidisciplinary oncology meetings and
national cancer registries. Before these data can be analysed, they
must be structured, checked, documented and made traceable.

This portfolio project simulates part of that workflow using a public
breast-cancer dataset. It focuses on technical data management,
quality control, analytical reproducibility and the production of
aggregated indicators.

The project is educational. It is not an official hospital registry
and must not be used for individual clinical decision-making.

## 3. Professional objectives

The project aims to demonstrate the following professional
competencies:

- document the origin, version and permitted use of a public dataset;
- preserve the original source file without manual modification;
- profile the structure and initial quality of clinical data;
- standardize variable names and data types with Python;
- define reproducible data quality rules;
- identify missing, duplicated, invalid or inconsistent values;
- maintain traceability between raw, prepared and validated data;
- structure validated data in a relational SQLite database;
- produce oncology-related indicators with SQL;
- perform descriptive and survival analyses;
- create aggregated dashboards and reports;
- test the main transformation and validation rules automatically;
- document methodological, ethical and privacy limitations.

## 4. Data source

The project uses the public dataset titled **SEER Breast Cancer Data**.

| Metadata | Information |
|---|---|
| Kaggle identifier | `sujithmandala/seer-breast-cancer-data` |
| Kaggle version | Version 1 |
| Kaggle uploader | Sujith K Mandala |
| Original cited author | Jing Teng |
| Original institutional source | National Cancer Institute — SEER Program |
| SEER release mentioned | November 2017 |
| DOI | `10.21227/a9qy-ph35` |
| License displayed by Kaggle | CC BY 4.0 |
| File format | CSV |
| Number of variables reported | 16 |

The original row-level CSV is stored locally in `data/raw` and is not
distributed through this GitHub repository.

The repository contains the code, documentation, aggregated outputs
and reproducible processing instructions, but not a copy of the
original individual-level dataset.

Detailed provenance information is available in
[`docs/data_source_register.md`](docs/data_source_register.md).

## 5. Repository architecture

data/raw         Original local data, never modified
data/interim     Prepared and quality-control files
data/processed   Validated analytical data and SQLite database
docs             Data source, quality, methodology and ethics
notebooks        Profiling and clinical analyses
src              Reusable Python pipeline
sql              Database schema and analytical queries
app              Local Streamlit dashboard
tests            Automated tests
outputs          Figures and aggregated reports

## 6. Data pipeline

The project follows a layered data-management workflow:

1. **Source documentation**  
   The dataset, version, license and provenance limitations are
   documented before processing.

2. **Raw data layer**  
   The original CSV is stored locally in `data/raw` and is never
   modified manually.

3. **Data profiling**  
   The initial notebook examines dimensions, column names, data types,
   missing values, duplicates and categorical modalities.

4. **Preparation layer — planned**  
   Python will standardize column names, numeric formats and selected
   categorical values.

5. **Validation layer — planned**  
   Documented quality rules will identify technical anomalies without
   silently deleting records.

6. **Processed data layer — planned**  
   The validated dataset will include a technical quality status for
   each record.

7. **Relational and analytical layers — planned**  
   Validated data will be loaded into SQLite and used for SQL
   indicators, clinical analyses and reporting.

8. **Presentation layer — planned**  
   Aggregated results will be presented through Streamlit, Excel and
   documented figures.

## 7. Data quality controls

The project applies technical controls across five dimensions:

- **completeness** — required values and expected columns;
- **uniqueness** — duplicated records or identifiers;
- **validity** — accepted formats, categories and numeric ranges;
- **consistency** — compatibility between related variables;
- **traceability** — documentation of sources and transformations.

Examples of planned controls include:

- age must not be missing and must remain within a plausible range;
- tumour size and survival duration must not be negative;
- the number of positive regional nodes cannot exceed the number of
  examined nodes;
- vital status must be coded as `Alive` or `Dead`;
- `Alive` must correspond to `event = 0`;
- `Dead` must correspond to `event = 1`;
- accepted T-stage values must be documented;
- accepted N-stage values must be documented;
- hormone-receptor categories must be checked.

Missing clinical values are not automatically replaced during the
preparation stage. No observation is silently deleted solely because
it violates a technical quality rule.

Complete rules are documented in
[`docs/data_quality_rules.md`](docs/data_quality_rules.md).

## 8. Relational database and SQL indicators

**Status: planned**

The validated analytical dataset will be loaded into a local SQLite
database.

The planned relational model will separate the main analytical
domains into tables such as:

- `patients`;
- `tumors`;
- `outcomes`;
- `data_quality_issues`.

The tables will be connected through a technical `case_id`. This
identifier is created for the portfolio workflow and is not a real
medical or hospital patient identifier.

Planned SQL indicators include:

- total number of registered cases;
- distribution of cases by recorded stage;
- vital status by stage;
- average lymph-node ratio by N stage;
- number of records by quality status;
- number of quality issues by rule and severity.

The SQL schema and analytical queries will be stored in the `sql`
directory.

## 9. Clinical and survival analyses

**Status: implemented and quality-checked**

The clinical and survival analysis component uses the validated
processed dataset:

`data/processed/oncology_registry_validated.csv`

Records are explicitly filtered to retain only observations with:

`quality_status == "valid"`

The latest validated run included **4,022 patient records**, with:

- **616 observed deaths**;
- **3,406 right-censored observations**;
- **2 records excluded** because their quality status was not valid.

The descriptive analysis covers:

- age;
- tumour size;
- regional nodes examined;
- regional nodes positive;
- recorded cancer stage;
- tumour grade;
- hormone-receptor status;
- survival duration;
- vital status.

Survival outcomes are analysed using the Kaplan–Meier method.
The implemented analyses include:

- an overall Kaplan–Meier survival curve;
- Kaplan–Meier curves stratified by recorded stage;
- confidence intervals and explicit censoring markers;
- numbers-at-risk tables at selected follow-up times;
- a global log-rank test across recorded stages;
- pairwise log-rank comparisons with Holm adjustment for multiple testing.

A primary multivariable Cox proportional-hazards model was fitted
using:

- age;
- recorded overall stage;
- tumour grade.

The explicit reference categories are:

- `IIA` for `overall_stage`;
- `Moderately differentiated; Grade II` for `grade`.

Because the proportional-hazards assumption was not supported for
the oestrogen- and progesterone-receptor variables when they were
initially included as ordinary Cox covariates, a sensitivity model
was also fitted using the same primary covariates while stratifying
the baseline hazard by:

- `estrogen_status`;
- `progesterone_status`.

Both the primary and stratified Cox models converged without recorded
convergence warnings. Statistical tests and graphical Schoenfeld
residual diagnostics did not identify unresolved proportional-hazards
violations in the final models.

The stage-specific results showed progressively higher adjusted
hazards from stage IIB through stage IIIC relative to stage IIA.
However, estimates for relatively small groups, particularly stage
IIIB and Grade IV, are interpreted cautiously because of their wider
confidence intervals.

The project does not use `survival_months` as an ordinary predictor
of vital status, because this would introduce target leakage.

All findings are interpreted as descriptive or associational. They
are not presented as causal effects, individual medical predictions,
or clinical decision-support recommendations.

Generated survival-analysis outputs are stored in:
- `outputs/figures/survival`;
- `outputs/reports/survival`.

## 10. Streamlit dashboard

**Status: planned**

A local Streamlit dashboard will present aggregated and
decision-oriented indicators generated from the validated database.

The planned dashboard will include:

- total number of cases;
- average age;
- number of recorded deaths;
- distribution of cases by stage;
- vital status by stage;
- distribution of quality statuses;
- filters based on selected clinical categories.

The dashboard will not display the original raw dataset or direct
identifiers.

The application code is stored in:

```text
app/streamlit_app.py

## 11. Excel reporting

## Excel reporting

**Status: planned**

The project will generate an Excel workbook automatically with
Python.

The workbook will contain aggregated information only and may include
the following worksheets:

| Worksheet | Content |
|---|---|
| `Overview` | Main dataset and quality indicators |
| `Quality_By_Rule` | Number of issues by rule and severity |
| `Missing_Data` | Missing values by variable |
| `Stage_KPIs` | Number of cases by recorded stage |
| `Vital_Status` | Vital status by recorded stage |
| `Instructions` | Data source, limitations and usage notes |

The report will be generated from the validated data rather than
constructed manually in Excel.

This component is intended to demonstrate both Python automation and
the production of an output that can be used by non-technical
stakeholders.

## Automated tests

## Automated tests

**Status: planned**

Automated tests will verify that the main preparation and validation
rules continue to behave as expected after code modifications.

The tests will cover examples such as:

- conversion of column names to `snake_case`;
- detection of negative survival durations;
- detection of positive regional nodes exceeding examined nodes;
- consistency between vital status and event coding;
- acceptance of a technically valid sample record.

Tests will be written with `pytest` and stored in the `tests`
directory.

After local validation, GitHub Actions will execute the tests
automatically after each push to the `main` branch.

## Running the project

## Main results

## Methodological limitations

## Privacy and ethical considerations

## Author