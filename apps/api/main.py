"""Primer recorrido vertical de HU-01: guardar y reabrir un pedido."""

import os
from pathlib import Path
import sqlite3
from contextlib import closing
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictStr

from apps.api.medidas import format_measure, parse_measure
from apps.api.plan_aluminio import calcular_plan_aluminio
from apps.api.plan_vidrio import calcular_plan_vidrio


ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "apps" / "web"
app = FastAPI(title="AVAO")
app.mount("/static", StaticFiles(directory=WEB), name="static")


class NewWindow(BaseModel):
    ancho: StrictStr
    alto: StrictStr


class NewOrder(BaseModel):
    ventanas: list[NewWindow]


class AluminumMark(BaseModel):
    accion: Literal["marcar", "deshacer"]


class GlassMark(BaseModel):
    accion: Literal["marcar", "deshacer"]


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
            width, height = parse_measure(width_text), parse_measure(height_text)
            aluminum = calcular_plan_aluminio(width, height)
            glass = calcular_plan_vidrio(width, height)
            measurements.append((width, height, aluminum, glass))
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
            for number, (width, height, aluminum, glass) in enumerate(measurements, start=1):
                window_cursor = connection.execute(
                    "INSERT INTO ventanas (pedido_id, numero_en_pedido, ancho_16, alto_16) "
                    "VALUES (?, ?, ?, ?)",
                    (order_id, number, width, height),
                )
                connection.executemany(
                    "INSERT INTO plan_aluminio (ventana_id, orden, perfil, longitud_16, cantidad) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [(window_cursor.lastrowid, index, perfil, length, quantity)
                     for index, (perfil, length, quantity) in enumerate(aluminum, start=1)],
                )
                connection.execute(
                    "INSERT INTO plan_vidrio (ventana_id, ancho_16, alto_16, cantidad) "
                    "VALUES (?, ?, ?, ?)",
                    (window_cursor.lastrowid, *glass),
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
        plan_rows = connection.execute(
            "SELECT a.ventana_id, a.orden, a.perfil, a.longitud_16, a.cantidad, a.cortadas "
            "FROM plan_aluminio AS a JOIN ventanas AS v ON v.id = a.ventana_id "
            "WHERE v.pedido_id = ? ORDER BY v.numero_en_pedido, a.orden",
            (order_id,),
        ).fetchall()
        glass_rows = connection.execute(
            "SELECT g.ventana_id, g.ancho_16, g.alto_16, g.cantidad, g.cortadas "
            "FROM plan_vidrio AS g JOIN ventanas AS v ON v.id = g.ventana_id "
            "WHERE v.pedido_id = ?",
            (order_id,),
        ).fetchall()

    plans = {window_id: [] for window_id, *_ in windows}
    progress = {window_id: [] for window_id, *_ in windows}
    for window_id, order, profile, length, quantity, cut in plan_rows:
        plans[window_id].append({
            "perfil": profile,
            "longitud": format_measure(length),
            "cantidad": quantity,
        })
        progress[window_id].append({
            "orden": order,
            "cortadas": cut,
            "pendientes": quantity - cut,
        })
    glass_plans = {
        window_id: {"ancho": format_measure(width), "alto": format_measure(height), "cantidad": quantity}
        for window_id, width, height, quantity, _ in glass_rows
    }
    glass_progress = {
        window_id: {"cortadas": cut, "pendientes": quantity - cut}
        for window_id, _, _, quantity, cut in glass_rows
    }

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
                "plan_aluminio": plans[window_id],
                "avance_aluminio": progress[window_id],
                "plan_vidrio": glass_plans.get(window_id),
                "avance_vidrio": glass_progress.get(window_id),
            }
            for window_id, number, width, height in windows
        ],
    }


@app.post("/api/ventanas/{window_id}/aluminio/{order}/marcas")
def mark_aluminum(window_id: int, order: int, mark: AluminumMark):
    difference = 1 if mark.accion == "marcar" else -1
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            row = connection.execute(
                "SELECT cantidad, cortadas FROM plan_aluminio "
                "WHERE ventana_id = ? AND orden = ?",
                (window_id, order),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Corte de aluminio no encontrado.")
            required, cut = row
            updated = cut + difference
            if not 0 <= updated <= required:
                raise HTTPException(status_code=409, detail="No se puede registrar esa marca de corte.")
            connection.execute(
                "UPDATE plan_aluminio SET cortadas = ? WHERE ventana_id = ? AND orden = ?",
                (updated, window_id, order),
            )
    return {"orden": order, "requeridas": required, "cortadas": updated, "pendientes": required - updated}


@app.post("/api/ventanas/{window_id}/vidrio/marcas")
def mark_glass(window_id: int, mark: GlassMark):
    difference = 1 if mark.accion == "marcar" else -1
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            row = connection.execute(
                "SELECT cantidad, cortadas FROM plan_vidrio WHERE ventana_id = ?",
                (window_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Plan de vidrio no encontrado.")
            required, cut = row
            updated = cut + difference
            if not 0 <= updated <= required:
                raise HTTPException(status_code=409, detail="No se puede registrar esa marca de corte.")
            connection.execute(
                "UPDATE plan_vidrio SET cortadas = ? WHERE ventana_id = ?",
                (updated, window_id),
            )
    return {"requeridas": required, "cortadas": updated, "pendientes": required - updated}


@app.get("/pedidos/{order_id}", include_in_schema=False)
def order_page(order_id: int):
    return FileResponse(WEB / "index.html")


@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(WEB / "index.html")
