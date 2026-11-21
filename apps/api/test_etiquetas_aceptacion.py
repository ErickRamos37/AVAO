"""Las letras pertenecen a pedidos aceptados, no a presupuestos."""
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from apps.api.test_pagos import PaymentTests
from apps.api.main import (NewOrder, MovementInput, create_order, get_order, list_orders,
    calculate_window_cost, add_movement, void_movement, database_path)


class LabelAcceptanceTests(PaymentTests):
    def price(self, order_id):
        for window in get_order(order_id)['ventanas']:
            calculate_window_cost(window['id'])

    def accept_order(self, order_id):
        return add_movement(order_id, MovementInput(tipo='pago', importe=get_order(order_id)['anticipo_requerido']))

    def test_reasignacion_sin_cambiar_identidades(self):
        first = get_order(self.order_id)
        self.assertIsNone(first['etiqueta'])
        self.assertTrue(all(w['codigo'] is None for w in first['ventanas']))
        second = create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        self.price(self.order_id); self.price(second)
        accepted = self.accept_order(self.order_id)
        self.assertEqual(accepted['etiqueta'], 'A')
        self.assertEqual([w['codigo'] for w in accepted['ventanas']], ['A1', 'A2'])
        void_movement(self.order_id, accepted['movimientos'][0]['id'])
        budget = get_order(self.order_id)
        self.assertFalse(budget['aceptado']); self.assertIsNone(budget['etiqueta'])
        self.assertEqual([w['id'] for w in first['ventanas']], [w['id'] for w in budget['ventanas']])
        self.assertEqual(self.accept_order(second)['etiqueta'], 'A')
        again = self.accept_order(self.order_id)
        self.assertEqual(again['etiqueta'], 'B')
        self.assertEqual([w['codigo'] for w in again['ventanas']], ['B1', 'B2'])
        self.assertEqual(again['id'], self.order_id)

    def test_aceptaciones_simultaneas_letras_distintas(self):
        second = create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        self.price(self.order_id); self.price(second)
        with ThreadPoolExecutor(max_workers=2) as pool:
            orders = list(pool.map(self.accept_order, [self.order_id, second]))
        self.assertEqual({o['etiqueta'] for o in orders}, {'A','B'})

    def test_migracion_limpia_solo_presupuestos_y_es_idempotente(self):
        self.price(self.order_id); self.accept_order(self.order_id)
        second = create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        with sqlite3.connect(database_path()) as db:
            db.execute("UPDATE pedidos SET etiqueta='B' WHERE id=?", (second,))
        for _ in range(2):
            subprocess.run([sys.executable, '-m', 'apps.api.init_db'], check=True, capture_output=True)
        self.assertEqual(get_order(self.order_id)['etiqueta'], 'A')
        self.assertIsNone(get_order(second)['etiqueta'])
        self.assertEqual(len(list_orders()['pedidos']), 2)
