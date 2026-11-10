"""Descarte reversible sin perder medidas ni avance del taller."""

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
    AluminumMark, AssemblyMark, GlassMark, NewOrder, WindowCorrection, WindowDiscard,
    correct_window_measures, create_order, get_order, list_orders, mark_aluminum,
    mark_assembly, mark_glass, set_window_discard,
)


class DiscardWindowTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "orders.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def test_discard_and_restore_preserve_identity_plans_marks_and_assembly(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        for cut in first["avance_aluminio"]:
            for _ in range(cut["pendientes"]):
                mark_aluminum(first["id"], cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(first["avance_vidrio"]["pendientes"]):
            mark_glass(first["id"], GlassMark(accion="marcar"))
        mark_assembly(first["id"], AssemblyMark(accion="marcar"))
        before = get_order(order_id)["ventanas"][0]

        with self.assertRaises(HTTPException) as error:
            set_window_discard(first["id"], WindowDiscard(descartada=True))
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(len(get_order(order_id)["ventanas"]), 2)

        set_window_discard(first["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        discarded_order = get_order(order_id)
        self.assertEqual([item["codigo"] for item in discarded_order["ventanas"]], ["A2"])
        self.assertEqual([item["codigo"] for item in discarded_order["ventanas_descartadas"]], ["A1"])
        self.assertEqual(list_orders()["pedidos"][0]["codigos"], ["A2"])
        self.assertEqual(discarded_order["ventanas_descartadas"][0], {**before, "descartada": True})
        self.assertEqual(discarded_order["ventanas"][0]["id"], second["id"])

        set_window_discard(first["id"], WindowDiscard(descartada=False))
        restored = get_order(order_id)
        self.assertEqual([item["codigo"] for item in restored["ventanas"]], ["A1", "A2"])
        self.assertEqual(restored["ventanas"][0], before)
        self.assertFalse(restored["ventanas_descartadas"])

    def test_last_window_may_be_discarded_and_cannot_be_edited_or_marked(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        set_window_discard(window_id, WindowDiscard(descartada=True, confirmar_descarte=True))
        self.assertEqual(get_order(order_id)["ventanas"], [])
        self.assertEqual(len(get_order(order_id)["ventanas_descartadas"]), 1)

        operations = [
            lambda: mark_aluminum(window_id, 1, AluminumMark(accion="marcar")),
            lambda: mark_glass(window_id, GlassMark(accion="marcar")),
            lambda: mark_assembly(window_id, AssemblyMark(accion="marcar")),
            lambda: correct_window_measures(window_id, WindowCorrection(
                ancho="49", alto="36", confirmar_correccion=True,
            )),
        ]
        for operation in operations:
            with self.assertRaises(HTTPException) as error:
                operation()
            self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(get_order(order_id)["ventanas_descartadas"][0]["ancho"], "48")

    def test_existing_database_gains_discard_column_without_losing_window(self):
        schema = (Path(__file__).resolve().parents[2] / "docs" / "technical" /
                  "HU01-modelo-sqlite.sql").read_text(encoding="utf-8")
        old_schema = schema.replace(
            "    descartada INTEGER NOT NULL DEFAULT 0 CHECK (descartada IN (0, 1)),\n", "",
        )
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("DROP TABLE plan_aluminio")
            connection.execute("DROP TABLE plan_vidrio")
            connection.execute("DROP TABLE ventanas")
            connection.executescript(old_schema)
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.assertEqual(get_order(order_id)["ventanas"][0]["codigo"], "A1")


if __name__ == "__main__":
    unittest.main()
