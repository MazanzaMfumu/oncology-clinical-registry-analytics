"""Dashboard local et public du registre oncologique.

Mode local :
    utilise la base SQLite produite par le pipeline.

Mode public :
    utilise uniquement des données entièrement synthétiques.
"""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import sys

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# 1. Définition des chemins
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry.sqlite"
)


# Ajoute la racine du projet au chemin Python.
# Cette précaution facilite l'import de src.demo_data
# en local et sur Streamlit Community Cloud.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.demo_data import generate_synthetic_demo


# ---------------------------------------------------------
# 2. Configuration de l'application
# ---------------------------------------------------------

st.set_page_config(
    page_title="Oncology Registry Dashboard",
    layout="wide",
)


# ---------------------------------------------------------
# 3. Détermination du mode
# ---------------------------------------------------------

# Cette variable sert à tester volontairement le mode public
# depuis votre propre ordinateur.
FORCE_SYNTHETIC_DEMO = (
    os.getenv(
        "USE_SYNTHETIC_DEMO",
        "0",
    )
    == "1"
)


@st.cache_data
def load_local_database() -> pd.DataFrame:
    """Charge les informations de la base SQLite locale."""

    query = """
        SELECT
            p.case_id,
            p.age,
            p.quality_status,
            t.overall_stage,
            t.estrogen_status,
            t.progesterone_status,
            t.tumor_size,
            o.vital_status,
            o.event
        FROM patients AS p
        INNER JOIN tumors AS t
            ON p.case_id = t.case_id
        INNER JOIN outcomes AS o
            ON p.case_id = o.case_id
    """

    with sqlite3.connect(
        DATABASE_FILE
    ) as connection:
        return pd.read_sql_query(
            query,
            connection,
        )


@st.cache_data
def load_synthetic_demo() -> pd.DataFrame:
    """Produit les données synthétiques de démonstration."""

    return generate_synthetic_demo(
        number_of_records=1_200,
        random_seed=42,
    )


def load_dashboard_data() -> tuple[pd.DataFrame, str]:
    """Choisit automatiquement la source appropriée.

    Sur votre ordinateur, la base SQLite est utilisée lorsqu'elle
    existe.

    Sur le cloud, la base n'est pas publiée. Le dashboard utilise
    alors automatiquement les données synthétiques.
    """

    local_database_available = (
        DATABASE_FILE.exists()
        and not FORCE_SYNTHETIC_DEMO
    )

    if local_database_available:
        dataframe = load_local_database()

        return (
            dataframe,
            "LOCAL_PIPELINE",
        )

    dataframe = load_synthetic_demo()

    return (
        dataframe,
        "PUBLIC_SYNTHETIC_DEMO",
    )


# ---------------------------------------------------------
# 4. Chargement des données
# ---------------------------------------------------------

try:
    df, data_mode = load_dashboard_data()

except Exception as error:
    st.error(
        "Le chargement des données a échoué."
    )

    st.exception(error)

    st.stop()


# ---------------------------------------------------------
# 5. Présentation et transparence
# ---------------------------------------------------------

st.title(
    "Oncology Clinical Registry Dashboard"
)

st.caption(
    "Prototype pédagogique de gestion et de valorisation "
    "de données oncologiques."
)


if data_mode == "PUBLIC_SYNTHETIC_DEMO":
    st.warning(
        "Mode public de démonstration : toutes les observations "
        "affichées sont entièrement synthétiques et fictives. "
        "Elles ne proviennent d'aucun patient et ne constituent "
        "pas des statistiques officielles."
    )

    st.write(
        "**Source active : données synthétiques générées "
        "par le code du projet.**"
    )

else:
    st.info(
        "Mode local : l'application utilise la base SQLite "
        "produite sur cet ordinateur par le pipeline de "
        "préparation et de validation."
    )

    st.write(
        "**Source active : base SQLite locale produite par "
        "le pipeline.**"
    )


# ---------------------------------------------------------
# 6. Vérification des variables nécessaires
# ---------------------------------------------------------

required_columns = {
    "case_id",
    "age",
    "quality_status",
    "overall_stage",
    "estrogen_status",
    "progesterone_status",
    "tumor_size",
    "vital_status",
    "event",
}

missing_columns = required_columns.difference(
    df.columns
)

if missing_columns:
    st.error(
        "Certaines variables nécessaires sont absentes : "
        f"{sorted(missing_columns)}"
    )

    st.stop()


# ---------------------------------------------------------
# 7. Filtres
# ---------------------------------------------------------

st.sidebar.header(
    "Filtres"
)


available_stages = sorted(
    df["overall_stage"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_stages = st.sidebar.multiselect(
    "Stades",
    options=available_stages,
    default=available_stages,
)


available_quality_statuses = sorted(
    df["quality_status"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_quality_statuses = st.sidebar.multiselect(
    "Statuts de qualité",
    options=available_quality_statuses,
    default=available_quality_statuses,
)


filtered_df = df.loc[
    df["overall_stage"].isin(selected_stages)
    & df["quality_status"].isin(
        selected_quality_statuses
    )
].copy()


if filtered_df.empty:
    st.warning(
        "Aucune observation ne correspond aux filtres."
    )

    st.stop()


# ---------------------------------------------------------
# 8. Indicateurs principaux
# ---------------------------------------------------------

st.subheader(
    "Indicateurs principaux"
)


column1, column2, column3 = st.columns(3)


column1.metric(
    "Nombre de cas",
    f"{len(filtered_df):,}",
)


average_age = filtered_df["age"].mean()

column2.metric(
    "Âge moyen",
    (
        f"{average_age:.1f}"
        if pd.notna(average_age)
        else "Non disponible"
    ),
)


number_of_events = int(
    filtered_df["event"]
    .fillna(0)
    .sum()
)

column3.metric(
    "Événements enregistrés",
    number_of_events,
)


# ---------------------------------------------------------
# 9. Visualisations agrégées
# ---------------------------------------------------------

st.subheader(
    "Répartition selon le stade"
)

stage_counts = (
    filtered_df["overall_stage"]
    .value_counts()
    .sort_index()
    .rename("Nombre de cas")
)

st.bar_chart(
    stage_counts
)


st.subheader(
    "Statut vital selon le stade"
)

vital_status_table = pd.crosstab(
    filtered_df["overall_stage"],
    filtered_df["vital_status"],
)

st.dataframe(
    vital_status_table,
    use_container_width=True,
)


st.subheader(
    "Statut de qualité"
)

quality_counts = (
    filtered_df["quality_status"]
    .value_counts()
    .rename("Nombre de cas")
)

st.bar_chart(
    quality_counts
)


st.subheader(
    "Statut des récepteurs aux œstrogènes"
)

estrogen_counts = (
    filtered_df["estrogen_status"]
    .value_counts()
    .rename("Nombre de cas")
)

st.bar_chart(
    estrogen_counts
)


# ---------------------------------------------------------
# 10. Limites
# ---------------------------------------------------------

st.divider()

st.subheader(
    "Limites d'interprétation"
)

st.write(
    "Ce dashboard est un prototype technique. Il ne fournit "
    "ni diagnostic, ni pronostic individuel, ni recommandation "
    "médicale."
)


if data_mode == "PUBLIC_SYNTHETIC_DEMO":
    st.write(
        "Les chiffres présentés dans cette version publique "
        "sont entièrement artificiels. Ils servent uniquement "
        "à démontrer les filtres, les indicateurs et les "
        "visualisations de l'application."
    )

else:
    st.write(
        "La version locale repose sur la base générée par le "
        "pipeline du projet. Elle ne doit pas être confondue "
        "avec un registre hospitalier opérationnel."
    )