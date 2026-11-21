"""Eventos de fabricación, correcciones y conservación histórica."""
from datetime import datetime
from unittest.mock import patch
from apps.api.test_corregir_medidas import CorrectWindowMeasuresTests
from apps.api.main import (AluminumMark, GlassMark, WindowCorrection, correct_window_measures,
                           get_order, mark_aluminum, mark_glass, database_path)
import sqlite3


class ProductionEventTests(CorrectWindowMeasuresTests):
    def test_correccion_manual_apunta_al_evento_de_la_marca_vigente(self):
        order_id = self.create_order(); window = get_order(order_id)['ventanas'][0]['id']
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return cls(2026, 1, 4, 12, 0, tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            mark_aluminum(window, 1, AluminumMark(accion='marcar'))
            mark_aluminum(window, 5, AluminumMark(accion='marcar'))
            mark_glass(window, GlassMark(accion='marcar'))
        correct_window_measures(window, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        mark_aluminum(window, 1, AluminumMark(accion='marcar'))
        mark_aluminum(window, 1, AluminumMark(accion='deshacer'))
        mark_aluminum(window, 5, AluminumMark(accion='deshacer'))
        events = get_order(order_id)['eventos_fabricacion']
        self.assertFalse(events[0]['corregido'])
        self.assertTrue(events[1]['corregido'])
        self.assertFalse(events[2]['corregido'])
        self.assertTrue(events[3]['corregido'])
        self.assertEqual(events[4]['original_id'], events[3]['id'])
        self.assertEqual(events[5]['original_id'], events[1]['id'])
        self.assertTrue(events[0]['fecha_hora'].startswith('2026-01-04'))

    def test_marca_antigua_deshacer_no_inventa_corte(self):
        order_id = self.create_order(); window = get_order(order_id)['ventanas'][0]['id']
        with sqlite3.connect(database_path()) as db:
            db.execute('UPDATE plan_vidrio SET cortadas = 1 WHERE ventana_id = ?', (window,))
        mark_glass(window, GlassMark(accion='deshacer'))
        event = get_order(order_id)['eventos_fabricacion']
        self.assertEqual(len(event), 1)
        self.assertEqual(event[0]['accion'], 'deshacer')
        self.assertIsNone(event[0]['original_id'])

from apps.api.test_instalacion import InstallationTests
from apps.api.main import InstallationUpdate, MovementInput, set_installation, add_movement


class ProductionClosureTests(InstallationTests):
    def test_cierre_conserva_eventos_y_el_error_revierte_marca(self):
        self.accept()
        with patch('apps.api.main.record_production', side_effect=RuntimeError('fallo')):
            with self.assertRaises(RuntimeError):
                mark_glass(self.window_id, GlassMark(accion='marcar'))
        self.assertEqual(get_order(self.order_id)['ventanas'][0]['avance_vidrio']['cortadas'], 0)
        self.assertEqual(get_order(self.order_id)['eventos_fabricacion'], [])
        self.finish()
        before = get_order(self.order_id)['eventos_fabricacion']
        self.assertEqual(before[-1]['area'], 'ensamble')
        installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
        self.assertEqual(closed['eventos_fabricacion'], before)
        with sqlite3.connect(database_path()) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM marcas_fabricacion_vigentes').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT count(*) FROM plan_aluminio').fetchone()[0], 0)
