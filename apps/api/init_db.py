"""Aplica el esquema inicial de HU-01 a un archivo SQLite local."""

from contextlib import closing
from pathlib import Path

from apps.api.main import connect_db, database_path


SCHEMA = Path(__file__).resolve().parents[2] / "docs" / "technical" / "HU01-modelo-sqlite.sql"


if __name__ == "__main__":
    database_path().parent.mkdir(parents=True, exist_ok=True)
    with closing(connect_db()) as connection:
        connection.executescript(SCHEMA.read_text(encoding="utf-8"))
    print("Esquema HU-01 aplicado.")
