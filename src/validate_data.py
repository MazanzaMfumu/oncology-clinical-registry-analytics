"""Validation de la qualité des données oncologiques."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "oncology_registry_prepared.csv"
)

ISSUES_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "data_quality_issues.csv"
)

PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry_validated.csv"
)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "data_quality_summary.md"
)


REQUIRED_COLUMNS = {
    "case_id",
    "age",
    "t_stage",
    "n_stage",
    "overall_stage",
    "tumor_size",
    "estrogen_status",
    "progesterone_status",
    "regional_nodes_examined",
    "regional_nodes_positive",
    "survival_months",
    "vital_status",
    "event",
}


ISSUE_COLUMNS = [
    "case_id",
    "rule_id",
    "field",
    "severity",
    "message",
]


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne une ligne par anomalie détectée."""

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        raise ValueError(
            "Colonnes nécessaires absentes : "
            f"{sorted(missing_columns)}"
        )

    issues: list[dict[str, str]] = []

    def add_issues(
        mask: pd.Series,
        rule_id: str,
        field: str,
        severity: str,
        message: str,
    ) -> None:
        """Ajoute les cas concernés au journal."""

        safe_mask = mask.fillna(False)

        for case_id in df.loc[safe_mask, "case_id"]:
            issues.append(
                {
                    "case_id": str(case_id),
                    "rule_id": rule_id,
                    "field": field,
                    "severity": severity,
                    "message": message,
                }
            )

    # Valeurs obligatoires.
    mandatory_fields = [
        "age",
        "t_stage",
        "n_stage",
        "overall_stage",
        "survival_months",
        "vital_status",
    ]

    for field in mandatory_fields:
        add_issues(
            df[field].isna(),
            f"DQ_MISSING_{field.upper()}",
            field,
            "error",
            f"Valeur manquante pour {field}.",
        )

    # Doublons exacts, en excluant les métadonnées techniques.
    excluded_columns = {
        "case_id",
        "source_file",
        "processing_timestamp_utc",
    }

    duplicate_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]

    add_issues(
        df.duplicated(
            subset=duplicate_columns,
            keep=False,
        ),
        "DQ_DUPLICATE_ROW",
        "all_fields",
        "warning",
        "Observation identique à une autre ligne.",
    )

    # Plages numériques.
    add_issues(
        df["age"].notna()
        & ~df["age"].between(0, 120),
        "DQ_INVALID_AGE",
        "age",
        "error",
        "Âge situé hors de l'intervalle 0-120.",
    )

    add_issues(
        df["tumor_size"].notna()
        & (df["tumor_size"] < 0),
        "DQ_NEGATIVE_TUMOR_SIZE",
        "tumor_size",
        "error",
        "La taille tumorale ne peut pas être négative.",
    )

    add_issues(
        df["regional_nodes_examined"].notna()
        & (df["regional_nodes_examined"] < 0),
        "DQ_NEGATIVE_EXAMINED_NODES",
        "regional_nodes_examined",
        "error",
        "Le nombre de ganglions examinés ne peut pas être négatif.",
    )

    add_issues(
        df["regional_nodes_positive"].notna()
        & (df["regional_nodes_positive"] < 0),
        "DQ_NEGATIVE_POSITIVE_NODES",
        "regional_nodes_positive",
        "error",
        "Le nombre de ganglions positifs ne peut pas être négatif.",
    )

    add_issues(
        (
            df["regional_nodes_positive"]
            > df["regional_nodes_examined"]
        ),
        "DQ_POSITIVE_NODES_GT_EXAMINED",
        "regional_nodes_positive",
        "error",
        (
            "Le nombre de ganglions positifs dépasse "
            "le nombre de ganglions examinés."
        ),
    )

    add_issues(
        df["survival_months"].notna()
        & (df["survival_months"] < 0),
        "DQ_NEGATIVE_SURVIVAL",
        "survival_months",
        "error",
        "La durée de survie ne peut pas être négative.",
    )

    # Domaines de valeurs.
    allowed_values = {
        "t_stage": {"T1", "T2", "T3", "T4"},
        "n_stage": {"N1", "N2", "N3"},
        "vital_status": {"Alive", "Dead"},
        "estrogen_status": {"Positive", "Negative"},
        "progesterone_status": {"Positive", "Negative"},
    }

    for field, accepted_values in allowed_values.items():
        invalid_mask = (
            df[field].notna()
            & ~df[field].isin(accepted_values)
        )

        add_issues(
            invalid_mask,
            f"DQ_INVALID_{field.upper()}",
            field,
            "warning",
            (
                f"Valeur différente des modalités attendues : "
                f"{sorted(accepted_values)}."
            ),
        )

    # Cohérence entre statut vital et événement.
    inconsistent_event = (
        (
            df["vital_status"].eq("Alive")
            & df["event"].ne(0)
        )
        |
        (
            df["vital_status"].eq("Dead")
            & df["event"].ne(1)
        )
    )

    add_issues(
        inconsistent_event,
        "DQ_INCONSISTENT_EVENT",
        "event",
        "error",
        "Incohérence entre le statut vital et l'événement.",
    )

    return pd.DataFrame(
        issues,
        columns=ISSUE_COLUMNS,
    )


def write_summary(
    df: pd.DataFrame,
    issues_df: pd.DataFrame,
) -> None:
    """Crée un rapport Markdown agrégé."""

    affected_cases = (
        issues_df["case_id"].nunique()
        if not issues_df.empty
        else 0
    )

    valid_cases = len(df) - affected_cases

    error_count = (
        int((issues_df["severity"] == "error").sum())
        if not issues_df.empty
        else 0
    )

    warning_count = (
        int((issues_df["severity"] == "warning").sum())
        if not issues_df.empty
        else 0
    )

    if issues_df.empty:
        rule_rows = "| Aucun | 0 |"
    else:
        counts = (
            issues_df["rule_id"]
            .value_counts()
            .sort_index()
        )

        rule_rows = "\n".join(
            f"| {rule_id} | {count} |"
            for rule_id, count in counts.items()
        )

    report = f"""# Data Quality Summary

## Overview

- Total records: {len(df)}
- Records classified as valid: {valid_cases}
- Records requiring review: {affected_cases}
- Total issues: {len(issues_df)}
- Errors: {error_count}
- Warnings: {warning_count}

## Issues by rule

| Rule | Number of issues |
|---|---:|
{rule_rows}

## Interpretation

A record requiring review is not automatically an incorrect
clinical record. It means that at least one technical quality
rule requires verification.

No record was silently deleted by the validation pipeline.
"""

    SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    SUMMARY_FILE.write_text(
        report,
        encoding="utf-8",
    )


def validate_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Exécute la validation complète."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Le fichier intermédiaire est absent. "
            "Exécutez d'abord python -m src.prepare_data."
        )

    df = pd.read_csv(INPUT_FILE)

    issues_df = validate_dataframe(df)

    affected_case_ids = set(
        issues_df["case_id"]
        if not issues_df.empty
        else []
    )

    df["quality_status"] = "valid"

    df.loc[
        df["case_id"].isin(affected_case_ids),
        "quality_status",
    ] = "needs_review"

    ISSUES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROCESSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    issues_df.to_csv(
        ISSUES_FILE,
        index=False,
        encoding="utf-8",
    )

    df.to_csv(
        PROCESSED_FILE,
        index=False,
        encoding="utf-8",
    )

    write_summary(df, issues_df)

    print(f"Observations : {len(df)}")
    print(f"Anomalies détectées : {len(issues_df)}")
    print(f"Fichier validé : {PROCESSED_FILE}")
    print(f"Rapport agrégé : {SUMMARY_FILE}")

    return df, issues_df


if __name__ == "__main__":
    validate_data()