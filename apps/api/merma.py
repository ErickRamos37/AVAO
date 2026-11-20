"""Recuperación de sobrante del último tramo de cada perfil del pedido."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from apps.api.costos_ventana import PERFILES, PERFILES_REQUERIDOS
from apps.api.costos_insumos import INSUMOS_POR_CODIGO
from apps.api.medidas import format_measure
from fastapi import HTTPException


def calcular_merma(planes, costos, umbral, *, incluir_detalle=False):
    if not planes:
        raise HTTPException(status_code=409, detail="No hay ventanas activas para calcular merma.")
    consumo = defaultdict(int)
    for plan in planes:
        if len(plan) != 10 or {fila["perfil"] for fila in plan} != PERFILES_REQUERIDOS:
            raise HTTPException(status_code=409, detail="Falta un plan de aluminio completo; no se calculó la merma.")
        for fila in plan:
            consumo[PERFILES[fila["perfil"]]] += fila["longitud_16"] * fila["cantidad"]
    cargo = Decimal(0)
    faltantes = []
    detalle = []
    for codigo, longitud in consumo.items():
        tramo = INSUMOS_POR_CODIGO[codigo][4] * 192
        residual = longitud % tramo
        if not umbral or not residual or residual * 100 < umbral * tramo:
            continue
        costo = costos.get(codigo)
        if costo is None:
            faltantes.append(INSUMOS_POR_CODIGO[codigo][1])
        else:
            importe = Decimal(costo) * Decimal(tramo - residual) / Decimal(tramo)
            cargo += importe
            detalle.append({
                "perfil": INSUMOS_POR_CODIGO[codigo][1],
                "consumo": format_measure(longitud),
                "tramo_pies": tramo // 192,
                "sobrante": format_measure(tramo - residual),
                "importe": f"{importe / 100:.4f}",
            })
    if faltantes:
        raise HTTPException(status_code=409, detail="Faltan costos de: " + ", ".join(sorted(faltantes)) + ". No se calculó la merma.")
    cents = int(cargo.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return (cents, detalle) if incluir_detalle else cents
