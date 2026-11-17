"""Pruebas del catálogo de costos de compra de HU-18."""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (CostUpdate, NewOrder, app, costs_page, create_order,
                           get_order, list_costs, update_cost)


class CostCatalogTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "avao.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        self.migrate()

    def migrate(self):
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True,
                       capture_output=True, text=True)

    def test_catalog_has_confirmed_costs_and_pending_values_without_zero_substitution(self):
        costs = {item["codigo"]: item for item in list_costs()["insumos"]}
        self.assertEqual(costs["jamba"]["costo_compra"], "428.00")
        self.assertEqual(costs["jamba"]["costo_derivado"], "20.380952")
        self.assertEqual(costs["jamba"]["unidad_derivada"], "$ / pie lineal")
        self.assertEqual(costs["moldura_screen"]["costo_derivado"], "9.583333")
        self.assertEqual(costs["vidrio_doble_fuerza"]["unidad_derivada"], "$ / pie cuadrado")
        self.assertIsNone(costs["tela_mosquitera"]["costo_compra"])
        self.assertIsNone(costs["vinil_doble_fuerza"]["costo_compra"])

    def test_update_persists_and_reinitialization_does_not_replace_user_value(self):
        updated = update_cost("jamba", CostUpdate(costo="500.25"))
        self.assertEqual(updated["costo_compra"], "500.25")
        self.migrate()
        jamba = next(item for item in list_costs()["insumos"] if item["codigo"] == "jamba")
        self.assertEqual(jamba["costo_compra"], "500.25")
        self.assertEqual(jamba["costo_derivado"], "23.821429")

    def test_pending_cost_can_be_entered_and_unknown_cost_code_is_rejected(self):
        update_cost("tela_mosquitera", CostUpdate(costo="12.34"))
        tela = next(item for item in list_costs()["insumos"] if item["codigo"] == "tela_mosquitera")
        self.assertEqual(tela["costo_compra"], "12.34")
        with self.assertRaises(HTTPException) as raised:
            update_cost("accesorio_no_definido", CostUpdate(costo="1.00"))
        self.assertEqual(raised.exception.status_code, 404)

    def test_rejects_negative_invalid_and_more_than_two_decimal_costs(self):
        for value in ("-0.01", "abc", "1.005", "NaN", "Infinity"):
            with self.subTest(value=value), self.assertRaises(HTTPException) as raised:
                update_cost("jamba", CostUpdate(costo=value))
            self.assertEqual(raised.exception.status_code, 422)
        self.assertEqual(
            next(item for item in list_costs()["insumos"] if item["codigo"] == "jamba")["costo_compra"],
            "428.00",
        )

    def test_cost_update_does_not_change_saved_order_plan_or_progress(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        before = get_order(order_id)["ventanas"]
        update_cost("jamba", CostUpdate(costo="600.00"))
        self.assertEqual(get_order(order_id)["ventanas"], before)
        with sqlite3.connect(self.path) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM costos_insumos").fetchone()[0], 22)

    def test_cost_page_and_api_routes_are_registered(self):
        page = costs_page()
        self.assertTrue(Path(page.path).is_file())
        self.assertIn("Costos de compra", Path(page.path).read_text(encoding="utf-8"))
        routes = {(route.path, method) for route in app.routes
                  for method in getattr(route, "methods", set())}
        self.assertIn(("/costos", "GET"), routes)
        self.assertIn(("/api/costos-insumos", "GET"), routes)
        self.assertIn(("/api/costos-insumos/{codigo}", "PUT"), routes)


if __name__ == "__main__":
    unittest.main()
