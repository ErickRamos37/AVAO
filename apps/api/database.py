"""Conexión a base de datos para la API AVAO.

Tarea #27, Historia de Usuario HU-01 — Registrar el pedido del cliente.
Provee engine, SessionLocal, Base (DeclarativeBase con convención de
nombres para migraciones determinísticas) y la dependencia FastAPI `get_db`.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://avao:avao_dev@localhost:5432/avao",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa con convención de nombres (ERD-FASE1 §6.3)."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def get_db():
    """Dependencia FastAPI: sesión por request con rollback ante error."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
