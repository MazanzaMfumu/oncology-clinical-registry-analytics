"""Generate an aggregated Excel report for the oncology registry project."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

VALIDATED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry_validated.csv"
)

QUALITY_ISSUES_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "data_quality_issues.csv"
)

DEFAULT_OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "oncology_registry_report.xlsx"
)


# ============================================================
# 2. EXPECTED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "case_id",
    "age",
    "quality_status",
    "overall_stage",
    "survival_months",
    "vital_status",
    "event",
}

STAGE_ORDER = [
    "IIA",
    "IIB",
    "IIIA",
    "IIIB",
    "IIIC",
]


# ============================================================
# 3. VALIDATION UTILITIES
# ============================================================

def require_file(path: Path) -> None:
    """Stop with a clear message when an input file is absent."""

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )


def require_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
) -> None:
    """Verify that all required columns are available."""

    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "Required columns are missing from the validated dataset: "
            f"{sorted(missing_columns)}\n"
            "Available columns: "
            f"{sorted(dataframe.columns.tolist())}"
        )


def first_existing_column(
    columns: pd.Index,
    candidates: list[str],
) -> str | None:
    """Return the first candidate column that exists."""

    for candidate in candidates:
        if candidate in columns:
            return candidate

    return None


# ============================================================
# 4. QUALITY REPORT
# ============================================================

def build_quality_by_rule(
    issues: pd.DataFrame,
    total_cases: int,
) -> pd.DataFrame:
    """Aggregate quality issues without exporting individual records."""

    if issues.empty:
        return pd.DataFrame(
            [
                {
                    "rule": "No quality issue recorded",
                    "severity": "not_applicable",
                    "issue_count": 0,
                    "impacted_records": 0,
                    "percent_of_cases": 0.0,
                }
            ]
        )

    rule_column = first_existing_column(
        issues.columns,
        [
            "rule",
            "rule_id",
            "rule_name",
            "validation_rule",
            "check",
            "check_name",
            "issue_type",
            "issue",
        ],
    )

    severity_column = first_existing_column(
        issues.columns,
        [
            "severity",
            "issue_severity",
            "level",
        ],
    )

    case_column = first_existing_column(
        issues.columns,
        [
            "case_id",
            "record_id",
            "row_id",
            "row_number",
        ],
    )

    if rule_column is None:
        raise ValueError(
            "No recognised quality-rule column was found in "
            f"{QUALITY_ISSUES_FILE.name}.\n"
            "Available columns: "
            f"{issues.columns.tolist()}"
        )

    grouping_columns = [rule_column]

    if severity_column is not None:
        grouping_columns.append(severity_column)

    if case_column is not None:
        summary = (
            issues
            .groupby(
                grouping_columns,
                dropna=False,
            )
            .agg(
                issue_count=(rule_column, "size"),
                impacted_records=(case_column, "nunique"),
            )
            .reset_index()
        )
    else:
        summary = (
            issues
            .groupby(
                grouping_columns,
                dropna=False,
            )
            .size()
            .reset_index(name="issue_count")
        )

        summary["impacted_records"] = summary["issue_count"]

    summary = summary.rename(
        columns={
            rule_column: "rule",
            severity_column: "severity",
        }
        if severity_column is not None
        else {
            rule_column: "rule",
        }
    )

    if "severity" not in summary.columns:
        summary.insert(
            1,
            "severity",
            "not_provided",
        )

    summary["percent_of_cases"] = (
        summary["impacted_records"]
        .div(total_cases)
        .mul(100)
        .round(2)
        if total_cases > 0
        else 0.0
    )

    return summary.sort_values(
        by=[
            "issue_count",
            "rule",
        ],
        ascending=[
            False,
            True,
        ],
    )


# ============================================================
# 5. REPORT GENERATION
# ============================================================

def generate_excel_report(
    output_file: Path | None = None,
) -> Path:
    """Generate the aggregated multi-worksheet Excel report."""

    require_file(VALIDATED_FILE)

    output_path = (
        Path(output_file)
        if output_file is not None
        else DEFAULT_OUTPUT_FILE
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = pd.read_csv(
        VALIDATED_FILE
    )

    require_columns(
        data,
        REQUIRED_COLUMNS,
    )

    if QUALITY_ISSUES_FILE.exists():
        quality_issues = pd.read_csv(
            QUALITY_ISSUES_FILE
        )
    else:
        quality_issues = pd.DataFrame()

    # Numeric conversion without silently replacing missing events.
    data["age"] = pd.to_numeric(
        data["age"],
        errors="coerce",
    )

    data["survival_months"] = pd.to_numeric(
        data["survival_months"],
        errors="coerce",
    )

    data["event"] = pd.to_numeric(
        data["event"],
        errors="coerce",
    )

    invalid_events = (
        data["event"]
        .dropna()
        .loc[
            ~data["event"]
            .dropna()
            .isin([0, 1])
        ]
        .unique()
        .tolist()
    )

    if invalid_events:
        raise ValueError(
            "The event column contains values other than 0 and 1: "
            f"{invalid_events}"
        )

    total_cases = len(data)

    quality_normalized = (
        data["quality_status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    valid_cases = int(
        quality_normalized.eq("valid").sum()
    )

    needs_review_cases = int(
        quality_normalized.eq("needs_review").sum()
    )

    deaths_observed = int(
        data["event"].eq(1).sum()
    )

    censored_records = int(
        data["event"].eq(0).sum()
    )

    missing_event_status = int(
        data["event"].isna().sum()
    )

    generated_at = datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )

    # --------------------------------------------------------
    # Instructions
    # --------------------------------------------------------

    instructions = pd.DataFrame(
        [
            {
                "Field": "Report purpose",
                "Value": (
                    "Aggregated quality and activity report for the "
                    "oncology clinical registry demonstration project."
                ),
            },
            {
                "Field": "Generated at",
                "Value": generated_at,
            },
            {
                "Field": "Source file",
                "Value": (
                    "data/processed/"
                    "oncology_registry_validated.csv"
                ),
            },
            {
                "Field": "Quality issues source",
                "Value": (
                    "data/interim/"
                    "data_quality_issues.csv"
                ),
            },
            {
                "Field": "Generation script",
                "Value": "src/generate_excel_report.py",
            },
            {
                "Field": "Refresh command",
                "Value": (
                    "python src/generate_excel_report.py"
                ),
            },
            {
                "Field": "Event definition",
                "Value": (
                    "event = 1: death observed; "
                    "event = 0: right-censored observation."
                ),
            },
            {
                "Field": "Confidentiality",
                "Value": (
                    "The workbook contains aggregated information "
                    "and does not export individual case records."
                ),
            },
            {
                "Field": "Interpretation limit",
                "Value": (
                    "This technical prototype does not provide "
                    "individual diagnosis, prognosis or medical advice."
                ),
            },
        ]
    )

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    overview = pd.DataFrame(
        [
            {
                "Indicator": "Total cases",
                "Value": total_cases,
            },
            {
                "Indicator": "Average age",
                "Value": round(
                    data["age"].mean(),
                    1,
                ),
            },
            {
                "Indicator": "Valid quality status",
                "Value": valid_cases,
            },
            {
                "Indicator": "Needs review",
                "Value": needs_review_cases,
            },
            {
                "Indicator": "Deaths observed",
                "Value": deaths_observed,
            },
            {
                "Indicator": "Right-censored records",
                "Value": censored_records,
            },
            {
                "Indicator": "Missing event status",
                "Value": missing_event_status,
            },
            {
                "Indicator": "Quality issues logged",
                "Value": len(quality_issues),
            },
        ]
    )

    # --------------------------------------------------------
    # Data quality summary
    # --------------------------------------------------------

    data_quality_summary = (
        data["quality_status"]
        .fillna("<missing>")
        .astype(str)
        .value_counts(dropna=False)
        .rename_axis("quality_status")
        .reset_index(name="case_count")
    )

    data_quality_summary["percent_of_cases"] = (
        data_quality_summary["case_count"]
        .div(total_cases)
        .mul(100)
        .round(2)
    )

    quality_by_rule = build_quality_by_rule(
        issues=quality_issues,
        total_cases=total_cases,
    )

    # --------------------------------------------------------
    # Missing-data summary
    # --------------------------------------------------------

    missing_data = pd.DataFrame(
        {
            "variable": data.columns,
            "missing_count": data.isna().sum().values,
        }
    )

    missing_data["missing_percent"] = (
        missing_data["missing_count"]
        .div(total_cases)
        .mul(100)
        .round(2)
    )

    missing_data = missing_data.sort_values(
        by=[
            "missing_count",
            "variable",
        ],
        ascending=[
            False,
            True,
        ],
    )

    # --------------------------------------------------------
    # Stage indicators
    # --------------------------------------------------------

    stage_data = data.copy()

    stage_data["stage_label"] = (
        stage_data["overall_stage"]
        .fillna("<missing>")
        .astype(str)
    )

    stage_kpis = (
        stage_data
        .groupby(
            "stage_label",
            dropna=False,
        )
        .agg(
            case_count=("case_id", "size"),
            average_age=("age", "mean"),
            event_documented=("event", "count"),
            deaths_observed=(
                "event",
                lambda values: int(
                    values.eq(1).sum()
                ),
            ),
            median_follow_up_months=(
                "survival_months",
                "median",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "stage_label": "overall_stage",
            }
        )
    )

    stage_kpis["percent_of_cases"] = (
        stage_kpis["case_count"]
        .div(total_cases)
        .mul(100)
        .round(2)
    )

    stage_kpis["death_rate_percent"] = (
        stage_kpis["deaths_observed"]
        .div(
            stage_kpis["event_documented"]
            .replace(0, pd.NA)
        )
        .mul(100)
        .round(2)
    )

    stage_kpis["average_age"] = (
        stage_kpis["average_age"]
        .round(1)
    )

    stage_kpis["median_follow_up_months"] = (
        stage_kpis["median_follow_up_months"]
        .round(1)
    )

    stage_sort_order = {
        stage: position
        for position, stage in enumerate(
            STAGE_ORDER
        )
    }

    stage_kpis["_sort_order"] = (
        stage_kpis["overall_stage"]
        .map(stage_sort_order)
        .fillna(len(STAGE_ORDER))
    )

    stage_kpis = (
        stage_kpis
        .sort_values(
            by=[
                "_sort_order",
                "overall_stage",
            ]
        )
        .drop(columns="_sort_order")
    )

    # --------------------------------------------------------
    # Vital status by stage
    # --------------------------------------------------------

    vital_status = (
        stage_data
        .assign(
            vital_status_label=(
                stage_data["vital_status"]
                .fillna("<missing>")
                .astype(str)
            )
        )
        .groupby(
            [
                "stage_label",
                "vital_status_label",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="case_count")
        .rename(
            columns={
                "stage_label": "overall_stage",
                "vital_status_label": "vital_status",
            }
        )
    )

    vital_status["stage_total"] = (
        vital_status
        .groupby("overall_stage")["case_count"]
        .transform("sum")
    )

    vital_status["percent_within_stage"] = (
        vital_status["case_count"]
        .div(vital_status["stage_total"])
        .mul(100)
        .round(2)
    )

    # --------------------------------------------------------
    # Survival summary
    # --------------------------------------------------------

    survival_eligible = data.dropna(
        subset=[
            "survival_months",
            "event",
        ]
    )

    survival_summary = pd.DataFrame(
        [
            {
                "Indicator": "Records with survival information",
                "Value": len(survival_eligible),
            },
            {
                "Indicator": "Deaths observed",
                "Value": int(
                    survival_eligible["event"]
                    .eq(1)
                    .sum()
                ),
            },
            {
                "Indicator": "Right-censored observations",
                "Value": int(
                    survival_eligible["event"]
                    .eq(0)
                    .sum()
                ),
            },
            {
                "Indicator": "Median observed follow-up in months",
                "Value": round(
                    survival_eligible[
                        "survival_months"
                    ].median(),
                    1,
                ),
            },
            {
                "Indicator": "Maximum observed follow-up in months",
                "Value": round(
                    survival_eligible[
                        "survival_months"
                    ].max(),
                    1,
                ),
            },
        ]
    )

    # --------------------------------------------------------
    # Excel writing
    # --------------------------------------------------------

    worksheets = {
        "Instructions": instructions,
        "Overview": overview,
        "Data_Quality_Summary": data_quality_summary,
        "Quality_By_Rule": quality_by_rule,
        "Missing_Data": missing_data,
        "Stage_KPIs": stage_kpis,
        "Vital_Status": vital_status,
        "Survival_Summary": survival_summary,
    }

    with pd.ExcelWriter(
        output_path,
        engine="xlsxwriter",
    ) as writer:

        workbook = writer.book

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 16,
            }
        )

        subtitle_format = workbook.add_format(
            {
                "italic": True,
                "text_wrap": True,
            }
        )

        wrap_format = workbook.add_format(
            {
                "text_wrap": True,
                "valign": "top",
            }
        )

        decimal_format = workbook.add_format(
            {
                "num_format": "0.00",
            }
        )

        for sheet_name, dataframe in worksheets.items():

            dataframe.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                startrow=3,
            )

            worksheet = writer.sheets[
                sheet_name
            ]

            worksheet.write(
                0,
                0,
                sheet_name.replace("_", " "),
                title_format,
            )

            worksheet.write(
                1,
                0,
                (
                    "Automatically generated from the "
                    "validated project data."
                ),
                subtitle_format,
            )

            row_count, column_count = (
                dataframe.shape
            )

            if row_count > 0 and column_count > 0:
                worksheet.add_table(
                    3,
                    0,
                    3 + row_count,
                    column_count - 1,
                    {
                        "columns": [
                            {
                                "header": str(column)
                            }
                            for column in dataframe.columns
                        ],
                        "style": "Table Style Medium 2",
                    },
                )

            worksheet.freeze_panes(
                4,
                0,
            )

            for column_number, column_name in enumerate(
                dataframe.columns
            ):
                if dataframe.empty:
                    content_width = 0
                else:
                    content_width = (
                        dataframe[column_name]
                        .astype(str)
                        .map(len)
                        .max()
                    )

                width = min(
                    max(
                        len(str(column_name)),
                        int(content_width),
                    )
                    + 2,
                    45,
                )

                if (
                    "percent" in column_name.lower()
                    or "rate" in column_name.lower()
                ):
                    worksheet.set_column(
                        column_number,
                        column_number,
                        width,
                        decimal_format,
                    )
                else:
                    worksheet.set_column(
                        column_number,
                        column_number,
                        width,
                    )

        instructions_sheet = writer.sheets[
            "Instructions"
        ]

        instructions_sheet.set_column(
            0,
            0,
            24,
        )

        instructions_sheet.set_column(
            1,
            1,
            75,
            wrap_format,
        )

        # Missing-data conditional formatting.
        if not missing_data.empty:
            missing_sheet = writer.sheets[
                "Missing_Data"
            ]

            missing_sheet.conditional_format(
                4,
                2,
                3 + len(missing_data),
                2,
                {
                    "type": "3_color_scale",
                },
            )

        # Cases by stage chart.
        if not stage_kpis.empty:
            stage_chart = workbook.add_chart(
                {
                    "type": "column",
                }
            )

            stage_chart.add_series(
                {
                    "name": "Number of cases",
                    "categories": [
                        "Stage_KPIs",
                        4,
                        0,
                        3 + len(stage_kpis),
                        0,
                    ],
                    "values": [
                        "Stage_KPIs",
                        4,
                        1,
                        3 + len(stage_kpis),
                        1,
                    ],
                }
            )

            stage_chart.set_title(
                {
                    "name": "Cases by recorded stage",
                }
            )

            stage_chart.set_x_axis(
                {
                    "name": "Stage",
                }
            )

            stage_chart.set_y_axis(
                {
                    "name": "Number of cases",
                    "major_gridlines": {
                        "visible": False,
                    },
                }
            )

            writer.sheets[
                "Stage_KPIs"
            ].insert_chart(
                "J4",
                stage_chart,
            )

        # Quality-status chart.
        if not data_quality_summary.empty:
            quality_chart = workbook.add_chart(
                {
                    "type": "column",
                }
            )

            quality_chart.add_series(
                {
                    "name": "Cases",
                    "categories": [
                        "Data_Quality_Summary",
                        4,
                        0,
                        3 + len(
                            data_quality_summary
                        ),
                        0,
                    ],
                    "values": [
                        "Data_Quality_Summary",
                        4,
                        1,
                        3 + len(
                            data_quality_summary
                        ),
                        1,
                    ],
                }
            )

            quality_chart.set_title(
                {
                    "name": "Cases by quality status",
                }
            )

            writer.sheets[
                "Data_Quality_Summary"
            ].insert_chart(
                "E4",
                quality_chart,
            )

    print(
        "Excel report generated successfully:"
    )

    print(
        output_path
    )

    return output_path


# ============================================================
# 6. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate_excel_report()