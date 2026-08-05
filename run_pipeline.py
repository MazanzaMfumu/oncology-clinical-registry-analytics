"""Run the complete oncology registry data pipeline."""

from __future__ import annotations

from src.prepare_data import prepare_data
from src.validate_data import validate_data
from src.build_database import build_database
from src.generate_excel_report import generate_excel_report


def main() -> None:
    """Execute all pipeline steps in the required order."""

    print()
    print("1. Préparation des données")
    prepare_data()

    print()
    print("2. Validation de la qualité des données")
    validate_data()

    print()
    print("3. Construction de la base SQLite")
    build_database()

    print()
    print("4. Génération du rapport Excel")
    generate_excel_report()

    print()
    print("Pipeline terminé avec succès.")


if __name__ == "__main__":
    main()