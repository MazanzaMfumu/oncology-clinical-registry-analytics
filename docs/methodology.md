# Methodology

## Data source

The project uses the public SEER Breast Cancer Data dataset documented
in `data_source_register.md`. The original row-level CSV is processed
locally and is not distributed through this repository.

## Data preparation

The preparation script standardizes variable names, converts numerical
fields, removes an entirely empty unnamed column, creates a technical
case identifier, derives the survival-event indicator and calculates
the lymph-node ratio.

## Data quality validation

Documented rules assess completeness, uniqueness, validity, consistency
and traceability. Detected anomalies are recorded in a separate issue
log. Source records are not silently deleted.

## Relational database

Validated data are loaded into a local SQLite database containing the
`patients`, `tumors`, `outcomes` and `data_quality_issues` tables.

## Analysis

The project produces descriptive indicators, Kaplan-Meier estimates,
log-rank comparisons and Cox proportional-hazards model outputs.

Only records classified as technically valid are included in the main
survival analysis.

## Reporting

Aggregated outputs are produced through SQL, Excel, figures and a
Streamlit dashboard.

## Limitations

This is an educational portfolio project based on a public dataset.
It does not reproduce an official hospital registry, medical validation,
ICD coding process, HD4DP transmission or Cancer Registry submission.