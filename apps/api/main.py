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


class AssemblyMark(BaseModel):
    accion: Literal["marcar", "deshacer"]


class OrderClient(BaseModel):
    nombre: StrictStr
    apellido_1: StrictStr
    apellido_2: StrictStr = ""
    celular: StrictStr
    direccion: StrictStr = ""
    notas: StrictStr = ""


class WindowCorrection(BaseModel):
    ancho: StrictStr
    alto: StrictStr
    confirmar_correccion: bool = False


class WindowMeasureUpdate(BaseModel):
    id: int
    ancho: StrictStr
    alto: StrictStr


class OrderWindowCorrection(BaseModel):
    ventanas: list[WindowMeasureUpdate]
    confirmar_correccion: bool = False


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
        order_row = connection.execute(
            "SELECT p.id, p.etiqueta, p.notas, c.nombre, c.apellido_1, c.apellido_2, "
            "c.celular, c.direccion FROM pedidos AS p "
            "LEFT JOIN clientes AS c ON c.id = p.cliente_id WHERE p.id = ?", (order_id,)
        ).fetchone()
        if order_row is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        label = order_row[1]
        windows = connection.execute(
            "SELECT id, numero_en_pedido, ancho_16, alto_16, ensamblada "
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
        "cliente": None if order_row[3] is None else {
            "nombre": order_row[3], "apellido_1": order_row[4], "apellido_2": order_row[5] or "",
            "celular": order_row[6], "direccion": order_row[7] or "",
        },
        "notas": order_row[2] or "",
        "ventanas": [
            {
                "id": window_id,
                "numero": number,
                "codigo": f"{label}{number}" if label is not None else None,
                "ancho": format_measure(width),
                "alto": format_measure(height),
                "ensamblada": bool(assembled),
                "plan_aluminio": plans[window_id],
                "avance_aluminio": progress[window_id],
                "plan_vidrio": glass_plans.get(window_id),
                "avance_vidrio": glass_progress.get(window_id),
            }
            for window_id, number, width, height, assembled in windows
        ],
    }


@app.put("/api/ventanas/{window_id}/medidas")
def correct_window_measures(window_id: int, correction: WindowCorrection):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            return _apply_window_measure_correction(
                connection,
                window_id,
                correction.ancho,
                correction.alto,
                correction.confirmar_correccion,
            )


@app.put("/api/pedidos/{order_id}/medidas")
def correct_order_window_measures(order_id: int, correction: OrderWindowCorrection):
    if not correction.ventanas:
        raise HTTPException(status_code=422, detail="Selecciona al menos una ventana para corregir.")
    window_ids = [item.id for item in correction.ventanas]
    if len(window_ids) != len(set(window_ids)):
        raise HTTPException(status_code=422, detail="No repitas una ventana en la corrección.")
    if not correction.confirmar_correccion:
        raise HTTPException(status_code=409, detail="Confirma las ventanas que vas a corregir antes de guardar.")

    results = []
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            if connection.execute("SELECT 1 FROM pedidos WHERE id = ?", (order_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
            for item in correction.ventanas:
                results.append(_apply_window_measure_correction(
                    connection, item.id, item.ancho, item.alto, True, order_id=order_id,
                ))
    return {"pedido_id": order_id, "resultados": results}


def _apply_window_measure_correction(
    connection: sqlite3.Connection,
    window_id: int,
    width_text: str,
    height_text: str,
    confirmed: bool,
    order_id: int | None = None,
):
    try:
        width = parse_measure(width_text.strip())
        height = parse_measure(height_text.strip())
        aluminum = calcular_plan_aluminio(width, height)
        glass_width, glass_height, glass_quantity = calcular_plan_vidrio(width, height)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=f"Ventana {window_id}: {error}") from error

    query = "SELECT ancho_16, alto_16, ensamblada FROM ventanas WHERE id = ?"
    if order_id is not None:
        query = "SELECT ancho_16, alto_16, ensamblada FROM ventanas WHERE id = ? AND pedido_id = ?"
        window = connection.execute(query, (window_id, order_id)).fetchone()
    else:
        window = connection.execute(query, (window_id,)).fetchone()
    if window is None:
        raise HTTPException(status_code=404, detail=f"Ventana {window_id} no encontrada en este pedido.")
    if (window[0], window[1]) == (width, height):
        raise HTTPException(status_code=422, detail=f"Ventana {window_id}: las medidas nuevas son iguales a las actuales.")

    old_aluminum = connection.execute(
        "SELECT orden, perfil, longitud_16, cantidad, cortadas "
        "FROM plan_aluminio WHERE ventana_id = ? ORDER BY orden",
        (window_id,),
    ).fetchall()
    old_glass = connection.execute(
        "SELECT ancho_16, alto_16, cantidad, cortadas FROM plan_vidrio WHERE ventana_id = ?",
        (window_id,),
    ).fetchone()
    if (len(old_aluminum) != 10 or {row[0] for row in old_aluminum} != set(range(1, 11))
            or old_glass is None):
        raise HTTPException(status_code=409, detail="No se puede corregir: el plan de corte está incompleto.")

    aluminum_cut_count = sum(row[4] for row in old_aluminum)
    glass_cut_count = old_glass[3]
    if not confirmed:
        raise HTTPException(
            status_code=409,
            detail=(f"La ventana tiene {aluminum_cut_count} cortes de aluminio y "
                    f"{glass_cut_count} cortes de vidrio marcados. Confirma para recalcular el plan."),
        )

    old_marks_by_piece = {}
    for _, profile, length, _, cut in old_aluminum:
        key = (profile, length)
        old_marks_by_piece[key] = old_marks_by_piece.get(key, 0) + cut

    preserved_aluminum = 0
    updated_aluminum = []
    for order, (profile, length, quantity) in enumerate(aluminum, start=1):
        preserved = min(old_marks_by_piece.get((profile, length), 0), quantity)
        preserved_aluminum += preserved
        updated_aluminum.append((window_id, order, profile, length, quantity, preserved))

    glass_unchanged = (old_glass[0], old_glass[1]) == (glass_width, glass_height)
    preserved_glass = min(old_glass[3], glass_quantity) if glass_unchanged else 0
    cleared_marks = aluminum_cut_count + glass_cut_count - preserved_aluminum - preserved_glass
    assembly_was_marked = bool(window[2])

    connection.execute(
        "UPDATE ventanas SET ancho_16 = ?, alto_16 = ?, ensamblada = 0 WHERE id = ?",
        (width, height, window_id),
    )
    connection.execute("DELETE FROM plan_aluminio WHERE ventana_id = ?", (window_id,))
    connection.executemany(
        "INSERT INTO plan_aluminio "
        "(ventana_id, orden, perfil, longitud_16, cantidad, cortadas) VALUES (?, ?, ?, ?, ?, ?)",
        updated_aluminum,
    )
    connection.execute(
        "UPDATE plan_vidrio SET ancho_16 = ?, alto_16 = ?, cantidad = ?, cortadas = ? WHERE ventana_id = ?",
        (glass_width, glass_height, glass_quantity, preserved_glass, window_id),
    )
    return {
        "id": window_id,
        "ancho": format_measure(width),
        "alto": format_measure(height),
        "marcas_aluminio_conservadas": preserved_aluminum,
        "marcas_vidrio_conservadas": preserved_glass,
        "marcas_retiradas": cleared_marks,
        "ensamble_reiniciado": assembly_was_marked,
    }


@app.put("/api/pedidos/{order_id}/cliente")
def save_order_client(order_id: int, details: OrderClient):
    name = details.nombre.strip()
    first_surname = details.apellido_1.strip()
    phone = details.celular.strip()
    if not name or not first_surname:
        raise HTTPException(status_code=422, detail="Completa nombre y primer apellido del cliente.")
    for value, field in ((name, "nombre"), (first_surname, "primer apellido"),
                         (details.apellido_2, "segundo apellido")):
        if any(character.isnumeric() for character in value):
            raise HTTPException(status_code=422, detail=f"El {field} no puede contener números.")
    if len(phone) != 10 or not phone.isascii() or not phone.isdigit():
        raise HTTPException(status_code=422, detail="El celular debe tener diez dígitos.")

    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            order = connection.execute("SELECT cliente_id FROM pedidos WHERE id = ?", (order_id,)).fetchone()
            if order is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
            client_values = (name, first_surname, details.apellido_2.strip() or None,
                             phone, details.direccion.strip() or None)
            if order[0] is None:
                cursor = connection.execute(
                    "INSERT INTO clientes (nombre, apellido_1, apellido_2, celular, direccion) "
                    "VALUES (?, ?, ?, ?, ?)", client_values,
                )
                connection.execute(
                    "UPDATE pedidos SET cliente_id = ?, notas = ? WHERE id = ?",
                    (cursor.lastrowid, details.notas.strip() or None, order_id),
                )
            else:
                connection.execute(
                    "UPDATE clientes SET nombre = ?, apellido_1 = ?, apellido_2 = ?, "
                    "celular = ?, direccion = ? WHERE id = ?",
                    (*client_values, order[0]),
                )
                connection.execute("UPDATE pedidos SET notas = ? WHERE id = ?",
                                   (details.notas.strip() or None, order_id))
    return {"id": order_id}


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
            if difference < 0 and connection.execute(
                "SELECT ensamblada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()[0]:
                raise HTTPException(status_code=409, detail="Deshaz primero la marca de ensamble de esta ventana.")
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
            if difference < 0 and connection.execute(
                "SELECT ensamblada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()[0]:
                raise HTTPException(status_code=409, detail="Deshaz primero la marca de ensamble de esta ventana.")
            required, cut = row
            updated = cut + difference
            if not 0 <= updated <= required:
                raise HTTPException(status_code=409, detail="No se puede registrar esa marca de corte.")
            connection.execute(
                "UPDATE plan_vidrio SET cortadas = ? WHERE ventana_id = ?",
                (updated, window_id),
            )
    return {"requeridas": required, "cortadas": updated, "pendientes": required - updated}


@app.post("/api/ventanas/{window_id}/ensamble/marcas")
def mark_assembly(window_id: int, mark: AssemblyMark):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            row = connection.execute(
                "SELECT ensamblada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Ventana no encontrada.")
            assembled = bool(row[0])
            if (mark.accion == "marcar") == assembled:
                raise HTTPException(status_code=409, detail="La ventana ya tiene ese estado de ensamble.")
            if mark.accion == "marcar":
                aluminum = connection.execute(
                    "SELECT orden, cantidad, cortadas FROM plan_aluminio WHERE ventana_id = ?",
                    (window_id,),
                ).fetchall()
                glass = connection.execute(
                    "SELECT cantidad, cortadas FROM plan_vidrio WHERE ventana_id = ?",
                    (window_id,),
                ).fetchone()
                if (len(aluminum) != 10 or {item[0] for item in aluminum} != set(range(1, 11))
                        or glass is None or any(cut != required for _, required, cut in aluminum)
                        or glass[1] != glass[0]):
                    raise HTTPException(
                        status_code=409,
                        detail="Completa primero todos los cortes de aluminio y vidrio de esta ventana.",
                    )
            connection.execute(
                "UPDATE ventanas SET ensamblada = ? WHERE id = ?",
                (int(mark.accion == "marcar"), window_id),
            )
    return {"ensamblada": mark.accion == "marcar"}


@app.get("/pedidos/{order_id}", include_in_schema=False)
def order_page(order_id: int):
    return FileResponse(WEB / "index.html")


@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(WEB / "index.html")
