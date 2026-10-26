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

from apps.api.main import NewOrder, create_order


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
        self.assertEqual(
            [(window["numero"], window["ancho"], window["alto"]) for window in opened["ventanas"]],
            [(1, "24 5/16", "26 1/2"), (2, "48", "36")],
        )
        self.assertEqual(self.count("ventanas"), 2)

    def test_rejects_partial_or_all_empty_without_creating_order(self):
        for windows in (
            [{"ancho": "24", "alto": ""}],
            [{"ancho": "24", "alto": "26"}, {"ancho": "", "alto": "36"}],
            [{"ancho": " ", "alto": " "}],
            [],
            [{"ancho": "24", "alto": "26"}, {"ancho": "1/32", "alto": "26"}],
        ):
            with self.subTest(windows=windows), self.assertRaises(HTTPException) as result:
                create_order(NewOrder(ventanas=windows))
            self.assertEqual(result.exception.status_code, 422)
        self.assertEqual(self.count("pedidos"), 0)
        self.assertEqual(self.count("ventanas"), 0)

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


if __name__ == "__main__":
    unittest.main()
