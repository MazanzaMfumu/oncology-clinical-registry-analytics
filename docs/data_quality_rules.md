# Data Quality Rules

## 1. Purpose

This document defines the technical data quality rules applied
to the public SEER breast cancer dataset used in this project.

These rules support data preparation and analytical reliability.
They do not constitute a medical validation of the records.

## 2. Quality dimensions

The controls cover:

- completeness;
- uniqueness;
- validity;
- consistency;
- traceability.

## 3. Rules

| Rule ID | Field | Rule | Severity |
|---|---|---|---|
| DQ-001 | Dataset | All expected columns must be present | Error |
| DQ-002 | Rows | Exact duplicate records must be identified | Warning |
| DQ-003 | age | Age must not be missing | Error |
| DQ-004 | age | Age must be between 0 and 120 | Error |
| DQ-005 | tumor_size | Tumor size must not be negative | Error |
| DQ-006 | regional_nodes_examined | Number examined must not be negative | Error |
| DQ-007 | regional_nodes_positive | Number positive must not be negative | Error |
| DQ-008 | Nodes | Positive nodes cannot exceed examined nodes | Error |
| DQ-009 | survival_months | Survival duration must not be negative | Error |
| DQ-010 | vital_status | Status must be Alive or Dead | Error |
| DQ-011 | event | Alive must correspond to 0 and Dead to 1 | Error |
| DQ-012 | t_stage | Accepted values are T1, T2, T3 and T4 | Warning |
| DQ-013 | n_stage | Accepted values are N1, N2 and N3 | Warning |
| DQ-014 | estrogen_status | Accepted values are Positive and Negative | Warning |
| DQ-015 | progesterone_status | Accepted values are Positive and Negative | Warning |

## 4. Missing data policy

Missing clinical values will not be automatically replaced during
the preparation stage.

A missing value may represent:

- information not collected;
- examination not performed;
- information unavailable;
- extraction error;
- loss to follow-up.

Imputation, if required for a specific statistical analysis, must
be documented separately and must not overwrite the source data.

## 5. Handling of anomalies

The validation pipeline will:

1. preserve the original row;
2. identify the affected case;
3. record the violated rule;
4. assign a severity;
5. classify the row as valid or requiring review.

No row will be silently deleted.

## 6. Clinical limitation

The project verifies technical formats and internal consistency.
It does not reproduce an official medical validation of TNM
classification, cancer staging or hospital registry submission.

## 7. Potential duplicate records

Two records, CASE_01010 and CASE_01011, contain identical values
across all available source variables.

Because the public dataset does not contain a stable original
patient identifier, these records cannot be conclusively classified
as duplicate patients.

They are therefore treated as potential duplicates:

- the original records are preserved;
- both records remain flagged with a warning;
- no raw record is manually modified or deleted;
- a sensitivity analysis will later retain only one of the two identical profiles.