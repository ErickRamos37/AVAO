"""Agregación de producción registrada entre pedidos."""
from datetime import datetime
import sqlite3
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.test_corregir_medidas import CorrectWindowMeasuresTests
from apps.api.main import (production_by_day, production_report, database_path, get_order, mark_aluminum, mark_glass,
    AluminumMark, GlassMark, WindowCorrection, correct_window_measures)


class ProductionReportTests(CorrectWindowMeasuresTests):
    def test_suma_pedidos_y_corrige_en_fecha_original(self):
        first = self.create_order(); second = self.create_order()
        first_window = get_order(first)['ventanas'][0]['id']
        second_window = get_order(second)['ventanas'][0]['id']
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2026, 1, 4, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            mark_aluminum(first_window, 1, AluminumMark(accion='marcar'))
            mark_aluminum(first_window, 5, AluminumMark(accion='marcar'))
            mark_glass(second_window, GlassMark(accion='marcar'))
        mark_aluminum(first_window, 5, AluminumMark(accion='deshacer'))
        correct_window_measures(first_window, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        result = production_by_day('2026-01-04', '2026-01-04')
        self.assertEqual(result['dias'], [{'fecha':'2026-01-04', 'aluminio':1, 'vidrio':1, 'ensamble':0}])
        self.assertEqual(production_by_day('2026-01-05', '2026-01-06')['dias'], [])
        for start, end in [('2026-1-1','2026-01-02'), ('2026-02-30','2026-03-01'), ('2026-01-02','2026-01-01')]:
            with self.subTest(start=start), self.assertRaises(HTTPException): production_by_day(start,end)

    def test_periodos_y_promedio_incluyen_ceros_sin_futuros(self):
        order = self.create_order(); window = get_order(order)['ventanas'][0]['id']
        class LeapClock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2024, 2, 29, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', LeapClock):
            mark_glass(window, GlassMark(accion='marcar'))
            day = production_report('dia', '2024-02-29')
            self.assertEqual(day['promedios_diarios']['vidrio'], 1)
            week = production_report('semana', '2024-02-29')
            self.assertEqual((week['inicio'], week['fin'], len(week['dias'])), ('2024-02-26', '2024-02-29', 4))
            self.assertEqual(week['promedios_diarios']['vidrio'], 0.25)
            month = production_report('mes', '2024-02-29')
            self.assertEqual(len(month['dias']), 29)
            self.assertEqual(month['totales']['vidrio'], 1)
            year = production_report('ano', '2024-02-29')
            self.assertEqual(len(year['dias']), 60)
            self.assertEqual(year['totales']['ensamble'], 0)
            previous_week = production_report('semana', '2024-02-25')
            self.assertEqual((previous_week['inicio'], previous_week['fin'], len(previous_week['dias'])), ('2024-02-19','2024-02-25',7))
            self.assertEqual(previous_week['totales']['vidrio'], 0)
            with self.assertRaises(HTTPException): production_report('dia', '2024-03-01')
            with sqlite3.connect(database_path()) as db:
                db.execute("UPDATE pedidos SET fecha_cierre = '2024-02-29' WHERE id = ?", (order,))
            self.assertEqual(production_report('dia', '2024-02-29')['totales']['vidrio'], 1)

    def test_anio_bisiesto_cerrado_y_limite_de_anio(self):
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return cls(2025, 1, 1, 12, tzinfo=tz)
        with patch('apps.api.main.datetime', Clock):
            year = production_report('ano', '2024-06-01')
            self.assertEqual(len(year['dias']), 366)
            self.assertEqual(year['promedios_diarios']['aluminio'], 0)
            week = production_report('semana', '2025-01-01')
            self.assertEqual((week['inicio'], week['fin'], len(week['dias'])), ('2024-12-30', '2025-01-01', 3))
