"""Merma estimada por área, sin acomodo físico de piezas."""
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException


def calcular_merma_vidrio(planes, costo, umbral):
    if not planes:
        raise HTTPException(status_code=409, detail="No hay ventanas activas para calcular merma de vidrio.")
    if any(plan is None for plan in planes):
        raise HTTPException(status_code=409, detail="Falta un plan de vidrio; no se calculó la merma.")
    area = sum(plan[0] * plan[1] * plan[2] for plan in planes)
    hoja = 71 * 102 * 256
    residual = area % hoja
    if not umbral or not residual or residual * 100 < umbral * hoja:
        return 0, []
    if costo is None:
        raise HTTPException(status_code=409, detail="Falta el costo de vidrio; no se calculó la merma.")
    sobrante = hoja - residual
    cents = (Decimal(costo) * Decimal(sobrante) / Decimal(hoja)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents), [{"vidrio": "Vidrio doble fuerza de 1/8″", "consumo": str(Decimal(area) / 256),
                         "hoja": "71 × 102", "sobrante": str(Decimal(sobrante) / 256),
                         "importe": f"{Decimal(costo) * Decimal(sobrante) / Decimal(hoja) / 100:.4f}"}]
