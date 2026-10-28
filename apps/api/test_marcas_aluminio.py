"""Avance de corte de aluminio en una base SQLite temporal."""

import json
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

from apps.api.main import AluminumMark, NewOrder, create_order, get_order, mark_aluminum


class AluminumMarkTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "cuts.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def test_partial_progress_persists_and_other_windows_and_profiles_stay_unchanged(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"},
            {"ancho": "48", "alto": "36"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        self.assertEqual(first["avance_aluminio"][0], {"orden": 1, "cortadas": 0, "pendientes": 2})
        self.assertEqual(
            mark_aluminum(first["id"], 1, AluminumMark(accion="marcar")),
            {"orden": 1, "requeridas": 2, "cortadas": 1, "pendientes": 1},
        )
        mark_aluminum(first["id"], 7, AluminumMark(accion="marcar"))  # Guía, no riel.
        mark_aluminum(first["id"], 9, AluminumMark(accion="marcar"))  # Screen horizontal.

        result = subprocess.run(
            [sys.executable, "-c", "import json; from apps.api.main import get_order; "
             f"print(json.dumps(get_order({order_id})))"],
            check=True, capture_output=True, text=True,
        )
        first, second = json.loads(result.stdout)["ventanas"]
        self.assertEqual(first["codigo"], "A1")
        self.assertEqual(second["codigo"], "A2")
        self.assertEqual(first["avance_aluminio"][0]["cortadas"], 1)
        self.assertEqual(first["avance_aluminio"][6]["cortadas"], 1)
        self.assertEqual(first["avance_aluminio"][7]["cortadas"], 0)
        self.assertEqual(first["avance_aluminio"][8]["cortadas"], 1)
        self.assertEqual(first["avance_aluminio"][9]["cortadas"], 0)
        self.assertTrue(all(row["cortadas"] == 0 for row in second["avance_aluminio"]))

        mark_aluminum(first["id"], 1, AluminumMark(accion="deshacer"))
        self.assertEqual(get_order(order_id)["ventanas"][0]["avance_aluminio"][0],
                         {"orden": 1, "cortadas": 0, "pendientes": 2})

    def test_limits_and_missing_profile_do_not_change_other_counts(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        for _ in range(2):
            mark_aluminum(window_id, 1, AluminumMark(accion="marcar"))
        for action, number, status in (
            ("marcar", 1, 409),
            ("deshacer", 11, 404),
            ("marcar", 7, 0),
        ):
            if status == 0:
                mark_aluminum(window_id, number, AluminumMark(accion=action))
            else:
                with self.assertRaises(HTTPException) as error:
                    mark_aluminum(window_id, number, AluminumMark(accion=action))
                self.assertEqual(error.exception.status_code, status)
        self.assertEqual(get_order(order_id)["ventanas"][0]["avance_aluminio"][0]["cortadas"], 2)
        mark_aluminum(window_id, 1, AluminumMark(accion="deshacer"))
        mark_aluminum(window_id, 1, AluminumMark(accion="deshacer"))
        with self.assertRaises(HTTPException) as error:
            mark_aluminum(window_id, 1, AluminumMark(accion="deshacer"))
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(get_order(order_id)["ventanas"][0]["avance_aluminio"][0]["cortadas"], 0)
        with closing(sqlite3.connect(self.path)) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE plan_aluminio SET cortadas = 3 WHERE ventana_id = ? AND orden = 1",
                                   (window_id,))

    def test_existing_plan_rows_gain_zero_progress_without_losing_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            old_path = Path(folder) / "previous.sqlite3"
            with closing(sqlite3.connect(old_path)) as connection:
                connection.executescript(
                    "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, etiqueta TEXT);"
                    "CREATE TABLE ventanas (id INTEGER PRIMARY KEY, pedido_id INTEGER NOT NULL, "
                    "numero_en_pedido INTEGER NOT NULL, ancho_16 INTEGER NOT NULL, alto_16 INTEGER NOT NULL);"
                    "CREATE TABLE plan_aluminio (ventana_id INTEGER NOT NULL, orden INTEGER NOT NULL, "
                    "perfil TEXT NOT NULL, longitud_16 INTEGER NOT NULL, cantidad INTEGER NOT NULL, "
                    "PRIMARY KEY (ventana_id, orden));"
                    "INSERT INTO pedidos VALUES (1, 'A');"
                    "INSERT INTO ventanas VALUES (1, 1, 1, 768, 576);"
                    "INSERT INTO plan_aluminio VALUES (1, 1, 'Jamba', 576, 2);"
                )
            with patch.dict(os.environ, AVAO_DB_PATH=str(old_path)):
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                order = get_order(1)
                self.assertEqual(order["ventanas"][0]["plan_aluminio"][0],
                                 {"perfil": "Jamba", "longitud": "36", "cantidad": 2})
                self.assertEqual(order["ventanas"][0]["avance_aluminio"][0],
                                 {"orden": 1, "cortadas": 0, "pendientes": 2})
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                self.assertEqual(get_order(1)["ventanas"][0]["avance_aluminio"][0]["cortadas"], 0)


if __name__ == "__main__":
    unittest.main()
