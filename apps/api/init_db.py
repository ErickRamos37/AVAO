"""Prepara el esquema SQLite sin borrar los pedidos existentes."""

from contextlib import closing
from pathlib import Path

from apps.api.main import connect_db, database_path


SCHEMA = Path(__file__).resolve().parents[2] / "docs" / "technical" / "HU01-modelo-sqlite.sql"


if __name__ == "__main__":
    database_path().parent.mkdir(parents=True, exist_ok=True)
    with closing(connect_db()) as connection:
        if connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'pedidos'"
        ).fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(pedidos)")}
            if "etiqueta" not in columns:
                connection.execute("ALTER TABLE pedidos ADD COLUMN etiqueta TEXT")
                connection.commit()
        if connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'plan_aluminio'"
        ).fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(plan_aluminio)")}
            if "cortadas" not in columns:
                connection.execute(
                    "ALTER TABLE plan_aluminio ADD COLUMN cortadas INTEGER NOT NULL DEFAULT 0 "
                    "CHECK (cortadas >= 0 AND cortadas <= cantidad)"
                )
                connection.commit()
        connection.executescript(SCHEMA.read_text(encoding="utf-8"))
    print("Esquema de pedidos preparado.")
