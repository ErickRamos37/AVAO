"""Marcas de los dos vidrios de cada ventana en una base temporal."""

from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import GlassMark, NewOrder, create_order, get_order, mark_glass


class GlassMarkTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "cuts.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def test_two_cuts_undo_and_persistence_are_isolated_by_window(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"},
            {"ancho": "48", "alto": "36"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        self.assertEqual(first["plan_vidrio"], {"ancho": "22", "alto": "34", "cantidad": 2})
        self.assertEqual(first["avance_vidrio"], {"cortadas": 0, "pendientes": 2})
        self.assertEqual(mark_glass(first["id"], GlassMark(accion="marcar")),
                         {"requeridas": 2, "cortadas": 1, "pendientes": 1})
        self.assertEqual(mark_glass(first["id"], GlassMark(accion="marcar")),
                         {"requeridas": 2, "cortadas": 2, "pendientes": 0})
        self.assertEqual(mark_glass(first["id"], GlassMark(accion="deshacer")),
                         {"requeridas": 2, "cortadas": 1, "pendientes": 1})

        result = subprocess.run(
            [sys.executable, "-c", "import json; from apps.api.main import get_order; "
             f"print(json.dumps(get_order({order_id})))"],
            check=True, capture_output=True, text=True,
        )
        first, second = json.loads(result.stdout)["ventanas"]
        self.assertEqual(first["codigo"], "A1")
        self.assertEqual(first["avance_vidrio"], {"cortadas": 1, "pendientes": 1})
        self.assertEqual(second["codigo"], "A2")
        self.assertEqual(second["avance_vidrio"], {"cortadas": 0, "pendientes": 2})
        self.assertTrue(all(row["cortadas"] == 0 for row in first["avance_aluminio"]))

    def test_bounds_and_missing_plan_do_not_change_progress(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        for _ in range(2):
            mark_glass(window_id, GlassMark(accion="marcar"))
        for target, action, status in (
            (window_id, "marcar", 409),
            (window_id + 100, "deshacer", 404),
        ):
            with self.assertRaises(HTTPException) as error:
                mark_glass(target, GlassMark(accion=action))
            self.assertEqual(error.exception.status_code, status)
        self.assertEqual(get_order(order_id)["ventanas"][0]["avance_vidrio"]["cortadas"], 2)
        mark_glass(window_id, GlassMark(accion="deshacer"))
        mark_glass(window_id, GlassMark(accion="deshacer"))
        with self.assertRaises(HTTPException) as error:
            mark_glass(window_id, GlassMark(accion="deshacer"))
        self.assertEqual(error.exception.status_code, 409)
        with closing(sqlite3.connect(self.path)) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE plan_vidrio SET cortadas = 3 WHERE ventana_id = ?",
                                   (window_id,))

    def test_existing_glass_plan_gains_zero_progress_without_losing_measurements(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("ALTER TABLE plan_vidrio RENAME TO plan_vidrio_new")
            connection.execute(
                "CREATE TABLE plan_vidrio (ventana_id INTEGER PRIMARY KEY REFERENCES ventanas(id), "
                "ancho_16 INTEGER NOT NULL, alto_16 INTEGER NOT NULL, cantidad INTEGER NOT NULL)"
            )
            connection.execute(
                "INSERT INTO plan_vidrio (ventana_id, ancho_16, alto_16, cantidad) "
                "SELECT ventana_id, ancho_16, alto_16, cantidad FROM plan_vidrio_new"
            )
            connection.execute("DROP TABLE plan_vidrio_new")
            connection.commit()
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        window = get_order(order_id)["ventanas"][0]
        self.assertEqual(window["id"], window_id)
        self.assertEqual(window["plan_vidrio"], {"ancho": "22", "alto": "34", "cantidad": 2})
        self.assertEqual(window["avance_vidrio"], {"cortadas": 0, "pendientes": 2})
        mark_glass(window_id, GlassMark(accion="marcar"))
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.assertEqual(get_order(order_id)["ventanas"][0]["avance_vidrio"],
                         {"cortadas": 1, "pendientes": 1})


if __name__ == "__main__":
    unittest.main()
