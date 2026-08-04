"""Génération des données synthétiques du dashboard public.

Les observations produites par ce module sont entièrement
fictives. Elles servent uniquement à démontrer le fonctionnement
technique de l'application Streamlit.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_synthetic_demo(
    number_of_records: int = 1_200,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Crée une cohorte synthétique reproductible.

    Parameters
    ----------
    number_of_records:
        Nombre d'observations fictives à générer.

    random_seed:
        Graine permettant de reproduire exactement les mêmes
        données à chaque exécution.

    Returns
    -------
    pandas.DataFrame
        Table synthétique adaptée au dashboard.
    """

    if number_of_records <= 0:
        raise ValueError(
            "number_of_records doit être strictement positif."
        )

    random_generator = np.random.default_rng(
        random_seed
    )

    case_ids = [
        f"SYNTHETIC_{number:05d}"
        for number in range(
            1,
            number_of_records + 1,
        )
    ]

    overall_stage = random_generator.choice(
        [
            "I",
            "IIA",
            "IIB",
            "IIIA",
            "IIIB",
        ],
        size=number_of_records,
        p=[
            0.18,
            0.27,
            0.23,
            0.19,
            0.13,
        ],
    )

    age = np.clip(
        np.rint(
            random_generator.normal(
                loc=58,
                scale=11,
                size=number_of_records,
            )
        ),
        25,
        90,
    ).astype(int)

    tumor_size = np.clip(
        random_generator.gamma(
            shape=2.4,
            scale=12,
            size=number_of_records,
        ),
        2,
        130,
    ).round(1)

    estrogen_status = random_generator.choice(
        [
            "Positive",
            "Negative",
        ],
        size=number_of_records,
        p=[
            0.74,
            0.26,
        ],
    )

    progesterone_status = random_generator.choice(
        [
            "Positive",
            "Negative",
        ],
        size=number_of_records,
        p=[
            0.66,
            0.34,
        ],
    )

    quality_status = random_generator.choice(
        [
            "valid",
            "needs_review",
        ],
        size=number_of_records,
        p=[
            0.97,
            0.03,
        ],
    )

    # Ces probabilités sont uniquement illustratives.
    # Elles ne constituent pas un modèle clinique.
    illustrative_event_probabilities = {
        "I": 0.06,
        "IIA": 0.10,
        "IIB": 0.15,
        "IIIA": 0.24,
        "IIIB": 0.33,
    }

    event_probability = np.array(
        [
            illustrative_event_probabilities[stage]
            for stage in overall_stage
        ]
    )

    event = random_generator.binomial(
        n=1,
        p=event_probability,
        size=number_of_records,
    )

    vital_status = np.where(
        event == 1,
        "Dead",
        "Alive",
    )

    return pd.DataFrame(
        {
            "case_id": case_ids,
            "age": age,
            "quality_status": quality_status,
            "overall_stage": overall_stage,
            "estrogen_status": estrogen_status,
            "progesterone_status": progesterone_status,
            "tumor_size": tumor_size,
            "vital_status": vital_status,
            "event": event,
        }
    )