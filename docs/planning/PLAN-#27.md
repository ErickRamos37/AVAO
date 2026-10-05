# PLAN #27 — API REST Recepción de Pedidos (FastAPI)

- **Tarea:** #27 — Subtarea 2: API REST Recepción de Pedidos (FastAPI)
- **Historia de Usuario:** HU-01 — "Registrar el pedido del cliente" (como encargado de ventas quiero anotar los pedidos con medidas exactas).
- **Rama:** `feature/27-api-recepcion-pedidos` (nace de `develop`).
- **Fecha:** 2026-10-04
- **Documento de referencia (diseño):** `docs/design/ERD-FASE1.md` (ERD Fase 1, DDL validado, modelos SQLAlchemy esperados §6.2, Alembic §6.3).
- **Stack existente:** `apps/api` con FastAPI 0.142, SQLAlchemy 2.0.54, Alembic 1.20, psycopg2-binary 2.9.13, Pydantic 2.13.5, pytest 9.1.1, uvicorn; venv en `apps/api/.venv` (Python 3.14); PostgreSQL 17 en `infra/docker-compose.yml` (aún sin levantar).

---

## 1. Objetivo y alcance

### Qué hace
- Expone `POST /pedidos` que recibe un pedido completo (cliente existente + lista de piezas con medidas y cantidades exactas) y lo persiste en PostgreSQL con integridad referencial completa (cliente, pedido, piezas, productos).
- Valida el payload con esquemas Pydantic v2 **antes** de tocar la BD (medidas positivas, cantidad > 0, tipo de producto vocabulario cerrado, payload bien formado). Respuestas 422 con detalle estándar de FastAPI.
- Crea en una sola transacción: fila en `pedidos` y N filas en `piezas` con estados iniciales por defecto (`pendiente`).
- Devuelve 201 con el pedido creado (id, estado, timestamps, piezas).

### Qué NO hace (YAGNI, explícito)
- **No** crea clientes (`POST /clientes`) — eso es otra subtarea; aquí se requiere `cliente_id`.
- **No** crea productos ni catálogo (`POST /productos`) — se requieren `producto_id` existentes (seed/fixture para desarrollo y pruebas).
- **No** autentica ni autoriza: sin JWT/fastapi-users todavía (fase posterior, HU-03). El endpoint queda abierto en local; Nginx + JWT se añadirán después.
- **No** optimiza cortes ni llama a `rectpack`; solo persiste medidas (la optimización JSON es fase posterior).
- **No** implementa offline-first ni sincronización: lo offline se resuelve en la PWA Ventas con Dexie.js (IndexedDB); la API asume conexión.
- **No** emite eventos WebSocket ni notifica a Taller (HU-02, #31+).
- **No** edita/elimina pedidos (endpoints PUT/DELETE posteriores).

---

## 2. Esquemas Pydantic propuestos (`apps/api/schemas.py`, nuevo archivo)

Pydantic v2. Validaciones a nivel de esquema (no solo BD) para dar 422 claros sin depender de checks de PostgreSQL. UUIDs como `uuid.UUID`, decimales como `decimal.Decimal` (serializados a número en JSON).

### Enums

```python
class TipoProducto(str, Enum):
    vidrio = "vidrio"
    aluminio = "aluminio"
    otro = "otro"

class EstadoPedido(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    completado = "completado"
    cancelado = "cancelado"

class EstadoPieza(str, Enum):
    pendiente = "pendiente"
    en_corte = "en_corte"
    completado = "completado"
```

> Justificación: mismos vocabularios cerrados que los `CHECK IN (...)` del ERD. `TipoProducto` se usa para validar payloads que incluyan producto embebido o referencias; en `PiezaCreate` basta con `producto_id`.

### `PiezaCreate`

| Campo | Tipo | Validación |
|---|---|---|
| `producto_id` | `uuid.UUID` | requerido |
| `ancho_mm` | `Decimal` | `Field(gt=0, max_digits=10, decimal_places=2)` |
| `largo_mm` | `Decimal` | `Field(gt=0, max_digits=10, decimal_places=2)` |
| `cantidad` | `int` | `Field(gt=0)` |
| `operario_asignado` | `str | None` | opcional, `max_length=100` |

### `PedidoCreate`

| Campo | Tipo | Validación |
|---|---|---|
| `cliente_id` | `uuid.UUID` | requerido |
| `fecha_entrega` | `date | None` | opcional |
| `notas` | `str | None` | opcional |
| `piezas` | `list[PiezaCreate]` | `Field(min_length=1)` — un pedido sin piezas no es válido para HU-01 |

### `PiezaResponse`

`id` (UUID), `producto_id`, `ancho_mm`, `largo_mm`, `cantidad`, `estado` (`EstadoPieza`), `operario_asignado`, `created_at`, `updated_at`. `model_config = ConfigDict(from_attributes=True)`.

### `PedidoResponse`

`id`, `cliente_id`, `estado` (`EstadoPedido`), `fecha_entrega`, `notas`, `created_at`, `updated_at`, `piezas: list[PiezaResponse]`. `from_attributes=True`.

> Nota de serialización: `Decimal` y `UUID` se serializan automáticamente en JSON por FastAPI. Los timestamps salen ISO-8601 con zona horaria.

---

## 3. Endpoint `POST /pedidos`

- **Ruta:** `POST /pedidos` (sin prefijo `/api` por ahora; cuando se introduzca versionado se migrará a `/api/v1/pedidos`).
- **Router:** `apps/api/routers/pedidos.py` (nuevo), incluido en `main.py` con `app.include_router(pedidos.router)`.
- **Request body:** `PedidoCreate`.
- **Dependencias:**
  - `db: Session = Depends(get_db)` de `apps/api/database.py`.
- **Lógica exacta:**
  1. Validar FK de cliente: `Cliente` existe → si no, **404** `{"detail": "Cliente no encontrado"}`.
  2. Validar cada `producto_id` → si alguno no existe, **404** `{"detail": "Producto no encontrado: <id>"}`. (Alternativa aceptada: 422; se elige 404 por semántica de recurso referenciado inexistente.)
  3. Crear `Order(cliente_id=..., fecha_entrega=..., notas=..., estado='pendiente')` y, por cada pieza, `Piece(pedido_id=..., producto_id=..., ancho_mm, largo_mm, cantidad, estado='pendiente', operario_asignado=...)`.
  4. `db.add(order)` con `order.pieces = [...]` (relación ORM), `db.commit()`, `db.refresh(order)` (y cascade para piezas).
  5. Devolver `PedidoResponse` con **201**.
- **Status codes:**
  | Código | Cuándo |
  |---|---|
  | 201 | Pedido y piezas creados |
  | 404 | `cliente_id` o algún `producto_id` no existe |
  | 422 | Medidas negativas/cero, `cantidad` 0 o negativa, tipo de producto inválido, `piezas` vacío, JSON malformado |
  | 500 | Error inesperado de BD (rollback en `get_db`) |

### Decisión: ¿crear cliente si no existe o exigir `cliente_id`?
**Se exige `cliente_id` (no se crea cliente inline).** Razones:
1. **Separación de responsabilidades:** HU-01 pide registrar el pedido; el alta de cliente es una operación distinta (probablemente su propio endpoint/subtarea) con sus propias validaciones (email único, teléfono). Mezclarlo acopla dos agregados.
2. **Integridad:** crear-o-buscar por nombre/teléfono introduce ambigüedad (¿dos "Juan Pérez"?). Mejor fallar explícito con 404 y que la App muestre "selecciona o registra el cliente primero".
3. **UX real de Ventas:** el encargado elige un cliente existente del catálogo; el flujo offline (Dexie) cachea clientes ya sincronizados.
4. **YAGNI:** evita lógica de "upsert" no solicitada.

---

## 4. Modelos SQLAlchemy a crear (`apps/api/models.py`, nuevo)

Estilo SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`), alineados 1:1 al DDL de `ERD-FASE1.md §5`:

| Modelo | Tabla | Notas clave |
|---|---|---|
| `Client` | `clientes` | `id` UUID PK (`default=uuid.uuid4`, `server_default=func.gen_random_uuid()`), `nombre` String(150) not null, `telefono` String(20), `email` String(255) unique, `direccion` String(255), `created_at`/`updated_at` TIMESTAMPTZ server_default `func.now()` |
| `Product` | `productos` | `nombre` String(100), `tipo` String(30) + `CheckConstraint("tipo IN ('vidrio','aluminio','otro')")`, `caracteristicas` String(150), `espesor_mm` Numeric(10,2) + `CheckConstraint('espesor_mm > 0')` |
| `Order` | `pedidos` | `cliente_id` FK→`clientes.id` ON DELETE RESTRICT, índice `idx_pedidos_cliente_id`; `estado` String(20) default `'pendiente'` + CHECK IN 4 valores; `fecha_entrega` Date; `notas` Text; relación `pieces` con `cascade="all, delete-orphan"` + `passive_deletes=True` |
| `Piece` | `piezas` | `pedido_id` FK→`pedidos.id` ON DELETE CASCADE (+ índice `idx_piezas_pedido_id`); `producto_id` FK→`productos.id` ON DELETE RESTRICT (+ `idx_piezas_producto_id`); `ancho_mm`/`largo_mm` Numeric(10,2) + CHECK `> 0`; `cantidad` Integer + CHECK `> 0`; `estado` String(20) default `'pendiente'` + CHECK 3 valores; `operario_asignado` String(100) + `idx_piezas_operario` |

- Convención de nombres de constraints en `Base.metadata` (`naming_convention`) para migraciones determinísticas (ERD §6.3).
- Índices de filtro: `idx_pedidos_estado`, `idx_piezas_estado`, `idx_productos_tipo`.
- El modelo `Order.pieces` debe usar `selectinload` al leer (o lazy='selectin') para que `PedidoResponse` serialice piezas sin N+1.

---

## 5. Migración Alembic necesaria

Inicializar Alembic en `apps/api` (si no existe `alembic.ini` + `alembic/`):

```bash
cd apps/api
alembic init alembic
# editar alembic.ini: sqlalchemy.url = postgresql+psycopg2://avao:avao_dev@localhost:5432/avao
# editar alembic/env.py: from models import Base; target_metadata = Base.metadata
```

Primera migración:

```bash
alembic revision --autogenerate -m "fase1_clientes_productos_pedidos_piezas"
alembic upgrade head
```

La migración creará: tablas `clientes`, `productos`, `pedidos`, `piezas`; FKs con ON DELETE RESTRICT/CASCADE; CHECKs de estado/tipo/medidas/cantidad; 7 índices (`idx_pedidos_cliente_id`, `idx_pedidos_estado`, `idx_piezas_pedido_id`, `idx_piezas_producto_id`, `idx_piezas_estado`, `idx_piezas_operario`, `idx_productos_tipo`); unique en `clientes.email`. `downgrade()` hace `DROP TABLE` en orden inverso (`piezas, pedidos, productos, clientes`).

> Equivalente al DDL validado en `ERD-FASE1.md §5` + §7.

---

## 6. Conexión a BD (`apps/api/database.py`, nuevo)

- **`DATABASE_URL`:** `postgresql+psycopg2://avao:avao_dev@localhost:5432/avao` (override por variable de entorno `DATABASE_URL` con `python-dotenv`; el venv ya incluye `python-dotenv`). En Docker Compose será `...@db:5432/avao`.
- `engine = create_engine(DATABASE_URL, pool_pre_ping=True)`.
- `SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)`.
- Dependencia `get_db()`: `db = SessionLocal(); try: yield db; finally: db.close()` (con `db.rollback()` ante excepción antes de cerrar).
- `Base = DeclarativeBase` (definida aquí o en `models.py`, importada por ambos).

---

## 7. Pruebas pytest (`apps/api/test_pedidos.py`, nuevo)

**Decisión de BD de prueba: SQLite en memoria con `StaticPool` + `create_all`.**

Justificación:
- Los CHECKs de estados/tipo/medidas se comportan igual en SQLite y PostgreSQL (ERD §6.1 eligió CHECK precisamente por portabilidad).
- UUID: SQLAlchemy 2.0 usa tipo `Uuid` portable (almacena como CHAR(32) en SQLite) — funciona.
- `gen_random_uuid()` es server-default de Postgres: en SQLite no existe, pero el modelo declara `default=uuid.uuid4` en Python, por lo que los INSERTs funcionan. Los tests no dependen del server_default.
- Evita acoplar CI/local a levantar Postgres con Docker; rápido y determinista. Se documenta que la validación real contra Postgres 17 la cubre el DDL (ERD §7) y, cuando exista, un job de integración (pendiente DevOps).
- Se overridea `get_db` con `app.dependency_overrides` apuntando a la sesión SQLite, y se usa `TestClient`.

Fixtures necesarios: tabla creada (`Base.metadata.create_all`), seed de un `Client` y un par de `Product`, `TestClient` con override.

### Casos obligatorios

| # | Caso | Esperado |
|---|---|---|
| 1 | 201 éxito: payload válido (cliente existente, 2 piezas, medidas `1200.50`/`800.00`, cantidad 3, producto válido) | HTTP 201, body con `id` UUID, `estado='pendiente'`, piezas anidadas con estado `pendiente`, timestamps presentes |
| 2 | 422 medidas negativas: `ancho_mm: -10` | HTTP 422 |
| 3 | 422 medidas en cero: `largo_mm: 0` | HTTP 422 |
| 4 | 422 cantidad 0 | HTTP 422 |
| 5 | 422 tipo de producto inválido (payload que incluya `tipo: 'plastico'` en un producto embebido o prueba directa del enum) | HTTP 422 |
| 6 | 422 payload malformado: JSON sin `piezas`, o `piezas: []`, o tipos erróneos (`cantidad: "tres"`) | HTTP 422 |
| 7 | 404 `cliente_id` inexistente | HTTP 404 |
| 8 | 404 `producto_id` inexistente | HTTP 404 |

Los casos 2–6 cubren el checklist ("medidas negativas → 422", "datos correctos → 201") y los amplían mínimamente.

---

## 8. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO/apps/api
source .venv/bin/activate

# 1) Dependencias (ya instaladas en el venv; reinstalar si se mueve el entorno)
pip install -r requirements.txt

# 2) Levantar PostgreSQL 17 (Docker aún sin correr)
cd /home/erick/Proyectos/AVAO/infra
docker compose up -d db
# esperar a que acepte conexiones: docker compose logs -f db

# 3) Alembic: primera migración
cd /home/erick/Proyectos/AVAO/apps/api
alembic revision --autogenerate -m "fase1_clientes_productos_pedidos_piezas"
alembic upgrade head

# 4) Pruebas
cd /home/erick/Proyectos/AVAO/apps/api
pytest -q test_pedidos.py
pytest -q            # todo (incluye test_main.py)

# 5) Lint / formato (si se adopta; el repo no tiene ruff/flake8 configurado aún)
pip install ruff
ruff check .
ruff format --check .

# 6) Levantar la API en local
uvicorn main:app --reload --port 8000
# probar: curl -X POST localhost:8000/pedidos -H 'Content-Type: application/json' -d @payload.json
```

---

## 9. Riesgos y decisiones de diseño

| Riesgo / decisión | Mitigación / justificación |
|---|---|
| Sin auth JWT todavía | El endpoint queda abierto en desarrollo local. HU-03 (RBAC) se implementa en fase posterior con fastapi-users. **No exponer a Internet sin Nginx+JWT.** |
| Offline-first pertenece al front, no a la API | La PWA Ventas acumula pedidos en Dexie.js y los sincroniza cuando hay red; la API solo valida/persiste. No se añade cola ni idempotencia por ahora (YAGNI). Si se requiere, agregar `Idempotency-Key` header en fase posterior. |
| SQLite en tests vs Postgres en prod | Los CHECKs y tipos usados son portables (ERD §6.1/§7). Riesgo residual: diferencias de `gen_random_uuid()`/TIMESTAMPTZ mitigadas por defaults en Python. Integración real contra Postgres 17 queda como job pendiente (DevOps). |
| `Decimal` vs `float` en Pydantic | Se usa `Decimal` para reflejar `NUMERIC(10,2)` exacto; cuidado al comparar en tests (`Decimal('1200.50')`). |
| No crear cliente/producto inline | Decisión §3: 404 explícito en lugar de upsert ambiguo. |
| Estados como CHECK, no ENUM nativo | Sigue ERD §6.1: cambios de CHECK son migraciones estándar; evita `ALTER TYPE` riesgoso. |
| SQLAlchemy 2.0 estilo `Mapped` | Coherente con ERD §6.2 y con `fastapi-users-db-sqlalchemy` ya instalado. |
| Transaccionalidad | Todo el alta de pedido+piezas va en una sola transacción; cualquier fallo de FK/CHECK hace rollback (la sesión no se commitea parcialmente). |
| Naming de índices | Respetar nombres del PMD (`idx_*`) para que Alembic autogenerate no cree duplicados. |

---

## 10. Trazabilidad

| Artefacto | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#27.md` | #27, HU-01 |
| Endpoint `POST /pedidos`, esquemas `PedidoCreate`/`PiezaCreate`/`PedidoResponse` | HU-01 — capturar pedido con medidas exactas (`ancho_mm`, `largo_mm`, `cantidad`) |
| Validaciones 422 (medidas negativas, cantidad 0, producto inválido, payload malformado) | Criterio de aceptación de #27: "Inyectar JSON inválido ... HTTP 422", "HTTP 201 con datos correctos" |
| Modelos `Client`, `Order`, `Product`, `Piece` + migración Alembic | `ERD-FASE1.md` §3–§6, #26 (HU-01, HU-02, HU-03) |
| No-auth, offline en front, sin rectpack | YAGNI Fase 1 (HU-03, HU-02, HU-14 diferidos) |
