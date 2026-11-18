"""Cálculo exacto del costo de materiales de una ventana California por mitad."""

from decimal import Decimal, ROUND_HALF_UP, localcontext

from apps.api.costos_insumos import INSUMOS_POR_CODIGO


PERFILES = {
    "Jamba": "jamba",
    "Aleta": "aleta",
    "Guía": "guia_aluminio",
    "Riel": "riel",
    "Horizontal fijo": "horizontal_fijo",
    "Horizontal corredizo": "horizontal_corredizo",
    "Mulio": "mulio",
    "Vertical fijo": "vertical_fijo",
    "Screen ancho": "moldura_screen",
    "Screen alto": "moldura_screen",
}
PERFILES_REQUERIDOS = frozenset(PERFILES)

UNIDADES_POR_VENTANA = {
    "rodajas": Decimal("2"),
    "guias_plasticas": Decimal("4"),
    "jaladeras": Decimal("1"),
    "escuadras": Decimal("4"),
    "chilillos": Decimal("24"),
    "taquetes": Decimal("4"),
}


def _cents_per_unit(costs: dict[str, int | None], code: str) -> Decimal | None:
    cents = costs.get(code)
    return None if cents is None else Decimal(cents)


def _linear_rate_cents(costs: dict[str, int | None], code: str) -> Decimal | None:
    """Return the unrounded cost per foot, deriving it from a segment if needed."""
    purchase_cost = _cents_per_unit(costs, code)
    if purchase_cost is None:
        return None
    purchase_length = INSUMOS_POR_CODIGO[code][4]
    return purchase_cost if purchase_length is None else purchase_cost / Decimal(purchase_length)


def _measure_cost(
    costs: dict[str, int | None], code: str, quantity_16: int
) -> Decimal | None:
    """Cost of a length in sixteenths of an inch against a per-foot rate."""
    rate = _linear_rate_cents(costs, code)
    if rate is None:
        return None
    return rate * Decimal(quantity_16) / Decimal(192)


def _format_quantity(value: Decimal) -> str:
    rounded = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    formatted = format(rounded, "f")
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted


def _calculate_window_material_cost(
    aluminum_plan: list[dict],
    glass_plan: dict | None,
    costs: dict[str, int | None],
    *,
    width_16: int,
    height_16: int,
) -> dict:
    """Return a complete cost, or only missing rates (never partial amounts).

    `costs` contains original purchase costs in cents, keyed by catalog code.
    Plan dimensions and lengths use the database's 1/16-inch integer units.
    """
    if (len(aluminum_plan) != 10 or glass_plan is None
            or {row.get("perfil") for row in aluminum_plan} != PERFILES_REQUERIDOS):
        return {"completo": False, "faltantes": ["Plan de corte completo"]}

    row_by_name = {row["perfil"]: row for row in aluminum_plan}
    required_codes = set(UNIDADES_POR_VENTANA)
    required_codes.update(("finger", "felpa", "cola_de_rata", "vinil_doble_fuerza", "tela_mosquitera", "vidrio_doble_fuerza", "pasta"))
    required_codes.update(PERFILES.values())
    missing = [
        INSUMOS_POR_CODIGO[code][1]
        for code in sorted(required_codes)
        if _cents_per_unit(costs, code) is None
    ]
    if missing:
        return {"completo": False, "faltantes": missing}

    details: list[tuple[str, Decimal, Decimal, str]] = []

    for row in aluminum_plan:
        code = PERFILES[row["perfil"]]
        length_16 = int(row["longitud_16"])
        piece_count = int(row["cantidad"])
        total_length_16 = length_16 * piece_count
        quantity = Decimal(total_length_16) / Decimal(192)
        details.append((code, quantity, _measure_cost(costs, code, total_length_16), "pie lineal"))

    glass_quantity = int(glass_plan["cantidad"])
    glass_area_sqft = (
        Decimal(int(glass_plan["ancho_16"]))
        * Decimal(int(glass_plan["alto_16"]))
        * Decimal(glass_quantity)
        / Decimal(256 * 144)
    )
    glass_sheet_area_sqft = Decimal(71 * 102) / Decimal(144)
    glass_cost_cents = Decimal(costs["vidrio_doble_fuerza"]) * glass_area_sqft / glass_sheet_area_sqft
    details.append(("vidrio_doble_fuerza", glass_area_sqft, glass_cost_cents, "pie cuadrado"))

    screen_width_16 = int(row_by_name["Screen ancho"]["longitud_16"])
    screen_height_16 = int(row_by_name["Screen alto"]["longitud_16"])
    screen_width_count = int(row_by_name["Screen ancho"]["cantidad"])
    screen_height_count = int(row_by_name["Screen alto"]["cantidad"])
    screen_width_inches = Decimal(screen_width_16) / Decimal(16)
    screen_height_inches = Decimal(screen_height_16) / Decimal(16)
    screen_area_sqft = screen_width_inches * screen_height_inches / Decimal(144)
    details.append(("tela_mosquitera", screen_area_sqft,
                    screen_area_sqft * Decimal(costs["tela_mosquitera"]), "pie cuadrado"))

    # Linear consumables are priced by exact total length in feet.
    linear_consumptions = {
        "finger": 2 * int(row_by_name["Horizontal fijo"]["longitud_16"])
        + 2 * int(row_by_name["Vertical fijo"]["longitud_16"]),
        "felpa": 2 * int(row_by_name["Aleta"]["longitud_16"])
        + 2 * int(row_by_name["Horizontal corredizo"]["longitud_16"]),
        "cola_de_rata": screen_width_16 * screen_width_count
        + screen_height_16 * screen_height_count,
        "vinil_doble_fuerza": 2 * (int(glass_plan["ancho_16"]) + int(glass_plan["alto_16"])) * glass_quantity,
    }
    for code, length_16 in linear_consumptions.items():
        quantity = Decimal(length_16) / Decimal(192)
        details.append((code, quantity, _measure_cost(costs, code, length_16), "pie lineal"))

    for code, quantity in UNIDADES_POR_VENTANA.items():
        details.append((code, quantity, Decimal(costs[code]) * quantity,
                        INSUMOS_POR_CODIGO[code][3]))

    # Apply the full perimeter on both faces using the fabrication dimensions.
    paste_inches = Decimal(4 * (width_16 + height_16)) / Decimal(16)
    paste_cost_cents = paste_inches * Decimal(costs["pasta"]) / Decimal(26 * 12)
    details.append(("pasta", paste_inches, paste_cost_cents, "pulgada lineal"))

    grouped: dict[str, tuple[Decimal, Decimal, str]] = {}
    for code, quantity, cost_cents, unit in details:
        if code in grouped:
            old_quantity, old_cost, old_unit = grouped[code]
            grouped[code] = (old_quantity + quantity, old_cost + cost_cents, old_unit)
        else:
            grouped[code] = (quantity, cost_cents, unit)

    items = []
    total_cost = Decimal(0)
    for code, (quantity, cost_cents, unit) in grouped.items():
        item_cost = (cost_cents / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_cost += item_cost
        items.append({
            "codigo": code,
            "nombre": INSUMOS_POR_CODIGO[code][1],
            "cantidad": _format_quantity(quantity),
            "unidad": unit,
            "costo": str(item_cost),
        })
    return {
        "completo": True,
        "faltantes": [],
        "items": items,
        "costo_base": str(total_cost),
    }


def calculate_window_material_cost(
    aluminum_plan: list[dict],
    glass_plan: dict | None,
    costs: dict[str, int | None],
    *,
    width_16: int,
    height_16: int,
) -> dict:
    """Calculate with enough decimal precision to round currency reliably later."""
    with localcontext() as context:
        context.prec = 50
        return _calculate_window_material_cost(
            aluminum_plan, glass_plan, costs, width_16=width_16, height_16=height_16
        )
