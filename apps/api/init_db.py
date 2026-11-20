"""Prepara el esquema SQLite sin borrar los pedidos existentes."""

from contextlib import closing
from pathlib import Path

from apps.api.main import connect_db, database_path
from apps.api.costos_insumos import INSUMOS


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
            if "cliente_id" not in columns:
                connection.execute("ALTER TABLE pedidos ADD COLUMN cliente_id INTEGER REFERENCES clientes (id)")
                connection.commit()
            if "notas" not in columns:
                connection.execute("ALTER TABLE pedidos ADD COLUMN notas TEXT")
                connection.commit()
            if "traslado_centavos" not in columns:
                connection.execute("ALTER TABLE pedidos ADD COLUMN traslado_centavos INTEGER CHECK (traslado_centavos IS NULL OR traslado_centavos >= 0)")
                connection.commit()
        if connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ventanas'"
        ).fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(ventanas)")}
            if "ensamblada" not in columns:
                connection.execute(
                    "ALTER TABLE ventanas ADD COLUMN ensamblada INTEGER NOT NULL DEFAULT 0 "
                    "CHECK (ensamblada IN (0, 1))"
                )
                connection.commit()
            if "descartada" not in columns:
                connection.execute(
                    "ALTER TABLE ventanas ADD COLUMN descartada INTEGER NOT NULL DEFAULT 0 "
                    "CHECK (descartada IN (0, 1))"
                )
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
        if connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'plan_vidrio'"
        ).fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(plan_vidrio)")}
            if "cortadas" not in columns:
                connection.execute(
                    "ALTER TABLE plan_vidrio ADD COLUMN cortadas INTEGER NOT NULL DEFAULT 0 "
                    "CHECK (cortadas >= 0 AND cortadas <= cantidad)"
                )
                connection.commit()
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'merma_pedido'").fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(merma_pedido)")}
            if "detalle_json" not in columns:
                connection.execute("ALTER TABLE merma_pedido ADD COLUMN detalle_json TEXT")
                connection.commit()
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'movimientos'").fetchone():
            columns = {row[1] for row in connection.execute("PRAGMA table_info(movimientos)")}
            if "fecha_anulacion" not in columns:
                connection.execute("ALTER TABLE movimientos ADD COLUMN fecha_anulacion TEXT")
                connection.commit()
        connection.executescript(SCHEMA.read_text(encoding="utf-8"))
        with connection:
            connection.executemany(
                "INSERT OR IGNORE INTO costos_insumos (codigo, costo_centavos) VALUES (?, ?)",
                ((item[0], item[6]) for item in INSUMOS),
            )
            connection.executemany(
                "UPDATE costos_insumos SET costo_centavos = ? "
                "WHERE codigo = ? AND costo_centavos IS NULL",
                ((item[6], item[0]) for item in INSUMOS
                 if item[0] in {"tela_mosquitera", "vinil_doble_fuerza"}),
            )
    print("Esquema de pedidos preparado.")
