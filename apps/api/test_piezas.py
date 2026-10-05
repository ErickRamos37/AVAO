"""Tests pytest para PATCH /piezas/{id}/completar.

Tarea #31, Historia de Usuario HU-02/HU-09 — Actualización de estado de pieza.
BD de prueba: SQLite en memoria (StaticPool) + dependency_overrides de get_db.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app
from models import Base, Client, Order, Piece, Product

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed(db_session):
    """Cliente, producto y pedido para siembra. #31 / HU-02, HU-09."""
    cliente = Client(nombre="Cliente Demo", email="demo@example.com")
    p1 = Product(nombre="Vidrio 6mm", tipo="vidrio", espesor_mm=6)
    db_session.add_all([cliente, p1])
    db_session.commit()
    pedido = Order(cliente_id=cliente.id, estado="pendiente")
    db_session.add(pedido)
    db_session.commit()
    return cliente, p1, pedido


def _pieza(pedido, producto, estado="pendiente", operario=None):
    return Piece(
        pedido_id=pedido.id,
        producto_id=producto.id,
        ancho_mm=1200.5,
        largo_mm=800,
        cantidad=2,
        estado=estado,
        operario_asignado=operario,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )


def test_completar_exito(client, db_session, seed):
    _, p1, pedido = seed
    pieza = _pieza(pedido, p1, estado="pendiente")
    db_session.add(pieza)
    db_session.commit()
    pieza_id = pieza.id

    r = client.patch(f"/piezas/{pieza_id}/completar")
    assert r.status_code == 200
    body = r.json()
    assert body["estado"] == "completado"
    assert body["id"] == str(pieza_id)

    # 31 / HU-09: verificar el cambio persistido en BD.
    db_session.expire_all()
    en_bd = db_session.get(Piece, pieza_id)
    assert en_bd.estado == "completado"

    updated = datetime.fromisoformat(body["updated_at"]).replace(tzinfo=None)
    created = datetime.fromisoformat(body["created_at"]).replace(tzinfo=None)
    assert updated >= created


def test_id_inexistente_404(client, db_session, seed):
    r = client.patch(f"/piezas/{uuid.uuid4()}/completar")
    assert r.status_code == 404
    assert r.json()["detail"] == "Pieza no encontrada"


def test_uuid_invalido_422(client, db_session, seed):
    r = client.patch("/piezas/no-es-uuid/completar")
    assert r.status_code == 422


def test_idempotente_ya_completado(client, db_session, seed):
    _, p1, pedido = seed
    pieza = _pieza(pedido, p1, estado="completado", operario="Ana")
    db_session.add(pieza)
    db_session.commit()
    pieza_id = pieza.id

    r = client.patch(f"/piezas/{pieza_id}/completar")
    assert r.status_code == 200
    body = r.json()
    assert body["estado"] == "completado"

    # 31: la llamada repetida no corrompe ni altera otros campos.
    db_session.expire_all()
    en_bd = db_session.get(Piece, pieza_id)
    assert en_bd.estado == "completado"
    assert en_bd.operario_asignado == "Ana"
    assert float(en_bd.ancho_mm) == 1200.5
    assert en_bd.cantidad == 2
