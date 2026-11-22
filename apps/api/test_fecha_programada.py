"""Persistencia de la fecha programada sin bloquear el anticipo."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.main import (NewOrder, MovementInput, InstallationDateUpdate, create_order, get_order,
                           calculate_window_cost, add_movement, update_installation_date)


from apps.api.testing import order_with_client
create_order = order_with_client(create_order)

class InstallationDateTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder.name) / "db.sqlite3")); env.start(); self.addCleanup(env.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.order_id = create_order(NewOrder(ventanas=[{"ancho":"48", "alto":"36"}]))["id"]

    def test_acceptance_without_date_and_edit_persistence(self):
        order = get_order(self.order_id)
        calculate_window_cost(order["ventanas"][0]["id"])
        accepted = add_movement(self.order_id, MovementInput(tipo="pago", importe=get_order(self.order_id)["total_pedido"]))
        self.assertTrue(accepted["aceptado"])
        self.assertIsNone(accepted["fecha_programada"])
        update_installation_date(self.order_id, InstallationDateUpdate(fecha="2026-12-15"))
        self.assertEqual(get_order(self.order_id)["fecha_programada"], "2026-12-15")
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        self.assertEqual(get_order(self.order_id)["fecha_programada"], "2026-12-15")
        update_installation_date(self.order_id, InstallationDateUpdate(fecha="2026-12-20", motivo="falta de material"))
        self.assertEqual(get_order(self.order_id)["fecha_programada"], "2026-12-20")
        self.assertTrue(get_order(self.order_id)["aceptado"])

    def test_invalid_date_does_not_overwrite(self):
        update_installation_date(self.order_id, InstallationDateUpdate(fecha="2026-12-15"))
        for value in ("", "2026-02-30", "20261215", "2026-1-1"):
            with self.subTest(value=value), self.assertRaises(HTTPException):
                update_installation_date(self.order_id, InstallationDateUpdate(fecha=value))
        self.assertEqual(get_order(self.order_id)["fecha_programada"], "2026-12-15")
        with self.assertRaises(HTTPException) as error:
            update_installation_date(999999, InstallationDateUpdate(fecha="2026-12-15"))
        self.assertEqual(error.exception.status_code, 404)

if __name__ == "__main__": unittest.main()
