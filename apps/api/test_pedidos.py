"""Tests pytest para POST /pedidos.

Tarea #27, Historia de Usuario HU-01 — Registrar el pedido del cliente.
BD de prueba: SQLite en memoria (StaticPool) + dependency_overrides de get_db.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app
from models import Base, Client, Product
from schemas import TipoProducto

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
    cliente = Client(nombre="Cliente Demo", email="demo@example.com")
    p1 = Product(nombre="Vidrio 6mm", tipo="vidrio", espesor_mm=6)
    p2 = Product(nombre="Perfil aluminio", tipo="aluminio", espesor_mm=2)
    db_session.add_all([cliente, p1, p2])
    db_session.commit()
    return cliente, p1, p2


def payload_valido(cliente_id, producto_id) -> dict:
    return {
        "cliente_id": str(cliente_id),
        "fecha_entrega": "2026-10-15",
        "notas": "Entrega en mostrador",
        "piezas": [
            {
                "producto_id": str(producto_id),
                "ancho_mm": "1200.50",
                "largo_mm": "800.00",
                "cantidad": 3,
            },
            {
                "producto_id": str(producto_id),
                "ancho_mm": "500.00",
                "largo_mm": "400.25",
                "cantidad": 1,
                "operario_asignado": "Juan",
            },
        ],
    }


def test_crear_pedido_201(client, seed):
    cliente_, p1, _ = seed
    r = client.post("/pedidos", json=payload_valido(cliente_.id, p1.id))
    assert r.status_code == 201, r.text
    body = r.json()
    uuid.UUID(body["id"])
    assert body["estado"] == "pendiente"
    assert body["cliente_id"] == str(cliente_.id)
    assert len(body["piezas"]) == 2
    for pieza in body["piezas"]:
        assert pieza["estado"] == "pendiente"
        assert pieza["created_at"] and pieza["updated_at"]
    assert body["piezas"][0]["cantidad"] == 3


def test_422_ancho_negativo(client, seed):
    cliente_, p1, _ = seed
    body = payload_valido(cliente_.id, p1.id)
    body["piezas"][0]["ancho_mm"] = "-10"
    r = client.post("/pedidos", json=body)
    assert r.status_code == 422


def test_422_largo_cero(client, seed):
    cliente_, p1, _ = seed
    body = payload_valido(cliente_.id, p1.id)
    body["piezas"][0]["largo_mm"] = "0"
    r = client.post("/pedidos", json=body)
    assert r.status_code == 422


def test_422_cantidad_cero(client, seed):
    cliente_, p1, _ = seed
    body = payload_valido(cliente_.id, p1.id)
    body["piezas"][0]["cantidad"] = 0
    r = client.post("/pedidos", json=body)
    assert r.status_code == 422


def test_422_tipo_producto_invalido_enum():
    with pytest.raises((ValidationError, ValueError)):
        TipoProducto("plastico")


def test_422_sin_piezas(client, seed):
    cliente_, p1, _ = seed
    body = payload_valido(cliente_.id, p1.id)
    del body["piezas"]
    assert client.post("/pedidos", json=body).status_code == 422
    body = payload_valido(cliente_.id, p1.id)
    body["piezas"] = []
    assert client.post("/pedidos", json=body).status_code == 422


def test_422_cantidad_tipo_erroneo(client, seed):
    cliente_, p1, _ = seed
    body = payload_valido(cliente_.id, p1.id)
    body["piezas"][0]["cantidad"] = "tres"
    assert client.post("/pedidos", json=body).status_code == 422


def test_404_cliente_inexistente(client, seed):
    _, p1, _ = seed
    body = payload_valido(uuid.uuid4(), p1.id)
    r = client.post("/pedidos", json=body)
    assert r.status_code == 404
    assert r.json()["detail"] == "Cliente no encontrado"


def test_404_producto_inexistente(client, seed):
    cliente_, _, _ = seed
    body = payload_valido(cliente_.id, uuid.uuid4())
    r = client.post("/pedidos", json=body)
    assert r.status_code == 404
    assert "Producto no encontrado" in r.json()["detail"]
