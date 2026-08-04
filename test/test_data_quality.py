"""Tests automatisés des principales règles de qualité."""

import pandas as pd

from src.prepare_data import to_snake_case
from src.validate_data import validate_dataframe


def create_valid_dataframe() -> pd.DataFrame:
    """Crée une petite observation techniquement valide."""

    return pd.DataFrame(
        {
            "case_id": ["CASE_00001"],
            "age": [55],
            "t_stage": ["T2"],
            "n_stage": ["N1"],
            "overall_stage": ["IIA"],
            "tumor_size": [25],
            "estrogen_status": ["Positive"],
            "progesterone_status": ["Positive"],
            "regional_nodes_examined": [10],
            "regional_nodes_positive": [2],
            "survival_months": [48],
            "vital_status": ["Alive"],
            "event": [0],
        }
    )


def test_to_snake_case() -> None:
    assert to_snake_case(
        "Tumor Size"
    ) == "tumor_size"


def test_valid_dataframe_has_no_issue() -> None:
    df = create_valid_dataframe()

    issues = validate_dataframe(df)

    assert issues.empty


def test_positive_nodes_cannot_exceed_examined() -> None:
    df = create_valid_dataframe()

    df.loc[
        0,
        "regional_nodes_positive",
    ] = 12

    issues = validate_dataframe(df)

    assert (
        "DQ_POSITIVE_NODES_GT_EXAMINED"
        in issues["rule_id"].tolist()
    )


def test_negative_survival_is_detected() -> None:
    df = create_valid_dataframe()

    df.loc[
        0,
        "survival_months",
    ] = -3

    issues = validate_dataframe(df)

    assert (
        "DQ_NEGATIVE_SURVIVAL"
        in issues["rule_id"].tolist()
    )


def test_alive_status_must_have_event_zero() -> None:
    df = create_valid_dataframe()

    df.loc[
        0,
        "event",
    ] = 1

    issues = validate_dataframe(df)

    assert (
        "DQ_INCONSISTENT_EVENT"
        in issues["rule_id"].tolist()
    )