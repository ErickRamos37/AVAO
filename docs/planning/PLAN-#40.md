# PLAN #40 — Cliente y producto reales en captura y sincronización de Ventas

- **Tarea:** #40 — "HU-01 · Resolver cliente y producto reales en captura y sincronización de Ventas" (issue: https://github.com/ErickRamos37/AVAO/issues/40 — verificada **abierta**, sub-issue de #1/HU-01, el 2026-10-05).
- **Historia de Usuario:** HU-01 — "Registrar el pedido del cliente" (issue #1).
- **Rama:** `feature/40-clientes-productos-reales` (nacer de `develop` al iniciar; si #39 ya mergeó, rebase sobre `develop`).
- **Fecha:** 2026-10-05
- **PR conceptual conjunto:** #39 y #40 tocan `POST /pedidos` y `apps/ventas-pwa/src/services/syncService.js`. Se entregan como planes separados con trazabilidad propia; pueden integrarse en **un solo PR conjunto** o en dos PR secuenciales (#39 primero, #40 con rebase). Ver §11.
- **Documentos de referencia:** issue #40 (cuerpo y AC), `docs/planning/DECISIONES-MVP-2026-10-05.md` (D3 y pendiente 3), `docs/planning/PLAN-#38.md` (§5 GAPS A/B/C), `docs/planning/AUDITORIA-CIERRES-2026-10-05.md` (patrón PostgreSQL desechable y CDP), `apps/api/routers/pedidos.py`, `apps/api/routers/tareas.py` (patrón de paginación), `apps/api/models.py`, `apps/api/schemas.py`, `apps/api/main.py`, `apps/api/alembic/versions/95354a0cc046_create_tables_for_pedidos_27.py`, `apps/ventas-pwa/src/db/dexieDb.js`, `apps/ventas-pwa/src/services/syncService.js`, `apps/ventas-pwa/src/constants/{mapeoApi,catalogoProductos}.js`, `apps/ventas-pwa/src/components/{PedidoForm,ClienteFields,ProductoSelect,PiezasList,PiezaRow}.jsx`, `apps/ventas-pwa/src/hooks/useSincronizacion.js`, `apps/ventas-pwa/src/test/{syncService,capturaPedido}.test.jsx`, `apps/ventas-pwa/src/test/setup.js`, `infra/seed.sql`, `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md`.
- **Stack:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL (dev) / SQLite en memoria (tests); pytest + Ruff en `apps/api`; Vitest + jsdom + fake-indexeddb en `apps/ventas-pwa`. **Sin dependencias nuevas.**

---

## 1. Objetivo y alcance exacto

### Origen y alta de clientes y catálogo (exigido por la issue antes del diseño)
- **Origen del cliente:** la captura en Ventas (nombre libre, obligatorio). **No hay pantalla de "alta" de clientes en el MVP**: el cliente se **materializa en la API** en el momento de la sincronización mediante `POST /clientes` con find-or-create (D3). "Seleccionar" = sugerencias desde la caché Dexie de clientes ya vistos (`datalist`); "registrar" = escribir el nombre libremente.
- **Origen del catálogo:** `infra/seed.sql` (desarrollo) y, futuro, gestión de productos (fuera de alcance). Ventas lo consume por `GET /productos` y lo **cachea en Dexie** (D3); el catálogo estático `catalogoProductos.js` y el mapeo manual `mapeoApi.js` se **eliminan**.
- **Unidad y precisión de medidas** (`docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` §1/§4 + D2/D7): pulgadas decimales por la API; el espesor de producto es decimal libre (excepción D2: propiedad del material, no medida de corte; no se cuantiza a 1/16). Hoy la API usa `espesor_mm`/`NUMERIC(10,2)` — alineación con **#35** en §10.

### Qué hace (checklist de la issue #40)
1. Ventas permite **seleccionar o registrar al cliente** (datalist de caché + nombre libre) y **elegir producto** desde el catálogo real (nombre, tipo y características visibles en la opción).
2. Al guardar sin conexión conserva **referencias estables** en Dexie: `clienteNombre` (texto) y `productoId` = **UUID real del servidor** (del caché).
3. Al recuperar conexión, `POST /pedidos` usa **identificadores reales del servidor**: la sync resuelve/crea el cliente vía `POST /clientes` (find-or-create; homónimos no se confunden por la normalización + UNIQUE) y el producto desde el caché Dexie.
4. Si una referencia no puede resolverse → el pedido **sigue pendiente** con error claro; **nunca se envía un UUID incorrecto** (la resolución falla antes del POST).
5. **Prueba integrada** captura → sync → API → PostgreSQL, incluido **regreso tras recarga** (§7.3, tres niveles).

### Qué NO hace (YAGNI, explícito)
- **No** hay CRUD de clientes ni de productos (D3); **no** hay `GET /clientes` — find-or-create hace innecesaria la búsqueda remota; las sugerencias son caché local.
- **No** implementa JWT (HU-03), Service Workers, optimización de corte, ni cambios en `apps/taller-pwa`.
- **No** cambia `PedidoCreate` (sigue sin `telefono`; GAP C de PLAN-#38 §5.2 persiste — ver §5.4).

---

## 2. API: `POST /clientes` con find-or-create (D3)

### 2.1 Contrato
- Request `ClienteCreate`: `nombre` (str, requerido, 1–150), `telefono` (≤20, **discriminador**), `email` (≤255, **discriminador alternativo**), `direccion` (≤255, opc.). **Al menos un discriminador (`telefono` o `email`) es obligatorio** (422 si no hay ninguno) — decisión del responsable humano 2026-10-05 (DECISIONES §Resueltas.2).
- Response `ClienteResponse` (Pydantic, `from_attributes`): `id` (UUID real), `nombre`, `telefono`, `email`, `direccion`, `creado` (bool), `created_at`, `updated_at`.
- Status: **201 si creó, 200 si encontró existente** (propuesta; alternativa 200 siempre — decisión del Coordinador, §10).
- Errores: 422 (sin/vacío `nombre`; sin discriminador); 409 si el `email` ya pertenece a otro cliente (§2.4).

### 2.2 Normalización + discriminador (pendientes 2 y 3 de DECISIONES-MVP — RESUELTOS por el responsable humano, 2026-10-05)
- **Columna materializada `clientes.nombre_normalizado`** (String(150), NOT NULL), poblada por la aplicación:
  `normalizar_nombre(n) = re.sub(r"\s+", " ", unicodedata.normalize("NFC", n)).strip().casefold()`
- Justificación frente a índice en expresión o columna generada: NFC y `casefold` **no son expresables en SQL** (SQLite `lower()` es ASCII-only; PostgreSQL `lower()` no hace NFC ni casefold); un índice en expresión o una columna generada no reproducirían la normalización de Python y la unicidad dependería del dialecto. La columna materializada es **idéntica en SQLite (tests) y PostgreSQL (prod)**.
- **Discriminador obligatorio (decisión de negocio):** dos clientes legítimamente distintos con el mismo nombre **no se fusionan**. La clave de find-or-create es **`(nombre_normalizado, discriminador)`** donde discriminador = `telefono` si se proporciona, si no `email`:
  - Búsqueda: `SELECT ... WHERE nombre_normalizado = :n AND telefono = :tel` (si `telefono` está en la petición); si no, `WHERE nombre_normalizado = :n AND email = :email`.
  - Creación: con los discriminadores proporcionados.
  - **Unicidad de BD:** `UNIQUE (nombre_normalizado, telefono)` (índice compuesto; los NULL de `telefono` son distintos en el índice, igual en PostgreSQL y SQLite) + el `UNIQUE (email)` ya existente. Consecuencia verificada: dos clientes con mismo nombre y **distinto teléfono** → dos filas (correcto); mismo nombre y mismo teléfono → una fila (correcto); clientes sin teléfono distinguibles por email → protegidos por `UNIQUE (email)`; sin teléfono y con email repetido → 409 (correcto: no se pueden distinguir).
- Población: `@validates("nombre")` en el modelo `Client` (toda creación ORM rellena `nombre_normalizado`) y valor explícito en `infra/seed.sql`.
- **Homónimos de texto:** dos escritos que normalizan igual **y** comparten discriminador (ej. "vidriería lópez" vs "  VIDRIERÍA   LÓPEZ " con el mismo teléfono) resuelven al **mismo** cliente; nunca se crea una segunda fila.
- **Límite aceptado:** el discriminador es dato capturado en Ventas (teléfono —ya existente en el formulario y ahora obligatorio—; email opcional futuro). Si el negocio captura dos clientes homónimos con el **mismo** teléfono, se fusionan — documentado aquí como límite (no hay discriminador mejor en el MVP).

### 2.3 Carrera de creación simultánea
- Dos `POST /clientes` simultáneos con el mismo `(nombre_normalizado, discriminador)`: la UNIQUE compuesta captura la carrera; el perdedor hace `rollback` y re-`SELECT` por la clave completa → devuelve el ganador (find-or-create real). Patrón análogo a PLAN-#39 §4 paso 5.

### 2.4 Email duplicado con nombre distinto
- El modelo ya tiene `email` UNIQUE. Si el `POST` no encuentra el nombre pero el email colisiona con otro cliente → `IntegrityError` → re-`SELECT` por nombre → no hay → **409 Conflict** "Email ya registrado". El teléfono y la dirección del cliente existente **no** se sobreescriben en el reencuentro: find-or-create devuelve lo que hay; actualizar datos de contacto es CRUD, fuera del alcance D3.

---

## 3. API: `GET /productos` (D3)

- `GET /productos` → `list[ProductoResponse]`: `id`, `nombre`, `tipo`, `caracteristicas`, `espesor_in` (ver §10, dependencia #35).
- Filtro opcional `?tipo=` validado contra `TipoProducto` (422 si inválido); paginación ligera `limit` (default 50, 1–200) y `offset` (default 0) — mismo patrón que `apps/api/routers/tareas.py`.
- Orden: `nombre` ascendente (determinista para el caché). El catálogo es pequeño (decenas); la paginación es defensiva y coincide con el patrón vigente.

---

## 4. Modelos, esquemas y migración

- `apps/api/models.py` (`Client`): añade `nombre_normalizado: Mapped[str] = mapped_column(String(150), nullable=False)` e **índice único compuesto** `uq_clientes_nombre_telefono` sobre `(nombre_normalizado, telefono)` (§2.2) y `@validates("nombre")` que rellena el campo. (`email` ya tiene `unique=True`.)
- Migración Alembic nueva (ej. `b4e5f6a7c8d9`; `down_revision` = revisión de #39 o de #35 según orden, §10):
  - `upgrade`: add column nullable → **backfill en Python** (importar `normalizar_nombre` y actualizar fila a fila vía `op.get_bind()`; determinista y agnóstico de dialecto) → alter a NOT NULL → create **unique index compuesto** `(nombre_normalizado, telefono)`.
  - `downgrade`: drop index → drop column. Reversible; verificar en PG17 desechable.
- `apps/api/schemas.py`: `ClienteCreate`, `ClienteResponse`, `ProductoResponse` (con `model_config = ConfigDict(from_attributes=True)`).
- `apps/api/main.py`: `include_router(clientes.router)` y `include_router(productos.router)`; routers nuevos `apps/api/routers/clientes.py` y `apps/api/routers/productos.py` con docstring in-line **#40 / HU-01**.

---

## 5. Ventas PWA: resolución desde la API con caché en Dexie (D3)

### 5.1 Dexie schema v3 (`src/db/dexieDb.js`)

> **Coordinación con #35 (orden de integración D1: #35 → #39 → #40):** #35 ya ocupa `db.version(2)` (renombrar `ancho_mm`→`ancho_in` con `upgrade()`). Esta tarea usa **`db.version(3)`** y debe re-declarar el schema **post-#35** (propiedades `ancho_in`/`largo_in` en `piezas`), además de añadir las tablas de caché.

```js
// AVAO — Tarea #28 (v1) + Tarea #35 (v2) + Tarea #40 (v3), HU-01
db.version(3).stores({
  // #28 (v1) + #35 (v2): propiedades de medidas ya en pulgadas
  pedidos: "++idLocal, clienteNombre, fechaEntrega, estadoSync, createdAt",
  piezas: "++idLocal, pedidoIdLocal, productoId, ancho_in, largo_in, cantidad",
  // #40: caché poblado desde la API (nuevas tablas)
  clientes: "++idLocal, &idApi, nombreNormalizado, nombre", // & = índice único
  productos: "idApi, nombre, tipo",                          // clave = UUID del servidor
})
```
- **Dato previo (Dexie v1):** las piezas guardadas con `productoId` semántico (`"vidrio-claro-6"`) no resolverán tras la actualización → error claro en la sync y quedan `pendiente`; en dev se re-capturan. No hay datos de producción en el MVP (documentado en §10).

### 5.2 `src/services/catalogoService.js` (nuevo; reemplaza `mapeoApi.js` + `catalogoProductos.js`) — #40 / HU-01
```js
export async function cargarCatalogoProductos()        // GET /productos → Dexie (solo con red)
export function getProductosCache()                     // lectura Dexie (compatible con useLiveQuery)
export async function resolverProducto(idLocal)         // Dexie → idApi; lanza si no existe
export async function resolverOCrearCliente(nombre, telefono) // POST /clientes (telefono = discriminador obligatorio) → idApi; cachea
export function getClientesCache()                      // sugerencias para el datalist
```
- `resolverProducto`: `db.productos.get(idLocal)`; si no existe lanza `Producto no está en el catálogo local: "<id>" — carga el catálogo con conexión y reintenta`.
- `resolverOCrearCliente`: `POST /clientes` con `{ nombre, telefono }` (**`telefono` obligatorio** — discriminador, §2.2; lanza antes de enviar si el pedido local no lo tiene); acepta 200/201; hace `db.clientes.put({...})`; devuelve `cliente.id`. **Siempre consulta al servidor** (la sync ya solo corre online; el servidor es la fuente de verdad del find-or-create).
- `normalizarNombre` util JS (NFC + trim + collapse + casefold) para el campo `nombreNormalizado` de la caché.
- `cargarCatalogoProductos`: transacción `rw` con `db.productos.clear()` + `bulkPut(lista)` — el caché es **espejo del servidor** (un producto borrado server-side desaparece del caché y su resolución falla con error claro).

### 5.3 Componentes de captura
- `ProductoSelect.jsx`: recibe los productos del caché (prop o `useLiveQuery`) en lugar de `catalogoProductos`; cada `<option>` muestra `nombre` y, cuando existan, `tipo`/`caracteristicas` (AC: "nombre, tipo y características"). `value` = **UUID del servidor**. Si el caché está vacío: opción inhabilitada "Catálogo no disponible — conecta para cargarlo" (no se fabrican ids).
- `ClienteFields.jsx`: el input de nombre gana `list="clientes-conocidos"` + `<datalist>` con `getClientesCache()` (seleccionar o registrar). **Teléfono obligatorio** (discriminador, §2.2): `validarPedido` exige `telefono` no vacío ("El teléfono del cliente es obligatorio para registrar el pedido") — es el discriminador del find-or-create; el email queda como dato opcional futuro de la API.
- `App.jsx`: en el montaje, si `hayConexion()`, `cargarCatalogoProductos()` best-effort (`.catch(console.warn)`); `useSincronizacion.js` también recarga el catálogo (best-effort) al evento `online`.

### 5.4 `src/services/syncService.js` — flujo por pedido pendiente — #40 / HU-01
```
para cada pedido pendiente (secuencial; cerrojo de #38 intacto):
  1. piezas = getPiezasDePedido(idLocal)
  2. payload = await construirPayloadPedido(pedido, piezas):   // ahora async
       a. cliente_id = await resolverOCrearCliente(pedido.clienteNombre, pedido.telefono)  ← POST /clientes
       b. por cada pieza: producto_id = await resolverProducto(p.productoId)                      ← caché Dexie
          (falla → lanza; el pedido queda pendiente; NUNCA se envía UUID incorrecto)
       c. armar PedidoCreate (fecha/notas/cantidades como hoy; GAP C intacto)
  3. POST /pedidos con headers Content-Type + Idempotency-Key (#39)
  4. 201 → marcarSincronizado; otro status o error → pendiente + ultimoError
```
- Orden de peticiones por pedido: `POST /clientes` → `POST /pedidos`. Dos pedidos del mismo cliente hacen dos find-or-create (el servidor deduplica por la UNIQUE; no se cachea `cliente_id` entre pedidos — simple y correcto; optimización futura documentada).
- `construirPayloadPedido` pasa a ser **async**; sus tests se adaptan (§7.2).
- **GAP C (teléfono):** se envía a `POST /clientes` (dato del cliente) y, transicionalmente, sigue plegado en `notas` (PLAN-#38 §5.2) hasta que `PedidoCreate` tenga campo propio; desplegar entonces.
- Se **eliminan** `src/constants/mapeoApi.js` y `src/constants/catalogoProductos.js` (el historial de git conserva la trazabilidad; el commit indica el reemplazo). `infra/seed.sql` se mantiene como seed de dev, con `nombre_normalizado` explícito y comentario actualizado: los UUIDs **ya no** deben coincidir con constantes de la PWA (solo con la BD de dev).

---

## 6. Políticas de deriva y errores
| Escenario | Comportamiento |
|---|---|
| Producto borrado del servidor entre captura y sync | el caché lo tiene → el payload lo lleva → la API responde 404 → `pendiente` + `ultimoError`; el operario re-selecciona el producto. Política: el id local se resuelve al vuelo desde el caché; si el servidor lo rechaza, no se corrige automáticamente |
| Producto nunca cargado en caché (primera ejecución offline) | `resolverProducto` lanza **antes** de cualquier fetch → `pendiente` + error claro |
| Cliente no resoluble (red caída en `POST /clientes`) | error de red → `pendiente` + `ultimoError`; reintento en el próximo disparador |
| Catálogo cambió entre captura y sync (nuevo id) | la referencia estable es el UUID del caché; si el producto sigue existiendo, sincroniza con el id de entonces — la captura queda "snapshotted" al UUID del caché (documentado) |

---

## 7. Pruebas

### 7.1 API — pytest (`apps/api`)
- **Nuevo** `apps/api/test_clientes.py`:

| # | Caso | Verifica |
|---|------|----------|
| 1 | `POST /clientes` nuevo | 201, `creado: true`, `id` UUID; persistido |
| 2 | Mismo nombre exacto | 200, `creado: false`, **mismo `id`**; count 1 |
| 3 | Variante de nombre (mayúsculas, tildes NFC, espacios múltiples) | mismo `id`; count 1 — **homónimos no se confunden** |
| 4 | Sin `nombre` / nombre vacío | 422 |
| 5 | Email duplicado con nombre distinto | 409 |
| 6 | **Concurrencia** (PG-gated): N threads, misma clave `(nombre_normalizado, discriminador)` | 1 fila; todas las respuestas con el mismo `id` |
| 7 | **Sin discriminador** (ni `telefono` ni `email`) | 422 |
| 8 | **Dos clientes homónimos con distinto teléfono** | 2 filas con `id` distintos — **no se fusionan** (decisión del responsable, §2.2) |
| 9 | Mismo homónimo, mismo teléfono, variante de texto | mismo `id`; 1 fila |

- **Nuevo** `apps/api/test_productos.py`: lista completa; `?tipo=vidrio` filtra; `?tipo=plastico` → 422; `limit`/`offset` pagan.
- **Nuevo** `apps/api/test_flujo_integrado.py` (PG-gated, `AVAO_TEST_DATABASE_URL`): `POST /clientes` → `POST /pedidos` con `cliente_id` real + `producto_id` de seed → 201 → verificación SQL de pedido + piezas; repetición con la misma `Idempotency-Key` (#39) → mismo `id`. Es el nivel API→PostgreSQL de la prueba integrada del checklist.

### 7.2 Ventas — Vitest (`apps/ventas-pwa`)
- **Nuevo** `src/test/catalogoService.test.jsx`: carga y cachea (`clear` + `bulkPut` en Dexie); `resolverProducto` desde caché; lanza si no existe; `resolverOCrearCliente` hace `POST /clientes` y cachea; `getClientesCache` lee Dexie.
- `src/test/syncService.test.jsx` (ajustes):
  - `beforeEach` siembra `db.productos` con UUIDs reales (fixture local).
  - Caso central actualizado: la sync llama primero a `POST /clientes` y luego a `POST /pedidos` con `cliente_id` y `producto_id` **reales** (aserción de orden y de valores; ya no hay constantes `a1b2c3d4…`).
  - Producto fuera de caché → error claro, `pendiente`, **fetch no llamado**.
  - `POST /clientes` con 500 → `pendiente` + `ultimoError`.
  - Se conservan los casos de #39 (header idempotente, respuesta 201 perdida).
- `src/test/capturaPedido.test.jsx` (ajustes): `beforeEach` siembra `db.productos`; `llenarFilaValida` selecciona por UUID del caché; nuevo caso: guardar offline conserva `productoId` = UUID real (referencia estable); nuevo caso: datalist de clientes conocidos desde Dexie `clientes`.

### 7.3 Prueba integrada (checklist #40: captura → sync → API → PostgreSQL, con regreso tras recarga)
Tres niveles, con el límite de cada uno documentado:
1. **PWA (Vitest, automatizado):** captura offline (catálogo precargado en Dexie) → `onLine=true` → sync → verifica `POST /clientes` (nombre capturado) y `POST /pedidos` (ids reales + `Idempotency-Key`) → `estadoSync: 'sincronizado'` → **regreso tras recarga simulado**: re-apertura de Dexie (nueva instancia `new Dexie('avao-ventas')` sobre fake-indexeddb) y lectura del estado. *Límite: fetch mockeado (igual que la auditoría de #28/#38); Dexie es real.*
2. **API + PostgreSQL (pytest, PG-gated):** §7.1 `test_flujo_integrado.py` contra PostgreSQL 17 desechable. *Límite: no hay navegador.*
3. **E2E manual (Chromium + API real + PG):** checklist para Implementador/Coordinador — levantar la API con migraciones y `infra/seed.sql`; DevTools/CDP con `Network.emulateNetworkConditions` offline y viewport móvil (patrón de `AUDITORIA-CIERRES-2026-10-05.md` §#28); capturar pedido; recuperar red; verificar en Network `POST /clientes` y `POST /pedidos` (201); **recargar la página** y verificar que el pedido sigue `sincronizado` y el catálogo persiste en IndexedDB (`avao-ventas`). *Este es el único nivel que verifica la recarga real en navegador.*

---

## 8. Comandos exactos para el Implementador
```bash
cd /home/erick/Proyectos/AVAO
git checkout -b feature/40-clientes-productos-reales develop   # rebase si #39/#35 ya mergearon

# API (comandos existentes, verificados en requirements.txt y ruff.toml)
cd apps/api
./.venv/bin/python -m pytest -q                 # suite existente + nuevas; todo verde
./.venv/bin/python -m ruff check .              # sin errores nuevos

# Migración en PostgreSQL 17 desechable (patrón AUDITORIA-CIERRES §Reproducción):
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/alembic upgrade head
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/alembic downgrade -1  # reversible
DATABASE_URL="postgresql+psycopg2://avao:…@127.0.0.1:55432/avao" ./.venv/bin/python -m pytest -q -k "clientes or productos or flujo_integrado"  # casos PG-gated

# Ventas PWA (scripts verificados en package.json)
cd ../ventas-pwa
npm test        # vitest run — existentes (ajustados) + nuevos
npm run lint    # oxlint
npm run build   # vite build
```
Prueba manual de aceptación (viewport móvil): con API y PG levantados, cargar catálogo online; emular offline; capturar pedido (cliente nuevo, producto del caché); recuperar red; verificar `POST /clientes` (201) y `POST /pedidos` (201) en Network; recargar la página y verificar `sincronizado` en IndexedDB.

**Commits** (conventional commits + trazabilidad, `WORKFLOWS.md` §4):
```bash
git add apps/api infra/seed.sql docs/planning/PLAN-#40.md
git commit -m "feat(api): POST /clientes find-or-create y GET /productos con cache en Ventas (#40, HU-01)"
git add apps/ventas-pwa
git commit -m "feat(ventas-pwa): resolver cliente y producto reales desde API con cache Dexie (#40, HU-01)"
```

---

## 9. Trazabilidad
| Artifato / decisión | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#40.md` | Issue #40 (verificada abierta, sub-issue de #1/HU-01) |
| `POST /clientes` find-or-create por `(nombre_normalizado, discriminador)` | D3; AC #40 "al recuperar conexión, POST /pedidos usa identificadores reales del servidor; clientes homónimos no se confunden"; decisión del responsable (discriminador, §2.2) |
| Columna `clientes.nombre_normalizado` + UNIQUE compuesto `(nombre_normalizado, teléfono)` | Pendientes 2–3 de DECISIONES-MVP (resueltos, §2.2) |
| `GET /productos` con filtro `tipo` y paginación ligera | D3; patrón de `routers/tareas.py` |
| Caché Dexie `clientes`/`productos` (schema v2) | D3 "resolución desde la API con caché local en Dexie"; AC #40 "conserva referencias estables a cliente y producto en Dexie" |
| `datalist` de clientes + catálogo en `ProductoSelect` | AC #40 "Ventas permite seleccionar o registrar al cliente y elegir producto con nombre, tipo y características" |
| Error claro y `pendiente` si no resuelve | AC #40 "si una referencia no puede resolverse, el pedido sigue pendiente y muestra un error claro, sin enviarse con un UUID incorrecto" |
| Prueba integrada en 3 niveles (Vitest / pytest PG / E2E Chromium) | AC #40 "una prueba integrada cubre captura en Ventas → sincronización → API → PostgreSQL, incluido regreso tras recarga" |
| Eliminación de `mapeoApi.js` y `catalogoProductos.js` | D3 "la PWA Ventas reemplaza el mapeo manual mapeoApi.js"; GAPS A/B de PLAN-#38 §5.3 |
| Unidad pulgada decimal; espesor libre | D2/D7; `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` §1/§4 |

---

## 10. Riesgos y límites explícitos
| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **Primera ejecución sin red** | El caché de productos está vacío → no se pueden capturar piezas (antes sí, con catálogo estático) | Carga del catálogo en el primer montaje con red (§5.3); cambio de comportamiento aceptado: la referencia estable exige un UUID real. Documentado |
| **Fusión de homónimos con igual discriminador** | Dos clientes distintos con el mismo nombre **y** el mismo teléfono quedan como uno | Límite aceptado por el responsable (§2.2): el teléfono es el discriminador del MVP; no hay discriminador mejor sin HU futura. Documentado |
| **Deriva de catálogo** (producto borrado o renombrado server-side) | 404 al sincronizar → pedido `pendiente` | §6: el operario re-selecciona; no hay corrección automática (YAGNI) |
| **Doble llamada `POST /clientes`** por pedido del mismo cliente | Una petición extra por pedido | El servidor deduplica por la UNIQUE; optimización futura (cachear `cliente_id` entre pedidos) documentada |
| **Dato previo Dexie v1** (`productoId` semántico) | Esos pedidos no resolverán tras la actualización | Error claro y quedan `pendiente`; re-captura en dev. No hay datos de producción en el MVP |
| **Carrera no reproducible en SQLite** | Los casos de concurrencia no se ejercen en el CI por defecto | Casos PG-gated + verificación de migración en PG17 desechable; mismo límite de entorno que la auditoría |
| **Dependencia #35 (secuencia)** | `ProductoResponse.espesor_in` asume #35 merged (columna `espesor_in`, `NUMERIC(10,4)`) | **Orden confirmado por el Coordinador (D1): #35 → #39 → #40.** Si #40 debe implementarse antes, el campo se expone como `espesor_mm`/`NUMERIC(10,2)` y #35 lo renombra después (doble churn en el caché Dexie y en la versión de Dexie: #35=v2, #40=v3). |
| **Dependencia #39** | La sync envía `Idempotency-Key` | Si #40 mergea antes, el header se añade con #39 después (planes independientes en ese punto). Encadenamiento de migraciones: `down_revision` de #40 apunta a la revisión de #39 (o a la de #35, según orden) |
| **Status de `POST /clientes`** (201/200 + flag `creado`) | Contracto por definir | Propuesta §2.1; alternativa 200 siempre. Decisión del Coordinador |

---

## 11. Integración con #39 y #35 (PR conceptual conjunto)
- **#39:** la sync de §5.4 ya incluye el header `Idempotency-Key`. **Orden confirmado (D1): #39 antes que #40** — PR separados: #39 primero (migración `clave_idempotencia` encadena sobre #35) y #40 con rebase sobre #39 (su migración encadena sobre la de #39). Un PR conjunto #39+#40 es la alternativa si el Coordinador prefiere un solo merge.
- **#35:** define la unidad canónica (pulgadas) y renombra `*_mm` → `*_in`. #40 nace alineada si #35 ya mergeó; ver §10.
- Los cambios de #40 en `syncService.js` (resolución de referencias) y los de #39 (header) se componen sin conflicto: #39 añade el header a un payload que #40 resuelve.

---

*Fin del plan. Entregado por el rol Planificador (`docs/planning/WORKFLOWS.md` §2) para ejecución por el Implementador en `feature/40-clientes-productos-reales`.*
