"""Registro transaccional de hitos comerciales."""
from datetime import datetime
import sqlite3
import os
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.test_pagos import PaymentTests
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (get_order, calculate_window_cost, update_delivery, DeliveryUpdate,
                           void_movement, set_installation, InstallationUpdate, add_movement, MovementInput,
                           calculate_order_waste, select_order_waste, WasteSelection,
                           set_window_discard, WindowDiscard, update_inventory, InventoryUpdate)


class EventPaymentsTests(PaymentTests):
    def test_transitions_reading_and_rollback(self):
        for window in self.windows:
            calculate_window_cost(window['id'])
        total = get_order(self.order_id)['total_pedido']
        paid = self.move('pago', total)
        kinds = lambda: [e['tipo'] for e in get_order(self.order_id)['eventos']]
        self.assertEqual(kinds(), ['presupuesto_creado', 'aceptado', 'liquidado'])
        self.assertIsNotNone(datetime.fromisoformat(paid['eventos'][0]['fecha_hora']).utcoffset())
        update_delivery(self.order_id, DeliveryUpdate(importe='1'))
        update_delivery(self.order_id, DeliveryUpdate(importe=None))
        self.assertEqual(kinds()[-2:], ['liquidacion_perdida', 'liquidado'])
        before = kinds()
        with patch('apps.api.main.record_event', side_effect=RuntimeError('error')):
            with self.assertRaises(RuntimeError):
                update_delivery(self.order_id, DeliveryUpdate(importe='1'))
        self.assertEqual(kinds(), before)
        self.assertIsNone(get_order(self.order_id)['traslado'])
        void_movement(self.order_id, paid['movimientos'][0]['id'])
        self.assertEqual(kinds()[-2:], ['aceptacion_revocada', 'liquidacion_perdida'])
        self.move('pago', total)
        self.assertEqual(kinds()[-2:], ['aceptado', 'liquidado'])
        self.assertEqual(kinds(), kinds())

    def test_merma_precio_y_descarte_cambian_liquidacion(self):
        for window in self.windows:
            calculate_window_cost(window['id'])
        self.move('pago', get_order(self.order_id)['total_pedido'])
        calculate_order_waste(self.order_id)
        with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db:
            db.execute('UPDATE merma_pedido SET cargo_centavos = 100, incluida = 0 WHERE pedido_id = ?', (self.order_id,))
        select_order_waste(self.order_id, WasteSelection(incluida=True))
        self.assertEqual(get_order(self.order_id)['eventos'][-1]['tipo'], 'liquidacion_perdida')
        select_order_waste(self.order_id, WasteSelection(incluida=False))
        self.assertEqual(get_order(self.order_id)['eventos'][-1]['tipo'], 'liquidado')
        update_inventory(InventoryUpdate(porcentaje_ganancia=100))
        calculate_window_cost(self.windows[0]['id'])
        self.assertEqual(get_order(self.order_id)['eventos'][-1]['tipo'], 'liquidacion_perdida')
        set_window_discard(self.windows[0]['id'], WindowDiscard(descartada=True, confirmar_descarte=True))
        self.assertEqual(get_order(self.order_id)['eventos'][-1]['tipo'], 'liquidado')
        set_window_discard(self.windows[0]['id'], WindowDiscard(descartada=False))
        self.assertEqual(get_order(self.order_id)['eventos'][-1]['tipo'], 'liquidacion_perdida')


class EventInstallationTests(InstallationTests):
    def test_install_undo_close_and_preserve(self):
        self.accept(); self.finish()
        set_installation(self.order_id, InstallationUpdate(instalado=True))
        set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True))
        installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
        kinds = [e['tipo'] for e in closed['eventos']]
        self.assertEqual(kinds[-5:], ['instalado', 'instalacion_desmarcada', 'instalado', 'liquidado', 'cierre'])
        self.assertEqual(get_order(self.order_id)['eventos'], closed['eventos'])
        with self.assertRaises(HTTPException):
            set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True))
        self.assertEqual(get_order(self.order_id)['eventos'], closed['eventos'])
