"""Preparación de pedidos aceptados para pruebas previas de fabricación."""
import sqlite3
from apps.api.main import database_path, assign_order_label


def accepted_orders(create):
    def create_accepted(order):
        result = create(order)
        with sqlite3.connect(database_path()) as connection:
            connection.execute("INSERT INTO aceptaciones (pedido_id) VALUES (?)", (result["id"],))
            assign_order_label(connection, result["id"])
        return result
    return create_accepted


def order_with_client(create):
    def create_with_client(order):
        from apps.api.main import OrderClient, save_order_client
        result = create(order)
        save_order_client(result["id"], OrderClient(nombre="Ana", apellido_1="Pérez", celular="1234567890"))
        return result
    return create_with_client
