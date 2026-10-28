"""Estado de ensamble por ventana con planes y cortes guardados."""

from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (
    AluminumMark, AssemblyMark, GlassMark, NewOrder,
    create_order, get_order, mark_aluminum, mark_assembly, mark_glass,
)


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "assembly.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def finish_cuts(self, window):
        for cut in window["avance_aluminio"]:
            for _ in range(cut["pendientes"]):
                mark_aluminum(window["id"], cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(window["avance_vidrio"]["pendientes"]):
            mark_glass(window["id"], GlassMark(accion="marcar"))

    def test_requires_all_cuts_and_keeps_other_window_pending(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"}, {"ancho": "48", "alto": "36"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        with self.assertRaises(HTTPException) as error:
            mark_assembly(first["id"], AssemblyMark(accion="marcar"))
        self.assertEqual(error.exception.status_code, 409)
        self.finish_cuts(first)
        # El segundo vidrio sigue pendiente: el ensamble aún no puede marcarse.
        mark_glass(first["id"], GlassMark(accion="deshacer"))
        with self.assertRaises(HTTPException) as error:
            mark_assembly(first["id"], AssemblyMark(accion="marcar"))
        self.assertEqual(error.exception.status_code, 409)
        mark_glass(first["id"], GlassMark(accion="marcar"))
        self.assertEqual(mark_assembly(first["id"], AssemblyMark(accion="marcar")),
                         {"ensamblada": True})
        first, second = get_order(order_id)["ventanas"]
        self.assertTrue(first["ensamblada"])
        self.assertFalse(second["ensamblada"])
        self.assertEqual(second["codigo"], "A2")
        mark_aluminum(second["id"], 1, AluminumMark(accion="marcar"))
        mark_aluminum(second["id"], 1, AluminumMark(accion="deshacer"))
        mark_glass(second["id"], GlassMark(accion="marcar"))
        mark_glass(second["id"], GlassMark(accion="deshacer"))
        self.assertTrue(get_order(order_id)["ventanas"][0]["ensamblada"])

    def test_assembled_window_blocks_cut_undo_until_assembly_is_undone(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window = get_order(order_id)["ventanas"][0]
        self.finish_cuts(window)
        mark_assembly(window["id"], AssemblyMark(accion="marcar"))
        for undo in (
            lambda: mark_aluminum(window["id"], 1, AluminumMark(accion="deshacer")),
            lambda: mark_glass(window["id"], GlassMark(accion="deshacer")),
        ):
            with self.assertRaises(HTTPException) as error:
                undo()
            self.assertEqual(error.exception.status_code, 409)
        self.assertTrue(get_order(order_id)["ventanas"][0]["ensamblada"])
        self.assertEqual(mark_assembly(window["id"], AssemblyMark(accion="deshacer")),
                         {"ensamblada": False})
        mark_aluminum(window["id"], 1, AluminumMark(accion="deshacer"))
        mark_glass(window["id"], GlassMark(accion="deshacer"))
        reopened = get_order(order_id)["ventanas"][0]
        self.assertFalse(reopened["ensamblada"])
        self.assertEqual(reopened["avance_aluminio"][0]["pendientes"], 1)
        self.assertEqual(reopened["avance_vidrio"]["pendientes"], 1)

    def test_planless_window_cannot_be_assembled(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO pedidos (id, etiqueta) VALUES (40, 'Z')"
            )
            connection.execute(
                "INSERT INTO ventanas (pedido_id, numero_en_pedido, ancho_16, alto_16) "
                "VALUES (40, 1, 768, 576)"
            )
            window_id = connection.execute("SELECT id FROM ventanas WHERE pedido_id = 40").fetchone()[0]
            connection.commit()
        with self.assertRaises(HTTPException) as error:
            mark_assembly(window_id, AssemblyMark(accion="marcar"))
        self.assertEqual(error.exception.status_code, 409)
        with self.assertRaises(HTTPException) as error:
            mark_assembly(window_id, AssemblyMark(accion="deshacer"))
        self.assertEqual(error.exception.status_code, 409)
        self.assertFalse(get_order(40)["ventanas"][0]["ensamblada"])
        with self.assertRaises(HTTPException) as error:
            mark_assembly(window_id + 100, AssemblyMark(accion="marcar"))
        self.assertEqual(error.exception.status_code, 404)

    def test_existing_windows_gain_pending_assembly_without_losing_measurements(self):
        with tempfile.TemporaryDirectory() as folder:
            old_path = Path(folder) / "previous.sqlite3"
            with closing(sqlite3.connect(old_path)) as connection:
                connection.executescript(
                    "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, etiqueta TEXT);"
                    "CREATE TABLE ventanas (id INTEGER PRIMARY KEY, pedido_id INTEGER NOT NULL, "
                    "numero_en_pedido INTEGER NOT NULL, ancho_16 INTEGER NOT NULL, alto_16 INTEGER NOT NULL);"
                    "INSERT INTO pedidos VALUES (1, 'A');"
                    "INSERT INTO ventanas VALUES (2, 1, 1, 768, 576);"
                )
            with patch.dict(os.environ, AVAO_DB_PATH=str(old_path)):
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                window = get_order(1)["ventanas"][0]
                self.assertEqual((window["id"], window["ancho"], window["alto"], window["ensamblada"]),
                                 (2, "48", "36", False))
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                self.assertFalse(get_order(1)["ventanas"][0]["ensamblada"])


if __name__ == "__main__":
    unittest.main()
