"""Modelos SQLAlchemy 2.0 de AVAO (estilo Mapped/mapped_column).

Tarea #27, Historia de Usuario HU-01 — Registrar el pedido del cliente.
Alineados 1:1 al DDL de docs/design/ERD-FASE1.md §5: clientes, productos,
pedidos y piezas, con FKs explícitas, CHECKs y 7 índices.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Client(Base):
    __tablename__ = "clientes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    direccion: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="cliente")


class Product(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("tipo IN ('vidrio','aluminio','otro')", name="tipo_valido"),
        CheckConstraint("espesor_mm > 0", name="espesor_positivo"),
        Index("idx_productos_tipo", "tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    caracteristicas: Mapped[str | None] = mapped_column(String(150))
    espesor_mm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Order(Base):
    __tablename__ = "pedidos"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente','en_proceso','completado','cancelado')",
            name="estado_valido",
        ),
        Index("idx_pedidos_cliente_id", "cliente_id"),
        Index("idx_pedidos_estado", "estado"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    fecha_entrega: Mapped[date | None] = mapped_column(Date)
    notas: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cliente: Mapped[Client] = relationship(back_populates="orders")
    pieces: Mapped[list["Piece"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    @property
    def piezas(self) -> list["Piece"]:
        """Alias para serialización Pydantic (PedidoResponse). #27 HU-01."""
        return self.pieces


class Piece(Base):
    __tablename__ = "piezas"
    __table_args__ = (
        CheckConstraint("ancho_mm > 0", name="ancho_positivo"),
        CheckConstraint("largo_mm > 0", name="largo_positivo"),
        CheckConstraint("cantidad > 0", name="cantidad_positiva"),
        CheckConstraint("estado IN ('pendiente','en_corte','completado')", name="estado_valido"),
        Index("idx_piezas_pedido_id", "pedido_id"),
        Index("idx_piezas_producto_id", "producto_id"),
        Index("idx_piezas_estado", "estado"),
        Index("idx_piezas_operario", "operario_asignado"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    pedido_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
    )
    producto_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ancho_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    largo_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    operario_asignado: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    pedido: Mapped[Order] = relationship(back_populates="pieces")
