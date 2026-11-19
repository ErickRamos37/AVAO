"""Pruebas del catálogo de costos de compra de HU-18."""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (CostUpdate, InventoryUpdate, update_inventory, NewOrder, app, costs_page, create_order,
                           calculate_window_cost, get_order, list_costs, update_cost)


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
        self.assertEqual(costs["jamba"]["costo_derivado"], "20.38")
        self.assertEqual(costs["jamba"]["unidad_derivada"], "$ / pie lineal")
        self.assertEqual(costs["moldura_screen"]["costo_derivado"], "9.58")
        self.assertEqual(costs["vidrio_doble_fuerza"]["unidad_derivada"], "$ / pie cuadrado")
        self.assertEqual(costs["guias_plasticas"]["nombre"], "Guías plásticas")
        self.assertEqual(costs["chilillos"]["nombre"], "Chilillos")
        self.assertEqual(costs["tela_mosquitera"]["costo_compra"], "3.00")
        self.assertEqual(costs["vinil_doble_fuerza"]["costo_compra"], "1.20")

    def test_update_persists_and_reinitialization_does_not_replace_user_value(self):
        updated = update_cost("jamba", CostUpdate(costo="500.25"))
        self.assertEqual(updated["costo_compra"], "500.25")
        self.migrate()
        jamba = next(item for item in list_costs()["insumos"] if item["codigo"] == "jamba")
        self.assertEqual(jamba["costo_compra"], "500.25")
        self.assertEqual(jamba["costo_derivado"], "23.82")

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

    def test_window_material_cost_is_available_from_order_and_stays_saved_until_recalculation(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        update_cost("tela_mosquitera", CostUpdate(costo="15.00"))
        update_cost("vinil_doble_fuerza", CostUpdate(costo="1.50"))

        first = calculate_window_cost(window_id)
        self.assertTrue(first["completo"])
        self.assertTrue(first["vigente"])
        self.assertEqual(len(first["items"]), 22)
        self.assertEqual(
            Decimal(first["costo_base"]),
            sum((Decimal(item["costo"]) for item in first["items"]), Decimal(0)),
        )
        saved_first = get_order(order_id)["ventanas"][0]["costo_materiales"]
        self.assertEqual(saved_first["costo_base"], first["costo_base"])

        update_cost("jamba", CostUpdate(costo="500.00"))
        self.assertEqual(
            get_order(order_id)["ventanas"][0]["costo_materiales"]["costo_base"],
            first["costo_base"],
        )
        second = calculate_window_cost(window_id)
        self.assertNotEqual(second["costo_base"], first["costo_base"])

    def test_measure_correction_marks_saved_material_cost_as_stale(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window = get_order(order_id)["ventanas"][0]
        update_cost("tela_mosquitera", CostUpdate(costo="15.00"))
        update_cost("vinil_doble_fuerza", CostUpdate(costo="1.50"))
        calculate_window_cost(window["id"])

        from apps.api.main import OrderWindowCorrection, WindowMeasureUpdate, correct_order_window_measures
        correct_order_window_measures(order_id, OrderWindowCorrection(
            ventanas=[WindowMeasureUpdate(id=window["id"], ancho="49", alto="36")],
            confirmar_correccion=True,
        ))

        saved_cost = get_order(order_id)["ventanas"][0]["costo_materiales"]
        self.assertFalse(saved_cost["vigente"])
        self.assertIn("costo_base", saved_cost)

    def test_cost_calculation_reports_missing_rates_without_amounts(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo = ?",
                ("tela_mosquitera",),
            )
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        result = calculate_window_cost(window_id)

        self.assertFalse(result["completo"])
        self.assertIn("Tela mosquitera", result["faltantes"])
        self.assertNotIn("costo_base", result)
        self.assertIsNone(get_order(order_id)["ventanas"][0]["costo_materiales"])

    def test_inventory_batch_is_atomic_and_percentage_persists(self):
        self.assertEqual(list_costs()["porcentaje_ganancia"], 25)
        with self.assertRaises(HTTPException):
            update_inventory(InventoryUpdate(costos={"jamba": "999", "aleta": "-1"}, porcentaje_ganancia=40))
        self.assertEqual(list_costs()["insumos"][0]["costo_compra"], "428.00")
        self.assertEqual(list_costs()["porcentaje_ganancia"], 25)
        for value in (0, 101):
            with self.subTest(value=value), self.assertRaises(HTTPException):
                update_inventory(InventoryUpdate(porcentaje_ganancia=value))
        from pydantic import ValidationError
        for value in (1.5, "25", True):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                InventoryUpdate(porcentaje_ganancia=value)
        update_inventory(InventoryUpdate(costos={"jamba": "999.00", "aleta": "500.00"}, porcentaje_ganancia=100))
        self.migrate()
        self.assertEqual(list_costs()["porcentaje_ganancia"], 100)
        self.assertEqual(list_costs()["insumos"][0]["costo_compra"], "999.00")
        update_inventory(InventoryUpdate(porcentaje_ganancia=1))
        self.assertEqual(list_costs()["porcentaje_ganancia"], 1)

    def test_profit_is_saved_and_changes_only_after_recalculation(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
        window_id = get_order(order_id)["ventanas"][0]["id"]
        first = calculate_window_cost(window_id)
        base = Decimal(first["costo_base"])
        from decimal import ROUND_HALF_UP
        self.assertEqual(first["porcentaje_ganancia"], 25)
        self.assertEqual(Decimal(first["ganancia"]), (base * Decimal("0.25")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        self.assertEqual(Decimal(first["precio"]), (base * Decimal("1.25")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        update_inventory(InventoryUpdate(porcentaje_ganancia=50))
        self.assertEqual(get_order(order_id)["ventanas"][0]["costo_materiales"]["precio"], first["precio"])
        second = calculate_window_cost(window_id)
        self.assertEqual(second["porcentaje_ganancia"], 50)
        self.assertEqual(second["costo_base"], first["costo_base"])
        self.assertNotEqual(second["precio"], first["precio"])

    def test_order_total_tracks_active_saved_prices_and_stale_plans(self):
        from apps.api.main import (WindowDiscard, set_window_discard, WindowCorrection,
                                   correct_window_measures)
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total, {"importe": None, "sin_precio": True, "desactualizado": False})
        first_price = int(calculate_window_cost(first["id"])["precio"])
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total["importe"], first_price)
        self.assertTrue(total["sin_precio"])
        second_price = int(calculate_window_cost(second["id"])["precio"])
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total["importe"], first_price + second_price)
        self.assertFalse(total["sin_precio"])
        update_inventory(InventoryUpdate(porcentaje_ganancia=50, costos={"jamba": "600"}))
        self.assertEqual(get_order(order_id)["total_ventanas"], total)
        correct_window_measures(first["id"], WindowCorrection(ancho="49", alto="36", confirmar_correccion=True))
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total["importe"], first_price + second_price)
        self.assertTrue(total["desactualizado"])
        set_window_discard(first["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total["importe"], second_price)
        self.assertFalse(total["desactualizado"])
        set_window_discard(first["id"], WindowDiscard(descartada=False))
        self.assertEqual(get_order(order_id)["total_ventanas"]["importe"], first_price + second_price)
        for window in (first, second):
            set_window_discard(window["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        self.assertIsNone(get_order(order_id)["total_ventanas"]["importe"])

    def test_legacy_cost_without_price_is_excluded_from_partial_total(self):
        import json
        order_id = create_order(NewOrder(ventanas=[
            {"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"},
        ]))["id"]
        first, second = get_order(order_id)["ventanas"]
        price = int(calculate_window_cost(first["id"])["precio"])
        calculate_window_cost(second["id"])
        with sqlite3.connect(self.path) as connection:
            raw = connection.execute("SELECT resultado_json FROM costos_ventana WHERE ventana_id = ?", (second["id"],)).fetchone()[0]
            snapshot = json.loads(raw)
            del snapshot["precio"]
            connection.execute("UPDATE costos_ventana SET resultado_json = ? WHERE ventana_id = ?", (json.dumps(snapshot), second["id"]))
        total = get_order(order_id)["total_ventanas"]
        self.assertEqual(total["importe"], price)
        self.assertTrue(total["sin_precio"])

    def test_cost_page_and_api_routes_are_registered(self):
        page = costs_page()
        self.assertTrue(Path(page.path).is_file())
        self.assertIn("Costos de compra", Path(page.path).read_text(encoding="utf-8"))
        routes = {(route.path, method) for route in app.routes
                  for method in getattr(route, "methods", set())}
        self.assertIn(("/costos", "GET"), routes)
        self.assertIn(("/api/costos-insumos", "GET"), routes)
        self.assertIn(("/api/costos-insumos/{codigo}", "PUT"), routes)
        self.assertIn(("/api/ventanas/{window_id}/costo-materiales", "POST"), routes)


if __name__ == "__main__":
    unittest.main()
