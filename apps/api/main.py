"""Primer recorrido vertical de HU-01: guardar y reabrir un pedido."""

import os
from pathlib import Path
import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictStr

from apps.api.medidas import format_measure, parse_measure


ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "apps" / "web"
app = FastAPI(title="AVAO")
app.mount("/static", StaticFiles(directory=WEB), name="static")


class NewOrder(BaseModel):
    ancho: StrictStr
    alto: StrictStr


def database_path() -> Path:
    return Path(os.environ.get("AVAO_DB_PATH", ROOT / "data" / "avao.sqlite3"))


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path(), timeout=5)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@app.post("/api/pedidos", status_code=201)
def create_order(order: NewOrder):
    try:
        width = parse_measure(order.ancho)
        height = parse_measure(order.alto)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    # La transacción evita pedidos vacíos si falla la inserción de la ventana.
    with closing(connect_db()) as connection:
        with connection:
            cursor = connection.execute("INSERT INTO pedidos DEFAULT VALUES")
            order_id = cursor.lastrowid
            connection.execute(
                "INSERT INTO ventanas (pedido_id, numero_en_pedido, ancho_16, alto_16) "
                "VALUES (?, 1, ?, ?)",
                (order_id, width, height),
            )

    return {"id": order_id}


@app.get("/api/pedidos/{order_id}")
def get_order(order_id: int):
    with closing(connect_db()) as connection:
        if connection.execute("SELECT id FROM pedidos WHERE id = ?", (order_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        windows = connection.execute(
            "SELECT id, numero_en_pedido, ancho_16, alto_16 "
            "FROM ventanas WHERE pedido_id = ? ORDER BY numero_en_pedido",
            (order_id,),
        ).fetchall()

    return {
        "id": order_id,
        "ventanas": [
            {
                "id": window_id,
                "numero": number,
                "ancho": format_measure(width),
                "alto": format_measure(height),
            }
            for window_id, number, width, height in windows
        ],
    }


@app.get("/pedidos/{order_id}", include_in_schema=False)
def order_page(order_id: int):
    return FileResponse(WEB / "index.html")


@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(WEB / "index.html")
