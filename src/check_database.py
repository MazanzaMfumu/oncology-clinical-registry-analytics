"""Simple check of the SQLite database."""

from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "oncology_registry.sqlite"
)


def check_database() -> None:
    """Affiche les tables et leur nombre de lignes."""

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            "La base SQLite n'existe pas. "
            "Exécutez d'abord python -m src.build_database."
        )

    with sqlite3.connect(DATABASE_FILE) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        ).fetchall()

        print("Tables trouvées :")

        for (table_name,) in tables:
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}";'
            ).fetchone()[0]

            print(
                f"- {table_name}: {count} ligne(s)"
            )


if __name__ == "__main__":
    check_database()