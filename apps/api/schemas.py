"""Esquemas Pydantic v2 para recepción de pedidos.

Tarea #27, Historia de Usuario HU-01 — Registrar el pedido del cliente.
Validaciones a nivel de esquema (422 claros sin depender de CHECKs de BD),
enums alineados al vocabulario cerrado del ERD-FASE1.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TipoProducto(str, Enum):
    vidrio = "vidrio"
    aluminio = "aluminio"
    otro = "otro"


class EstadoPedido(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    completado = "completado"
    cancelado = "cancelado"


class EstadoPieza(str, Enum):
    pendiente = "pendiente"
    en_corte = "en_corte"
    completado = "completado"


class PiezaCreate(BaseModel):
    producto_id: uuid.UUID
    ancho_mm: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    largo_mm: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    cantidad: int = Field(gt=0)
    operario_asignado: str | None = Field(default=None, max_length=100)


class PedidoCreate(BaseModel):
    cliente_id: uuid.UUID
    fecha_entrega: date | None = None
    notas: str | None = None
    piezas: list[PiezaCreate] = Field(min_length=1)


class PiezaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    producto_id: uuid.UUID
    ancho_mm: Decimal
    largo_mm: Decimal
    cantidad: int
    estado: EstadoPieza
    operario_asignado: str | None
    created_at: datetime
    updated_at: datetime


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cliente_id: uuid.UUID
    estado: EstadoPedido
    fecha_entrega: date | None
    notas: str | None
    created_at: datetime
    updated_at: datetime
    piezas: list[PiezaResponse]
