# Data Dictionary

## 1. Purpose

This data dictionary documents the variables used by the oncology
clinical registry analytics pipeline.

It distinguishes between:

* source variables obtained from the public dataset;
* variables renamed during preparation;
* variables derived by the project code;
* technical metadata used for traceability;
* quality-control variables created during validation.

The original source file contains 16 physical columns. One unnamed
column is entirely empty and is removed with traceability. The pipeline
therefore retains 15 usable source variables.

The variable `differentiation` is not included because it is not present
as an independent usable field in the source CSV processed by this
project. No replacement clinical variable is invented.

## 2. General conventions

| Convention                 | Description                                                                               |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| Variable naming            | Prepared variables use lowercase `snake_case` names                                       |
| Missing numerical values   | Invalid numerical conversions are stored as missing values                                |
| Missing categorical values | Empty strings are converted to missing values                                             |
| Imputation                 | Missing clinical values are not automatically imputed                                     |
| Record deletion            | Records are not silently deleted because of a quality issue                               |
| Quality review             | Records affected by at least one detected issue receive `quality_status = "needs_review"` |
| Technical identifiers      | Project-generated identifiers are not hospital or medical-record identifiers              |

## 3. Source and prepared variables

| Prepared variable         | Source variable                                       | Description                                                | Type    | Unit or format                                            | Expected values or domain                                                           | Missing-value and validation rules                                                            |
| ------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- | ------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `age`                     | `Age`                                                 | Age recorded for the case                                  | Numeric | Years                                                     | Expected range: 0–120                                                               | Required. Missing or out-of-range values generate an error                                    |
| `race`                    | `Race`                                                | Race category recorded in the source dataset               | String  | Categorical                                               | Source-defined categories                                                           | Empty strings are converted to missing values. No category is inferred                        |
| `marital_status`          | `Marital Status`                                      | Marital-status category recorded in the source dataset     | String  | Categorical                                               | Source-defined categories                                                           | Empty strings are converted to missing values                                                 |
| `t_stage`                 | `T Stage`                                             | Recorded tumour T category                                 | String  | TNM category                                              | `T1`, `T2`, `T3`, `T4`                                                              | Required. Values outside the accepted domain generate a warning                               |
| `n_stage`                 | `N Stage`                                             | Recorded regional lymph-node N category                    | String  | TNM category                                              | `N1`, `N2`, `N3`                                                                    | Required. Values outside the accepted domain generate a warning                               |
| `overall_stage`           | `6th Stage`                                           | Recorded overall cancer-stage category                     | String  | Categorical stage                                         | Source-defined categories                                                           | Required. Renamed from `6th_stage` during preparation                                         |
| `grade`                   | `Grade`                                               | Histological grade category recorded in the source dataset | String  | Categorical                                               | Source-defined categories                                                           | Empty strings are converted to missing values. This field is not renamed as `differentiation` |
| `a_stage`                 | `A Stage`                                             | Additional stage category supplied by the source dataset   | String  | Categorical                                               | Source-defined categories                                                           | Retained without clinical reinterpretation                                                    |
| `tumor_size`              | `Tumor Size`                                          | Recorded tumour-size measurement                           | Numeric | Source unit not independently verified in this repository | Must be greater than or equal to zero when present                                  | Negative values generate an error. Invalid numerical values become missing                    |
| `estrogen_status`         | `Estrogen Status`                                     | Recorded oestrogen-receptor status                         | String  | Categorical                                               | `Positive`, `Negative`                                                              | Values outside the accepted domain generate a warning                                         |
| `progesterone_status`     | `Progesterone Status`                                 | Recorded progesterone-receptor status                      | String  | Categorical                                               | `Positive`, `Negative`                                                              | Values outside the accepted domain generate a warning                                         |
| `regional_nodes_examined` | `Regional Node Examined`                              | Number of regional lymph nodes examined                    | Numeric | Count                                                     | Must be greater than or equal to zero when present                                  | Negative values generate an error                                                             |
| `regional_nodes_positive` | `Reginol Node Positive` or equivalent source spelling | Number of regional lymph nodes recorded as positive        | Numeric | Count                                                     | Must be greater than or equal to zero and must not exceed `regional_nodes_examined` | Negative values or values exceeding examined nodes generate an error                          |
| `survival_months`         | `Survival Months`                                     | Recorded follow-up or survival duration                    | Numeric | Months                                                    | Must be greater than or equal to zero                                               | Required. Negative values generate an error                                                   |
| `vital_status`            | `Status`                                              | Recorded vital status at the end of follow-up              | String  | Categorical                                               | `Alive`, `Dead`                                                                     | Required. Other values generate a warning                                                     |

## 4. Derived and technical variables

| Variable                   | Description                                                 | Type    | Values or calculation                               | Validation or usage                                                                                                                         |
| -------------------------- | ----------------------------------------------------------- | ------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `case_id`                  | Sequential technical identifier generated by the project    | String  | `CASE_00001`, `CASE_00002`, etc.                    | Used to connect prepared data, validation issues and relational database tables. It is not a hospital identifier                            |
| `event`                    | Event indicator used for survival analysis                  | Integer | `Alive = 0`; `Dead = 1`                             | Must remain consistent with `vital_status`                                                                                                  |
| `lymph_node_ratio`         | Ratio of positive regional nodes to examined regional nodes | Numeric | `regional_nodes_positive / regional_nodes_examined` | Calculated only when the number of examined nodes is greater than zero                                                                      |
| `source_file`              | Name of the source CSV used during processing               | String  | Source filename                                     | Added for traceability                                                                                                                      |
| `processing_timestamp_utc` | Date and time at which the preparation script was executed  | String  | ISO 8601 UTC timestamp                              | Added for execution traceability                                                                                                            |
| `quality_status`           | Technical quality classification assigned after validation  | String  | `valid`, `needs_review`                             | `needs_review` means that at least one technical rule requires review; it does not automatically mean that the clinical record is incorrect |

## 5. Quality-issue log

Detected anomalies are stored separately in:

```text
data/interim/data_quality_issues.csv
```

The issue log contains the following fields:

| Variable   | Description                                       |
| ---------- | ------------------------------------------------- |
| `case_id`  | Technical identifier of the affected record       |
| `rule_id`  | Identifier of the quality rule that was triggered |
| `field`    | Variable affected by the issue                    |
| `severity` | Technical severity: `error` or `warning`          |
| `message`  | Human-readable description of the detected issue  |

## 6. Implemented validation rules

The validation pipeline currently checks:

* presence of the required variables;
* missing values in required fields;
* exact duplicate records;
* age outside the range 0–120;
* negative tumour size;
* negative numbers of examined or positive lymph nodes;
* positive lymph nodes exceeding examined lymph nodes;
* negative survival duration;
* unexpected T-stage values;
* unexpected N-stage values;
* unexpected receptor-status values;
* unexpected vital-status values;
* inconsistency between `vital_status` and `event`.

The complete rule specifications are available in:

[`data_quality_rules.md`](data_quality_rules.md)

## 7. Source limitations

The variable definitions in this document describe how the fields are
processed and used by this portfolio project..

They do not replace an official SEER data dictionary or an institutional
oncology-registry specification.

The exact clinical interpretation, coding version and units of fields
whose metadata remain incomplete must be confirmed against authoritative
source documentation before any institutional, research or clinical use.

The dataset provenance and known documentation discrepancies are
described in:

[`data_source_register.md`](data_source_register.md)


