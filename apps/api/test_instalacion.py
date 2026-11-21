"""Instalación completa y protección de fabricación."""
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from apps.api.main import (NewOrder, InstallationUpdate, AluminumMark, GlassMark, AssemblyMark,
    WindowDiscard, WindowCorrection, MovementInput, create_order, get_order, calculate_window_cost,
    add_movement, mark_aluminum, mark_glass, mark_assembly, set_installation, set_window_discard,
    correct_window_measures, list_order_progress)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder.name) / "db.sqlite3")); env.start(); self.addCleanup(env.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.order_id = create_order(NewOrder(ventanas=[{"ancho":"48", "alto":"36"}]))["id"]
        self.window_id = get_order(self.order_id)["ventanas"][0]["id"]

    def accept(self):
        calculate_window_cost(self.window_id)
        add_movement(self.order_id, MovementInput(tipo="pago", importe=get_order(self.order_id)["anticipo_requerido"]))

    def finish(self):
        window = get_order(self.order_id)["ventanas"][0]
        for cut in window["avance_aluminio"]:
            for _ in range(cut["pendientes"]): mark_aluminum(self.window_id, cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(window["avance_vidrio"]["pendientes"]): mark_glass(self.window_id, GlassMark(accion="marcar"))
        mark_assembly(self.window_id, AssemblyMark(accion="marcar"))

    def test_requires_accepted_nonempty_fully_finished(self):
        with self.assertRaises(HTTPException): set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.accept()
        with self.assertRaises(HTTPException): set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.finish()
        set_window_discard(self.window_id, WindowDiscard(descartada=True, confirmar_descarte=True))
        with self.assertRaises(HTTPException): set_installation(self.order_id, InstallationUpdate(instalado=True))
        set_window_discard(self.window_id, WindowDiscard(descartada=False))
        result = set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.assertTrue(result["instalado"])
        self.assertEqual(result["fecha_real"], datetime.now(ZoneInfo("America/Tijuana")).date().isoformat())
        self.assertTrue(list_order_progress()["pedidos"][0]["instalado"])
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.assertTrue(get_order(self.order_id)["instalado"])

    def test_discarded_window_cannot_be_restored_while_installed(self):
        order_id = create_order(NewOrder(ventanas=[{"ancho":"48", "alto":"36"}, {"ancho":"50", "alto":"38"}]))["id"]
        first, second = get_order(order_id)["ventanas"]
        set_window_discard(second["id"], WindowDiscard(descartada=True, confirmar_descarte=True))
        calculate_window_cost(first["id"])
        add_movement(order_id, MovementInput(tipo="pago", importe=get_order(order_id)["total_pedido"]))
        for cut in first["avance_aluminio"]:
            for _ in range(cut["pendientes"]): mark_aluminum(first["id"], cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(first["avance_vidrio"]["pendientes"]): mark_glass(first["id"], GlassMark(accion="marcar"))
        mark_assembly(first["id"], AssemblyMark(accion="marcar"))
        set_installation(order_id, InstallationUpdate(instalado=True))
        with self.assertRaises(HTTPException): set_window_discard(second["id"], WindowDiscard(descartada=False))
        self.assertEqual(len(get_order(order_id)["ventanas_descartadas"]), 1)

    def test_uninstall_requires_confirmation_and_clears_date(self):
        self.accept(); self.finish()
        set_installation(self.order_id, InstallationUpdate(instalado=True))
        with self.assertRaises(HTTPException):
            set_installation(self.order_id, InstallationUpdate(instalado=False))
        self.assertTrue(get_order(self.order_id)["instalado"])
        result = set_installation(self.order_id, InstallationUpdate(instalado=False, confirmar_desmarcado=True))
        self.assertFalse(result["instalado"])
        self.assertIsNone(result["fecha_real"])
        result = set_installation(self.order_id, InstallationUpdate(instalado=True))
        self.assertEqual(result["fecha_real"], datetime.now(ZoneInfo("America/Tijuana")).date().isoformat())

    def test_installed_blocks_modifications_but_permits_payments(self):
        self.accept(); self.finish(); set_installation(self.order_id, InstallationUpdate(instalado=True))
        operations = [
            lambda: set_window_discard(self.window_id, WindowDiscard(descartada=True, confirmar_descarte=True)),
            lambda: correct_window_measures(self.window_id, WindowCorrection(ancho="49", alto="36", confirmar_correccion=True)),
            lambda: mark_aluminum(self.window_id, 1, AluminumMark(accion="deshacer")),
            lambda: mark_glass(self.window_id, GlassMark(accion="deshacer")),
            lambda: mark_assembly(self.window_id, AssemblyMark(accion="deshacer")),
        ]
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(HTTPException): operation()
        result = add_movement(self.order_id, MovementInput(tipo="pago", importe="1"))
        self.assertFalse(result["liquidado"])
        self.assertIsNone(result["fecha_cierre"])

if __name__ == "__main__": unittest.main()
