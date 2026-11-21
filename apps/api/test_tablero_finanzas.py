"""Importes exactos, movimientos y ganancias del tablero financiero."""
import json
import sqlite3
from datetime import datetime
from unittest.mock import patch
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (NewOrder, create_order, get_order, calculate_window_cost, dashboard_finances, database_path)
from apps.api.testing import accepted_orders


class FinanceReportTests(InstallationTests):
    def test_centavos_anulaciones_ganancias_y_saldos_actuales(self):
        self.accept()
        order = get_order(self.order_id)
        with sqlite3.connect(database_path()) as db:
            raw = db.execute('SELECT resultado_json FROM costos_ventana WHERE ventana_id=?', (self.window_id,)).fetchone()[0]
            data = json.loads(raw); data['ganancia'] = '0.11'
            db.execute('UPDATE costos_ventana SET resultado_json=? WHERE ventana_id=?', (json.dumps(data), self.window_id))
            db.execute("UPDATE costos_ventana SET plan_fingerprint='desactualizado' WHERE ventana_id=?", (self.window_id,))
        accepted_create = accepted_orders(create_order)
        missing_id = accepted_create(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        closed = accepted_create(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        closed_window = get_order(closed)['ventanas'][0]['id']; calculate_window_cost(closed_window)
        budget = create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        with sqlite3.connect(database_path()) as db:
            raw = db.execute('SELECT resultado_json FROM costos_ventana WHERE ventana_id=?', (closed_window,)).fetchone()[0]
            data = json.loads(raw); data['ganancia'] = '3.33'
            db.execute('UPDATE costos_ventana SET resultado_json=? WHERE ventana_id=?', (json.dumps(data), closed_window))
            db.execute("UPDATE pedidos SET fecha_cierre='2024-02-29', instalado=1 WHERE id=?", (closed,))
            for order_id, kind, cents, day, void in [(budget,'pago',105,'2024-02-26',0), (self.order_id,'pago',99,'2024-02-26',0),
                (closed,'devolucion',120,'2024-02-27',0), (closed,'pago',50000,'2024-02-27',1)]:
                db.execute('INSERT INTO movimientos (pedido_id,tipo,importe_centavos,fecha,anulado) VALUES (?,?,?,?,?)', (order_id,kind,cents,day,void))
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024,2,29,12,tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            report = dashboard_finances('semana','2024-02-29')
            self.assertEqual(report['totales'], {'pagos':'2.04','devoluciones':'1.20','neto':'0.84'})
            self.assertEqual(report['dias'][1]['neto'], '-1.20')
            self.assertEqual(report['promedios_diarios']['neto'], '0.21')
            self.assertEqual(report['dias_semana'][0]['promedio_neto'], '2.04')
            self.assertTrue(report['dias_semana'][0]['mayor'])
            self.assertEqual(report['dias_semana'][1]['promedio_neto'], '-1.20')
            self.assertEqual(report['dias_semana'][6]['ocurrencias'], 0)
            self.assertEqual(report['actual']['ganancia'], '0.11')
            self.assertEqual(report['actual']['faltantes'], 1)
            self.assertEqual(report['actual']['desactualizadas'], 1)
            self.assertEqual(report['actual']['sin_saldo'], 1)
            self.assertEqual(report['finalizados'], {'ganancia':'3.33','faltantes':0,'con_ganancia':1})
            prior = dashboard_finances('dia','2024-02-26')
            self.assertEqual(prior['actual'], report['actual'])
            self.assertEqual(prior['finalizados']['ganancia'], '0.00')

    def test_promedio_por_dia_semana_incluye_ocurrencias_sin_movimiento(self):
        with sqlite3.connect(database_path()) as db:
            db.execute("INSERT INTO movimientos (pedido_id,tipo,importe_centavos,fecha,anulado) VALUES (?, 'pago', 101, '2024-02-05', 0)", (self.order_id,))
            db.execute("INSERT INTO movimientos (pedido_id,tipo,importe_centavos,fecha,anulado) VALUES (?, 'pago', 100, '2024-02-06', 0)", (self.order_id,))
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024,2,29,12,tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            report = dashboard_finances('mes','2024-02-29')
        self.assertEqual(report['dias_semana'][0]['ocurrencias'], 4)
        self.assertEqual(report['dias_semana'][0]['promedio_neto'], '0.25')
        self.assertEqual(report['dias_semana'][1]['promedio_neto'], '0.25')
        self.assertTrue(report['dias_semana'][0]['mayor'])
        self.assertFalse(report['dias_semana'][1]['mayor'])
        self.assertEqual(report['promedios_diarios']['pagos'], '0.07')

    def test_cierre_sin_ganancia_descartadas_y_redondeo_centavos(self):
        from apps.api.main import average_cents
        self.assertEqual(average_cents(1, 2), '0.01')
        self.assertEqual(average_cents(-1, 2), '-0.01')
        closed = accepted_orders(create_order)(NewOrder(ventanas=[{'ancho':'48','alto':'36'}, {'ancho':'48','alto':'36'}]))['id']
        with sqlite3.connect(database_path()) as db:
            db.execute("UPDATE pedidos SET fecha_cierre='2024-02-29', instalado=1 WHERE id=?", (closed,))
            db.execute('UPDATE ventanas SET descartada=1 WHERE pedido_id=? AND numero_en_pedido=2', (closed,))
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024,2,29,12,tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            report = dashboard_finances('dia','2024-02-29')
        self.assertEqual(report['finalizados'], {'ganancia':'0.00', 'faltantes':1, 'con_ganancia':0})
        self.assertEqual(report['dias'][0]['ganancias_faltantes'], 1)
        self.assertEqual(report['dias'][0]['ganancias_disponibles'], 0)
