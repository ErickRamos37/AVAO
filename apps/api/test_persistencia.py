"""Comprueba guardado y reapertura sobre un archivo SQLite real."""

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

from apps.api.main import NewOrder, create_order, get_order, list_orders


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "avao.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run(
            [sys.executable, "-m", "apps.api.init_db"],
            check=True,
            capture_output=True,
            text=True,
        )

    def count(self, table: str) -> int:
        with sqlite3.connect(self.path) as connection:
            return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_list_is_empty_before_first_order(self):
        self.assertEqual(list_orders(), {"pedidos": []})

    def test_lists_several_orders_and_opens_any_of_them(self):
        first = create_order(NewOrder(ventanas=[{"ancho": "24", "alto": "26"}]))["id"]
        second = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"},
            {"ancho": "50 3/4", "alto": "38 1/2"},
        ]))["id"]
        result = subprocess.run(
            [sys.executable, "-c", "import json; from apps.api.main import list_orders; "
             "print(json.dumps(list_orders()))"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), {"pedidos": [
            {"id": first, "etiqueta": "A", "codigos": ["A1"]},
            {"id": second, "etiqueta": "B", "codigos": ["B1", "B2"]},
        ]})
        self.assertEqual(get_order(first)["ventanas"][0]["ancho"], "24")
        self.assertEqual(
            [(window["numero"], window["ancho"]) for window in get_order(second)["ventanas"]],
            [(1, "48"), (2, "50 3/4")],
        )

    def test_reopens_multiple_windows_in_a_new_process(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "24 1/4 1/16", "alto": "26 1/2"},
            {"ancho": "  ", "alto": ""},
            {"ancho": "48", "alto": "36"},
        ]))["id"]
        result = subprocess.run(
            [sys.executable, "-c", "import json; from apps.api.main import get_order; "
             f"print(json.dumps(get_order({order_id})))"],
            check=True,
            capture_output=True,
            text=True,
        )
        opened = json.loads(result.stdout)
        self.assertEqual(opened["etiqueta"], "A")
        self.assertEqual(
            [(window["codigo"], window["ancho"], window["alto"]) for window in opened["ventanas"]],
            [("A1", "24 5/16", "26 1/2"), ("A2", "48", "36")],
        )
        self.assertEqual(opened["ventanas"][1]["plan_aluminio"][6],
                         {"perfil": "Guía", "longitud": "46 1/8", "cantidad": 1})
        self.assertEqual(opened["ventanas"][1]["plan_vidrio"],
                         {"ancho": "22", "alto": "34", "cantidad": 2})
        self.assertEqual(self.count("ventanas"), 2)

    def test_three_reference_plans_have_seventeen_pieces_each(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"},
            {"ancho": "47 1/16", "alto": "35 7/8 1/16"},
            {"ancho": "50 3/4", "alto": "38 1/2"},
        ]))["id"]
        expected = [
            ["36", "35", "34 3/4", "33 1/2", "21 1/2", "23 1/8", "46 1/8", "46 1/8", "22 3/8", "34 3/4"],
            ["35 15/16", "34 15/16", "34 11/16", "33 7/16", "21 1/16", "22 11/16", "45 3/16", "45 3/16", "21 15/16", "34 11/16"],
            ["38 1/2", "37 1/2", "37 1/4", "36", "22 7/8", "24 1/2", "48 7/8", "48 7/8", "23 3/4", "37 1/4"],
        ]
        expected_glass = [
            {"ancho": "22", "alto": "34", "cantidad": 2},
            {"ancho": "21 9/16", "alto": "33 15/16", "cantidad": 2},
            {"ancho": "23 3/8", "alto": "36 1/2", "cantidad": 2},
        ]
        profiles = ["Jamba", "Mulio", "Vertical fijo", "Aleta", "Horizontal fijo",
                    "Horizontal corredizo", "Guía", "Riel", "Screen ancho", "Screen alto"]
        quantities = [2, 1, 2, 2, 2, 2, 1, 1, 2, 2]
        self.assertEqual(sum(quantities), 17)
        for window, lengths, glass in zip(get_order(order_id)["ventanas"], expected, expected_glass, strict=True):
            plan = window["plan_aluminio"]
            self.assertEqual([cut["perfil"] for cut in plan], profiles)
            self.assertEqual([cut["longitud"] for cut in plan], lengths)
            self.assertEqual([cut["cantidad"] for cut in plan], quantities)
            self.assertEqual(window["plan_vidrio"], glass)
        self.assertEqual(self.count("plan_aluminio"), 30)
        self.assertEqual(self.count("plan_vidrio"), 3)

    def test_reopened_order_reads_saved_plan_without_recalculating(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        with (patch("apps.api.main.calcular_plan_aluminio", side_effect=AssertionError("recalculated")),
              patch("apps.api.main.calcular_plan_vidrio", side_effect=AssertionError("recalculated"))):
            self.assertEqual(get_order(order_id)["ventanas"][0]["plan_aluminio"][0],
                             {"perfil": "Jamba", "longitud": "36", "cantidad": 2})
            self.assertEqual(get_order(order_id)["ventanas"][0]["plan_vidrio"],
                             {"ancho": "22", "alto": "34", "cantidad": 2})

    def test_code_sequence_continues_from_z_to_aa(self):
        ids = [create_order(NewOrder(ventanas=[{"ancho": "24", "alto": "26"}]))["id"]
               for _ in range(27)]
        self.assertEqual(get_order(ids[25])["ventanas"][0]["codigo"], "Z1")
        self.assertEqual(get_order(ids[26])["ventanas"][0]["codigo"], "AA1")

    def test_old_orders_survive_schema_update_without_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            old_path = Path(folder) / "previous.sqlite3"
            with sqlite3.connect(old_path) as connection:
                connection.executescript(
                    "CREATE TABLE pedidos (id INTEGER PRIMARY KEY);"
                    "CREATE TABLE ventanas (id INTEGER PRIMARY KEY, pedido_id INTEGER NOT NULL, "
                    "numero_en_pedido INTEGER NOT NULL, ancho_16 INTEGER NOT NULL, alto_16 INTEGER NOT NULL);"
                )
                for number in range(1, 9):
                    connection.execute("INSERT INTO pedidos (id) VALUES (?)", (number,))
                    connection.execute(
                        "INSERT INTO ventanas (pedido_id, numero_en_pedido, ancho_16, alto_16) "
                        "VALUES (?, 1, 384, 416)",
                        (number,),
                    )

            with patch.dict(os.environ, AVAO_DB_PATH=str(old_path)):
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                previous = list_orders()["pedidos"]
                self.assertEqual(len(previous), 8)
                self.assertTrue(all(order["etiqueta"] is None and order["codigos"] == []
                                    for order in previous))
                self.assertEqual(get_order(1)["ventanas"][0]["codigo"], None)
                self.assertEqual(get_order(1)["ventanas"][0]["plan_aluminio"], [])
                self.assertIsNone(get_order(1)["ventanas"][0]["plan_vidrio"])
                new_id = create_order(NewOrder(ventanas=[{"ancho": "24", "alto": "26"}]))["id"]
                self.assertEqual(new_id, 9)
                self.assertEqual(get_order(new_id)["ventanas"][0]["codigo"], "A1")
                subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
                self.assertEqual(len(list_orders()["pedidos"]), 9)

    def test_rejects_partial_or_all_empty_without_creating_order(self):
        for windows in (
            [{"ancho": "24", "alto": ""}],
            [{"ancho": "24", "alto": "26"}, {"ancho": "", "alto": "36"}],
            [{"ancho": " ", "alto": " "}],
            [],
            [{"ancho": "24", "alto": "26"}, {"ancho": "1/32", "alto": "26"}],
            [{"ancho": "5", "alto": "36"}],
            [{"ancho": "48", "alto": "2 1/2"}],
        ):
            with self.subTest(windows=windows), self.assertRaises(HTTPException) as result:
                create_order(NewOrder(ventanas=windows))
            self.assertEqual(result.exception.status_code, 422)
        self.assertEqual(self.count("pedidos"), 0)
        self.assertEqual(self.count("ventanas"), 0)
        self.assertEqual(self.count("plan_aluminio"), 0)
        self.assertEqual(self.count("plan_vidrio"), 0)
        self.assertEqual(create_order(NewOrder(ventanas=[{"ancho": "24", "alto": "26"}]))["id"], 1)
        self.assertEqual(get_order(1)["ventanas"][0]["codigo"], "A1")

    def test_rolls_back_order_if_second_window_cannot_be_saved(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TRIGGER fail_second BEFORE INSERT ON ventanas "
                               "WHEN NEW.numero_en_pedido = 2 BEGIN SELECT RAISE(FAIL, 'test'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            create_order(NewOrder(ventanas=[
                {"ancho": "24", "alto": "26"},
                {"ancho": "48", "alto": "36"},
            ]))
        self.assertEqual(self.count("pedidos"), 0)
        self.assertEqual(self.count("ventanas"), 0)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER fail_second")
        order_id = create_order(NewOrder(ventanas=[{"ancho": "24", "alto": "26"}]))["id"]
        self.assertEqual(get_order(order_id)["ventanas"][0]["codigo"], "A1")

    def test_rolls_back_order_windows_and_plan_if_plan_insert_fails(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TRIGGER fail_second_plan BEFORE INSERT ON plan_aluminio "
                               "WHEN NEW.ventana_id = 2 BEGIN SELECT RAISE(FAIL, 'test'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            create_order(NewOrder(ventanas=[
                {"ancho": "48", "alto": "36"},
                {"ancho": "50 3/4", "alto": "38 1/2"},
            ]))
        for table in ("pedidos", "ventanas", "plan_aluminio", "plan_vidrio"):
            self.assertEqual(self.count(table), 0)

    def test_rolls_back_order_and_aluminum_if_glass_insert_fails(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TRIGGER fail_glass BEFORE INSERT ON plan_vidrio "
                               "BEGIN SELECT RAISE(FAIL, 'test'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))
        for table in ("pedidos", "ventanas", "plan_aluminio", "plan_vidrio"):
            self.assertEqual(self.count(table), 0)


if __name__ == "__main__":
    unittest.main()
