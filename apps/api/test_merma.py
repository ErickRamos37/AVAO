"""Reglas de merma y conservación del cargo explícitamente calculado."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.costos_insumos import INSUMOS
from apps.api.costos_ventana import PERFILES
from apps.api.merma import calcular_merma
from apps.api.main import (NewOrder, InventoryUpdate, WasteSelection, WindowDiscard,
    calculate_order_waste, create_order, get_order, update_inventory, select_order_waste, set_window_discard)


def rounded_pesos(value):
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def plan(length, profile="Jamba"):
    return [{"perfil": name, "longitud_16": length if name == profile else 0, "cantidad": 1} for name in PERFILES]


class WasteTests(unittest.TestCase):
    def test_last_segment_examples_and_zero_threshold(self):
        costs = {item[0]: item[6] for item in INSUMOS}
        costs["jamba"] = 2100
        for feet, cents in [(18, 300), (30, 0), (39, 300), (42, 0)]:
            with self.subTest(feet=feet):
                self.assertEqual(calcular_merma([plan(feet * 192)], costs, 80), cents)
        self.assertEqual(calcular_merma([plan(18 * 192)], costs, 0), 0)
        costs["moldura_screen"] = 1200
        self.assertEqual(calcular_merma([plan(10 * 192, "Screen ancho")], costs, 80), 200)
        self.assertEqual(calcular_merma([plan(9 * 192), plan(9 * 192)], costs, 80), 300)

    def test_detail_contains_only_charged_profiles_and_keeps_original_formula(self):
        costs = {item[0]: item[6] for item in INSUMOS}
        costs["jamba"] = 2100
        cents, details = calcular_merma([plan(18 * 192)], costs, 80, incluir_detalle=True)
        self.assertEqual(cents, 300)
        self.assertEqual(details, [{"perfil": "Jamba de aluminio", "consumo": "216", "tramo_pies": 21,
                                    "sobrante": "36", "importe": "3.0000"}])
        self.assertEqual(calcular_merma([plan(18 * 192)], costs, 0, incluir_detalle=True), (0, []))

    def test_old_snapshot_migration_does_not_invent_details(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "data.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
            with sqlite3.connect(os.environ["AVAO_DB_PATH"]) as connection:
                connection.execute("DROP TABLE merma_pedido")
                connection.execute("CREATE TABLE merma_pedido (pedido_id INTEGER PRIMARY KEY, cargo_centavos INTEGER NOT NULL, incluida INTEGER NOT NULL)")
                connection.execute("INSERT INTO merma_pedido VALUES (?, 1234, 0)", (order_id,))
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            self.assertEqual(get_order(order_id)["merma"], {"cargo": "12.34", "incluida": False, "detalle": None})

    def test_missing_required_rate_and_incomplete_plan_fail_without_partial_charge(self):
        costs = {item[0]: item[6] for item in INSUMOS}
        costs["jamba"] = None
        with self.assertRaises(HTTPException):
            calcular_merma([plan(18 * 192)], costs, 80)
        with self.assertRaises(HTTPException):
            calcular_merma([plan(18 * 192)[:-1]], costs, 80)

    def test_threshold_validation_and_total_includes_only_selected_waste(self):
        from decimal import Decimal
        from pydantic import ValidationError
        from apps.api.main import calculate_window_cost, list_costs
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "data.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            self.assertEqual(list_costs()["umbral_merma"], 80)
            for value in (-1, 101, None):
                with self.subTest(value=value), self.assertRaises(HTTPException):
                    update_inventory(InventoryUpdate(umbral_merma=value))
            for value in (2.5, "80", True):
                with self.subTest(value=value), self.assertRaises(ValidationError):
                    InventoryUpdate(umbral_merma=value)
            update_inventory(InventoryUpdate(umbral_merma=100))
            self.assertEqual(list_costs()["umbral_merma"], 100)
            update_inventory(InventoryUpdate(umbral_merma=1))
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
            window_id = get_order(order_id)["ventanas"][0]["id"]
            window_price = Decimal(calculate_window_cost(window_id)["precio"])
            result = calculate_order_waste(order_id)
            charge = Decimal(result["merma"]["cargo"])
            self.assertGreater(charge, 0)
            self.assertEqual(Decimal(result["total_pedido"]), rounded_pesos(window_price + charge))
            result = select_order_waste(order_id, WasteSelection(incluida=False))
            self.assertEqual(Decimal(result["total_pedido"]), window_price)
            result = select_order_waste(order_id, WasteSelection(incluida=True))
            self.assertEqual(Decimal(result["total_pedido"]), rounded_pesos(window_price + charge))

    def test_recalculation_uses_only_active_windows_and_current_costs(self):
        from apps.api.main import CostUpdate, update_cost
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "data.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}, {"ancho": "48", "alto": "36"}]))["id"]
            first, second = get_order(order_id)["ventanas"]
            update_inventory(InventoryUpdate(umbral_merma=1))
            original = calculate_order_waste(order_id)["merma"]
            update_cost("jamba", CostUpdate(costo="999.00"))
            self.assertEqual(get_order(order_id)["merma"], original)
            set_window_discard(second["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            recalculated = get_order(order_id)["merma"]
            self.assertNotEqual(recalculated["cargo"], original["cargo"])
            self.assertEqual(calculate_order_waste(order_id)["merma"], recalculated)
            one_order = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
            self.assertEqual(calculate_order_waste(one_order)["merma"], recalculated)
            set_window_discard(second["id"], WindowDiscard(descartada=False))
            restored = get_order(order_id)["merma"]
            self.assertNotEqual(restored["cargo"], recalculated["cargo"])
            self.assertEqual(calculate_order_waste(order_id)["merma"], restored)

    def test_snapshot_and_selection_persist_through_changes_and_recalculation(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "data.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"}]))["id"]
            windows = get_order(order_id)["ventanas"]
            first = calculate_order_waste(order_id)["merma"]
            self.assertTrue(first["incluida"])
            select_order_waste(order_id, WasteSelection(incluida=False))
            update_inventory(InventoryUpdate(umbral_merma=0))
            set_window_discard(windows[0]["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            stored = get_order(order_id)["merma"]
            self.assertEqual(stored["cargo"], "0.00")
            self.assertEqual(stored["detalle"], [])
            self.assertFalse(stored["incluida"])
            second = calculate_order_waste(order_id)["merma"]
            self.assertEqual(second, {"cargo": "0.00", "incluida": False, "detalle": []})
            self.assertEqual(get_order(order_id)["merma"], second)
            set_window_discard(windows[1]["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            with self.assertRaises(HTTPException):
                calculate_order_waste(order_id)
            self.assertEqual(get_order(order_id)["merma"], second)

if __name__ == "__main__":
    unittest.main()
