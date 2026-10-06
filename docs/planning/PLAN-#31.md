# PLAN #31 — Lógica de actualización de estado (FastAPI)

- **Tarea:** #31 — Subtarea 1: Lógica de actualización de estado.
- **Historia de Usuario:** HU-02 (Taller/Operario marca piezas) y HU-09 (trazabilidad de estado de piezas).
- **Rama:** `feature/31-logica-actualizacion-estado` (nace de `develop`).
- **Fecha:** 2026-10-04.
- **Documentos de referencia:** `apps/api/main.py`, `apps/api/models.py` (modelo `Piece`), `apps/api/schemas.py` (`PiezaResponse`, `EstadoPieza`), `apps/api/routers/pedidos.py`, `apps/api/routers/tareas.py`, `apps/api/database.py` (`get_db`), `apps/api/test_tareas.py` (patrón de tests), `apps/taller-pwa/src/components/CorteCard.jsx` (TODO #31, fuera de alcance), `docs/planning/PLAN-#29.md`, `docs/planning/PLAN-#30.md`.
- **Stack:** FastAPI + SQLAlchemy 2.0, SQLite in-memory (StaticPool) para tests, pytest, ruff.

---

## 1. Objetivo y alcance exacto

### Qué hace
- Implementar `PATCH /piezas/{id}/completar` en `apps/api`, que cambia el estado de una pieza a `"completado"` y actualiza `updated_at`.
- Devolver la pieza actualizada con el contrato de respuesta existente (`PiezaResponse`).
- Responder `404` cuando el `id` no existe y `422` cuando el `id` no es un UUID válido (comportamiento nativo de FastAPI al tipar el path param como `uuid.UUID`).
- Tests pytest en `apps/api/test_piezas.py` que confirmen el cambio de estado en BD, el 404, la idempotencia del estado ya completado y la validación de UUID.

### Qué NO hace (límites explícitos)
- **No** implementa asignación de operario (`operario_asignado`) ni ningún otro endpoint de piezas.
- **No** implementa la transición a otros estados (`pendiente` → `en_corte` queda para una tarea posterior); solo `→ completado`.
- **No** toca el frontend Taller (`apps/taller-pwa/src/components/CorteCard.jsx`): el botón "Marcar completado" permanece deshabilitado con su TODO #31; habilitarlo será una subtarea posterior.
- **No** agrega auth/JWT (HU-03, fase posterior) ni WebSockets/WSS.
- **No** modifica `models.py` ni `schemas.py` salvo lo estrictamente descrito en §4 (preferencia: reusar `PiezaResponse` sin cambios).
- **No** crea migraciones Alembic nuevas (no hay cambio de esquema: `estado` y `updated_at` ya existen).

---

## 2. Endpoint

### Ruta y método

```
PATCH /piezas/{id}/completar
```

- **Método:** `PATCH` (actualización parcial semántica: solo `estado`/`updated_at`).
- **Path param:** `id: uuid.UUID` — FastAPI devuelve `422` automáticamente si no es UUID.
- **Body:** ninguno.
- **Dependencias:** `db: Session = Depends(get_db)`.

### Lógica (pseudocódigo)

```python
@router.patch("/piezas/{id}/completar", response_model=PiezaResponse)
def completar_pieza(id: uuid.UUID, db: Session = Depends(get_db)) -> Piece:
    pieza = db.get(Piece, id)
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")
    pieza.estado = "completado"
    pieza.updated_at = datetime.now(timezone.utc)  # ver nota
    db.commit()
    db.refresh(pieza)
    return pieza
```

Notas de implementación:
- `db.get(Piece, id)` replica el patrón de `routers/pedidos.py`.
- `updated_at`: el modelo ya tiene `onupdate=func.now()`, que en PostgreSQL actualiza la columna al hacer `UPDATE`; por robustez en SQLite (donde `server_default`/`onupdate` de SQLAlchemy sí se aplican en el UPDATE generado por ORM, pero conviene ser explícitos en tests), el Implementador puede fijar `pieza.updated_at = datetime.now(timezone.utc)` explícitamente. Se recomienda hacerlo explícito para que el test pueda verificarlo con SQLite.
- Idempotencia: si `pieza.estado` ya es `"completado"`, se acepta igualmente, se refresca `updated_at` (opcional: dejar el valor previo) y se devuelve 200. **Justificación:** el endpoint representa la intención "la pieza debe quedar completada" (operación de convergencia, no transición estricta); devolver 409 complicaría al cliente Taller (que puede reintentar por timeout de red) sin aportar seguridad, porque el CHECK de BD ya restringe al vocabulario cerrado.
- No validar la transición anterior (`en_corte` → `completado`): fuera de alcance; cualquier origen termina en `completado`.

### Router nuevo

Crear `apps/api/routers/piezas.py` con el mismo estilo de `tareas.py`/`pedidos.py` (docstring con Tarea/HU, `APIRouter()`, imports de `database`, `models`, `schemas`). Registrar en `main.py`:

```python
from routers import pedidos, piezas, tareas

app.include_router(piezas.router)
```

y actualizar el docstring de `main.py` con la línea `#31 / HU-02+HU-09: include router de completar pieza`.

---

## 3. Esquema Pydantic de respuesta

Usar **`PiezaResponse` existente** (`apps/api/schemas.py`), sin modificaciones. Justificación: ya modela `id`, `producto_id`, `ancho_mm`, `largo_mm`, `cantidad`, `estado` (como `EstadoPieza`), `operario_asignado`, `created_at`, `updated_at` con `from_attributes=True`, y es el contrato que el cliente Taller ya conoce vía otras respuestas.

**No** crear `PiezaEstadoResponse` salvo que el Implementador detecte un consumidor que requiera un subset — no es el caso actual. Si se necesitara en el futuro, sería un cambio aditivo, nunca reemplazar `PiezaResponse`.

Respuesta 200 de ejemplo:

```json
{
  "id": "uuid",
  "producto_id": "uuid",
  "ancho_mm": "1200.50",
  "largo_mm": "800.00",
  "cantidad": 2,
  "estado": "completado",
  "operario_asignado": "Juan",
  "created_at": "2026-10-04T10:00:00Z",
  "updated_at": "2026-10-04T12:30:00Z"
}
```

---

## 4. Trazabilidad en código

- `apps/api/routers/piezas.py` — docstring: `Tarea #31, HU-02/HU-09 — Marcar pieza como completada.`
- `apps/api/main.py` — docstring actualizado + `include_router(piezas.router)`.
- `apps/api/test_piezas.py` — docstring: `Tests pytest para PATCH /piezas/{id}/completar. Tarea #31, HU-02/HU-09.`
- Comentario in-line `#31 / HU-02, HU-09` junto a la ruta.
- **No** modificar `CorteCard.jsx` (sigue con TODO #31); al implementarse el frontend en una tarea posterior, remover el TODO.

---

## 5. Pruebas (pytest, `apps/api/test_piezas.py`)

Reutilizar el andamiaje de `test_tareas.py`: engine SQLite `:memory:` con `StaticPool`, fixture `db_session` (create_all/drop_all), fixture `client` con `app.dependency_overrides[get_db]`, fixture `seed` con Cliente + Producto + Pedido.

Casos requeridos:

1. **Éxito con cambio de estado (200)** — crear pieza con `estado="pendiente"`; `PATCH /piezas/{id}/completar`; assert `status_code == 200`, `body["estado"] == "completado"`, y **verificar en BD** que `db_session.get(Piece, id).estado == "completado"`; assert `updated_at` corresponde a un instante >= `created_at`.
2. **ID inexistente (404)** — `PATCH /piezas/{uuid4()}/completar` con UUID válido pero no sembrado; assert `status_code == 404` y `detail == "Pieza no encontrada"`.
3. **Idempotencia (200 aunque ya esté completado)** — sembrar pieza con `estado="completado"`; PATCH; assert 200 y `estado` sigue `"completado"`; la pieza no se corrompe ni cambia de otro campo.
4. **UUID inválido (422)** — `PATCH /piezas/no-es-uuid/completar`; assert `status_code == 422`.
5. **(Recomendado)** La misma llamada ya completada no altera otros campos (`ancho_mm`, `cantidad`, `operario_asignado` intactos).

---

## 6. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO/apps/api
source .venv/bin/activate   # el repo ya tiene .venv; verificar pytest/ruff disponibles

# Pruebas (todas, con énfasis en piezas)
pytest test_piezas.py -v
pytest -v

# Lint
ruff check .
ruff format --check .   # si el repo adopta formato; si falla por formato preexistente, solo reportar

# Levantar API en local para smoke manual (opcional; requiere Postgres o override de DATABASE_URL)
uvicorn main:app --reload --port 8000
```

Smoke manual opcional (con la app levantada y BD migrada con `alembic upgrade head`):

```bash
curl -X PATCH http://localhost:8000/piezas/<uuid>/completar
```

---

## 7. Trazabilidad #31, HU-02 / HU-09

- **Tarea:** #31 — Subtarea 1: Lógica de actualización de estado (`PATCH /piezas/{id}/completar`).
- **HU-02:** Taller/Operario debe ver las piezas y reportar su avance; este endpoint es la confirmación de corte terminado.
- **HU-09:** cada pieza conserva historial de estado vía `estado` + `updated_at`; el endpoint es el punto único de transición a `completado`.
- Depende de: #27 (`PedidoCreate`/modelos), #29 (patrón router/tests), #30 (la PWA Taller que consumirá esto en una fase posterior).
- `main.py` y routers deben registrar el trabajo con comentarios `#31 / HU-02, HU-09` y docstrings homólogos.

---

## 8. Riesgos y límites

- **No implementar asignación de operario**: cualquier endpoint `PATCH /piezas/{id}/asignar` u otro queda fuera de este PR.
- **No cambiar otros estados todavía**: no exponer endpoints para `pendiente`, `en_corte`, `cancelado`, ni la transición a `en_corte`.
- **Frontend Taller intacto**: `CorteCard.jsx` conserva el botón deshabilitado con TODO #31; ningún archivo de `apps/taller-pwa` se modifica aquí.
- **Sin migraciones nuevas**: no tocar `models.py` ni `alembic/versions/`.
- **Riesgo de scope creep**: resistencia a agregar body opcional, estado intermedio, o notificaciones WSS — todos posteriores.
- **`updated_at` en SQLite**: verificar en el test que el valor cambia; si `onupdate` no se refleja, fijarlo explícitamente en la ruta (aceptado).
- **Idempotencia vs 409**: documentar la decisión en el docstring de la ruta para evitar retrabajo de revisión.
