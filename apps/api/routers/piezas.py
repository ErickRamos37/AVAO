"""Router de piezas — PATCH /piezas/{id}/completar.

Tarea #31, Historia de Usuario HU-02/HU-09 — Marcar pieza como completada.
Sin auth/JWT todavía (HU-03, fase posterior).
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Piece
from schemas import PiezaResponse

router = APIRouter()


@router.patch("/piezas/{id}/completar", response_model=PiezaResponse)
def completar_pieza(id: uuid.UUID, db: Session = Depends(get_db)) -> Piece:
    """Marca la pieza como completada. #31 / HU-02, HU-09.

    Idempotente: si la pieza ya estaba ``completado``, se acepta igualmente
    y se devuelve 200 (convergencia de estado, no transición estricta), para
    que el cliente Taller pueda reintentar sin recibir 409.
    """
    pieza = db.get(Piece, id)
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")
    pieza.estado = "completado"  # 31 / HU-02, HU-09
    pieza.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pieza)
    return pieza
