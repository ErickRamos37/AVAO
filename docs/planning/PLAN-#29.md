# PLAN #29 — Endpoint de Listado de Tareas (FastAPI)

- **Tarea:** #29 — Subtarea 1: Endpoint de Listado de Tareas (FastAPI)
- **Historia de Usuario:** HU-02 — Taller/Operario debe ver las piezas pendientes de corte.
- **Rama:** `feature/29-endpoint-listado-tareas` (nace de `develop`)
- **Fecha:** 2026-10-04
- **Documentos de referencia:** `apps/api/main.py`, `apps/api/models.py`, `apps/api/schemas.py`, `apps/api/routers/pedidos.py`, `apps/api/database.py`, `apps/api/test_pedidos.py`, `docs/design/ERD-FASE1.md`, `docs/planning/PLAN-#27.md`, `docs/planning/PLAN-#28.md`.
- **Stack:** FastAPI + SQLAlchemy 2.0 + PostgreSQL (tests con SQLite en memoria, igual que `test_pedidos.py`).

---

## 1. Objetivo y alcance exacto

### Qué hace
- Expone `GET /tareas/pendientes` que devuelve la lista de piezas (`Piece`) cuyo `estado == "pendiente"`.
- Filtra estrictamente por `estado == "pendiente"`: **omite** piezas con estado `en_corte` o `completado`.
- Ordena por `Piece.created_at` ascendente (más antiguas primero).
- Soporta `limit` y `offset` opcionales para evitar respuestas enormes (paginación simple, sin metadatos).

### Qué NO hace (YAGNI, explícito)
- **No** implementa autenticación/JWT ni control de acceso (HU-03, fase posterior).
- **No** implementa WebSockets ni push a la PWA Taller.
- **No** cambia estados de piezas (eso es otro endpoint/tarea).
- **No** filtra por operario ni por pedido (se puede añadir en tareas posteriores si se necesita).
- **No** implementa el frontend Taller/Operario (tarea #30).
- **No** modifica `Piece`, `Order` ni migraciones: el modelo ya tiene todos los campos necesarios.

---

## 2. Esquema Pydantic de respuesta

Definir en `apps/api/schemas.py` un nuevo esquema `TareaPendienteResponse` (no reutilizar `PiezaResponse` directamente, porque se requiere incluir `pedido_id`, que `PiezaResponse` no expone actualmente, y semánticamente la tarea del operario es la pieza dentro de su pedido):

```python
class TareaPendienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pieza_id: uuid.UUID       # alias de Piece.id
    pedido_id: uuid.UUID
    product_id: uuid.UUID     # alias de Piece.producto_id
    ancho_mm: Decimal
    largo_mm: Decimal
    cantidad: int
    estado: EstadoPieza       # == "pendiente" garantizado por el filtro
    operario_asignado: str | None
    fecha: datetime           # Piece.created_at (ISO 8601)
```

Notas de mapeo (por la diferencia de nombres del modelo SQLAlchemy):
- `pieza_id` ← `Piece.id`, `product_id` ← `Piece.producto_id`, `fecha` ← `Piece.created_at`.
- Implementar con `Field(validation_alias=...)` / `AliasChoices` o con una propiedad/serializer en el endpoint. La opción más simple y explícita: construir los dicts en el router o usar `model_validate` con aliases de `validation_alias` sobre el modelo ORM.
- `estado` debe ser siempre `"pendiente"` en la respuesta (contrato verificable en tests).
- La respuesta del endpoint es `list[TareaPendienteResponse]`.

---

## 3. Endpoint `GET /tareas/pendientes`

Crear `apps/api/routers/tareas.py` y registrarlo en `main.py` (`app.include_router(tareas.router)`), siguiendo el patrón de `routers/pedidos.py`.

```python
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
```

- **Ruta:** `GET /tareas/pendientes`
- **Dependencia:** `get_db` (de `database.py`).
- **Filtro:** `Piece.estado == "pendiente"` — obligatorio, no exponer como parámetro en esta tarea.
- **Orden:** `Piece.created_at` ascendente (FIFO de producción).
- **Paginación:** `limit` (1–200, default 50) y `offset` (default 0), validados con `Query`. Sin paginación agresiva ni metadatos envolventes.
- Sin auth/JWT todavía; registrar el router sin `dependencies`.

---

## 4. Modelos SQLAlchemy a consultar

- **Primario:** `Piece` (`piezas`): `id`, `pedido_id`, `producto_id`, `ancho_mm`, `largo_mm`, `cantidad`, `estado`, `operario_asignado`, `created_at`.
- **Join opcional a `Order` (`pedidos`):** solo si se necesita información del pedido (p. ej. `fecha_entrega`, `notas`). Para el contrato mínimo de esta tarea **no se requiere**; acceder vía `Piece.pedido` (relación ya definida) si se decide incluir más adelante.
- Índices existentes que respaldan la consulta: `idx_piezas_estado` y `idx_piezas_operario`.

---

## 5. Pruebas pytest — `apps/api/test_tareas.py`

Reutilizar la misma estrategia de `test_pedidos.py`: SQLite en memoria con `StaticPool`, `dependency_overrides[get_db]`, tablas creadas con `Base.metadata.create_all`, y sembrar `Client`, `Product`, `Order`, `Piece`.

Casos obligatorios:

1. **`test_lista_vacia_sin_pendientes`** — BD con solo piezas `en_corte`/`completado` (o sin piezas) → `GET /tareas/pendientes` responde `200` y `[]`.
2. **`test_solo_incluye_pendientes`** — sembrar piezas con estados `pendiente`, `en_corte` y `completado` → la respuesta incluye **únicamente** las `pendiente`; una pieza `completado` jamás aparece en el JSON (aserción explícita sobre el cuerpo).
3. **`test_respeta_operario_asignado`** — pieza pendiente con `operario_asignado="Juan"` aparece con ese valor; pieza sin operario aparece con `null` (no se filtra ni se pierde el campo).
4. **`test_formato_fecha_iso`** — el campo `fecha` de cada elemento cumple formato ISO 8601 (parseable con `datetime.fromisoformat`, o regex ISO).
5. **`test_orden_por_created_at`** — con 2+ pendientes creadas en momentos distintos, el orden devuelto es ascendente por `created_at`.
6. **`test_paginacion_limit_offset`** — `?limit=1&offset=1` devuelve el segundo elemento y `limit=0`/`limit=500` producen `422`.
7. **Contrato de campos** — cada elemento contiene exactamente: `pieza_id`, `pedido_id`, `product_id`, `ancho_mm`, `largo_mm`, `cantidad`, `estado`, `operario_asignado`, `fecha`; y `estado == "pendiente"`.

---

## 6. Comandos exactos para el Implementador

```bash
# Tests (desde la raíz del repo o apps/api según convenio del proyecto)
cd apps/api
python -m pytest test_tareas.py -v
python -m pytest test_pedidos.py test_main.py -v   # regresión

# Migraciones: NO se requiere nueva migración (Piece ya existe con todos
# los campos). Verificar estado con:
alembic current
alembic check   # o "alembic revision --autogenerate -m 'x'" solo para confirmar que no hay cambios pendientes; descartar el archivo si aparece

# Servidor de desarrollo
uvicorn main:app --reload --port 8000
# Probar manualmente:
curl http://localhost:8000/tareas/pendientes
```

Notas: `main:app` asume que el módulo `main.py` expone `app` (ya existente). Sin cambios de esquema, no crear revisión Alembic nueva.

---

## 7. Trazabilidad

- **Tarea:** #29 (Subtarea 1 — Endpoint de Listado de Tareas).
- **Historia de Usuario:** HU-02 — "Como operario de taller quiero ver mis tareas pendientes para saber qué cortar".
- Todo comentario en el código nuevo debe citar `#29 / HU-02`, igual que el código existente cita `#27 / HU-01`.

---

## 8. Riesgos y límites

- **Sin JWT todavía:** el endpoint es público en esta fase; no añadir `Depends` de auth ni encabezados especiales.
- **No paginar agresivamente:** usar `limit`/`offset` simples con tope `le=200`; no introducir cursores ni metadatos de paginación.
- **Nombres de campos:** el modelo usa `producto_id`/`created_at`; el contrato expone `product_id`/`fecha`. Un mapeo incorrecto romperá el contrato con Taller — los tests de contrato de campos lo cubren.
- **Zona horaria:** `created_at` es `DateTime(timezone=True)`; asegurar serialización ISO con offset.
- **Frontend Taller (PWA) y envío por WebSocket:** fuera de alcance; se hará en #30.
- **No tocar modelos ni migraciones:** cualquier cambio de esquema escapa al alcance de #29.
