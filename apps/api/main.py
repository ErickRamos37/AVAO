"""Primer recorrido vertical de HU-01: guardar y reabrir un pedido."""

import json
import os
from pathlib import Path
import sqlite3
from contextlib import closing, nullcontext
from typing import Literal
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictStr, StrictInt

from apps.api.medidas import format_measure, parse_measure
from apps.api.costos_insumos import INSUMOS, INSUMOS_POR_CODIGO, cents_from_input, serialize_cost
from apps.api.costos_ventana import calculate_window_material_cost
from apps.api.merma import calcular_merma
from apps.api.merma_vidrio import calcular_merma_vidrio
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


class CostUpdate(BaseModel):
    costo: StrictStr


class InventoryUpdate(BaseModel):
    costos: dict[str, StrictStr] = {}
    porcentaje_ganancia: StrictInt | None = None
    umbral_merma: StrictInt | None = None
    umbral_merma_vidrio: StrictInt | None = None
    anticipo_minimo: StrictInt | None = None


class MovementInput(BaseModel):
    tipo: Literal["pago", "devolucion"]
    importe: StrictStr


class InstallationUpdate(BaseModel):
    instalado: bool
    confirmar_desmarcado: bool = False


class InstallationDateUpdate(BaseModel):
    fecha: StrictStr


class DeliveryUpdate(BaseModel):
    importe: StrictStr | None


class WasteSelection(BaseModel):
    incluida: bool


class WindowDiscard(BaseModel):
    descartada: bool
    confirmar_descarte: bool = False


def database_path() -> Path:
    return Path(os.environ.get("AVAO_DB_PATH", ROOT / "data" / "avao.sqlite3"))


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path(), timeout=5)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def window_plan_fingerprint(aluminum: list[dict], glass: dict | None) -> str:
    return json.dumps({"aluminio": aluminum, "vidrio": glass}, sort_keys=True, ensure_ascii=False)


@app.get("/api/costos-insumos")
def list_costs():
    with closing(connect_db()) as connection:
        saved = dict(connection.execute(
            "SELECT codigo, costo_centavos FROM costos_insumos"
        ).fetchall())
        percentage = connection.execute("SELECT porcentaje FROM configuracion_ganancia WHERE id = 1").fetchone()[0]
        threshold = connection.execute("SELECT umbral FROM configuracion_merma WHERE id = 1").fetchone()[0]
        glass_threshold = connection.execute("SELECT umbral FROM configuracion_merma_vidrio WHERE id = 1").fetchone()[0]
        advance = connection.execute("SELECT porcentaje FROM configuracion_anticipo WHERE id = 1").fetchone()[0]
    return {"insumos": [
        serialize_cost(item, saved.get(item[0])) for item in INSUMOS
    ], "porcentaje_ganancia": percentage, "umbral_merma": threshold, "umbral_merma_vidrio": glass_threshold, "anticipo_minimo": advance}


@app.put("/api/costos-insumos")
def update_inventory(update: InventoryUpdate):
    # Validate every change before writing any of them.
    costs = {}
    for code, value in update.costos.items():
        if code not in INSUMOS_POR_CODIGO:
            raise HTTPException(status_code=404, detail="Insumo no encontrado.")
        costs[code] = cents_from_input(value)
    percentage = update.porcentaje_ganancia
    if ("porcentaje_ganancia" in update.model_fields_set and percentage is None) or (percentage is not None and not 1 <= percentage <= 100):
        raise HTTPException(status_code=422, detail="La ganancia debe ser un entero de 1 a 100.")
    threshold = update.umbral_merma
    if ("umbral_merma" in update.model_fields_set and threshold is None) or (threshold is not None and not 0 <= threshold <= 100):
        raise HTTPException(status_code=422, detail="El umbral de merma debe ser un entero de 0 a 100.")
    glass_threshold = update.umbral_merma_vidrio
    if ("umbral_merma_vidrio" in update.model_fields_set and glass_threshold is None) or (glass_threshold is not None and not 0 <= glass_threshold <= 100):
        raise HTTPException(status_code=422, detail="El umbral de vidrio debe ser un entero de 0 a 100.")
    advance = update.anticipo_minimo
    if ("anticipo_minimo" in update.model_fields_set and advance is None) or (advance is not None and not 1 <= advance <= 100):
        raise HTTPException(status_code=422, detail="El anticipo mínimo debe ser un entero de 1 a 100.")
    with closing(connect_db()) as connection:
        with connection:
            for code, cents in costs.items():
                cursor = connection.execute("UPDATE costos_insumos SET costo_centavos = ? WHERE codigo = ?", (cents, code))
                if cursor.rowcount != 1:
                    raise HTTPException(status_code=503, detail="Inicializa la base de datos antes de guardar costos.")
            if percentage is not None:
                cursor = connection.execute("UPDATE configuracion_ganancia SET porcentaje = ? WHERE id = 1", (percentage,))
                if cursor.rowcount != 1:
                    raise HTTPException(status_code=503, detail="Inicializa la base de datos antes de guardar la ganancia.")
            if threshold is not None:
                connection.execute("UPDATE configuracion_merma SET umbral = ? WHERE id = 1", (threshold,))
            if glass_threshold is not None:
                connection.execute("UPDATE configuracion_merma_vidrio SET umbral = ? WHERE id = 1", (glass_threshold,))
            if advance is not None:
                connection.execute("UPDATE configuracion_anticipo SET porcentaje = ? WHERE id = 1", (advance,))
    return list_costs()


@app.put("/api/costos-insumos/{codigo}")
def update_cost(codigo: str, update: CostUpdate):
    item = INSUMOS_POR_CODIGO.get(codigo)
    if item is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado.")
    cents = cents_from_input(update.costo)
    with closing(connect_db()) as connection:
        with connection:
            cursor = connection.execute(
                "UPDATE costos_insumos SET costo_centavos = ? WHERE codigo = ?",
                (cents, codigo),
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=503, detail="Inicializa la base de datos antes de guardar costos.")
    return serialize_cost(item, cents)


def require_open_order(connection, order_id):
    row = connection.execute("SELECT fecha_cierre FROM pedidos WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    if row[0] is not None:
        raise HTTPException(status_code=409, detail="El pedido finalizado es de solo lectura.")


def simplify_closed_snapshots(connection, order_id):
    rows = connection.execute(
        "SELECT c.ventana_id, c.resultado_json FROM costos_ventana c "
        "JOIN ventanas v ON v.id = c.ventana_id WHERE v.pedido_id = ?", (order_id,)
    ).fetchall()
    for window_id, result_json in rows:
        result = json.loads(result_json)
        summary = {key: result[key] for key in ("costo_base", "porcentaje_ganancia", "ganancia", "precio") if key in result}
        connection.execute("UPDATE costos_ventana SET resultado_json = ?, plan_fingerprint = '' WHERE ventana_id = ?",
                           (json.dumps(summary, ensure_ascii=False), window_id))
    for table in ("merma_pedido", "merma_vidrio_pedido"):
        connection.execute(f"UPDATE {table} SET detalle_json = '[]' WHERE pedido_id = ?", (order_id,))


def record_event(connection, order_id, kind):
    connection.execute("INSERT INTO eventos_pedido (pedido_id, tipo, fecha_hora) VALUES (?, ?, ?)",
                       (order_id, kind, datetime.now(ZoneInfo("America/Tijuana")).isoformat(timespec="seconds")))


def record_settlement_change(connection, order_id, before):
    after = _get_order(order_id, connection)["liquidado"]
    if before != after:
        record_event(connection, order_id, "liquidado" if after else "liquidacion_perdida")


def record_production(connection, window_id, area, order, action):
    order_id = connection.execute("SELECT pedido_id FROM ventanas WHERE id = ?", (window_id,)).fetchone()[0]
    original = None
    if action == "deshacer":
        row = connection.execute(
            "SELECT evento_id FROM marcas_fabricacion_vigentes WHERE ventana_id = ? AND area = ? AND orden = ? ORDER BY evento_id DESC LIMIT 1",
            (window_id, area, order),
        ).fetchone()
        if row:
            original = row[0]
            connection.execute("DELETE FROM marcas_fabricacion_vigentes WHERE evento_id = ?", (original,))
    cursor = connection.execute(
        "INSERT INTO eventos_fabricacion (pedido_id, ventana_id, area, accion, fecha_hora, original_id) VALUES (?, ?, ?, ?, ?, ?)",
        (order_id, window_id, area, action, datetime.now(ZoneInfo("America/Tijuana")).isoformat(timespec="seconds"), original),
    )
    if action == "marcar":
        connection.execute("INSERT INTO marcas_fabricacion_vigentes VALUES (?, ?, ?, ?)", (cursor.lastrowid, window_id, area, order))


def close_order(connection, order_id):
    today = datetime.now(ZoneInfo("America/Tijuana")).date().isoformat()
    record_event(connection, order_id, "cierre")
    simplify_closed_snapshots(connection, order_id)
    connection.execute("DELETE FROM marcas_fabricacion_vigentes WHERE ventana_id IN (SELECT id FROM ventanas WHERE pedido_id = ?)", (order_id,))
    connection.execute("UPDATE pedidos SET fecha_cierre = ?, etiqueta = NULL WHERE id = ?", (today, order_id))
    for table in ("plan_aluminio", "plan_vidrio"):
        connection.execute(f"DELETE FROM {table} WHERE ventana_id IN (SELECT id FROM ventanas WHERE pedido_id = ?)", (order_id,))
    connection.execute("UPDATE ventanas SET ensamblada = 0 WHERE pedido_id = ?", (order_id,))


@app.post("/api/ventanas/{window_id}/costo-materiales")
def calculate_window_cost(window_id: int):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        parent = connection.execute("SELECT pedido_id FROM ventanas WHERE id = ?", (window_id,)).fetchone()
        if parent:
            require_open_order(connection, parent[0])
        window = connection.execute(
            "SELECT ancho_16, alto_16 FROM ventanas WHERE id = ?", (window_id,)
        ).fetchone()
        if window is None:
            raise HTTPException(status_code=404, detail="Ventana no encontrada.")
        aluminum = [
            {"perfil": profile, "longitud_16": length, "cantidad": quantity}
            for profile, length, quantity in connection.execute(
                "SELECT perfil, longitud_16, cantidad FROM plan_aluminio "
                "WHERE ventana_id = ? ORDER BY orden", (window_id,)
            ).fetchall()
        ]
        glass_row = connection.execute(
            "SELECT ancho_16, alto_16, cantidad FROM plan_vidrio WHERE ventana_id = ?",
            (window_id,),
        ).fetchone()
        glass = None if glass_row is None else {
            "ancho_16": glass_row[0], "alto_16": glass_row[1], "cantidad": glass_row[2],
        }
        costs = dict(connection.execute(
            "SELECT codigo, costo_centavos FROM costos_insumos"
        ).fetchall())
        result = calculate_window_material_cost(
            aluminum, glass, costs, width_16=window[0], height_16=window[1]
        )
        if not result["completo"]:
            return result
        percentage = connection.execute("SELECT porcentaje FROM configuracion_ganancia WHERE id = 1").fetchone()[0]
        base = Decimal(result["costo_base"])
        profit = base * Decimal(percentage) / 100
        result.update(porcentaje_ganancia=percentage, ganancia=str(profit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                      precio=str((base + profit).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        fingerprint = window_plan_fingerprint(aluminum, glass)
        with connection:
            before = _get_order(parent[0], connection)["liquidado"]
            connection.execute(
                "INSERT INTO costos_ventana (ventana_id, plan_fingerprint, resultado_json) "
                "VALUES (?, ?, ?) ON CONFLICT(ventana_id) DO UPDATE SET "
                "plan_fingerprint = excluded.plan_fingerprint, resultado_json = excluded.resultado_json",
                (window_id, fingerprint, json.dumps(result, ensure_ascii=False)),
            )
            record_settlement_change(connection, parent[0], before)
    return {**result, "vigente": True}


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


def assign_order_label(connection, order_id):
    used = {row[0] for row in connection.execute("SELECT etiqueta FROM pedidos WHERE etiqueta IS NOT NULL")}
    label = following_label(None)
    while label in used:
        label = following_label(label)
    connection.execute("UPDATE pedidos SET etiqueta = ? WHERE id = ?", (label, order_id))


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

    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            cursor = connection.execute("INSERT INTO pedidos DEFAULT VALUES")
            order_id = cursor.lastrowid
            record_event(connection, order_id, "presupuesto_creado")
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
            "SELECT p.id, p.etiqueta, v.numero_en_pedido, EXISTS(SELECT 1 FROM aceptaciones a WHERE a.pedido_id = p.id) "
            "FROM pedidos AS p LEFT JOIN ventanas AS v ON v.pedido_id = p.id AND v.descartada = 0 "
            "WHERE p.fecha_cierre IS NULL ORDER BY p.id ASC, v.numero_en_pedido ASC"
        ).fetchall()
    orders = {}
    for order_id, label, number, accepted in rows:
        if order_id not in orders:
            orders[order_id] = {"id": order_id, "etiqueta": label, "codigos": [], "aceptado": bool(accepted)}
        if label is not None and number is not None:
            orders[order_id]["codigos"].append(f"{label}{number}")
    return {"pedidos": list(orders.values())}


@app.get("/api/pedidos/avance")
def list_order_progress():
    """Summarize active workshop work without storing a second progress state."""
    orders = []
    for order in list_orders()["pedidos"]:
        if not order["aceptado"]:
            continue
        details = get_order(order["id"])
        windows = details["ventanas"]
        aluminum_done = sum(
            cut["cortadas"] for window in windows for cut in window["avance_aluminio"]
        )
        aluminum_required = sum(
            cut["cantidad"] for window in windows for cut in window["plan_aluminio"]
        )
        glass_done = sum(window["avance_vidrio"]["cortadas"] for window in windows if window["avance_vidrio"])
        glass_required = sum(window["plan_vidrio"]["cantidad"] for window in windows if window["plan_vidrio"])
        assembly_done = sum(window["ensamblada"] for window in windows)
        assembly_required = len(windows)
        has_aluminum = bool(windows) and all(window["plan_aluminio"] for window in windows)
        has_glass = bool(windows) and all(window["plan_vidrio"] for window in windows)
        has_plan = has_aluminum and has_glass

        def area(done: int, required: int, available: bool):
            return {
                "hechas": done,
                "requeridas": required,
                "porcentaje": round(done / required * 100) if available and required else None,
            }

        aluminum = area(aluminum_done, aluminum_required, has_aluminum)
        glass = area(glass_done, glass_required, has_glass)
        assembly = area(assembly_done, assembly_required, bool(windows))
        ratios = [
            aluminum_done / aluminum_required if aluminum["porcentaje"] is not None else None,
            glass_done / glass_required if glass["porcentaje"] is not None else None,
            assembly_done / assembly_required if assembly["porcentaje"] is not None else None,
        ]
        orders.append({
            "id": order["id"],
            "etiqueta": order["etiqueta"],
            "sin_ventanas": not windows,
            "sin_plan": bool(windows) and not has_plan,
            "porcentaje": round(sum(ratios) / 3 * 100) if all(value is not None for value in ratios) else None,
            "listo_instalacion": bool(windows) and assembly_done == assembly_required and has_plan,
            "instalado": details["instalado"],
            "aluminio": aluminum,
            "vidrio": glass,
            "ensamble": assembly,
        })
    return {"pedidos": orders}


@app.get("/api/pedidos/historico")
def list_history():
    with closing(connect_db()) as connection:
        rows = connection.execute("SELECT id, fecha_cierre FROM pedidos WHERE fecha_cierre IS NOT NULL ORDER BY fecha_cierre DESC, id DESC").fetchall()
    return {"pedidos": [{"id": row[0], "fecha_cierre": row[1]} for row in rows]}


@app.get("/api/pedidos/{order_id}")
def get_order(order_id: int):
    return _get_order(order_id)


def _get_order(order_id, existing_connection=None):
    with (nullcontext(existing_connection) if existing_connection else closing(connect_db())) as connection:
        order_row = connection.execute(
            "SELECT p.id, p.etiqueta, p.notas, c.nombre, c.apellido_1, c.apellido_2, "
            "c.celular, c.direccion, p.traslado_centavos, p.fecha_programada, p.instalado, p.fecha_real, p.fecha_cierre FROM pedidos AS p "
            "LEFT JOIN clientes AS c ON c.id = p.cliente_id WHERE p.id = ?", (order_id,)
        ).fetchone()
        if order_row is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        label = order_row[1]
        windows = connection.execute(
            "SELECT id, numero_en_pedido, ancho_16, alto_16, ensamblada, descartada "
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
        waste_row = connection.execute("SELECT cargo_centavos, incluida, detalle_json FROM merma_pedido WHERE pedido_id = ?", (order_id,)).fetchone()
        accepted = connection.execute("SELECT 1 FROM aceptaciones WHERE pedido_id = ?", (order_id,)).fetchone() is not None
        movement_rows = connection.execute("SELECT id, tipo, importe_centavos, fecha, anulado, fecha_anulacion FROM movimientos WHERE pedido_id = ? ORDER BY id", (order_id,)).fetchall()
        events = connection.execute("SELECT tipo, fecha_hora FROM eventos_pedido WHERE pedido_id = ? ORDER BY id", (order_id,)).fetchall()
        production = connection.execute(
            "SELECT e.id, e.ventana_id, v.numero_en_pedido, e.area, e.accion, e.fecha_hora, e.original_id, "
            "EXISTS(SELECT 1 FROM eventos_fabricacion c WHERE c.original_id = e.id) "
            "FROM eventos_fabricacion e JOIN ventanas v ON v.id = e.ventana_id WHERE e.pedido_id = ? ORDER BY e.id", (order_id,)
        ).fetchall()
        measure_changes = connection.execute(
            "SELECT c.fecha_hora, v.numero_en_pedido, c.ancho_anterior_16, c.alto_anterior_16, "
            "c.ancho_nuevo_16, c.alto_nuevo_16, c.afectadas_json "
            "FROM cambios_medidas c JOIN ventanas v ON v.id = c.ventana_id "
            "WHERE v.pedido_id = ? ORDER BY c.id", (order_id,)
        ).fetchall()
        minimum = connection.execute("SELECT porcentaje FROM configuracion_anticipo WHERE id = 1").fetchone()[0]
        glass_waste_row = connection.execute("SELECT cargo_centavos, incluida, detalle_json FROM merma_vidrio_pedido WHERE pedido_id = ?", (order_id,)).fetchone()
        cost_rows = connection.execute(
            "SELECT c.ventana_id, c.plan_fingerprint, c.resultado_json "
            "FROM costos_ventana AS c JOIN ventanas AS v ON v.id = c.ventana_id "
            "WHERE v.pedido_id = ?", (order_id,)
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
    aluminum_for_cost = {window_id: [] for window_id, *_ in windows}
    for window_id, _, profile, length, quantity, _ in plan_rows:
        aluminum_for_cost[window_id].append({
            "perfil": profile, "longitud_16": length, "cantidad": quantity,
        })
    glass_for_cost = {
        window_id: {"ancho_16": width, "alto_16": height, "cantidad": quantity}
        for window_id, width, height, quantity, _ in glass_rows
    }
    saved_costs = {
        window_id: (fingerprint, json.loads(result_json))
        for window_id, fingerprint, result_json in cost_rows
    }

    window_details = [
        {
            "id": window_id,
            "numero": number,
            "codigo": f"{label}{number}" if label is not None else None,
            "ancho": format_measure(width),
            "alto": format_measure(height),
            "ensamblada": bool(assembled),
            "descartada": bool(discarded),
            "plan_aluminio": plans[window_id],
            "avance_aluminio": progress[window_id],
            "plan_vidrio": glass_plans.get(window_id),
            "avance_vidrio": glass_progress.get(window_id),
            "costo_materiales": (
                None if window_id not in saved_costs else {
                    **saved_costs[window_id][1],
                    "vigente": bool(order_row[12]) or saved_costs[window_id][0] == window_plan_fingerprint(
                        aluminum_for_cost[window_id], glass_for_cost.get(window_id)
                    ),
                }
            ),
        }
        for window_id, number, width, height, assembled, discarded in windows
    ]

    active = [window for window in window_details if not window["descartada"]]
    costs = [window["costo_materiales"] for window in active]
    missing_price = any(cost is None or cost.get("precio") is None for cost in costs)
    priced_costs = [cost for cost in costs if cost is not None and cost.get("precio") is not None]
    total = sum(int(cost["precio"]) for cost in priced_costs) if priced_costs else None

    waste_cents = waste_row[0] if waste_row and waste_row[1] else 0
    waste_cents += glass_waste_row[0] if glass_waste_row and glass_waste_row[1] else 0
    total_cents = None if total is None or missing_price else total * 100 + (order_row[8] or 0) + waste_cents
    net = sum((cents if kind == "pago" else -cents) for _, kind, cents, _, void, _ in movement_rows if not void)
    return {
        "id": order_id,
        "etiqueta": label,
        "aceptado": accepted,
        "eventos": [{"tipo": kind, "fecha_hora": timestamp} for kind, timestamp in events],
        "eventos_fabricacion": [{"id": event_id, "ventana_id": window_id, "ventana": number, "area": area,
                                  "accion": action, "fecha_hora": timestamp, "original_id": original,
                                  "corregido": bool(corrected)}
                                 for event_id, window_id, number, area, action, timestamp, original, corrected in production],
        "cambios_medidas": [
            {"fecha_hora": timestamp, "ventana": number,
             "anterior": {"ancho": format_measure(old_width), "alto": format_measure(old_height)},
             "nueva": {"ancho": format_measure(new_width), "alto": format_measure(new_height)},
             "afectadas": json.loads(affected)}
            for timestamp, number, old_width, old_height, new_width, new_height, affected in measure_changes
        ],
        "fecha_programada": order_row[9],
        "instalado": bool(order_row[10]),
        "fecha_real": order_row[11],
        "fecha_cierre": order_row[12],
        "anticipo_minimo": minimum,
        "anticipo_requerido": None if total_cents is None else f"{Decimal((total_cents * minimum + 99) // 100) / 100:.2f}",
        "movimientos": [{"id": mid, "tipo": kind, "importe": f"{Decimal(cents) / 100:.2f}", "fecha": day, "anulado": bool(void), "fecha_anulacion": void_day} for mid, kind, cents, day, void, void_day in movement_rows],
        "pagado_neto": f"{Decimal(net) / 100:.2f}",
        "saldo": None if total_cents is None else f"{Decimal(max(0, total_cents - net)) / 100:.2f}",
        "excedente": None if total_cents is None else f"{Decimal(max(0, net - total_cents)) / 100:.2f}",
        "liquidado": total_cents is not None and accepted and net >= total_cents,
        "merma_vidrio": None if glass_waste_row is None else {"cargo": f"{Decimal(glass_waste_row[0]) / 100:.2f}", "incluida": bool(glass_waste_row[1]), "detalle": json.loads(glass_waste_row[2])},
        "merma": None if waste_row is None else {"cargo": f"{Decimal(waste_row[0]) / 100:.2f}", "incluida": bool(waste_row[1]), "detalle": None if waste_row[2] is None else json.loads(waste_row[2])},
        "traslado": None if order_row[8] is None else f"{Decimal(order_row[8]) / 100:.2f}",
        "total_pedido": None if total is None else f"{Decimal(total) + Decimal((order_row[8] or 0) + waste_cents) / 100:.2f}",
        "total_ventanas": {
            "importe": total,
            "sin_precio": missing_price,
            "desactualizado": any(cost is not None and not cost["vigente"] for cost in costs),
        },
        "cliente": None if order_row[3] is None else {
            "nombre": order_row[3], "apellido_1": order_row[4], "apellido_2": order_row[5] or "",
            "celular": order_row[6], "direccion": order_row[7] or "",
        },
        "notas": order_row[2] or "",
        "ventanas": active,
        "ventanas_descartadas": [window for window in window_details if window["descartada"]],
    }


@app.post("/api/pedidos/{order_id}/merma")
def calculate_order_waste(order_id: int):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            if connection.execute("SELECT 1 FROM pedidos WHERE id = ?", (order_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
            ids = [row[0] for row in connection.execute("SELECT id FROM ventanas WHERE pedido_id = ? AND descartada = 0", (order_id,))]
            plans = [[{"perfil": name, "longitud_16": length, "cantidad": qty} for name, length, qty in connection.execute(
                "SELECT perfil, longitud_16, cantidad FROM plan_aluminio WHERE ventana_id = ?", (window_id,))] for window_id in ids]
            costs = dict(connection.execute("SELECT codigo, costo_centavos FROM costos_insumos"))
            threshold = connection.execute("SELECT umbral FROM configuracion_merma WHERE id = 1").fetchone()[0]
            cents, details = calcular_merma(plans, costs, threshold, incluir_detalle=True)
            connection.execute("INSERT INTO merma_pedido (pedido_id, cargo_centavos, detalle_json) VALUES (?, ?, ?) "
                               "ON CONFLICT(pedido_id) DO UPDATE SET cargo_centavos = excluded.cargo_centavos, detalle_json = excluded.detalle_json",
                               (order_id, cents, json.dumps(details, ensure_ascii=False)))
            record_settlement_change(connection, order_id, before)
    return get_order(order_id)


@app.put("/api/pedidos/{order_id}/merma")
def select_order_waste(order_id: int, selection: WasteSelection):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            cursor = connection.execute("UPDATE merma_pedido SET incluida = ? WHERE pedido_id = ?", (int(selection.incluida), order_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Calcula primero la merma del pedido.")
            record_settlement_change(connection, order_id, before)
    return get_order(order_id)


@app.post("/api/pedidos/{order_id}/merma-vidrio")
def calculate_order_glass_waste(order_id: int):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            if connection.execute("SELECT 1 FROM pedidos WHERE id = ?", (order_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
            plans = connection.execute(
                "SELECT g.ancho_16, g.alto_16, g.cantidad FROM ventanas v LEFT JOIN plan_vidrio g ON g.ventana_id = v.id "
                "WHERE v.pedido_id = ? AND v.descartada = 0", (order_id,)).fetchall()
            plans = [None if row[0] is None else row for row in plans]
            row = connection.execute("SELECT costo_centavos FROM costos_insumos WHERE codigo = 'vidrio_doble_fuerza'").fetchone()
            threshold = connection.execute("SELECT umbral FROM configuracion_merma_vidrio WHERE id = 1").fetchone()[0]
            cents, details = calcular_merma_vidrio(plans, None if row is None else row[0], threshold)
            connection.execute("INSERT INTO merma_vidrio_pedido (pedido_id, cargo_centavos, detalle_json) VALUES (?, ?, ?) "
                               "ON CONFLICT(pedido_id) DO UPDATE SET cargo_centavos = excluded.cargo_centavos, detalle_json = excluded.detalle_json",
                               (order_id, cents, json.dumps(details, ensure_ascii=False)))
            record_settlement_change(connection, order_id, before)
    return get_order(order_id)


@app.put("/api/pedidos/{order_id}/merma-vidrio")
def select_order_glass_waste(order_id: int, selection: WasteSelection):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            cursor = connection.execute("UPDATE merma_vidrio_pedido SET incluida = ? WHERE pedido_id = ?", (int(selection.incluida), order_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Calcula primero la merma de vidrio del pedido.")
            record_settlement_change(connection, order_id, before)
    return get_order(order_id)


@app.post("/api/pedidos/{order_id}/movimientos")
def add_movement(order_id: int, movement: MovementInput):
    cents = cents_from_input(movement.importe)
    if not 0 < cents <= 9223372036854775807:
        raise HTTPException(status_code=422, detail="Ingresa un importe positivo válido.")
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            order = _get_order(order_id, connection)
            if order["total_pedido"] is None or order["total_ventanas"]["sin_precio"]:
                raise HTTPException(status_code=409, detail="Calcula el precio de todas las ventanas antes de registrar movimientos.")
            total = cents_from_input(order["total_pedido"])
            net = sum((cents_from_input(m["importe"]) if m["tipo"] == "pago" else -cents_from_input(m["importe"])) for m in order["movimientos"] if not m["anulado"])
            if movement.tipo == "devolucion" and cents > max(0, net - total):
                raise HTTPException(status_code=409, detail="La devolución no puede superar el excedente.")
            connection.execute("INSERT INTO movimientos (pedido_id, tipo, importe_centavos, fecha) VALUES (?, ?, ?, ?)", (order_id, movement.tipo, cents, datetime.now(ZoneInfo("America/Tijuana")).date().isoformat()))
            if movement.tipo == "pago" and (net + cents) * 100 >= total * order["anticipo_minimo"]:
                cursor = connection.execute("INSERT OR IGNORE INTO aceptaciones (pedido_id) VALUES (?)", (order_id,))
                if cursor.rowcount:
                    assign_order_label(connection, order_id)
                    record_event(connection, order_id, "aceptado")
            record_settlement_change(connection, order_id, order["liquidado"])
            if order["instalado"] and movement.tipo == "pago" and net + cents >= total:
                close_order(connection, order_id)
    return get_order(order_id)


@app.post("/api/pedidos/{order_id}/movimientos/{movement_id}/anular")
def void_movement(order_id: int, movement_id: int):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            order = _get_order(order_id, connection)
            if order["total_pedido"] is None or order["total_ventanas"]["sin_precio"]:
                raise HTTPException(status_code=409, detail="Calcula el precio de todas las ventanas antes de anular.")
            cursor = connection.execute("UPDATE movimientos SET anulado = 1, fecha_anulacion = ? WHERE id = ? AND pedido_id = ? AND anulado = 0", (datetime.now(ZoneInfo("America/Tijuana")).date().isoformat(), movement_id, order_id))
            if not cursor.rowcount:
                raise HTTPException(status_code=404, detail="Movimiento no encontrado o ya anulado.")
            net = connection.execute("SELECT COALESCE(SUM(CASE tipo WHEN 'pago' THEN importe_centavos ELSE -importe_centavos END), 0) FROM movimientos WHERE pedido_id = ? AND anulado = 0", (order_id,)).fetchone()[0]
            if net * 100 < cents_from_input(order["total_pedido"]) * order["anticipo_minimo"]:
                cursor = connection.execute("DELETE FROM aceptaciones WHERE pedido_id = ?", (order_id,))
                if cursor.rowcount:
                    connection.execute("UPDATE pedidos SET etiqueta = NULL WHERE id = ?", (order_id,))
                    record_event(connection, order_id, "aceptacion_revocada")
            record_settlement_change(connection, order_id, order["liquidado"])
    return get_order(order_id)


@app.put("/api/pedidos/{order_id}/instalacion")
def set_installation(order_id: int, change: InstallationUpdate):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            order = _get_order(order_id, connection)
            if order["instalado"] == change.instalado:
                raise HTTPException(status_code=409, detail="El pedido ya tiene ese estado de instalación.")
            if change.instalado:
                windows = order["ventanas"]
                if not order["aceptado"] or not windows or any(
                    not w["ensamblada"] or len(w["plan_aluminio"]) != 10 or len(w["avance_aluminio"]) != 10
                    or any(cut["pendientes"] != 0 for cut in w["avance_aluminio"])
                    or not w["plan_vidrio"] or not w["avance_vidrio"] or w["avance_vidrio"]["pendientes"] != 0
                    for w in windows
                ):
                    raise HTTPException(status_code=409, detail="Completa todos los cortes y ensambles activos antes de marcar instalado.")
                today = datetime.now(ZoneInfo("America/Tijuana")).date().isoformat()
                connection.execute("UPDATE pedidos SET instalado = 1, fecha_real = ? WHERE id = ?", (today, order_id))
                record_event(connection, order_id, "instalado")
                if order["liquidado"]:
                    close_order(connection, order_id)
            else:
                if not change.confirmar_desmarcado:
                    raise HTTPException(status_code=409, detail="Confirma que deseas desmarcar la instalación.")
                connection.execute("UPDATE pedidos SET instalado = 0, fecha_real = NULL WHERE id = ?", (order_id,))
                record_event(connection, order_id, "instalacion_desmarcada")
    return get_order(order_id)


@app.put("/api/pedidos/{order_id}/fecha-programada")
def update_installation_date(order_id: int, update: InstallationDateUpdate):
    try:
        parsed = date.fromisoformat(update.fecha)
        if parsed.isoformat() != update.fecha:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=422, detail="Ingresa una fecha válida.") from None
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            cursor = connection.execute("UPDATE pedidos SET fecha_programada = ? WHERE id = ?", (update.fecha, order_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return get_order(order_id)


@app.put("/api/pedidos/{order_id}/traslado")
def update_delivery(order_id: int, update: DeliveryUpdate):
    cents = None if update.importe is None else cents_from_input(update.importe)
    if cents is not None and cents > 9223372036854775807:
        raise HTTPException(status_code=422, detail="El importe es demasiado grande.")
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            cursor = connection.execute("UPDATE pedidos SET traslado_centavos = ? WHERE id = ?", (cents, order_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Pedido no encontrado.")
            record_settlement_change(connection, order_id, before)
    return get_order(order_id)


def require_not_installed(connection, window_id):
    installed = connection.execute("SELECT p.instalado FROM pedidos p JOIN ventanas v ON v.pedido_id = p.id WHERE v.id = ?", (window_id,)).fetchone()
    if installed and installed[0]:
        raise HTTPException(status_code=409, detail="Desmarca la instalación antes de modificar ventanas o fabricación.")


@app.put("/api/ventanas/{window_id}/descarte")
def set_window_discard(window_id: int, change: WindowDiscard):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            row = connection.execute(
                "SELECT v.pedido_id, v.numero_en_pedido, v.descartada, p.etiqueta "
                "FROM ventanas AS v JOIN pedidos AS p ON p.id = v.pedido_id WHERE v.id = ?",
                (window_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Ventana no encontrada.")
            order_id, number, discarded, label = row
            require_open_order(connection, order_id)
            before = _get_order(order_id, connection)["liquidado"]
            require_not_installed(connection, window_id)
            if bool(discarded) == change.descartada:
                raise HTTPException(status_code=409, detail="La ventana ya tiene ese estado.")
            if change.descartada and not change.confirmar_descarte:
                raise HTTPException(status_code=409, detail="Confirma el descarte de esta ventana.")
            connection.execute(
                "UPDATE ventanas SET descartada = ? WHERE id = ?",
                (int(change.descartada), window_id),
            )
            record_settlement_change(connection, order_id, before)
    return {
        "pedido_id": order_id,
        "ventana_id": window_id,
        "codigo": f"{label}{number}" if label is not None else None,
        "descartada": change.descartada,
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
            require_open_order(connection, order_id)
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

    query = "SELECT ancho_16, alto_16, ensamblada, descartada FROM ventanas WHERE id = ?"
    if order_id is not None:
        query = "SELECT ancho_16, alto_16, ensamblada, descartada FROM ventanas WHERE id = ? AND pedido_id = ?"
        window = connection.execute(query, (window_id, order_id)).fetchone()
    else:
        window = connection.execute(query, (window_id,)).fetchone()
    if window is None:
        raise HTTPException(status_code=404, detail=f"Ventana {window_id} no encontrada en este pedido.")
    require_not_installed(connection, window_id)
    if window[3]:
        raise HTTPException(status_code=409, detail="Reincorpora la ventana antes de corregir sus medidas.")
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

    accepted = connection.execute(
        "SELECT 1 FROM ventanas v JOIN aceptaciones a ON a.pedido_id = v.pedido_id WHERE v.id = ?", (window_id,)
    ).fetchone()
    if accepted:
        affected = []
        for (_, profile, old_length, _, cut), (new_profile, new_length, _) in zip(old_aluminum, aluminum, strict=True):
            if cut and old_length != new_length:
                affected.append({"tipo": "aluminio", "perfil": profile, "cantidad": cut,
                                 "anterior": format_measure(old_length), "nueva": format_measure(new_length),
                                 "clasificacion": "sobrante recuperable por cambio de medida" if new_length > old_length else "posible recorte"})
        if glass_cut_count and not glass_unchanged:
            affected.append({"tipo": "vidrio", "cantidad": glass_cut_count,
                             "anterior": f"{format_measure(old_glass[0])} × {format_measure(old_glass[1])}",
                             "nueva": f"{format_measure(glass_width)} × {format_measure(glass_height)}",
                             "clasificacion": None})
        connection.execute(
            "INSERT INTO cambios_medidas (ventana_id, fecha_hora, ancho_anterior_16, alto_anterior_16, "
            "ancho_nuevo_16, alto_nuevo_16, afectadas_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (window_id, datetime.now(ZoneInfo("America/Tijuana")).isoformat(timespec="seconds"),
             window[0], window[1], width, height, json.dumps(affected, ensure_ascii=False)),
        )

    # Los cortes afectados siguen en el historial, pero dejan de representar marcas vigentes.
    associations = connection.execute(
        "SELECT m.evento_id, a.perfil, a.longitud_16 FROM marcas_fabricacion_vigentes m "
        "JOIN plan_aluminio a ON a.ventana_id = m.ventana_id AND a.orden = m.orden "
        "WHERE m.ventana_id = ? AND m.area = 'aluminio' ORDER BY m.evento_id DESC", (window_id,)
    ).fetchall()
    connection.execute("DELETE FROM marcas_fabricacion_vigentes WHERE ventana_id = ? AND area IN ('aluminio', 'ensamble')", (window_id,))
    if not glass_unchanged:
        connection.execute("DELETE FROM marcas_fabricacion_vigentes WHERE ventana_id = ? AND area = 'vidrio'", (window_id,))
    grouped = {}
    for event_id, profile, length in associations:
        grouped.setdefault((profile, length), []).append(event_id)
    for _, order, profile, length, _, preserved in updated_aluminum:
        pool = grouped.get((profile, length), [])
        for event_id in pool[:preserved]:
            connection.execute("INSERT INTO marcas_fabricacion_vigentes VALUES (?, ?, 'aluminio', ?)", (event_id, window_id, order))
        del pool[:preserved]

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
            require_open_order(connection, order_id)
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


def require_accepted_window(connection, window_id):
    require_not_installed(connection, window_id)
    if not connection.execute("SELECT 1 FROM ventanas v JOIN aceptaciones a ON a.pedido_id = v.pedido_id WHERE v.id = ?", (window_id,)).fetchone():
        raise HTTPException(status_code=409, detail="Registra el anticipo mínimo antes de marcar fabricación.")


@app.post("/api/ventanas/{window_id}/aluminio/{order}/marcas")
def mark_aluminum(window_id: int, order: int, mark: AluminumMark):
    difference = 1 if mark.accion == "marcar" else -1
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_not_installed(connection, window_id)
            row = connection.execute(
                "SELECT cantidad, cortadas FROM plan_aluminio "
                "WHERE ventana_id = ? AND orden = ?",
                (window_id, order),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Corte de aluminio no encontrado.")
            assembled, discarded = connection.execute(
                "SELECT ensamblada, descartada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()
            if discarded:
                raise HTTPException(status_code=409, detail="Reincorpora la ventana antes de registrar cortes.")
            require_accepted_window(connection, window_id)
            if difference < 0 and assembled:
                raise HTTPException(status_code=409, detail="Deshaz primero la marca de ensamble de esta ventana.")
            required, cut = row
            updated = cut + difference
            if not 0 <= updated <= required:
                raise HTTPException(status_code=409, detail="No se puede registrar esa marca de corte.")
            connection.execute(
                "UPDATE plan_aluminio SET cortadas = ? WHERE ventana_id = ? AND orden = ?",
                (updated, window_id, order),
            )
            record_production(connection, window_id, "aluminio", order, mark.accion)
    return {"orden": order, "requeridas": required, "cortadas": updated, "pendientes": required - updated}


@app.post("/api/ventanas/{window_id}/vidrio/marcas")
def mark_glass(window_id: int, mark: GlassMark):
    difference = 1 if mark.accion == "marcar" else -1
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            require_not_installed(connection, window_id)
            row = connection.execute(
                "SELECT cantidad, cortadas FROM plan_vidrio WHERE ventana_id = ?",
                (window_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Plan de vidrio no encontrado.")
            assembled, discarded = connection.execute(
                "SELECT ensamblada, descartada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()
            if discarded:
                raise HTTPException(status_code=409, detail="Reincorpora la ventana antes de registrar cortes.")
            require_accepted_window(connection, window_id)
            if difference < 0 and assembled:
                raise HTTPException(status_code=409, detail="Deshaz primero la marca de ensamble de esta ventana.")
            required, cut = row
            updated = cut + difference
            if not 0 <= updated <= required:
                raise HTTPException(status_code=409, detail="No se puede registrar esa marca de corte.")
            connection.execute(
                "UPDATE plan_vidrio SET cortadas = ? WHERE ventana_id = ?",
                (updated, window_id),
            )
            record_production(connection, window_id, "vidrio", 0, mark.accion)
    return {"requeridas": required, "cortadas": updated, "pendientes": required - updated}


@app.post("/api/ventanas/{window_id}/ensamble/marcas")
def mark_assembly(window_id: int, mark: AssemblyMark):
    with closing(connect_db()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        with connection:
            row = connection.execute(
                "SELECT ensamblada, descartada FROM ventanas WHERE id = ?", (window_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Ventana no encontrada.")
            if row[1]:
                raise HTTPException(status_code=409, detail="Reincorpora la ventana antes de marcar su ensamble.")
            require_accepted_window(connection, window_id)
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
            record_production(connection, window_id, "ensamble", 0, mark.accion)
    return {"ensamblada": mark.accion == "marcar"}


@app.get("/pedidos/{order_id}", include_in_schema=False)
def order_page(order_id: int):
    return FileResponse(WEB / "index.html")


@app.get("/costos", include_in_schema=False)
def costs_page():
    return FileResponse(WEB / "costos.html")


@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(WEB / "index.html")
