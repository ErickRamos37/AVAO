"""Catálogo acotado de costos de compra para California por mitad (HU-18)."""

from decimal import Decimal, InvalidOperation

from fastapi import HTTPException


# Las presentaciones provienen de docs/domain/CostosInsumosCalifornia.md.
# El valor None representa un costo pendiente; no equivale a cero.
INSUMOS = (
    ("jamba", "Jamba de aluminio", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 42800),
    ("aleta", "Aleta de aluminio", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 36400),
    ("guia_aluminio", "Guía de aluminio", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 42600),
    ("riel", "Riel de aluminio", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 51200),
    ("horizontal_fijo", "Horizontal fijo", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 16800),
    ("horizontal_corredizo", "Horizontal corredizo", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 16000),
    ("mulio", "Mulio", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 33200),
    ("vertical_fijo", "Vertical fijo", "Tramo de 21 pies", "por tramo", 21, "$ / pie lineal", 14900),
    ("moldura_screen", "Moldura de screen", "Tramo de 12 pies", "por tramo", 12, "$ / pie lineal", 11500),
    ("vidrio_doble_fuerza", "Vidrio doble fuerza de 1/8″", "Hoja de 71″ × 102″", "por hoja", Decimal(71 * 102) / 144, "$ / pie cuadrado", 78000),
    ("tela_mosquitera", "Tela mosquitera", "Tarifa directa", "por pie cuadrado", None, None, None),
    ("vinil_doble_fuerza", "Vinil doble fuerza", "Pie lineal", "por pie lineal", None, None, None),
    ("finger", "Finger", "Pie lineal", "por pie lineal", None, None, 44),
    ("felpa", "Felpa", "Pie lineal", "por pie lineal", None, None, 44),
    ("cola_de_rata", "Cola de rata", "Pie lineal", "por pie lineal", None, None, 188),
    ("rodajas", "Rodajas", "Unidad", "por unidad", None, None, 550),
    ("guias_plasticas", "Guías plásticas", "Unidad", "por unidad", None, None, 115),
    ("jaladeras", "Jaladeras", "Unidad", "por unidad", None, None, 1400),
    ("escuadras", "Escuadras", "Unidad", "por unidad", None, None, 300),
    ("chilillos", "Chilillos", "Unidad", "por unidad", None, None, 20),
    ("taquetes", "Taquetes", "Unidad", "por unidad", None, None, 45),
    ("pasta", "Pasta", "Tubo", "por tubo", None, None, 4700),
)

INSUMOS_POR_CODIGO = {item[0]: item for item in INSUMOS}


def cents_from_input(value: str) -> int:
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise HTTPException(status_code=422, detail="Ingresa un costo numérico válido.") from None
    if not amount.is_finite() or amount < 0:
        raise HTTPException(status_code=422, detail="El costo debe ser un importe no negativo.")
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise HTTPException(status_code=422, detail="El costo admite hasta dos decimales.")
    return int(cents)


def serialize_cost(item: tuple, cents: int | None) -> dict:
    code, name, purchase, cost_unit, divisor, derived_unit, initial_cents = item
    result = {
        "codigo": code,
        "nombre": name,
        "presentacion_compra": purchase,
        "unidad_costo": cost_unit,
        "costo_compra": None if cents is None else f"{Decimal(cents) / 100:.2f}",
        "costo_derivado": None,
        "unidad_derivada": derived_unit,
    }
    if cents is None:
        return result
    purchase_cost = Decimal(cents) / 100
    if divisor is not None:
        result["costo_derivado"] = f"{(purchase_cost / divisor):.2f}"
    return result
