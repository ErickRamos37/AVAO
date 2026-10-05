"""Router de tareas — GET /tareas/pendientes.

Tarea #29, Historia de Usuario HU-02 — Taller/Operario debe ver las
piezas pendientes de corte. Sin auth/JWT todavía (HU-03, fase posterior).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Piece
from schemas import TareaPendienteResponse

router = APIRouter()


@router.get("/tareas/pendientes", response_model=list[TareaPendienteResponse])
def listar_tareas_pendientes(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Piece]:
    return (
        db.query(Piece)
        .filter(Piece.estado == "pendiente")
        .order_by(Piece.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
