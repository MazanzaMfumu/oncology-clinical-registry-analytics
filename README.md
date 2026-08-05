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

**Status: implemented**

The validated analytical dataset is loaded into a local SQLite
database.

The relational model separates the main analytical domains into four
tables:

- `patients`;
- `tumors`;
- `outcomes`;
- `data_quality_issues`.

The tables are connected through a technical `case_id`. This
identifier is created for the portfolio workflow and is not a real
medical or hospital patient identifier.

Implemented SQL indicators include:

- total number of registered cases;
- distribution of cases by recorded stage;
- vital status by stage;
- average lymph-node ratio by N stage;
- number of records by quality status;
- number of quality issues by rule and severity.

Project files:

- [`sql/schema.sql`](sql/schema.sql)
- [`sql/analysis_queries.sql`](sql/analysis_queries.sql)
- [`src/build_database.py`](src/build_database.py)
- [`src/check_database.py`](src/check_database.py)

The generated SQLite database is stored locally in
`data/processed/oncology_registry.sqlite` and is not distributed
through GitHub.

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

**Status: implemented locally**

A functional Streamlit dashboard is available in
`app/streamlit_app.py`.

In local mode, the application reads the validated SQLite database
generated by the project pipeline:

```text
data/processed/oncology_registry.sqlite
```

When the local database is unavailable, or when synthetic demonstration
mode is activated, the application uses fully synthetic data generated
by the project code.

The dashboard currently includes:

- total number of filtered cases;
- average age;
- number of recorded events;
- distribution of cases by stage;
- vital status by stage;
- distribution of quality statuses;
- estrogen receptor status;
- filters by stage and quality status.

The dashboard displays aggregated indicators and does not expose the
original raw dataset or direct identifiers.

To run the application locally from the project root:

```bash
streamlit run app/streamlit_app.py
```

The application is then available at:

```text
http://localhost:8501
```

The local version uses the SQLite database generated by the pipeline.
Any future public deployment must use only fully synthetic data or
appropriately aggregated and non-identifying information.

# Dashboard preview

![Dashboard overview](docs/screenshots/dashboard_full_page1.png)

![Dashboard quality and receptor indicators](docs/screenshots/dashboard_full_page2.png)

## 11. Automated reporting

**Status: implemented**

The project generates reproducible reporting outputs automatically with
Python. These outputs include a formatted multi-worksheet Excel workbook,
supporting CSV files and text-based analytical diagnostics.

### Excel workbook

The project generates an aggregated Excel workbook from the validated
dataset and the data-quality issue log.

The workbook is available at:

`outputs/reports/oncology_registry_report.xlsx`

It currently contains the following worksheets:

| Worksheet | Content |
|---|---|
| `Instructions` | Data sources, generation details, definitions, confidentiality notes and interpretation limits |
| `Overview` | Main registry, event and quality indicators |
| `Data_Quality_Summary` | Number and percentage of cases by quality status |
| `Quality_By_Rule` | Aggregated issues by validation rule and severity |
| `Missing_Data` | Number and percentage of missing values by variable |
| `Stage_KPIs` | Aggregated case, event and follow-up indicators by recorded stage |
| `Vital_Status` | Vital-status distribution by recorded stage |
| `Survival_Summary` | Aggregated follow-up, death and censoring indicators |

The Excel report can be regenerated from the project root with:

```bash
python src/generate_excel_report.py
```

The workbook is generated programmatically and is not constructed
manually in Excel.

### Supporting CSV and text outputs

The project also generates machine-readable CSV files and text-based
diagnostics during data preparation, validation and survival analysis.

The main output locations are:

```text
data/interim/
data/processed/
outputs/reports/survival/
```

These supporting outputs include:

- the prepared dataset;
- the data-quality issue log;
- the validated dataset;
- case-identifier validation results;
- survival-analysis sample-flow summaries;
- at-risk counts at selected follow-up times;
- Cox model summaries and performance metrics;
- missing-data diagnostics;
- proportional-hazards diagnostics;
- model warnings and readiness checks.

The CSV and text outputs support traceability, reproducibility and
technical review, while the Excel workbook provides a consolidated
stakeholder-facing report.

### Confidentiality and intended use

The stakeholder-facing Excel workbook contains aggregated information
only. It does not expose the original raw dataset, individual case
records or direct identifiers.

The reporting component is intended to demonstrate:

- Python-based reporting automation;
- data-quality monitoring;
- reproducible production of analytical outputs;
- traceability between validated data and final deliverables;
- communication of results to technical and non-technical stakeholders.

## 12. Automated tests

**Status: implemented and passing locally and on GitHub Actions**

Automated tests verify that the main data-preparation and validation
rules continue to behave as expected after code modifications.

The current test suite covers:

- conversion of column names to `snake_case`;
- acceptance of a technically valid sample record;
- detection of negative survival durations;
- detection of positive regional nodes exceeding examined nodes;
- consistency between vital status and event coding.

Tests are written with `pytest` and stored in:

```text
tests/test_data_quality.py
```
## 13. Running the project


## 14. Main results

## 15. Methodological limitations

## 16. Privacy and ethical considerations

## 17. Author