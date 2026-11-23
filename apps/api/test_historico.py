"""Cierre definitivo, conservación e integridad del histórico."""
import sqlite3
import json
from fastapi import HTTPException
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (MovementInput, InstallationUpdate, DeliveryUpdate, OrderClient,
    WasteSelection, add_movement, set_installation, get_order, list_orders, list_history,
    create_order, NewOrder, calculate_window_cost, update_delivery, save_order_client,
    select_order_waste, void_movement, database_path, calculate_order_waste, calculate_order_glass_waste)


from apps.api.testing import order_with_client
create_order = order_with_client(create_order)

class HistoryTests(InstallationTests):
    def test_close_on_installation_preserves_snapshot_and_reuses_label(self):
        calculate_window_cost(self.window_id)
        before = get_order(self.order_id)
        add_movement(self.order_id, MovementInput(tipo='pago', importe=before['total_pedido']))
        self.assertIsNone(get_order(self.order_id)['fecha_cierre'])
        active_label = get_order(self.order_id)['etiqueta']
        self.finish()
        closed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.assertIsNotNone(closed['fecha_cierre'])
        cost = closed['ventanas'][0]['costo_materiales']
        for key in ('costo_base', 'porcentaje_ganancia', 'ganancia', 'precio'):
            self.assertEqual(cost[key], before['ventanas'][0]['costo_materiales'][key])
        self.assertNotIn('items', cost)
        self.assertEqual(closed['total_pedido'], before['total_pedido'])
        self.assertEqual(closed['ventanas'][0]['ancho'], before['ventanas'][0]['ancho'])
        self.assertEqual(closed['ventanas'][0]['plan_aluminio'], [])
        self.assertIsNone(closed['ventanas'][0]['plan_vidrio'])
        self.assertFalse(list_orders()['pedidos'])
        historical = list_history()['pedidos'][0]
        self.assertEqual(historical['id'], self.order_id)
        self.assertNotIn('etiqueta', historical)
        self.assertIsNone(closed['etiqueta'])
        self.assertIsNone(closed['ventanas'][0]['codigo'])
        self.assertEqual(closed['ventanas'][0]['numero'], 1)
        other = create_order(NewOrder(ventanas=[{'ancho': '48', 'alto': '36'}]))['id']
        self.assertNotEqual(other, self.order_id)
        self.assertIsNone(get_order(other)['etiqueta'])
        calculate_window_cost(get_order(other)['ventanas'][0]['id'])
        add_movement(other, MovementInput(tipo='pago', importe=get_order(other)['anticipo_requerido']))
        self.assertEqual(get_order(other)['etiqueta'], active_label)
        with sqlite3.connect(database_path()) as connection:
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(connection.execute('SELECT count(*) FROM plan_aluminio WHERE ventana_id = ?', (self.window_id,)).fetchone()[0], 0)

    def test_closing_removes_details_only_for_closed_order(self):
        self.accept()
        calculate_order_waste(self.order_id)
        calculate_order_glass_waste(self.order_id)
        other = create_order(NewOrder(ventanas=[{'ancho': '48', 'alto': '36'}]))['id']
        other_window = get_order(other)['ventanas'][0]['id']
        calculate_window_cost(other_window)
        with sqlite3.connect(database_path()) as db:
            active_snapshot = db.execute('SELECT resultado_json, plan_fingerprint FROM costos_ventana WHERE ventana_id = ?', (other_window,)).fetchone()
            db.execute("UPDATE merma_pedido SET detalle_json = '[{\"perfil\":\"test\"}]' WHERE pedido_id = ?", (self.order_id,))
            db.execute("UPDATE merma_vidrio_pedido SET detalle_json = '[{\"vidrio\":\"test\"}]' WHERE pedido_id = ?", (self.order_id,))
        before = get_order(self.order_id)
        self.finish()
        installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
        self.assertEqual(closed['total_pedido'], before['total_pedido'])
        self.assertEqual(closed['merma']['cargo'], before['merma']['cargo'])
        self.assertEqual(closed['merma_vidrio']['cargo'], before['merma_vidrio']['cargo'])
        self.assertEqual(closed['merma']['detalle'], [])
        self.assertEqual(closed['merma_vidrio']['detalle'], [])
        with sqlite3.connect(database_path()) as db:
            snapshot, fingerprint = db.execute('SELECT resultado_json, plan_fingerprint FROM costos_ventana WHERE ventana_id = ?', (self.window_id,)).fetchone()
            self.assertNotIn('items', json.loads(snapshot))
            self.assertEqual(fingerprint, '')
            self.assertEqual(db.execute('SELECT resultado_json, plan_fingerprint FROM costos_ventana WHERE ventana_id = ?', (other_window,)).fetchone(), active_snapshot)

    def test_close_on_payment_and_reject_modifications(self):
        self.accept(); self.finish()
        installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.assertIsNone(installed['fecha_cierre'])
        closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
        self.assertIsNotNone(closed['fecha_cierre'])
        operations = [
            lambda: set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True)),
            lambda: add_movement(self.order_id, MovementInput(tipo='pago', importe='1')),
            lambda: add_movement(self.order_id, MovementInput(tipo='devolucion', importe='1')),
            lambda: void_movement(self.order_id, closed['movimientos'][0]['id']),
            lambda: calculate_window_cost(self.window_id),
            lambda: update_delivery(self.order_id, DeliveryUpdate(importe='1')),
            lambda: select_order_waste(self.order_id, WasteSelection(incluida=False)),
            lambda: save_order_client(self.order_id, OrderClient(nombre='Ana', apellido_1='Perez', celular='1234567890')),
        ]
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(HTTPException) as error:
                operation()
            self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(get_order(self.order_id), closed)
