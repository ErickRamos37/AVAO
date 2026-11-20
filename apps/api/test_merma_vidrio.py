"""Cálculo y persistencia de la merma de vidrio."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
from fastapi import HTTPException
from pydantic import ValidationError
from apps.api.merma_vidrio import calcular_merma_vidrio
from apps.api.main import (NewOrder, InventoryUpdate, WasteSelection, WindowDiscard, CostUpdate,
    calculate_order_glass_waste, select_order_glass_waste, calculate_window_cost,
    update_inventory, update_cost, create_order, get_order, list_costs, set_window_discard)


class GlassWasteTests(unittest.TestCase):
    def test_area_threshold_multiples_and_missing_cost(self):
        sheet = (71 * 16, 102 * 16, 1)
        self.assertEqual(calcular_merma_vidrio([sheet], 10000, 80), (0, []))
        self.assertEqual(calcular_merma_vidrio([sheet, sheet], 10000, 80), (0, []))
        self.assertEqual(calcular_merma_vidrio([(56 * 16, 102 * 16, 1)], 10000, 80), (0, []))
        self.assertEqual(calcular_merma_vidrio([(71 * 16, 51 * 16, 1)], 10000, 50)[0], 5000)
        cents, details = calcular_merma_vidrio([(57 * 16, 102 * 16, 1)], 7100, 80)
        self.assertEqual(cents, 1400)
        self.assertEqual(details[0]["sobrante"], "1428")
        self.assertEqual(calcular_merma_vidrio([(57 * 16, 102 * 16, 1)], None, 0), (0, []))
        with self.assertRaises(HTTPException): calcular_merma_vidrio([(57 * 16, 102 * 16, 1)], None, 80)
        with self.assertRaises(HTTPException): calcular_merma_vidrio([None], 10000, 80)
        with self.assertRaises(HTTPException): calcular_merma_vidrio([], 10000, 80)

    def test_recalculation_uses_only_active_windows_and_current_price(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "db.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            update_inventory(InventoryUpdate(umbral_merma_vidrio=1))
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}, {"ancho": "48", "alto": "36"}]))["id"]
            second = get_order(order_id)["ventanas"][1]
            first_snapshot = calculate_order_glass_waste(order_id)["merma_vidrio"]
            update_cost("vidrio_doble_fuerza", CostUpdate(costo="900"))
            set_window_discard(second["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            self.assertEqual(get_order(order_id)["merma_vidrio"], first_snapshot)
            revised = calculate_order_glass_waste(order_id)["merma_vidrio"]
            other_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]
            self.assertEqual(revised, calculate_order_glass_waste(other_id)["merma_vidrio"])
            set_window_discard(second["id"], WindowDiscard(descartada=False))
            self.assertEqual(get_order(order_id)["merma_vidrio"], revised)
            self.assertNotEqual(calculate_order_glass_waste(order_id)["merma_vidrio"]["detalle"], revised["detalle"])

    def test_threshold_snapshot_selection_discard_and_totals(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "db.sqlite3")):
            subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
            self.assertEqual(list_costs()["umbral_merma_vidrio"], 80)
            for value in (-1, 101, None):
                with self.subTest(value=value), self.assertRaises(HTTPException): update_inventory(InventoryUpdate(umbral_merma_vidrio=value))
            for value in (1.5, "80", True):
                with self.subTest(value=value), self.assertRaises(ValidationError): InventoryUpdate(umbral_merma_vidrio=value)
            update_inventory(InventoryUpdate(umbral_merma_vidrio=1))
            self.assertEqual(list_costs()["umbral_merma"], 80)
            order_id = create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}, {"ancho": "48", "alto": "36"}]))["id"]
            first, second = get_order(order_id)["ventanas"]
            base = Decimal(calculate_window_cost(first["id"])["precio"]) + Decimal(calculate_window_cost(second["id"])["precio"])
            calculated = calculate_order_glass_waste(order_id)
            charge = Decimal(calculated["merma_vidrio"]["cargo"])
            self.assertGreater(charge, 0)
            self.assertEqual(Decimal(calculated["total_pedido"]), base + charge)
            select_order_glass_waste(order_id, WasteSelection(incluida=False))
            self.assertEqual(Decimal(get_order(order_id)["total_pedido"]), base)
            update_cost("vidrio_doble_fuerza", CostUpdate(costo="900"))
            set_window_discard(second["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            stored = get_order(order_id)["merma_vidrio"]
            self.assertEqual(stored["detalle"], calculated["merma_vidrio"]["detalle"])
            self.assertFalse(stored["incluida"])
            update_inventory(InventoryUpdate(umbral_merma_vidrio=0))
            result = calculate_order_glass_waste(order_id)["merma_vidrio"]
            self.assertEqual(result, {"cargo":"0.00", "incluida":False, "detalle":[]})
            self.assertEqual(get_order(order_id)["merma_vidrio"], result)
            set_window_discard(first["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
            with self.assertRaises(HTTPException): calculate_order_glass_waste(order_id)
            self.assertEqual(get_order(order_id)["merma_vidrio"], result)

if __name__ == "__main__": unittest.main()
