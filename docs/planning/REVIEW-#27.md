# REVIEW #27 — API REST Recepción de Pedidos (HU-01)

- **Tarea:** #27 — Subtarea 2: API REST Recepción de Pedidos
- **Plan revisado:** `docs/planning/PLAN-#27.md`
- **Commit revisado:** `a58b9ff` (`feat(api): agregar POST /pedidos con validación Pydantic y modelos SQLAlchemy (#27)`)
- **Rama:** `feature/27-api-recepcion-pedidos`
- **Fecha de revisión:** 2026-10-04
- **Revisor:** Subagente Revisor de Código

---

## Checklist de verificación

| # | Ítem | Estado | Evidencia |
|---|---|---|---|
| 1 | **Esquemas Pydantic** (`PedidoCreate`, `PiezaCreate`, `PedidoResponse`, `PiezaResponse`) | ✅ Aprobado | `apps/api/schemas.py`: los 4 esquemas existen; `Decimal` con `Field(gt=0, max_digits=10, decimal_places=2)` en medidas, `cantidad: int = Field(gt=0)`, `piezas: Field(min_length=1)`; enums `TipoProducto`, `EstadoPedido`, `EstadoPieza` alineados al vocabulario del ERD; `ConfigDict(from_attributes=True)` presente. |
| 2 | **Endpoint `POST /pedidos`** | ✅ Aprobado | `apps/api/routers/pedidos.py`: ruta `POST /pedidos`, `status_code=201`, 404 para cliente/producto inexistente con mensajes del plan, transacción única (`db.add(order)` con `pieces` + `db.commit()` + `db.refresh()`), incluido en `main.py` vía `app.include_router(pedidos.router)`. |
| 3 | **Modelos SQLAlchemy 2.0** | ✅ Aprobado | `apps/api/models.py`: `Client`/`Product`/`Order`/`Piece` con `Mapped`/`mapped_column` (estilo 2.0); FKs explícitas `ondelete="RESTRICT"`/`"CASCADE"`; CHECKs de estado/tipo/medidas/cantidad; 7 índices nombrados `idx_*`; `naming_convention` en `Base.metadata`; `pieces` con `cascade="all, delete-orphan"`, `passive_deletes=True`, `lazy="selectin"`; property `piezas` para serialización. Mapeo 1:1 a tablas del ERD Fase 1. |
| 4 | **Alembic** | ⚠️ Observación | `alembic/env.py` apunta a `target_metadata = Base.metadata` con import de `models`, y la migración `95354a0cc046_create_tables_for_pedidos_27.py` está autogenerada (tablas, FKs, CHECKs, índices presentes, `downgrade()` con drops). **No se pudo verificar la ejecución real de `upgrade head`/`downgrade base`**: Docker no está disponible en el entorno (`permission denied` en `/var/run/docker.sock`, conexión a BD rechazada al ejecutar `alembic current`). Recomendación (no bloqueante): levantar `infra/docker-compose.yml` y reejecutar `alembic upgrade head && alembic downgrade base` antes de merge final, validando contra PostgreSQL 17 real. |
| 5 | **Pruebas** | ✅ Aprobado | `apps/api/test_pedidos.py` existe y cubre: 201 con datos correctos (medidas `1200.50`/`800.00`, cantidad 3, estados `pendiente`, timestamps), 422 medidas negativas, 422 medida en cero, 422 cantidad 0, 422 tipo de producto inválido (enum directo, aceptado por el plan), 422 payload malformado (sin `piezas`, `piezas: []`, `cantidad: "tres"`), 404 cliente y 404 producto. Ejecutado `pytest -q`: **10 passed**. |
| 6 | **Linter/Formato** | ✅ Aprobado | `ruff.toml` presente (line-length 100, reglas E/F/I/B/UP/RUF, ignores por archivo para migraciones). Ejecutado `ruff check .` → *All checks passed!*; `ruff format --check .` → *10 files already formatted*. |
| 7 | **Trazabilidad** | ⚠️ Observación menor | `schemas.py`, `models.py`, `database.py`, `routers/pedidos.py`, `main.py`, `env.py`, migración y tests mencionan `#27`/`HU-01` en docstrings/comentarios. `test_main.py` solo añade una línea en blanco sin mención de #27 (cosmético). Contrato cumplido en lo esencial. |
| 8 | **Cambios prohibidos** | ✅ Aprobado | Todo el trabajo (`9314639`, `a58b9ff`) está únicamente en `feature/27-api-recepcion-pedidos`. `origin/develop` y `origin/main` no contienen los cambios (`git diff origin/develop -- apps/api` muestra todo como nuevo, sin commitear en develop). Sin push directo a `main`/`develop`. |

## Comandos de verificación ejecutados

| Comando | Directorio | Resultado |
|---|---|---|
| `git log --oneline -5` / `git branch -a` | repo | Rama `feature/27-api-recepcion-pedidos`, HEAD `a58b9ff` ✅ |
| `pytest -q` | `apps/api` (venv) | **10 passed, 1 warning** (deprecación Starlette/httpx, no del código propio) ✅ |
| `ruff check .` | `apps/api` | **All checks passed!** ✅ |
| `ruff format --check .` | `apps/api` | **10 files already formatted** ✅ |
| `docker compose -f infra/docker-compose.yml ps` | repo | `permission denied` en docker.sock — Docker no disponible ⚠️ |
| `alembic current` | `apps/api` | Falla de conexión a BD (servidor PostgreSQL no levantado) ⚠️ |
| `git diff origin/develop -- apps/api` / `git log origin/develop` | repo | Cambios solo en rama feature; sin push a develop/main ✅ |

## Decisión final

**✅ APROBADO** — con observaciones no bloqueantes.

### Justificación
- Los 8 ítems del checklist se cumplen en código: esquemas correctos, endpoint 201/404/422 con transaccionalidad, modelos 2.0 alineados al ERD, Alembic configurado, suite pytest 100% verde, ruff limpio, trazabilidad presente y rama aislada.
- Las dos observaciones son de verificación operativa, no de defectos de implementación:
  1. **Recomendado:** reejecutar `alembic upgrade head && alembic downgrade base` contra PostgreSQL 17 real (Docker) antes del merge definitivo — la migración parece válida pero no se pudo ejecutar en esta sesión.
  2. **Cosmético:** añadir referencia `#27`/`HU-01` al docstring de `test_main.py` en una pasada posterior.

### Recomendación de merge
Se recomienda **merge a `develop`** una vez que el equipo confirme la corrida exitosa de `alembic upgrade head`/`downgrade base` contra PostgreSQL 17 (ítem ⚠️ #4). Si el owner ya validó la migración localmente, el merge puede proceder sin esperar.
