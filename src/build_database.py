"""Construction of the SQLite relational database."""

from pathlib import Path
import sqlite3

import pandas as pd


# Project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Input files.
VALIDATED_DATA_FILE = (
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

# File containing the SQL structure.
SCHEMA_FILE = (
    PROJECT_ROOT
    / "sql"
    / "schema.sql"
)

# Locally generated SQLite database.
DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry.sqlite"
)


# Columns required to build the database.
EXPECTED_COLUMNS = {
    "case_id",
    "age",
    "race",
    "marital_status",
    "quality_status",
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
    "survival_months",
    "vital_status",
    "event",
}


QUALITY_ISSUE_COLUMNS = [
    "case_id",
    "rule_id",
    "field",
    "severity",
    "message",
]


def load_validated_data() -> pd.DataFrame:
    """Charge les données validées et contrôle leurs colonnes."""

    if not VALIDATED_DATA_FILE.exists():
        raise FileNotFoundError(
            "Le fichier validé est absent : "
            f"{VALIDATED_DATA_FILE}\n"
            "Exécutez d'abord : "
            "python -m src.prepare_data puis "
            "python -m src.validate_data."
        )

    df = pd.read_csv(VALIDATED_DATA_FILE)

    missing_columns = EXPECTED_COLUMNS.difference(
        df.columns
    )

    if missing_columns:
        raise ValueError(
            "Certaines colonnes nécessaires sont absentes : "
            f"{sorted(missing_columns)}"
        )

    if df["case_id"].duplicated().any():
        raise ValueError(
            "La colonne case_id contient des doublons. "
            "La base ne peut pas être créée avec plusieurs "
            "cas portant le même identifiant."
        )

    return df


def load_quality_issues() -> pd.DataFrame:
    """Charge le journal des anomalies s'il existe."""

    if not QUALITY_ISSUES_FILE.exists():
        return pd.DataFrame(
            columns=QUALITY_ISSUE_COLUMNS
        )

    issues = pd.read_csv(QUALITY_ISSUES_FILE)

    missing_columns = set(
        QUALITY_ISSUE_COLUMNS
    ).difference(issues.columns)

    if missing_columns:
        raise ValueError(
            "Le fichier des anomalies ne possède pas "
            "les colonnes attendues : "
            f"{sorted(missing_columns)}"
        )

    return issues[QUALITY_ISSUE_COLUMNS].copy()


def build_database() -> Path:
    """Crée la base SQLite et alimente ses tables."""

    df = load_validated_data()
    issues = load_quality_issues()

    # Une table par domaine analytique.
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

    # The output directory must exist.
    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # The previous base is removed in order to obtain
    # a complete and reproducible reconstruction.
    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    schema_sql = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(DATABASE_FILE) as connection:
        # Enables relationships defined by foreign keys.
        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        # Crée les tables à partir de schema.sql.
        connection.executescript(schema_sql)

        # Create the tables from schema.sql.
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

        connection.commit()

    print("=" * 60)
    print("BASE SQLITE CRÉÉE AVEC SUCCÈS")
    print("=" * 60)
    print(f"Fichier : {DATABASE_FILE}")
    print(f"Patients : {len(patients)}")
    print(f"Tumeurs : {len(tumors)}")
    print(f"Résultats de suivi : {len(outcomes)}")
    print(f"Anomalies de qualité : {len(issues)}")

    return DATABASE_FILE


if __name__ == "__main__":
    build_database()