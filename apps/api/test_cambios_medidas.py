"""Historial de medidas posteriores a la aceptación y piezas afectadas."""
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.test_corregir_medidas import CorrectWindowMeasuresTests
from apps.api.test_instalacion import InstallationTests
from apps.api.main import (NewOrder, create_order, get_order, mark_aluminum, mark_glass,
    AluminumMark, GlassMark, WindowCorrection, OrderWindowCorrection, correct_window_measures,
    correct_order_window_measures, set_installation, InstallationUpdate, add_movement, MovementInput)


class ChangeHistoryTests(CorrectWindowMeasuresTests):
    def test_cambio_presupuesto_excluido_y_aceptado_sin_cortes_registrado(self):
        budget = create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']
        wid = get_order(budget)['ventanas'][0]['id']
        correct_window_measures(wid, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        self.assertEqual(get_order(budget)['cambios_medidas'], [])
        order = self.create_order(); wid = get_order(order)['ventanas'][0]['id']
        correct_window_measures(wid, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        changes = get_order(order)['cambios_medidas']
        self.assertEqual(changes[0]['anterior'], {'ancho':'48','alto':'36'})
        self.assertEqual(changes[0]['nueva'], {'ancho':'48','alto':'37'})
        self.assertEqual(changes[0]['afectadas'], [])
        moment = datetime.fromisoformat(changes[0]['fecha_hora'])
        self.assertEqual(moment.utcoffset(), moment.astimezone(ZoneInfo("America/Tijuana")).utcoffset())
        with self.assertRaises(HTTPException):
            correct_window_measures(wid, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        self.assertEqual(len(get_order(order)['cambios_medidas']), 1)

    def test_perfiles_vidrio_y_correccion_manual(self):
        order = self.create_order(); wid = get_order(order)['ventanas'][0]['id']
        for index in (1, 2, 5): mark_aluminum(wid, index, AluminumMark(accion='marcar'))
        mark_aluminum(wid, 2, AluminumMark(accion='deshacer'))
        mark_glass(wid, GlassMark(accion='marcar'))
        production = get_order(order)['eventos_fabricacion']
        correct_window_measures(wid, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        updated = get_order(order); affected = updated['cambios_medidas'][0]['afectadas']
        self.assertEqual([(p['tipo'], p.get('perfil'), p['cantidad']) for p in affected], [('aluminio','Jamba',1),('vidrio',None,1)])
        self.assertEqual(affected[0]['clasificacion'], 'sobrante recuperable por cambio de medida')
        self.assertEqual((affected[0]['anterior'], affected[0]['nueva']), ('36','37'))
        self.assertIsNone(affected[1]['clasificacion'])
        self.assertEqual(updated['ventanas'][0]['avance_aluminio'][4]['cortadas'], 1)
        self.assertEqual(updated['eventos_fabricacion'], production)
        mark_aluminum(wid, 1, AluminumMark(accion='marcar'))
        correct_window_measures(wid, WindowCorrection(ancho='48', alto='36', confirmar_correccion=True))
        second = get_order(order)['cambios_medidas'][-1]['afectadas']
        self.assertEqual(second[0]['clasificacion'], 'posible recorte')
        self.assertEqual((second[0]['anterior'], second[0]['nueva']), ('37','36'))

    def test_lote_fallido_no_guarda_cambios(self):
        order = self.create_order(); windows = get_order(order)['ventanas']
        changes = OrderWindowCorrection(ventanas=[{'id':windows[0]['id'],'ancho':'48','alto':'37'},
                                                  {'id':windows[1]['id'],'ancho':'50','alto':'38'}], confirmar_correccion=True)
        with self.assertRaises(HTTPException): correct_order_window_measures(order, changes)
        result = get_order(order)
        self.assertEqual(result['cambios_medidas'], [])
        self.assertEqual(result['ventanas'][0]['alto'], '36')


class ChangeClosureTests(InstallationTests):
    def test_historial_permanece_tras_cierre(self):
        self.accept()
        mark_glass(self.window_id, GlassMark(accion='marcar'))
        correct_window_measures(self.window_id, WindowCorrection(ancho='48', alto='37', confirmar_correccion=True))
        before = get_order(self.order_id)['cambios_medidas']
        self.finish()
        installed = set_installation(self.order_id, InstallationUpdate(instalado=True))
        closed = add_movement(self.order_id, MovementInput(tipo='pago', importe=installed['saldo']))
        self.assertEqual(closed['cambios_medidas'], before)
        self.assertEqual(closed['ventanas'][0]['plan_aluminio'], [])
