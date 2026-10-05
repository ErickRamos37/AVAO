# REVISIÓN #29 — Endpoint de Listado de Tareas

- **Tarea:** #29 — Subtarea 1: Endpoint de Listado de Tareas (FastAPI)
- **HU:** HU-02 — Taller/Operario debe ver las piezas pendientes de corte
- **Rama:** `feature/29-endpoint-listado-tareas`
- **Commit revisado:** `5e30a40`
- **Fecha de revisión:** 2026-10-04
- **Revisor:** Subagente Revisor de Código

---

## Checklist de validación

### 1. Schema `TareaPendienteResponse` en `apps/api/schemas.py` — ✅ PASA
Campos alineados al plan: `pieza_id` (validation_alias="id"), `pedido_id`, `product_id` (validation_alias="producto_id"), `ancho_mm`, `largo_mm`, `cantidad`, `estado` (EstadoPieza), `operario_asignado`, `fecha` (validation_alias="created_at"). Usa `ConfigDict(from_attributes=True)` y aliases de `Field` según indica el plan (§2).

### 2. Endpoint `GET /tareas/pendientes` en `apps/api/routers/tareas.py` — ✅ PASA
Filtro `Piece.estado == "pendiente"`, orden `Piece.created_at.asc()`, `limit: int = Query(default=50, ge=1, le=200)` y `offset: int = Query(default=0, ge=0)`. `response_model=list[TareaPendienteResponse]`, sin auth/JWT. Cumple §3 del plan.

### 3. Router incluido en `main.py` — ✅ PASA
`from routers import pedidos, tareas` + `app.include_router(tareas.router)`; comentario de trazabilidad `#29 / HU-02` presente.

### 4. `test_tareas.py` con 7 casos — ✅ PASA
Comando: `cd apps/api && .venv/bin/python -m pytest test_tareas.py -v`
Resultado: **7 passed** (test_lista_vacia_sin_pendientes, test_solo_incluye_pendientes, test_respeta_operario_asignado, test_formato_fecha_iso, test_orden_por_created_at, test_paginacion_limit_offset, test_contrato_de_campos).
Regresión: `.venv/bin/python -m pytest test_pedidos.py test_main.py` → **10 passed**.

### 5. `ruff check` y `ruff format` — ✅ PASA
- `.venv/bin/ruff check .` → "All checks passed!"
- `.venv/bin/ruff format --check .` → "12 files already formatted"

### 6. Trazabilidad #29 / HU-02 — ✅ PASA
Presente en cabeceras/docstrings de `schemas.py`, `routers/tareas.py`, `main.py` y `test_tareas.py`.

### 7. No push a `main` ni `develop` — ✅ PASA
`origin/main` (4751067) y `origin/develop` (0e43acb) no contienen `5e30a40`. La rama feature es solo local; ningún push a ramas protegidas.

---

## Observaciones menores (no bloqueantes)

- Warning de deprecación de Starlette `TestClient` respecto a `httpx` — preexistente, no introducido por #29.
- No se ejecuta `alembic check` porque la tarea no modifica modelos; correcto según §6 del plan.

## Decisión final

**APROBADO** — La implementación cumple todos los ítems del plan `PLAN-#29.md`: contrato de campos correcto, filtro/orden/paginación exactos, 7 tests obligatorios en verde, regresión limpia, lint y formato OK, trazabilidad completa y sin pushes indebidos.

**Recomendación de merge:** Proceder con merge de `feature/29-endpoint-listado-tareas` a `develop` (siguiendo el flujo GitHub Flow del repo), previo push de la rama feature si se desea revisión en PR.
