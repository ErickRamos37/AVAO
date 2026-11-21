"""Listas y salidas en el tablero de pedidos."""
import sqlite3
from datetime import datetime
from unittest.mock import patch
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (database_path, NewOrder, create_order, dashboard_orders, dashboard_departures,
                           get_order, set_installation, InstallationUpdate, add_movement, MovementInput)
from apps.api.testing import accepted_orders


class DashboardOrdersTests(InstallationTests):
    def test_agenda_hoy_cinco_dias_y_estados(self):
        self.accept()
        create_accepted = accepted_orders(create_order)
        ids = [create_accepted(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id'] for _ in range(5)]
        create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))
        with sqlite3.connect(database_path()) as db:
            for order_id, day in zip(ids, ['2026-12-14','2026-12-15','2026-12-20','2026-12-21','2026-12-13'], strict=True):
                db.execute('UPDATE pedidos SET fecha_programada = ? WHERE id = ?', (day, order_id))
            db.execute('UPDATE ventanas SET ensamblada=1 WHERE pedido_id=?', (ids[1],))
            db.execute('UPDATE ventanas SET descartada=1 WHERE pedido_id=?', (ids[3],))
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2026, 12, 15, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', Clock): result = dashboard_orders()
        self.assertEqual([p['id'] for p in result['atrasados']], [ids[4], ids[0]])
        self.assertEqual([p['id'] for p in result['proximos']], [ids[1], ids[2]])
        self.assertEqual([p['id'] for p in result['listos']], [ids[1]])
        self.assertTrue(any(p['id'] == ids[3] and p['sin_ventanas'] for p in result['pendientes']))
        self.assertEqual(len(result['pendientes']) + len(result['listos']), 6)

    def test_instalacion_vigente_cierre_y_dias_cero(self):
        self.accept(); self.finish()
        class FirstClock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024, 2, 26, 12, tzinfo=tz)
        class LaterClock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024, 2, 29, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', FirstClock):
            set_installation(self.order_id, InstallationUpdate(instalado=True))
            self.assertEqual(dashboard_departures('semana', '2024-02-26')['totales']['instalados'], 1)
        with patch('apps.api.main.datetime', LaterClock):
            set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True))
            self.assertEqual(dashboard_departures('semana', '2024-02-29')['totales']['instalados'], 0)
            installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
            self.assertEqual(len(dashboard_orders()['instalados_por_liquidar']), 1)
            current = dashboard_departures('semana', '2024-02-29')
            self.assertEqual(current['totales'], {'instalados':1,'finalizados':0})
            self.assertEqual(current['promedios_diarios']['instalados'], 0.25)
            self.assertEqual(current['dias'][0]['instalados'], 0)
            add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
            closed = dashboard_departures('mes', '2024-02-29')
            self.assertEqual(closed['totales'], {'instalados':1,'finalizados':1})
            self.assertEqual(len(closed['dias']), 29)
            self.assertEqual(dashboard_orders()['instalados_por_liquidar'], [])

    def test_historial_fechas_legadas_y_anio_bisiesto(self):
        self.accept()
        with sqlite3.connect(database_path()) as db:
            db.execute("UPDATE pedidos SET instalado=1, fecha_real='2024-12-30', fecha_cierre='2024-12-31' WHERE id=?", (self.order_id,))
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2025, 1, 1, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            week = dashboard_departures('semana', '2025-01-01')
            self.assertEqual((week['inicio'], week['fin']), ('2024-12-30','2025-01-01'))
            self.assertEqual(week['totales'], {'instalados':1,'finalizados':1})
            year = dashboard_departures('ano', '2024-01-01')
            self.assertEqual(len(year['dias']), 366)
