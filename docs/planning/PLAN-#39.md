# PLAN #39 — Idempotencia de POST /pedidos (reintentos de sincronización)

- **Tarea:** #39 — "Evitar pedidos duplicados al reintentar la sincronización offline" (issue: https://github.com/ErickRamos37/AVAO/issues/39 — verificada **abierta**, sub-issue de #1/HU-01, el 2026-10-05).
- **Historias de Usuario:** HU-01 — "Registrar el pedido del cliente" (issue #1); extiende HU-08 — "Trabajar sin internet" (issue #10): cierra el límite residual de #38 ("si el servidor crea el pedido y la respuesta se pierde, el reintento puede duplicarlo").
- **Rama:** `feature/39-idempotencia-post-pedidos` (nacer de `develop` al iniciar; verificar con `git status`).
- **Fecha:** 2026-10-05
- **PR conceptual conjunto:** #39 y #40 tocan el mismo endpoint (`POST /pedidos`) y el mismo servicio (`apps/ventas-pwa/src/services/syncService.js`). Se entregan como planes separados con trazabilidad propia; pueden integrarse en **un solo PR conjunto** o en dos PR secuenciales (#39 primero, #40 con rebase). Ver §11.
- **Documentos de referencia:** issue #39 (cuerpo y AC), `docs/planning/PLAN-#38.md` (§2 manejo de errores, §9 riesgo de duplicado), `docs/planning/DECISIONES-MVP-2026-10-05.md` (pendiente 2), `docs/planning/AUDITORIA-CIERRES-2026-10-05.md` (límite de #39 y patrón PostgreSQL desechable), `apps/api/routers/pedidos.py`, `apps/api/models.py`, `apps/api/schemas.py`, `apps/api/database.py`, `apps/api/test_pedidos.py`, `apps/api/alembic/versions/95354a0cc046_create_tables_for_pedidos_27.py`, `apps/ventas-pwa/src/db/dexieDb.js`, `apps/ventas-pwa/src/services/syncService.js`, `apps/ventas-pwa/src/test/syncService.test.jsx`.
- **Stack:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL (dev) / SQLite en memoria (tests); pytest + Ruff en `apps/api`; Vitest + jsdom + fake-indexeddb en `apps/ventas-pwa`. **Sin dependencias nuevas.**

---

## 1. Objetivo y alcance exacto

### Qué hace (checklist de la issue #39)
1. Cada pedido local lleva una **clave de idempotencia estable en todos sus intentos de envío**: UUID v4 generada por Ventas al crear el pedido local y persistida en Dexie con él (`pedidos.idempotencyKey`).
2. El servidor impide duplicados mediante una **restricción persistente**: columna `pedidos.clave_idempotencia` UUID `UNIQUE` (migración Alembic nueva, reversible).
3. El servidor **responde a un reintento con el identificador del pedido ya creado** (mismo `id`, HTTP 201 — decisión §2.3).
4. **Dos solicitudes concurrentes con la misma clave no crean dos pedidos ni piezas duplicadas**: la restricción UNIQUE captura la carrera; el perdedor recupera el ganador (§4 paso 5).
5. **La respuesta perdida tras la creación y un reintento posterior dejan exactamente un pedido**: cubierto por (2)+(3)+(4) y por las pruebas de §7.
6. **Ventas lo marca sincronizado al recibir HTTP 201** (contrato vigente, corregido en PR #42): sin cambio de contrato; solo se añade el header.
7. **Vida útil de la clave y comportamiento ante reutilización con payload diferente quedan documentados** (§5): clave permanente; reutilización con payload distinto → 409 Conflict.

### Qué NO hace (YAGNI, explícito)
- **No** cambia el contrato de `PedidoCreate`/`PedidoResponse` (el body es idéntico; la clave viaja en header).
- **No** implementa expiración ni limpieza de claves (§5).
- **No** implementa JWT/auth (HU-03), reintentos automáticos con backoff, Service Workers, ni la resolución de cliente/producto reales (**#40**).
- **No** toca `apps/taller-pwa` ni el flujo de tareas.

---

## 2. Decisiones de diseño

### 2.1 Mecanismo: header `Idempotency-Key` (propuesta para el pendiente 2 de DECISIONES-MVP)
- **Recomendación: header HTTP `Idempotency-Key: <UUID>`**, no campo en body.
- Justificación: (a) es el patrón estándar de la industria (Stripe, PayPal, AWS) para idempotencia de transporte; (b) no contamina el modelo de negocio `PedidoCreate` — la clave es metadato del *intento de envío*, no dato del pedido; (c) permite a proxies/Nginx tratarla como metadato sin tocar el schema; (d) CORS ya la admite (`apps/api/main.py` usa `allow_headers=["*"]`, incluido el preflight de un header custom).
- Alternativa rechazada: campo `idempotency_key` en `PedidoCreate` — obligaría a cambiar el schema y todos sus tests, mezclaría responsabilidades de transporte con datos de negocio y no es convención.
- **Formato:** UUID v4. Validación automática por FastAPI (`uuid.UUID = Header(...)`) → 422 si está malformada o ausente.

### 2.2 Generación y persistencia en Ventas
- `apps/ventas-pwa/src/db/dexieDb.js`: `addPedido` genera la clave con `generarIdempotencyKey()` (§6.1) y la persiste en la fila `pedidos` como `idempotencyKey`.
- La clave **nunca se regenera**: el mismo valor viaja en todos los reintentos (evento `online`, montaje, botón manual de `SyncStatus`).

### 2.3 Código de reintento: HTTP 201 (propuesta para el pendiente 2 de DECISIONES-MVP)
- **Recomendación: el replay responde 201** con el pedido existente, no 200.
- Justificación: el contrato vigente de Ventas (corregido en PR #42 y verificado en la auditoría de cierres) exige **exactamente 201** para marcar sincronizado; `syncService.js` trata cualquier otro status como error (`API respondió N; se esperaba 201`). Aceptar 200 obligaría a re-editar el servicio y contradeciría esa corrección auditada. Es una **desviación intencional** de la semántica REST pura (donde el replay suele ser 200), a cambio de la estabilidad del contrato cliente. Queda registrada aquí y en DECISIONES-MVP (pendiente 2) para decisión del Coordinador al integrar.
- El cuerpo del replay es el `PedidoResponse` completo del pedido existente (mismo `id`, piezas originales).

### 2.4 Obligatoriedad del header (decisión del Coordinador)
- **Recomendación: obligatorio** en `POST /pedidos` (422 si falta). Justificación: garantiza que *todo* pedido nuevo tenga clave estable (la AC dice "cada pedido local"); el único cliente actual (Ventas) se actualiza en este mismo PR; evita una ruta silenciosa sin protección.
- Impacto aceptado: los tests API existentes se ajustan para enviar el header (§7.1). Si el Coordinador prefiere **opcional**, la columna sigue siendo nullable y el endpoint omite la protección cuando no hay clave — el resto del plan no cambia.

---

## 3. Persistencia en el servidor

### 3.1 Modelo (`apps/api/models.py`, clase `Order`) — #39 / HU-01, HU-08
```python
clave_idempotencia: Mapped[uuid.UUID | None] = mapped_column(
    Uuid, unique=True
)  # UNIQUE persistente: la restricción que impide duplicados (#39)
payload_hash: Mapped[str | None] = mapped_column(String(64))  # SHA-256 del payload canónico
```
- `unique=True` crea la restricción `uq_pedidos_clave_idempotencia` (convención de nombres de `apps/api/database.py`).
- **Nullable**: las filas pre-#39 (si existieran en alguna BD de dev) no tienen clave; PostgreSQL admite múltiples NULL en un índice UNIQUE. Todo pedido nuevo sí la lleva (header obligatorio, §2.4).
- `payload_hash` detecta "misma clave, payload diferente" → 409. **No** es único: varios pedidos distintos pueden compartir contenido; la identidad de reintentos es la clave.

### 3.2 Migración Alembic (nueva revisión, ej. `a3f1c2d4e5b6`)
```python
# apps/api/alembic/versions/a3f1c2d4e5b6_idempotencia_pedidos_39.py  — #39 / HU-01
revision = "a3f1c2d4e5b6"
down_revision = "95354a0cc046"   # o la revisión de #35 si ya está merged (§11)

def upgrade() -> None:
    op.add_column("pedidos", sa.Column("clave_idempotencia", sa.Uuid(), nullable=True))
    op.add_column("pedidos", sa.Column("payload_hash", sa.String(length=64), nullable=True))
    op.create_index(
        "uq_pedidos_clave_idempotencia", "pedidos", ["clave_idempotencia"], unique=True
    )

def downgrade() -> None:
    op.drop_index("uq_pedidos_clave_idempotencia", table_name="pedidos")
    op.drop_column("pedidos", "payload_hash")
    op.drop_column("pedidos", "clave_idempotencia")
```
- Reversible; verificar con `alembic upgrade head` y `alembic downgrade -1` contra PostgreSQL 17 desechable (patrón de `AUDITORIA-CIERRES-2026-10-05.md` §Reproducción).

---

## 4. Comportamiento del endpoint `POST /pedidos`

Flujo (`apps/api/routers/pedidos.py`):
```
1. Validar payload (Pydantic + formato UUID del header)  → 422 si inválido
2. Buscar por clave_idempotencia                          → si existe:
     2a. payload_hash coincide  → devolver el pedido existente (201, mismo id)
     2b. payload_hash difiere   → 409 Conflict, detail explícito
3. Validar cliente/producto (404, código actual)
4. Crear Order con clave_idempotencia + payload_hash; db.add; db.commit
5. Si commit lanza IntegrityError (carrera: otra solicitud ganó la UNIQUE):
     db.rollback() → re-query por clave → devolver el ganador (201).
     Si no aparece (imposible en la práctica) → 500.
```
- Hash canónico: `sha256(json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":")))` — determinista para un mismo contrato.
- La búsqueda (paso 2) va **antes** de la validación de referencias: un reintento no debe fallar 404 por estado transitorio del catálogo — las referencias ya fueron validadas en la creación. Si la primera intentona falló 404, no existe fila con esa clave y el reintento vuelve a 404 (comportamiento consistente).

### Tabla de escenarios
| # | Escenario | Respuesta | Estado BD |
|---|-----------|-----------|-----------|
| 1 | Clave nueva, payload válido | 201 + pedido creado | 1 pedido, N piezas |
| 2 | Misma clave, payload idéntico (reintento) | 201 + **mismo id** | 1 pedido (sin piezas nuevas) |
| 3 | Misma clave, payload diferente | **409** "La clave Idempotency-Key ya se usó con un payload diferente…" | 1 pedido |
| 4 | Clave malformada (no UUID) | 422 | sin cambios |
| 5 | Header ausente (si §2.4 obligatoria) | 422 | sin cambios |
| 6 | Body inválido + clave válida | 422 (Pydantic primero) | sin cambios |
| 7 | Cliente/producto inexistente + clave nueva | 404 (comportamiento actual) | sin cambios |
| 8 | Dos POST simultáneos, misma clave y payload | ambos 201, **mismo id** | 1 pedido (UNIQUE + recuperación por IntegrityError) |

---

## 5. Vida útil de la clave (documentación exigida por la AC)
- **Permanente**: la clave nunca expira y **no hay limpieza automática** (YAGNI: no hay volumen ni política de retención que justifique un job de purga).
- **Un solo uso útil**: reutilizar la clave con payload distinto siempre devuelve 409; para un pedido genuinamente nuevo se genera una clave nueva. Ventas genera una clave por fila de Dexie, por lo que esto ocurre de forma natural.
- Documentado in-line en el docstring del router (convención de `README.md` §4) y en este plan.

---

## 6. Cambios en Ventas PWA

### 6.1 `src/db/dexieDb.js` — #39 / HU-01, HU-08
```js
/** UUID v4 para la clave de idempotencia (#39). Fallback para jsdom sin crypto.randomUUID. */
export function generarIdempotencyKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function")
    return crypto.randomUUID()
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16)
  })
}
// addPedido: añade idempotencyKey: generarIdempotencyKey() a la fila de pedidos
```
### 6.2 `src/services/syncService.js` — #39 / HU-08
- En `ejecutarSync`, el fetch incluye el header en **cada** intento:
```js
headers: {
  "Content-Type": "application/json",
  "Idempotency-Key": pedido.idempotencyKey, // #39: estable en todos los reintentos
},
```
- Guardia: si `pedido.idempotencyKey` falta (fila previa a #39), lanza `Error("Pedido local sin clave de idempotencia: regístrelo de nuevo")` → el pedido queda `pendiente` con `ultimoError` (no se envía desprotegido).
- No hay otro cambio: el contrato 201 → `marcarSincronizado` ya existe (checklist #38 punto 4).

---

## 7. Pruebas

### 7.1 API — pytest (`apps/api`)
- **Ajuste:** `payload_valido()` de `apps/api/test_pedidos.py` añade `headers={"Idempotency-Key": str(uuid.uuid4())}`; los tests existentes pasan a enviarlo (§8).
- **Nuevo** `apps/api/test_idempotencia.py` (mismos fixtures SQLite + TestClient):

| # | Caso | Verifica |
|---|------|----------|
| 1 | Primer POST con clave nueva | 201; `pedidos` count 1; piezas creadas |
| 2 | Repetición misma clave + payload idéntico | 201; **mismo `id`**; count 1; piezas sin duplicar |
| 3 | Misma clave + payload diferente (ej. cantidad) | 409; detail contiene "payload diferente"; count 1 |
| 4 | Clave malformada (`"no-es-uuid"`) | 422 |
| 5 | Header ausente | 422 (si §2.4) |
| 6 | Body inválido (ancho negativo) + clave válida | 422 |
| 7 | 404 cliente inexistente + clave nueva | 404; sin fila con esa clave (reintento vuelve a 404) |
| 8 | **Concurrencia** (PG-gated): 2 threads, misma clave y payload | exactamente 1 pedido; ambas respuestas 201 con el mismo `id` |

- El caso 8 usa un fixture `pg_client` propio (engine desde `AVAO_TEST_DATABASE_URL`; `get_db` sobreescrito con un sessionmaker que abre sesión por request — necesario para threads). **Solo se ejecuta cuando la variable está definida** (`pytest.mark.skipif`), contra PostgreSQL 17 desechable (patrón documentado en `AUDITORIA-CIERRES-2026-10-05.md` §Reproducción). SQLite en memoria con `StaticPool` comparte una conexión y no reproduce fielmente la carrera de escritura — límite documentado, equivalente al de la auditoría.
- La migración se verifica aparte con `alembic upgrade head` / `downgrade -1` en el PG desechable.

### 7.2 Ventas — Vitest (`apps/ventas-pwa/src/test/syncService.test.jsx`)
| # | Caso | Verifica |
|---|------|----------|
| 1 | `addPedido` genera y persiste `idempotencyKey` | UUID v4 válida en la fila Dexie |
| 2 | Sync exitoso envía header `Idempotency-Key` (actualiza el caso 2 actual) | header presente en el fetch; valor = el de Dexie |
| 3 | **Respuesta 201 perdida** (issue #39): primer intento rechaza con `TypeError` (el servidor creó el pedido pero la respuesta se perdió); reintento → 201 | fetch llamado 2 veces con **la misma clave y el mismo body**; tras el segundo, `estadoSync: 'sincronizado'`; **un solo** registro local con el **mismo `idLocal`** |
| 4 | Fila sin `idempotencyKey` (simulada manualmente) | error claro; sigue `pendiente`; fetch no llamado |

- La verificación de "exactamente un pedido en el servidor" corresponde a los tests API (§7.1 casos 2 y 8); el test de Ventas verifica el lado cliente (misma clave en todos los intentos, misma identidad local).

Esqueleto del caso central (caso 3):
```jsx
// AVAO — Tarea #39, HU-08 / HU-01
it("respuesta 201 perdida: reintento con la misma clave deja un solo pedido", async () => {
  const idLocal = await agregarPedido() // addPedido ahora persiste idempotencyKey
  fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch")) // 201 creado en servidor; respuesta perdida
  fetchMock.mockResolvedValueOnce({ ok: true, status: 201 })
  const resumen = await syncPedidosPendientes()

  expect(fetchMock).toHaveBeenCalledTimes(2)
  const h1 = fetchMock.mock.calls[0][1].headers["Idempotency-Key"]
  const h2 = fetchMock.mock.calls[1][1].headers["Idempotency-Key"]
  expect(h1).toBe(h2)
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual(
    JSON.parse(fetchMock.mock.calls[1][1].body),
  )
  const fila = await db.pedidos.get(idLocal)
  expect(fila.estadoSync).toBe("sincronizado")
  expect(fila.idempotencyKey).toBe(h1)
  expect(await db.pedidos.count()).toBe(1) // mismo idLocal, sin duplicado local
  expect(resumen.sincronizados).toBe(1)
})
```

---

## 8. Comandos exactos para el Implementador
```bash
cd /home/erick/Proyectos/AVAO
git checkout -b feature/39-idempotencia-post-pedidos develop   # o rebase si #35/#40 ya avanzaron

# API (comandos existentes, verificados en requirements.txt y ruff.toml)
cd apps/api
./.venv/bin/python -m pytest -q                 # suite existente (21, ajustada) + nueva; todo verde
./.venv/bin/python -m ruff check .              # sin errores nuevos

# Migración en PostgreSQL 17 desechable (patrón AUDITORIA-CIERRES §Reproducción):
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/alembic upgrade head
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/alembic downgrade -1  # reversible
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/python -m pytest -q -k idempotencia  # casos PG-gated

# Ventas PWA (scripts verificados en package.json)
cd ../ventas-pwa
npm test        # vitest run — 19 existentes (ajustados) + nuevos
npm run lint    # oxlint
npm run build   # vite build
```
Prueba manual de aceptación (Ventas es PWA móvil: emular viewport móvil en DevTools): Network → Offline; capturar pedido; detener la API; intentar sync (error, sigue `pendiente`); levantar la API; recuperar red → `POST /pedidos` con header `Idempotency-Key` visible en Network; **recargar la página** → el pedido sigue `sincronizado` en IndexedDB.

**Commits** (conventional commits + trazabilidad, `WORKFLOWS.md` §4):
```bash
git add apps/api docs/planning/PLAN-#39.md
git commit -m "feat(api): idempotencia en POST /pedidos con Idempotency-Key y restriccion UNIQUE (#39, HU-01, HU-08)"
git add apps/ventas-pwa
git commit -m "feat(ventas-pwa): clave de idempotencia estable al sincronizar pedidos (#39, HU-01, HU-08)"
```

---

## 9. Trazabilidad
| Artefacto / decisión | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#39.md` | Issue #39 (verificada abierta, sub-issue de #1/HU-01) |
| Clave UUID generada por el cliente, persistente en Dexie | AC #39 "clave de idempotencia estable en todos sus intentos de envío" |
| Columna `pedidos.clave_idempotencia` UNIQUE (migración Alembic) | AC #39 "el servidor impide duplicados mediante una restricción persistente" |
| Replay 201 con el id existente | AC #39 "responde a un reintento con el identificador del pedido ya creado"; contrato 201 de PR #42 |
| Recuperación por `IntegrityError` + UNIQUE | AC #39 "dos solicitudes concurrentes con la misma clave no crean dos pedidos ni piezas duplicadas" |
| 409 ante payload diferente; vida útil permanente | AC #39 "quedan documentados la vida útil de la clave y el comportamiento si se reutiliza con un payload diferente" |
| Header en cada reintento; marca sincronizado al 201 | AC #39 "Ventas lo marca sincronizado al recibir HTTP 201"; PLAN-#38 §2 |
| pytest (primer POST, repetición, concurrencia, payload diferente) | AC #39 "Pruebas requeridas: API y PostgreSQL" |
| Vitest (respuesta 201 perdida, reintento, idLocal conservado) | AC #39 "Pruebas requeridas: … Ventas: respuesta 201 perdida, reintento y conservación del mismo identificador local" |
| Mecanismo header y código 201 en replay | DECISIONES-MVP-2026-10-05 pendiente 2 (propuesta; decide el Coordinador) |

---

## 10. Riesgos y límites explícitos
| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **Cambio de contrato** (header obligatorio, §2.4) | Otros consumidores de `POST /pedidos` dejarían de funcionar; hoy solo existe Ventas | Ajuste en el mismo PR; decisión pendiente del Coordinador |
| **Semántica 201 en replay** | Puristas HTTP esperarían 200 | Justificada en §2.3 por el contrato corregido de #38 (PR #42); registrada en DECISIONES-MVP pendiente 2 |
| **Carrera no reproducible en SQLite** | El caso de concurrencia no se ejerce en el CI por defecto | Caso 8 PG-gated + verificación de migración en PG17 desechable; mismo límite de entorno que la auditoría |
| **Fugas de clave entre entornos** (misma clave en BD distinta) | Sin impacto: la unicidad es por BD | No aplica en MVP (una BD por entorno) |
| **Claves en filas previas a #39** | Sin clave → protección omitida | Guardia en `syncService`: error claro y sigue `pendiente` (§6.2) |
| **Evolución del schema de `PedidoCreate`** | Un cambio de contrato puede hashear distinto el "mismo" body | El hash se calcula siempre del payload recibido; los reintentos conservan el body original. Documentado |
| **Dependencia con #35/#40** | Las migraciones encadenan `down_revision` | Ver §11 |

---

## 11. Integración con #35 y #40 (PR conceptual conjunto)
- **#35 (pulgadas):** independiente del mecanismo de idempotencia; solo encadena la migración. El orden de planificación vigente (D1) es #35 antes de #39+#40. Si #35 mergea primero, `down_revision` de esta migración apunta a la revisión de #35.
- **#40:** toca `syncService.js` y `dexieDb.js` en el mismo bloque de sync. Opciones: (a) **PR conjunto #39+#40** (recomendado: un solo endpoint y un solo servicio; evita resolver conflictos); (b) PR separados: #39 primero y #40 con rebase sobre #39 (el header de #39 se conserva; #40 añade la resolución de referencias antes del fetch).
- El payload de `PedidoCreate` **no cambia** en #39; #40 sí afecta la *resolución* de `cliente_id`/`producto_id` (no el contrato).

---

*Fin del plan. Entregado por el rol Planificador (`docs/planning/WORKFLOWS.md` §2) para ejecución por el Implementador en `feature/39-idempotencia-post-pedidos`.*
