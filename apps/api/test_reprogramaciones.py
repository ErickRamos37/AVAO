"""Historial y atraso de la programación de instalación."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.test_fecha_programada import InstallationDateTests
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (InstallationDateUpdate, update_installation_date, get_order, database_path,
                           list_order_progress, set_installation, InstallationUpdate, add_movement, MovementInput)


class ScheduleHistoryTests(InstallationDateTests):
    def test_programacion_motivos_e_idempotencia(self):
        initial = update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-15'))
        self.assertEqual(len(initial['programaciones']), 1)
        self.assertIsNone(initial['programaciones'][0]['anterior'])
        update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-15'))
        for reason, other in [(None,None), ('falso',None), ('Otros','  ')]:
            with self.subTest(reason=reason), self.assertRaises(HTTPException):
                update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-20', motivo=reason, motivo_otro=other))
        self.assertEqual(len(get_order(self.order_id)['programaciones']), 1)
        changed = update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-20', motivo='Otros', motivo_otro='  lluvia  '))
        event = changed['programaciones'][-1]
        self.assertEqual((event['anterior'], event['nueva'], event['motivo'], event['motivo_otro']), ('2026-12-15','2026-12-20','Otros','lluvia'))
        stamp = datetime.fromisoformat(event['fecha_hora'])
        self.assertEqual(stamp.utcoffset(), stamp.astimezone(ZoneInfo('America/Tijuana')).utcoffset())
        with sqlite3.connect(database_path()) as db:
            db.execute("CREATE TRIGGER fail_schedule BEFORE INSERT ON programaciones_instalacion BEGIN SELECT RAISE(FAIL, 'test'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-21', motivo='falta de material'))
        self.assertEqual(get_order(self.order_id)['fecha_programada'], '2026-12-20')
        self.assertEqual(len(get_order(self.order_id)['programaciones']), 2)

    def test_fecha_antigua_no_se_presenta_como_original(self):
        with sqlite3.connect(database_path()) as db:
            db.execute('UPDATE pedidos SET fecha_programada = ? WHERE id = ?', ('2026-12-15', self.order_id))
        self.assertEqual(get_order(self.order_id)['programaciones'], [])
        order = update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-20', motivo='fabricación pendiente'))
        self.assertEqual(order['programaciones'][0]['anterior'], '2026-12-15')


class ScheduleStatusTests(InstallationTests):
    def test_atraso_hoy_manana_instalado_desmarcado_y_cierre(self):
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2026, 12, 15, 12, tzinfo=tz)
        self.accept()
        with patch('apps.api.main.datetime', Clock):
            update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-15'))
            self.assertFalse(get_order(self.order_id)['instalacion_atrasada'])
            update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-16', motivo='disponibilidad del cliente'))
            self.assertFalse(list_order_progress()['pedidos'][0]['instalacion_atrasada'])
            update_installation_date(self.order_id, InstallationDateUpdate(fecha='2026-12-14', motivo='disponibilidad del taller/transporte'))
            self.assertTrue(list_order_progress()['pedidos'][0]['instalacion_atrasada'])
            self.finish()
            installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
            self.assertFalse(installed['instalacion_atrasada'])
            uninstalled = set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True))
            self.assertTrue(uninstalled['instalacion_atrasada'])
            installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
            closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
            self.assertEqual(len(closed['programaciones']), 3)
            self.assertFalse(closed['instalacion_atrasada'])
