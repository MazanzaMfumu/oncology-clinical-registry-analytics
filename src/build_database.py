"""Construction de la base relationnelle SQLite."""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VALIDATED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry_validated.csv"
)

ISSUES_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "data_quality_issues.csv"
)

SCHEMA_FILE = (
    PROJECT_ROOT
    / "sql"
    / "schema.sql"
)

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry.sqlite"
)


def build_database() -> None:
    """Crée et alimente les tables SQLite."""

    if not VALIDATED_FILE.exists():
        raise FileNotFoundError(
            "Le fichier validé est absent. "
            "Exécutez d'abord python -m src.validate_data."
        )

    df = pd.read_csv(VALIDATED_FILE)

    patients = df[
        [
            "case_id",
            "age",
            "race",
            "marital_status",
            "quality_status",
        ]
    ].copy()

    tumors = df[
        [
            "case_id",
            "t_stage",
            "n_stage",
            "overall_stage",
            "grade",
            "a_stage",
            "tumor_size",
            "estrogen_status",
            "progesterone_status",
            "regional_nodes_examined",
            "regional_nodes_positive",
            "lymph_node_ratio",
        ]
    ].copy()

    outcomes = df[
        [
            "case_id",
            "survival_months",
            "vital_status",
            "event",
        ]
    ].copy()

    if ISSUES_FILE.exists():
        issues = pd.read_csv(ISSUES_FILE)
    else:
        issues = pd.DataFrame(
            columns=[
                "case_id",
                "rule_id",
                "field",
                "severity",
                "message",
            ]
        )

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Supprime uniquement l'ancienne base produite.
    # Les fichiers CSV sources ne sont pas touchés.
    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    schema_sql = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        connection.executescript(schema_sql)

        patients.to_sql(
            "patients",
            connection,
            if_exists="append",
            index=False,
        )

        tumors.to_sql(
            "tumors",
            connection,
            if_exists="append",
            index=False,
        )

        outcomes.to_sql(
            "outcomes",
            connection,
            if_exists="append",
            index=False,
        )

        if not issues.empty:
            issues.to_sql(
                "data_quality_issues",
                connection,
                if_exists="append",
                index=False,
            )

    print(f"Base créée : {DATABASE_FILE}")
    print(f"Nombre de patients : {len(patients)}")
    print(f"Nombre de tumeurs : {len(tumors)}")
    print(f"Nombre de suivis : {len(outcomes)}")
    print(f"Nombre d'anomalies : {len(issues)}")


if __name__ == "__main__":
    build_database()