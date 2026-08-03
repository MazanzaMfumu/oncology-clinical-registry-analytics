"""Préparation reproductible du dataset oncologique.

- le fichier Kaggle contient 16 colonnes physiques ;
- la colonne source `Unnamed: 3` est entièrement vide ;
- cette colonne vide est supprimée ;
- aucune variable `differentiation` n'est inventée ;
- les 15 variables sources réellement exploitables sont conservées.
"""

from pathlib import Path
import re

import pandas as pd


# ------------------------------------------------------------
# 1. Définition des chemins du projet
# ------------------------------------------------------------

# __file__ représente le fichier src/prepare_data.py.
# parents[1] remonte jusqu'à la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

INTERIM_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "oncology_registry_prepared.csv"
)


# ------------------------------------------------------------
# 2. Recherche du fichier CSV brut
# ------------------------------------------------------------

def find_raw_csv() -> Path:
    """Trouve l'unique fichier CSV placé directement dans data/raw."""

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Le dossier data/raw est absent : {RAW_DATA_DIR}"
        )

    # La recherche n'est pas récursive.
    # Un fichier placé dans data/raw/_quarantine ne sera donc pas utilisé.
    csv_files = sorted(
        path
        for path in RAW_DATA_DIR.glob("*.csv")
        if path.is_file()
    )

    if not csv_files:
        raise FileNotFoundError(
            "Aucun fichier CSV trouvé directement dans data/raw."
        )

    if len(csv_files) > 1:
        file_names = [
            path.name
            for path in csv_files
        ]

        raise RuntimeError(
            "Plusieurs fichiers CSV ont été trouvés dans data/raw : "
            f"{file_names}. "
            "Conservez un seul fichier source directement dans data/raw."
        )

    return csv_files[0]


# ------------------------------------------------------------
# 3. Normalisation des noms de colonnes
# ------------------------------------------------------------

def to_snake_case(column_name: str) -> str:
    """Transforme par exemple 'Tumor Size' en 'tumor_size'."""

    normalized = str(column_name).strip().lower()

    # Remplace les espaces et caractères spéciaux
    # par un seul underscore.
    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized,
    )

    # Retire les underscores placés au début ou à la fin.
    return normalized.strip("_")


# ------------------------------------------------------------
# 4. Préparation des données
# ------------------------------------------------------------

def prepare_data() -> pd.DataFrame:
    """Lit, harmonise et enregistre les données intermédiaires."""

    input_file = find_raw_csv()

    print(f"Fichier source utilisé : {input_file.name}")

    # Le fichier brut est seulement lu.
    # Il n'est jamais modifié ou réenregistré dans data/raw.
    df = pd.read_csv(input_file)

    original_rows, original_columns = df.shape

    print(
        "Dimensions originales : "
        f"{original_rows} lignes et "
        f"{original_columns} colonnes"
    )

    # --------------------------------------------------------
    # 4.1. Normaliser les noms des colonnes
    # --------------------------------------------------------

    df.columns = [
        to_snake_case(column)
        for column in df.columns
    ]

    # Vérifier qu'aucun nom de colonne n'est dupliqué
    # après la normalisation.
    duplicated_columns = (
        df.columns[
            df.columns.duplicated()
        ]
        .tolist()
    )

    if duplicated_columns:
        raise ValueError(
            "Des noms de colonnes sont dupliqués "
            "après normalisation : "
            f"{duplicated_columns}"
        )

    # --------------------------------------------------------
    # 4.2. Traiter les colonnes anonymes
    # --------------------------------------------------------

    unnamed_columns = [
        column
        for column in df.columns
        if column.startswith("unnamed_")
    ]

    # Colonnes anonymes entièrement vides :
    # elles peuvent être supprimées avec traçabilité.
    empty_unnamed_columns = [
        column
        for column in unnamed_columns
        if df[column].isna().all()
    ]

    # Une colonne anonyme contenant des données ne doit jamais
    # être supprimée automatiquement.
    nonempty_unnamed_columns = [
        column
        for column in unnamed_columns
        if not df[column].isna().all()
    ]

    if nonempty_unnamed_columns:
        raise ValueError(
            "Certaines colonnes anonymes contiennent des données : "
            f"{nonempty_unnamed_columns}. "
            "Une vérification manuelle de la source est nécessaire."
        )

    if empty_unnamed_columns:
        print(
            "Colonnes anonymes entièrement vides supprimées : "
            f"{empty_unnamed_columns}"
        )

        df = df.drop(
            columns=empty_unnamed_columns
        ).copy()

    # --------------------------------------------------------
    # 4.3. Contrôler les autres colonnes entièrement vides
    # --------------------------------------------------------

    other_empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if other_empty_columns:
        raise ValueError(
            "Colonnes métier entièrement vides détectées : "
            f"{other_empty_columns}. "
            "Elles ne seront pas supprimées automatiquement."
        )

    # --------------------------------------------------------
    # 4.4. Harmoniser les noms propres au dataset
    # --------------------------------------------------------

    rename_map = {
        "6th_stage": "overall_stage",
        "regional_node_examined": "regional_nodes_examined",
        "reginol_node_positive": "regional_nodes_positive",
        "regional_node_positive": "regional_nodes_positive",
        "status": "vital_status",
    }

    df = df.rename(
        columns=rename_map
    )

    # Contrôle supplémentaire :
    # deux colonnes différentes ne doivent pas recevoir
    # le même nom après le renommage.
    duplicated_columns_after_rename = (
        df.columns[
            df.columns.duplicated()
        ]
        .tolist()
    )

    if duplicated_columns_after_rename:
        raise ValueError(
            "Des noms de colonnes sont dupliqués "
            "après renommage : "
            f"{duplicated_columns_after_rename}"
        )

    # --------------------------------------------------------
    # 4.5. Vérifier le schéma attendu — Option B
    # --------------------------------------------------------

    # La variable differentiation n'est pas incluse :
    # elle est absente du fichier Kaggle réellement téléchargé.
    expected_columns = {
        "age",
        "race",
        "marital_status",
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
        "survival_months",
        "vital_status",
    }

    available_columns = set(
        df.columns
    )

    missing_columns = (
        expected_columns
        .difference(available_columns)
    )

    if missing_columns:
        raise ValueError(
            "Certaines colonnes attendues sont absentes : "
            f"{sorted(missing_columns)}\n"
            "Colonnes disponibles après préparation : "
            f"{sorted(df.columns.tolist())}"
        )

    unexpected_columns = (
        available_columns
        .difference(expected_columns)
    )

    if unexpected_columns:
        raise ValueError(
            "Certaines colonnes inattendues sont présentes : "
            f"{sorted(unexpected_columns)}\n"
            "Le schéma de la source doit être vérifié avant "
            "de poursuivre."
        )

    print(
        "Colonnes sources exploitables : "
        f"{len(expected_columns)}"
    )

    # --------------------------------------------------------
    # 4.6. Créer un identifiant technique
    # --------------------------------------------------------

    # Cet identifiant est créé uniquement pour le projet.
    # Il ne correspond pas à un identifiant médical réel.
    df.insert(
        0,
        "case_id",
        [
            f"CASE_{number:05d}"
            for number in range(
                1,
                len(df) + 1,
            )
        ],
    )

    # --------------------------------------------------------
    # 4.7. Convertir les variables numériques
    # --------------------------------------------------------

    numeric_columns = [
        "age",
        "tumor_size",
        "regional_nodes_examined",
        "regional_nodes_positive",
        "survival_months",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Une valeur impossible à convertir devient manquante.
    # Elle sera signalée plus tard par validate_data.py.
    # Elle n'est pas remplacée automatiquement.

    # --------------------------------------------------------
    # 4.8. Nettoyer les variables catégorielles
    # --------------------------------------------------------

    categorical_columns = [
        "race",
        "marital_status",
        "t_stage",
        "n_stage",
        "overall_stage",
        "grade",
        "a_stage",
        "estrogen_status",
        "progesterone_status",
        "vital_status",
    ]

    for column in categorical_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # --------------------------------------------------------
    # 4.9. Créer la variable d'événement
    # --------------------------------------------------------

    # Pour l'analyse de survie :
    # Alive = 0 : décès non observé au dernier suivi.
    # Dead = 1 : décès observé.
    event_map = {
        "alive": 0,
        "dead": 1,
    }

    normalized_vital_status = (
        df["vital_status"]
        .str.lower()
    )

    df["event"] = (
        normalized_vital_status
        .map(event_map)
        .astype("Int64")
    )

    # Une modalité inconnue de vital_status produit une valeur
    # manquante dans event. validate_data.py la signalera.

    # --------------------------------------------------------
    # 4.10. Créer le ratio ganglionnaire
    # --------------------------------------------------------

    # Le dénominateur n'est utilisé que s'il est strictement
    # supérieur à zéro.
    valid_examined_nodes = (
        df["regional_nodes_examined"]
        .where(
            df["regional_nodes_examined"] > 0
        )
    )

    df["lymph_node_ratio"] = (
        df["regional_nodes_positive"]
        / valid_examined_nodes
    )

    # --------------------------------------------------------
    # 4.11. Ajouter les métadonnées de traçabilité
    # --------------------------------------------------------

    df["source_file"] = (
        input_file.name
    )

    df["processing_timestamp_utc"] = (
        pd.Timestamp.now(
            tz="UTC"
        ).isoformat()
    )

    # --------------------------------------------------------
    # 4.12. Enregistrer le fichier intermédiaire
    # --------------------------------------------------------

    INTERIM_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        INTERIM_FILE,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Fichier intermédiaire créé : "
        f"{INTERIM_FILE}"
    )

    print(
        f"Dimensions préparées : "
        f"{df.shape}"
    )

    return df


# ------------------------------------------------------------
# 5. Point d'entrée du script
# ------------------------------------------------------------

if __name__ == "__main__":
    prepare_data()