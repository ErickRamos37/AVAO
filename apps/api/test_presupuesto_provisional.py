"""Captura provisional sin escritura y guardado atómico del presupuesto."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.main import (BudgetPreview, BudgetSave, OrderClient, NewOrder, MovementInput,
    preview_budget, save_budget, create_order, get_order, add_movement, update_inventory,
    InventoryUpdate, calculate_window_cost, calculate_combined_waste, BudgetWithPayment, save_budget_with_payment, list_orders, home_page)


class BudgetPreviewTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder.name) / 'db.sqlite3'))
        env.start(); self.addCleanup(env.stop)
        subprocess.run([sys.executable, '-m', 'apps.api.init_db'], check=True, capture_output=True)
        self.data = {'ventanas': [{'ancho': '48', 'alto': '36'}], 'incluir_merma': True}
        self.client = {'nombre': 'Ana', 'apellido_1': 'Perez', 'celular': '1234567890'}

    def count(self, table):
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            return db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]

    def test_preview_is_pure_and_save_persists_complete_snapshot(self):
        preview = preview_budget(BudgetPreview(**self.data))
        self.assertEqual([self.count(t) for t in ('pedidos', 'ventanas', 'eventos_pedido', 'clientes')], [0, 0, 0, 0])
        saved = save_budget(BudgetSave(**self.data, cliente=self.client, version=preview['version']))
        order = get_order(saved['id'])
        self.assertEqual(order['cliente']['nombre'], 'Ana')
        self.assertEqual(order['ventanas'][0]['costo_materiales']['precio'], preview['ventanas'][0]['costo']['precio'])
        self.assertEqual(order['merma']['cargo'], f"{preview['merma']['aluminio'] / 100:.2f}")
        self.assertEqual(order['merma_vidrio']['cargo'], f"{preview['merma']['vidrio'] / 100:.2f}")
        self.assertFalse(order['aceptado']); self.assertEqual(order['movimientos'], [])

    def test_preview_rounds_final_total_and_minimum_advance_to_whole_pesos(self):
        from decimal import ROUND_CEILING
        first = preview_budget(BudgetPreview(ventanas=self.data['ventanas'], traslado='0.49', incluir_merma=False))
        second = preview_budget(BudgetPreview(ventanas=self.data['ventanas'], traslado='0.50', incluir_merma=False))
        window_price = int(first['ventanas'][0]['costo']['precio'])
        self.assertEqual(first['total_estimado_pesos'], window_price)
        self.assertEqual(second['total_estimado_pesos'], window_price + 1)
        total = Decimal(second['total_estimado_pesos'])
        expected_minimum = (total * Decimal(second['anticipo_minimo']) / 100).quantize(Decimal('1'), rounding=ROUND_CEILING)
        self.assertEqual(Decimal(second['anticipo_requerido_pesos']), expected_minimum)

    def test_stale_invalid_client_and_partial_window_do_not_persist(self):
        preview = preview_budget(BudgetPreview(**self.data))
        update_inventory(InventoryUpdate(porcentaje_ganancia=30))
        with self.assertRaises(HTTPException) as error:
            save_budget(BudgetSave(**self.data, cliente=self.client, version=preview['version']))
        self.assertEqual(error.exception.status_code, 409)
        data = {'ventanas': [{'ancho': '48', 'alto': ''}]}
        preview = preview_budget(BudgetPreview(**data))
        with self.assertRaises(HTTPException): save_budget(BudgetSave(**data, cliente=self.client, version=preview['version']))
        preview = preview_budget(BudgetPreview(**self.data))
        with self.assertRaises(HTTPException): save_budget(BudgetSave(**self.data, cliente={**self.client, 'celular': '123'}, version=preview['version']))
        self.assertEqual([self.count(t) for t in ('pedidos', 'ventanas', 'eventos_pedido', 'clientes')], [0, 0, 0, 0])

    def test_failure_rolls_back_all_writes(self):
        preview = preview_budget(BudgetPreview(**self.data))
        with patch('apps.api.main.record_event', side_effect=RuntimeError('fallo')), self.assertRaises(RuntimeError):
            save_budget(BudgetSave(**self.data, cliente=self.client, version=preview['version']))
        self.assertEqual([self.count(t) for t in ('pedidos', 'ventanas', 'eventos_pedido', 'clientes')], [0, 0, 0, 0])

    def test_missing_cost_can_save_but_cannot_receive_payment(self):
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            db.execute("UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo='jamba'")
        preview = preview_budget(BudgetPreview(**self.data))
        self.assertFalse(preview['ventanas'][0]['costo']['completo'])
        order = get_order(save_budget(BudgetSave(**self.data, cliente=self.client, version=preview['version']))['id'])
        self.assertIsNone(order['total_pedido'])
        with self.assertRaises(HTTPException): add_movement(order['id'], MovementInput(tipo='pago', importe='1'))

    def test_missing_selected_waste_is_pending_and_not_zero(self):
        update_inventory(InventoryUpdate(umbral_merma=1))
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            db.execute("UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo='jamba'")
        preview = preview_budget(BudgetPreview(**self.data))
        self.assertIsNone(preview['merma']); self.assertIsNotNone(preview['merma_error'])
        order = get_order(save_budget(BudgetSave(**self.data, cliente=self.client, version=preview['version']))['id'])
        self.assertTrue(order['merma_pendiente']); self.assertIsNone(order['merma'])
        with self.assertRaises(HTTPException): add_movement(order['id'], MovementInput(tipo='pago', importe='1'))
        unselected = {**self.data, 'incluir_merma': False}
        preview = preview_budget(BudgetPreview(**unselected))
        order = get_order(save_budget(BudgetSave(**unselected, cliente=self.client, version=preview['version']))['id'])
        self.assertFalse(order['merma_pendiente'])

    def test_legacy_order_without_client_cannot_receive_payment(self):
        order_id = create_order(NewOrder(ventanas=self.data['ventanas']))['id']
        calculate_window_cost(get_order(order_id)['ventanas'][0]['id'])
        with self.assertRaises(HTTPException): add_movement(order_id, MovementInput(tipo='pago', importe='1'))
        self.assertEqual(get_order(order_id)['movimientos'], [])

    def test_home_opens_dashboard_and_query_views_use_order_screen(self):
        self.assertEqual(Path(home_page().path).name, 'dashboard.html')
        self.assertEqual(Path(home_page('desconocida').path).name, 'dashboard.html')
        for view in ('nuevo', 'pedidos', 'presupuestos', 'historico'):
            with self.subTest(view=view):
                self.assertEqual(Path(home_page(view).path).name, 'index.html')

    def test_budget_list_uses_creation_event_without_inventing_legacy_date(self):
        first = create_order(NewOrder(ventanas=self.data['ventanas']))['id']
        second = create_order(NewOrder(ventanas=self.data['ventanas']))['id']
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            db.execute("DELETE FROM eventos_pedido WHERE pedido_id = ? AND tipo = 'presupuesto_creado'", (second,))
        orders = {item['id']: item for item in list_orders()['pedidos']}
        self.assertIsNotNone(orders[first]['fecha_creacion'])
        self.assertIsNone(orders[second]['fecha_creacion'])

    def test_payment_is_atomic_and_retry_is_idempotent(self):
        preview = preview_budget(BudgetPreview(**self.data))
        data = BudgetWithPayment(**self.data, cliente=self.client, version=preview['version'], importe='1.23', token='intento-1')
        first = save_budget_with_payment(data); again = save_budget_with_payment(data)
        self.assertEqual(first['id'], again['id']); self.assertTrue(again['repetido'])
        order = get_order(first['id'])
        self.assertEqual(len(order['movimientos']), 1); self.assertEqual(order['pagado_neto'], '1.23')
        self.assertFalse(order['aceptado']); self.assertIsNone(order['fecha_programada'])
        self.assertTrue(order['merma']['incluida']); self.assertTrue(order['merma_vidrio']['incluida'])
        with self.assertRaises(HTTPException) as error:
            save_budget_with_payment(data.model_copy(update={'importe': '2.00'}))
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(self.count('pedidos'), 1); self.assertEqual(self.count('movimientos'), 1)

    def test_payment_rollback_missing_cost_and_invalid_amount(self):
        preview = preview_budget(BudgetPreview(**self.data))
        for amount in ('0', '1.001', '-1'):
            with self.subTest(amount=amount), self.assertRaises(HTTPException):
                save_budget_with_payment(BudgetWithPayment(**self.data, cliente=self.client, version=preview['version'], importe=amount, token='invalido'))
        self.assertEqual([self.count(t) for t in ('pedidos', 'clientes', 'movimientos', 'capturas_pago')], [0, 0, 0, 0])
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            db.execute("UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo='jamba'")
        preview = preview_budget(BudgetPreview(**self.data))
        with self.assertRaises(HTTPException):
            save_budget_with_payment(BudgetWithPayment(**self.data, cliente=self.client, version=preview['version'], importe='1', token='faltante'))
        self.assertEqual([self.count(t) for t in ('pedidos', 'clientes', 'movimientos', 'capturas_pago')], [0, 0, 0, 0])

    def test_payment_failure_rolls_back_budget_and_customer(self):
        preview = preview_budget(BudgetPreview(**self.data))
        data = BudgetWithPayment(**self.data, cliente=self.client, version=preview['version'], importe='1.00', token='error-pago')
        with patch('apps.api.main._add_movement', side_effect=RuntimeError('fallo')), self.assertRaises(RuntimeError):
            save_budget_with_payment(data)
        self.assertEqual([self.count(t) for t in ('pedidos', 'clientes', 'ventanas', 'movimientos', 'eventos_pedido', 'capturas_pago')], [0, 0, 0, 0, 0, 0])

    def test_full_payment_and_excluded_waste(self):
        data = {**self.data, 'incluir_merma': False}
        preview = preview_budget(BudgetPreview(**data))
        result = save_budget_with_payment(BudgetWithPayment(**data, cliente=self.client, version=preview['version'], importe='99999.99', token='completo'))
        order = get_order(result['id']); self.assertTrue(order['aceptado']); self.assertIsNone(order['fecha_programada'])
        self.assertFalse(order['merma']['incluida']); self.assertFalse(order['merma_vidrio']['incluida'])

    def test_concurrent_same_intention_registers_one_payment(self):
        from concurrent.futures import ThreadPoolExecutor
        preview = preview_budget(BudgetPreview(**self.data))
        data = BudgetWithPayment(**self.data, cliente=self.client, version=preview['version'], importe='5.00', token='concurrente')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: save_budget_with_payment(data), range(2)))
        self.assertEqual(results[0]['id'], results[1]['id'])
        self.assertEqual(self.count('pedidos'), 1); self.assertEqual(self.count('movimientos'), 1)


if __name__ == '__main__': unittest.main()
