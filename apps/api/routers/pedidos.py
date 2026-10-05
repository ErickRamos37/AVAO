"""Router de pedidos — POST /pedidos.

Tarea #27, Historia de Usuario HU-01 — Registrar el pedido del cliente.
Persiste en una sola transacción el pedido y sus piezas con estado inicial
'pendiente'. Sin auth/JWT todavía (HU-03, fase posterior).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Client, Order, Piece, Product
from schemas import PedidoCreate, PedidoResponse

router = APIRouter()


@router.post("/pedidos", response_model=PedidoResponse, status_code=201)
def crear_pedido(payload: PedidoCreate, db: Session = Depends(get_db)) -> Order:
    cliente = db.get(Client, payload.cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for pieza in payload.piezas:
        if db.get(Product, pieza.producto_id) is None:
            raise HTTPException(
                status_code=404, detail=f"Producto no encontrado: {pieza.producto_id}"
            )

    order = Order(
        cliente_id=payload.cliente_id,
        fecha_entrega=payload.fecha_entrega,
        notas=payload.notas,
        estado="pendiente",
        pieces=[
            Piece(
                producto_id=p.producto_id,
                ancho_mm=p.ancho_mm,
                largo_mm=p.largo_mm,
                cantidad=p.cantidad,
                estado="pendiente",
                operario_asignado=p.operario_asignado,
            )
            for p in payload.piezas
        ],
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
