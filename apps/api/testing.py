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
