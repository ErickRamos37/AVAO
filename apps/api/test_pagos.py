"""Pagos, aceptación y protección de presupuestos."""
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.main import (NewOrder, MovementInput, InventoryUpdate, AluminumMark, GlassMark, AssemblyMark,
    create_order, get_order, calculate_window_cost, add_movement, void_movement, update_inventory,
    list_costs, list_order_progress, mark_aluminum, mark_glass, mark_assembly, DeliveryUpdate, update_delivery)


class PaymentTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder.name) / "db.sqlite3")); env.start(); self.addCleanup(env.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.order_id = create_order(NewOrder(ventanas=[{"ancho":"48", "alto":"36"}, {"ancho":"50", "alto":"38"}]))["id"]
        self.windows = get_order(self.order_id)["ventanas"]

    def move(self, kind, amount):
        return add_movement(self.order_id, MovementInput(tipo=kind, importe=str(amount)))

    def test_budget_blocks_manufacture_and_payments_with_partial_price(self):
        self.assertEqual(list_order_progress()["pedidos"], [])
        for operation in (lambda: mark_aluminum(self.windows[0]["id"], 1, AluminumMark(accion="marcar")),
                          lambda: mark_glass(self.windows[0]["id"], GlassMark(accion="marcar")),
                          lambda: mark_assembly(self.windows[0]["id"], AssemblyMark(accion="marcar"))):
            with self.assertRaises(HTTPException): operation()
        with self.assertRaises(HTTPException): self.move("pago", "1")
        calculate_window_cost(self.windows[0]["id"])
        with self.assertRaises(HTTPException): self.move("pago", "1")
        self.assertEqual(get_order(self.order_id)["movimientos"], [])

    def test_acceptance_payments_excess_refunds_and_void(self):
        for window in self.windows: calculate_window_cost(window["id"])
        total = Decimal(get_order(self.order_id)["total_pedido"])
        self.assertEqual(Decimal(get_order(self.order_id)["anticipo_requerido"]), (total * Decimal("0.50")).quantize(Decimal("0.01")))
        half = (total / 2).quantize(Decimal("0.01"))
        first = self.move("pago", half - Decimal("0.01"))
        self.assertFalse(first["aceptado"])
        second = self.move("pago", "0.01")
        self.assertTrue(second["aceptado"])
        self.assertEqual(len(list_order_progress()["pedidos"]), 1)
        mark_glass(self.windows[0]["id"], GlassMark(accion="marcar"))
        before = get_order(self.order_id)
        update_delivery(self.order_id, DeliveryUpdate(importe="100.00"))
        self.assertTrue(get_order(self.order_id)["aceptado"])
        self.assertEqual(Decimal(get_order(self.order_id)["saldo"]), Decimal(before["saldo"]) + 100)
        paid = self.move("pago", total + 200)
        excess = Decimal(paid["excedente"])
        self.assertGreater(excess, 0)
        with self.assertRaises(HTTPException): self.move("devolucion", excess + 1)
        refunded = self.move("devolucion", excess)
        self.assertEqual(refunded["excedente"], "0.00")
        self.assertTrue(refunded["liquidado"])
        payment_id = paid["movimientos"][-1]["id"]
        after = void_movement(self.order_id, payment_id)
        self.assertFalse(after["aceptado"])
        annulled = next(m for m in after["movimientos"] if m["id"] == payment_id)
        self.assertTrue(annulled["anulado"])
        self.assertEqual(annulled["fecha"], datetime.now(ZoneInfo("America/Tijuana")).date().isoformat())
        self.assertEqual(annulled["fecha_anulacion"], datetime.now(ZoneInfo("America/Tijuana")).date().isoformat())
        self.assertEqual(list_order_progress()["pedidos"], [])
        with self.assertRaises(HTTPException): mark_glass(self.windows[0]["id"], GlassMark(accion="marcar"))
        with self.assertRaises(HTTPException): mark_glass(self.windows[0]["id"], GlassMark(accion="deshacer"))
        self.assertEqual(get_order(self.order_id)["ventanas"][0]["avance_vidrio"]["cortadas"], 1)

    def test_partial_total_prevents_void_without_changing_history(self):
        for window in self.windows: calculate_window_cost(window["id"])
        saved = self.move("pago", "1")
        move_id = saved["movimientos"][0]["id"]
        from apps.api.main import WindowCorrection, correct_window_measures
        # Historical cost remains present after a correction; remove its price to emulate a legacy snapshot.
        import sqlite3, json
        with sqlite3.connect(os.environ["AVAO_DB_PATH"]) as connection:
            raw = connection.execute("SELECT resultado_json FROM costos_ventana WHERE ventana_id=?", (self.windows[1]["id"],)).fetchone()[0]
            data = json.loads(raw); del data["precio"]
            connection.execute("UPDATE costos_ventana SET resultado_json=? WHERE ventana_id=?", (json.dumps(data), self.windows[1]["id"]))
        with self.assertRaises(HTTPException): void_movement(self.order_id, move_id)
        self.assertFalse(get_order(self.order_id)["movimientos"][0]["anulado"])

    def test_server_date_ignores_caller_date_and_required_advance_rounds_up(self):
        for window in self.windows: calculate_window_cost(window["id"])
        update_delivery(self.order_id, DeliveryUpdate(importe="0.01"))
        order = get_order(self.order_id)
        total = Decimal(order["total_pedido"])
        from decimal import ROUND_CEILING
        self.assertEqual(Decimal(order["anticipo_requerido"]), (total / 2).quantize(Decimal("0.01"), rounding=ROUND_CEILING))
        movement = MovementInput(tipo="pago", importe="1", fecha="1900-01-01")
        saved = add_movement(self.order_id, movement)["movimientos"][0]
        self.assertEqual(saved["fecha"], datetime.now(ZoneInfo("America/Tijuana")).date().isoformat())
        self.assertIsNone(saved["fecha_anulacion"])

    def test_old_movements_gain_void_date_without_losing_rows(self):
        import sqlite3
        with sqlite3.connect(os.environ["AVAO_DB_PATH"]) as db:
            db.execute("DROP TABLE movimientos")
            db.execute("CREATE TABLE movimientos (id INTEGER PRIMARY KEY, pedido_id INTEGER, tipo TEXT, importe_centavos INTEGER, fecha TEXT, anulado INTEGER)")
            db.execute("INSERT INTO movimientos VALUES (1, ?, 'pago', 100, '2026-01-01', 1)", (self.order_id,))
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        saved = get_order(self.order_id)["movimientos"][0]
        self.assertEqual(saved["fecha"], "2026-01-01")
        self.assertTrue(saved["anulado"])
        self.assertIsNone(saved["fecha_anulacion"])

    def test_minimum_configuration(self):
        self.assertEqual(list_costs()["anticipo_minimo"], 50)
        for invalid in (0,101,None):
            with self.assertRaises(HTTPException): update_inventory(InventoryUpdate(anticipo_minimo=invalid))
        update_inventory(InventoryUpdate(anticipo_minimo=100))
        self.assertEqual(list_costs()["anticipo_minimo"],100)

if __name__ == "__main__": unittest.main()
