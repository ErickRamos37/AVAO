"""Tests pytest para GET /tareas/pendientes.

Tarea #29, Historia de Usuario HU-02 — Ver piezas pendientes de corte.
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

CAMPOS_CONTRATO = {
    "pieza_id",
    "pedido_id",
    "product_id",
    "ancho_mm",
    "largo_mm",
    "cantidad",
    "estado",
    "operario_asignado",
    "fecha",
}


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
    """Cliente, producto, pedido y piezas para siembra. #29 / HU-02."""
    cliente = Client(nombre="Cliente Demo", email="demo@example.com")
    p1 = Product(nombre="Vidrio 6mm", tipo="vidrio", espesor_mm=6)
    db_session.add_all([cliente, p1])
    db_session.commit()
    pedido = Order(cliente_id=cliente.id, estado="pendiente")
    db_session.add(pedido)
    db_session.commit()
    return cliente, p1, pedido


def _pieza(pedido, producto, estado="pendiente", operario=None, offset_min=0):
    return Piece(
        pedido_id=pedido.id,
        producto_id=producto.id,
        ancho_mm=1200.5,
        largo_mm=800,
        cantidad=2,
        estado=estado,
        operario_asignado=operario,
        created_at=datetime.now(timezone.utc) + timedelta(minutes=offset_min),
    )


def test_lista_vacia_sin_pendientes(client, db_session, seed):
    _, p1, pedido = seed
    db_session.add_all(
        [
            _pieza(pedido, p1, estado="en_corte"),
            _pieza(pedido, p1, estado="completado"),
        ]
    )
    db_session.commit()
    r = client.get("/tareas/pendientes")
    assert r.status_code == 200
    assert r.json() == []


def test_solo_incluye_pendientes(client, db_session, seed):
    _, p1, pedido = seed
    pendiente = _pieza(pedido, p1, estado="pendiente", offset_min=0)
    db_session.add_all(
        [
            pendiente,
            _pieza(pedido, p1, estado="en_corte", offset_min=1),
            _pieza(pedido, p1, estado="completado", offset_min=2),
        ]
    )
    db_session.commit()
    r = client.get("/tareas/pendientes")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["pieza_id"] == str(pendiente.id)
    for item in body:
        assert item["estado"] == "pendiente"
        assert item["estado"] != "completado"


def test_respeta_operario_asignado(client, db_session, seed):
    _, p1, pedido = seed
    db_session.add_all(
        [
            _pieza(pedido, p1, operario="Juan", offset_min=0),
            _pieza(pedido, p1, operario=None, offset_min=1),
        ]
    )
    db_session.commit()
    body = client.get("/tareas/pendientes").json()
    assert len(body) == 2
    assert body[0]["operario_asignado"] == "Juan"
    assert body[1]["operario_asignado"] is None


def test_formato_fecha_iso(client, db_session, seed):
    _, p1, pedido = seed
    db_session.add(_pieza(pedido, p1))
    db_session.commit()
    body = client.get("/tareas/pendientes").json()
    assert len(body) == 1
    datetime.fromisoformat(body[0]["fecha"])  # no lanza excepción


def test_orden_por_created_at(client, db_session, seed):
    _, p1, pedido = seed
    nueva = _pieza(pedido, p1, offset_min=10)
    antigua = _pieza(pedido, p1, offset_min=0)
    db_session.add_all([nueva, antigua])
    db_session.commit()
    body = client.get("/tareas/pendientes").json()
    assert [item["pieza_id"] for item in body] == [str(antigua.id), str(nueva.id)]


def test_paginacion_limit_offset(client, db_session, seed):
    _, p1, pedido = seed
    p1_, p2_, p3_ = (
        _pieza(pedido, p1, offset_min=0),
        _pieza(pedido, p1, offset_min=1),
        _pieza(pedido, p1, offset_min=2),
    )
    db_session.add_all([p1_, p2_, p3_])
    db_session.commit()

    body = client.get("/tareas/pendientes?limit=1&offset=1").json()
    assert len(body) == 1
    assert body[0]["pieza_id"] == str(p2_.id)

    assert client.get("/tareas/pendientes?limit=0").status_code == 422
    assert client.get("/tareas/pendientes?limit=500").status_code == 422
    assert client.get("/tareas/pendientes?offset=-1").status_code == 422


def test_contrato_de_campos(client, db_session, seed):
    _, p1, pedido = seed
    db_session.add(_pieza(pedido, p1, operario="Ana"))
    db_session.commit()
    r = client.get("/tareas/pendientes")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    item = body[0]
    assert set(item.keys()) == CAMPOS_CONTRATO
    assert item["estado"] == "pendiente"
    uuid.UUID(item["pieza_id"])
    uuid.UUID(item["pedido_id"])
    uuid.UUID(item["product_id"])
    assert item["operario_asignado"] == "Ana"
