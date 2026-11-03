"""Cortes de aluminio para una ventana California por mitad, en dieciseisavos."""

from apps.api.medidas import centro_16


def calcular_plan_aluminio(ancho_16: int, alto_16: int) -> list[tuple[str, int, int]]:
    centro = centro_16(ancho_16)
    guia_riel_16 = ancho_16 - 30
    vertical_fijo_16 = alto_16 - 20
    plan = [
        ("Jamba", alto_16, 2),
        ("Mulio", alto_16 - 16, 1),
        ("Vertical fijo", vertical_fijo_16, 2),
        ("Aleta", alto_16 - 40, 2),
        ("Horizontal fijo", centro - 40, 2),
        ("Horizontal corredizo", centro - 14, 2),
        ("Guía", guia_riel_16, 1),
        ("Riel", guia_riel_16, 1),
        ("Screen ancho", centro - 26, 2),
        ("Screen alto", vertical_fijo_16, 2),
    ]
    if any(longitud_16 <= 0 for _, longitud_16, _ in plan):
        raise ValueError("las medidas producen un corte de aluminio de longitud cero o negativa")
    return plan
