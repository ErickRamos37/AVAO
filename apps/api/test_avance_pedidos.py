"""El avance del taller se deriva de las ventanas activas y sus marcas."""

from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from starlette.routing import Match

from apps.api.main import (
    AluminumMark, AssemblyMark, GlassMark, NewOrder, WindowDiscard,
    app, create_order, get_order, list_order_progress, mark_aluminum, mark_assembly,
    mark_glass, set_window_discard,
)


class OrderProgressTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "orders.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def _finish_window(self, window):
        for cut in window["avance_aluminio"]:
            for _ in range(cut["pendientes"]):
                mark_aluminum(window["id"], cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(window["avance_vidrio"]["pendientes"]):
            mark_glass(window["id"], GlassMark(accion="marcar"))
        mark_assembly(window["id"], AssemblyMark(accion="marcar"))

    def test_http_progress_route_is_not_captured_as_order_id(self):
        scope = {"type": "http", "method": "GET", "path": "/api/pedidos/avance"}
        first_match = next(
            route for route in app.router.routes
            if route.matches(scope)[0] == Match.FULL
        )
        self.assertIs(first_match.endpoint, list_order_progress)

    def test_progress_uses_three_equal_areas_and_keeps_order(self):
        first_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        second_id = create_order(NewOrder(ventanas=[{"ancho": "50", "alto": "38"}]))["id"]
        first_window = get_order(first_id)["ventanas"][0]
        first_cut = first_window["avance_aluminio"][0]
        mark_aluminum(first_window["id"], first_cut["orden"], AluminumMark(accion="marcar"))
        mark_glass(first_window["id"], GlassMark(accion="marcar"))

        first, second = list_order_progress()["pedidos"]
        required_aluminum = sum(piece["cantidad"] for piece in first_window["plan_aluminio"])
        self.assertEqual([first["id"], second["id"]], [first_id, second_id])
        self.assertEqual(first["aluminio"]["hechas"], 1)
        self.assertEqual(first["vidrio"], {"hechas": 1, "requeridas": 2, "porcentaje": 50})
        self.assertEqual(first["ensamble"], {"hechas": 0, "requeridas": 1, "porcentaje": 0})
        self.assertEqual(first["porcentaje"], round((1 / required_aluminum + 1 / 2) / 3 * 100))
        self.assertFalse(first["listo_instalacion"])
        self.assertEqual(second["porcentaje"], 0)

        self._finish_window(get_order(second_id)["ventanas"][0])
        completed = list_order_progress()["pedidos"][1]
        self.assertEqual(completed["porcentaje"], 100)
        self.assertTrue(completed["listo_instalacion"])
        self.assertFalse(list_order_progress()["pedidos"][0]["listo_instalacion"])

    def test_discarded_window_is_excluded_and_zero_active_has_no_progress(self):
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        self._finish_window(first)
        mark_glass(second["id"], GlassMark(accion="marcar"))
        set_window_discard(second["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        summary = list_order_progress()["pedidos"][0]
        self.assertEqual(summary["porcentaje"], 100)
        self.assertEqual(summary["vidrio"], {"hechas": 2, "requeridas": 2, "porcentaje": 100})
        self.assertTrue(summary["listo_instalacion"])

        set_window_discard(first["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        empty = list_order_progress()["pedidos"][0]
        self.assertTrue(empty["sin_ventanas"])
        self.assertIsNone(empty["porcentaje"])
        self.assertFalse(empty["listo_instalacion"])
        self.assertEqual(len(get_order(order_id)["ventanas_descartadas"]), 2)

    def test_missing_plan_never_looks_complete(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("DELETE FROM plan_vidrio WHERE ventana_id = ?", (window_id,))
        summary = list_order_progress()["pedidos"][0]
        self.assertTrue(summary["sin_plan"])
        self.assertIsNone(summary["porcentaje"])
        self.assertIsNone(summary["vidrio"]["porcentaje"])
        self.assertFalse(summary["listo_instalacion"])


if __name__ == "__main__":
    unittest.main()
