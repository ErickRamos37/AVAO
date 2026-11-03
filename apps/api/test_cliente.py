"""Comprueba los datos del cliente sin alterar el trabajo guardado del pedido."""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (AluminumMark, GlassMark, NewOrder, OrderClient,
                           create_order, get_order, mark_aluminum, mark_glass,
                           save_order_client)


class ClientTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "avao.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        self.migrate()

    def migrate(self):
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True,
                       capture_output=True, text=True)

    def new_order(self):
        return create_order(NewOrder(ventanas=[{"ancho": "48", "alto": "36"}]))["id"]

    def test_register_correct_and_reopen_without_changing_cuts(self):
        order_id = self.new_order()
        window_id = get_order(order_id)["ventanas"][0]["id"]
        mark_aluminum(window_id, 1, AluminumMark(accion="marcar"))
        mark_glass(window_id, GlassMark(accion="marcar"))
        before = get_order(order_id)["ventanas"]
        self.assertIsNone(get_order(order_id)["cliente"])
        details = OrderClient(nombre=" Ana ", apellido_1=" Ruiz ", celular="0123456789",
                              direccion=" Calle 2 ", notas="Después de las 4")
        save_order_client(order_id, details)
        save_order_client(order_id, OrderClient(nombre="Ana María", apellido_1="Ruiz",
                                               apellido_2="López", celular="0123456789",
                                               notas="Llamar antes"))
        reopened = get_order(order_id)
        self.assertEqual(reopened["cliente"], {
            "nombre": "Ana María", "apellido_1": "Ruiz", "apellido_2": "López",
            "celular": "0123456789", "direccion": "",
        })
        self.assertEqual(reopened["notas"], "Llamar antes")
        self.assertEqual(reopened["ventanas"], before)
        with sqlite3.connect(self.path) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clientes").fetchone()[0], 1)

    def test_client_data_does_not_leak_between_orders(self):
        first, second = self.new_order(), self.new_order()
        save_order_client(first, OrderClient(nombre="Ana", apellido_1="Ruiz",
                                            celular="0123456789", notas="Entrada lateral"))
        self.assertIsNone(get_order(second)["cliente"])
        self.assertEqual(get_order(second)["notas"], "")
        save_order_client(second, OrderClient(nombre="Luis", apellido_1="Paz",
                                             celular="1234567890"))
        self.assertEqual(get_order(first)["cliente"]["nombre"], "Ana")
        self.assertEqual(get_order(second)["cliente"]["nombre"], "Luis")

    def test_rejects_missing_required_fields_and_wrong_phone_without_partial_save(self):
        order_id = self.new_order()
        for details in [
            OrderClient(nombre=" ", apellido_1="Ruiz", celular="0123456789"),
            OrderClient(nombre="Ana", apellido_1=" ", celular="0123456789"),
            OrderClient(nombre="Ana", apellido_1="Ruiz", celular="123456789"),
            OrderClient(nombre="Ana", apellido_1="Ruiz", celular="abcdefghij"),
        ]:
            with self.assertRaises(HTTPException) as raised:
                save_order_client(order_id, details)
            self.assertEqual(raised.exception.status_code, 422)
        self.assertIsNone(get_order(order_id)["cliente"])
        with self.assertRaises(HTTPException) as raised:
            save_order_client(9999, OrderClient(nombre="Ana", apellido_1="Ruiz",
                                                celular="0123456789"))
        self.assertEqual(raised.exception.status_code, 404)

    def test_rejects_numbers_in_any_name_without_changing_saved_client(self):
        order_id = self.new_order()
        valid = OrderClient(nombre="Ana María", apellido_1="O'Connor-Sáenz",
                            apellido_2="Núñez", celular="0123456789")
        for field, value in (("nombre", "Ana2"), ("apellido_1", "Ruiz 3"),
                             ("apellido_2", "López4"), ("nombre", "Ana²")):
            invalid = valid.model_copy(update={field: value})
            with self.assertRaises(HTTPException) as raised:
                save_order_client(order_id, invalid)
            self.assertEqual(raised.exception.status_code, 422)
            self.assertIn("no puede contener números", raised.exception.detail)
            self.assertIsNone(get_order(order_id)["cliente"])

        save_order_client(order_id, valid)
        saved = get_order(order_id)["cliente"]
        self.assertEqual(saved["apellido_1"], "O'Connor-Sáenz")
        for field, value in (("nombre", "Ana2"), ("apellido_1", "Ruiz 3"),
                             ("apellido_2", "López4")):
            with self.assertRaises(HTTPException) as raised:
                save_order_client(order_id, valid.model_copy(update={field: value}))
            self.assertEqual(raised.exception.status_code, 422)
            self.assertEqual(get_order(order_id)["cliente"], saved)

    def test_migrates_an_order_saved_before_client_fields(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TABLE clientes")
            connection.execute("ALTER TABLE pedidos DROP COLUMN cliente_id")
            connection.execute("ALTER TABLE pedidos DROP COLUMN notas")
            connection.execute("INSERT INTO pedidos (etiqueta) VALUES ('A')")
        self.migrate()
        self.assertIsNone(get_order(1)["cliente"])
        save_order_client(1, OrderClient(nombre="Ana", apellido_1="Ruiz", celular="0123456789"))
        self.assertEqual(get_order(1)["cliente"]["nombre"], "Ana")


if __name__ == "__main__":
    unittest.main()
