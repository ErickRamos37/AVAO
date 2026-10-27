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


class NewWindow(BaseModel):
    ancho: StrictStr
    alto: StrictStr


class NewOrder(BaseModel):
    ventanas: list[NewWindow]


def database_path() -> Path:
    return Path(os.environ.get("AVAO_DB_PATH", ROOT / "data" / "avao.sqlite3"))


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path(), timeout=5)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def following_label(current: str | None) -> str:
    number = 0
    for letter in current or "":
        number = number * 26 + ord(letter) - ord("A") + 1
    number += 1
    label = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


@app.post("/api/pedidos", status_code=201)
def create_order(order: NewOrder):
    measurements = []
    for row_number, window in enumerate(order.ventanas, start=1):
        width_text, height_text = window.ancho.strip(), window.alto.strip()
        if not width_text and not height_text:
            continue
        if not width_text or not height_text:
            raise HTTPException(status_code=422, detail=f"Ventana {row_number}: completa ancho y alto o descarta la fila.")
        try:
            measurements.append((parse_measure(width_text), parse_measure(height_text)))
        except ValueError as error:
            raise HTTPException(status_code=422, detail=f"Ventana {row_number}: {error}") from error

    if not measurements:
        raise HTTPException(status_code=422, detail="Agrega al menos una ventana con ancho y alto completos.")

    # BEGIN IMMEDIATE serializa la elección de etiqueta entre guardados simultáneos.
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            latest = connection.execute(
                "SELECT etiqueta FROM pedidos WHERE etiqueta IS NOT NULL "
                "ORDER BY LENGTH(etiqueta) DESC, etiqueta DESC LIMIT 1"
            ).fetchone()
            label = following_label(latest[0] if latest else None)
            cursor = connection.execute("INSERT INTO pedidos (etiqueta) VALUES (?)", (label,))
            order_id = cursor.lastrowid
            for number, (width, height) in enumerate(measurements, start=1):
                connection.execute(
                    "INSERT INTO ventanas (pedido_id, numero_en_pedido, ancho_16, alto_16) "
                    "VALUES (?, ?, ?, ?)",
                    (order_id, number, width, height),
                )

    return {"id": order_id}


@app.get("/api/pedidos")
def list_orders():
    with closing(connect_db()) as connection:
        rows = connection.execute(
            "SELECT p.id, p.etiqueta, v.numero_en_pedido "
            "FROM pedidos AS p LEFT JOIN ventanas AS v ON v.pedido_id = p.id "
            "ORDER BY p.id ASC, v.numero_en_pedido ASC"
        ).fetchall()
    orders = {}
    for order_id, label, number in rows:
        if order_id not in orders:
            orders[order_id] = {"id": order_id, "etiqueta": label, "codigos": []}
        if label is not None and number is not None:
            orders[order_id]["codigos"].append(f"{label}{number}")
    return {"pedidos": list(orders.values())}


@app.get("/api/pedidos/{order_id}")
def get_order(order_id: int):
    with closing(connect_db()) as connection:
        order = connection.execute(
            "SELECT id, etiqueta FROM pedidos WHERE id = ?", (order_id,)
        ).fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        label = order[1]
        windows = connection.execute(
            "SELECT id, numero_en_pedido, ancho_16, alto_16 "
            "FROM ventanas WHERE pedido_id = ? ORDER BY numero_en_pedido",
            (order_id,),
        ).fetchall()

    return {
        "id": order_id,
        "etiqueta": label,
        "ventanas": [
            {
                "id": window_id,
                "numero": number,
                "codigo": f"{label}{number}" if label is not None else None,
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
