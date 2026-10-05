# PLAN #38 — Sincronización offline → API (Ventas PWA)

- **Tarea:** #38 — Subtarea 4: Sincronización offline → API (Ventas PWA) (issue de GitHub: "Subtarea 4: Sincronización offline → API")
- **Historias de Usuario:** HU-08 — "Trabajar sin internet (PWA)" (issue #10: *los cambios realizados sin conexión deben encolarse y sincronizarse automáticamente con el servidor al recuperar la red*); extiende HU-01 — "Registrar el pedido del cliente".
- **Rama:** `feature/38-sync-offline-api` (nacida de `develop`, ya checkouteada).
- **Fecha:** 2026-10-04
- **Documentos de referencia:** `docs/planning/PLAN-#28.md` (§4 estrategia offline-first, §10 brechas), `apps/ventas-pwa/src/db/dexieDb.js`, `apps/ventas-pwa/src/components/PedidoForm.jsx`, `apps/ventas-pwa/src/pages/PedidosPage.jsx`, `apps/api/schemas.py` (`PedidoCreate`/`PiezaCreate`), `apps/api/routers/pedidos.py` (POST /pedidos → 201/404), `apps/api/models.py`, `apps/taller-pwa/src/services/tareasApi.js` (patrón de cliente HTTP a copiar), `docs/planning/WORKFLOWS.md` (flujo Planificador→Implementador→Revisor).
- **Stack existente:** `apps/ventas-pwa` con Vite 8.3, React 19.2, react-router-dom 7, Dexie 4.4 + dexie-react-hooks, vitest 5 + jsdom + fake-indexeddb + Testing Library ya configurados (`vite.config.js` tiene bloque `test`). **No se requieren dependencias nuevas** (fetch nativo).

---

## 1. Objetivo y alcance exacto

### Qué hace
- Implementa la **sincronización de pedidos locales hacia la API** en `apps/ventas-pwa`: los pedidos guardados offline con `estadoSync: 'pendiente'` se envían a `POST /pedidos` de `apps/api` automáticamente al recuperar la conexión.
- **Checklist de #38 cubierto:**
  1. Detecta `navigator.onLine` y escucha `window.addEventListener('online')`.
  2. Al detectar conexión, busca pedidos con `estadoSync === 'pendiente'` en Dexie.
  3. Envía cada pedido a `POST /pedidos` con el payload mapeado a `PedidoCreate`.
  4. Al éxito (HTTP 201), marca `estadoSync = 'sincronizado'` en Dexie.
  5. Al error (red caída, 4xx/5xx), mantiene `estadoSync = 'pendiente'` y registra el mensaje de error.
- Añade **UI de estado de sincronización**: indicador con cantidad de pedidos pendientes y mensaje de resultado (`role="status"`).
- Dispara sincronización también: al montar la app (si ya hay red), manualmente (botón "Sincronizar") y tras guardar un pedido estando online (intento inmediato best-effort).

### Qué NO hace (YAGNI, explícito)
- **No** implementa Service Workers ni cacheo del shell de la PWA (otro criterio de HU-08; tarea futura separada). #38 cubre solo el criterio de *"encolar y sincronizar al recuperar la red"*.
- **No** implementa JWT/auth en el envío (HU-03, fase posterior; la API aún no lo exige).
- **No** implementa reintentos automáticos con backoff exponencial, cola persistente de reintentos programada, ni resolución de conflictos. El reintento ocurre en los disparadores naturales (evento `online`, montaje, guardado, botón manual).
- **No** crea endpoints nuevos en la API ni edita `apps/api` ni `apps/taller-pwa`. Cambios limitados a `apps/ventas-pwa` + este documento.
- **No** borra registros locales tras sincronizar: Dexie sigue siendo la fuente de verdad en campo; el servidor es la réplica.

---

## 2. Lógica de sincronización

### Cuándo ejecutar (disparadores)
| # | Disparador | Dónde | Condición |
|---|------------|-------|-----------|
| 1 | Montaje de la app | `useSincronizacion()` (useEffect en mount) | solo si `hayConexion()` |
| 2 | Recuperación de red | listener `window.addEventListener('online', ...)` con cleanup en el mismo effect | siempre (el evento solo se dispara con red) |
| 3 | Tras guardar un pedido | `PedidoForm.onSubmit` → `onGuardado` → `sincronizar()` | mejor esfuerzo; si no hay red, no hace nada |
| 4 | Botón manual "Sincronizar" | componente `SyncStatus` | siempre; sin red muestra mensaje "sin conexión" |

> Nota: hay dos instancias del hook (una en `App.jsx` para la UI y otra en `CapturarPedidoPage` para el post-guardado). La corrección ante posibles doble-envíos está en el **servicio**, no en el hook: `syncPedidosPendientes()` tiene cerrojo a nivel de módulo (§3.3), por lo que dos instancias nunca envían el mismo pedido dos veces.

### Algoritmo de cola
```
syncPedidosPendientes():
  1. Si !navigator.onLine → retornar { sincronizados: 0, errores: 0, mensaje: "Sin conexión..." } SIN tocar fetch.
  2. Cerrojo: si ya hay una ejecución en curso → encadenar una re-verificación al terminar (evita duplicados por StrictMode/multi-disparador y recoge pedidos guardados durante la corrida).
  3. Snapshot: pendientes = db.pedidos.where('estadoSync').equals('pendiente').toArray()
  4. Para CADA pendiente, SECUENCIAL (for..of con await, NO Promise.all — orden determinista, sin carreras por el cerrojo):
       a. piezas = db.piezas.where('pedidoIdLocal').equals(idLocal).toArray()
       b. payload = construirPayload(pedido, piezas)          ← §5 (lanza si no resuelve cliente/producto)
       c. resp = fetch(`${API_URL}/pedidos`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
       d. Si !resp.ok → lanzar Error(`API respondió ${resp.status}`)
       e. marcarSincronizado(idLocal)  →  db.pedidos.update(idLocal, { estadoSync:'sincronizado', ultimoError:null })
  5. Retornar resumen { sincronizados, errores, erroresDetalle[], mensaje } para la UI.
```

### Manejo de errores
| Escenario | Comportamiento |
|---|---|
| Sin red (`navigator.onLine === false`) | No se llama a fetch; resumen con mensaje "Sin conexión"; todo sigue `pendiente`. |
| `fetch` rechaza (TypeError: Failed to fetch, CORS, DNS) | `catch` por pedido → mantiene `pendiente`, escribe `ultimoError` en la fila, `console.warn`, cuenta en `errores`. |
| HTTP 4xx/5xx (p. ej. 404 cliente/producto no existe, 500) | Se lanza `Error("API respondió <status>")` → mismo camino de error: `pendiente` preservado + mensaje registrado. |
| Fallo al escribir `ultimoError` en Dexie | No bloquea: el `catch` interno del update se ignora (el estado `pendiente` ya es el rollback natural). |
| Pedido guardado DURANTE una corrida de sync | El cerrojo encadena una nueva pasada al terminar (§3.3), así se recoge sin perderlo. |

El estado `pendiente` es a la vez la **cola** y el **rollback**: nunca se muta a `sincronizado` salvo tras 201 confirmado, por lo que cualquier fallo deja el pedido listo para reintentar en el próximo disparador.

---

## 3. Servicio `src/services/syncService.js`

Módulo **puro (sin React)**, testeable en aislamiento, siguiendo el patrón de `apps/taller-pwa/src/services/tareasApi.js`.

```js
// AVAO — Tarea #38, HU-08 / HU-01
// Servicio de sincronización offline→API: envía pedidos 'pendientes' a POST /pedidos.
import { db, getPiezasDePedido } from '../db/dexieDb'
import { CLIENTES_POR_NOMBRE, PRODUCTOS_POR_ID_LOCAL } from '../constants/mapeoApi'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/** Detecta conectividad. En tests se pisa via Object.defineProperty(navigator,'onLine'). */
export function hayConexion() {
  return typeof navigator === 'undefined' || navigator.onLine !== false
}

/** Mapea fila Dexie + piezas → body de PedidoCreate. Lanza si no resuelve cliente/producto (§5). */
export function construirPayloadPedido(pedido, piezas) {
  return {
    cliente_id: resolverClienteId(pedido.clienteNombre),      // UUID string
    fecha_entrega: pedido.fechaEntrega || null,               // 'YYYY-MM-DD' del <input type=date>
    notas: combinarNotas(pedido),                             // notas + teléfono (GAP C, §5.2)
    piezas: piezas.map((p) => ({
      producto_id: resolverProductoId(p.productoId),          // UUID string
      ancho_mm: Number(p.ancho_mm),
      largo_mm: Number(p.largo_mm),
      cantidad: Number(p.cantidad),
    })),
  }
}

export async function marcarSincronizado(pedidoIdLocal) {
  await db.pedidos.update(pedidoIdLocal, { estadoSync: 'sincronizado', ultimoError: null })
}

let syncEnCurso = null // cerrojo a nivel de módulo (§3.3)

export function syncPedidosPendientes() {
  if (!hayConexion()) {
    return Promise.resolve({
      sincronizados: 0, errores: 0, erroresDetalle: [],
      mensaje: 'Sin conexión: los pedidos siguen guardados localmente',
    })
  }
  if (syncEnCurso) return syncEnCurso.then(() => syncPedidosPendientes())
  syncEnCurso = ejecutarSync().finally(() => { syncEnCurso = null })
  return syncEnCurso
}

async function ejecutarSync() {
  const resumen = { sincronizados: 0, errores: 0, erroresDetalle: [], mensaje: '' }
  const pendientes = await db.pedidos.where('estadoSync').equals('pendiente').toArray()
  for (const pedido of pendientes) {
    try {
      const piezas = await getPiezasDePedido(pedido.idLocal)
      const payload = construirPayloadPedido(pedido, piezas)
      const resp = await fetch(`${API_URL}/pedidos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!resp.ok) throw new Error(`API respondió ${resp.status}`)
      await marcarSincronizado(pedido.idLocal)
      resumen.sincronizados++
    } catch (err) {
      // Mantiene 'pendiente' (checklist #38) y registra el mensaje.
      resumen.errores++
      resumen.erroresDetalle.push({ idLocal: pedido.idLocal, mensaje: err.message })
      await db.pedidos.update(pedido.idLocal, { ultimoError: err.message }).catch(() => {})
      console.warn(`[sync] pedido local ${pedido.idLocal} sigue pendiente:`, err.message)
    }
  }
  resumen.mensaje =
    resumen.sincronizados > 0
      ? `${resumen.sincronizados} pedido(s) sincronizado(s) con la API`
      : resumen.errores > 0
        ? `Error al sincronizar ${resumen.errores} pedido(s); se reintentará al recuperar la red`
        : 'No hay pedidos pendientes'
  return resumen
}
```

### 3.1 `navigator.onLine` — manejo
- `hayConexion()` centraliza la lectura (`navigator.onLine !== false`; en jsdom/tests se sobreescribe con `Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true })`).
- El hook añade el listener de evento:
```js
// src/hooks/useSincronizacion.js — AVAO — Tarea #38, HU-08
import { useCallback, useEffect, useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db } from '../db/dexieDb'
import { hayConexion, syncPedidosPendientes } from '../services/syncService'

export function useSincronizacion() {
  const pendientes = useLiveQuery(
    () => db.pedidos.where('estadoSync').equals('pendiente').count(), [], 0,
  )
  const [sincronizando, setSincronizando] = useState(false)
  const [resultado, setResultado] = useState(null)
  const enCurso = useRef(false)

  const sincronizar = useCallback(async () => {
    if (enCurso.current) return            // guardia por instancia (StrictMode dev)
    enCurso.current = true
    setSincronizando(true)
    try { setResultado(await syncPedidosPendientes()) }
    finally { setSincronizando(false); enCurso.current = false }
  }, [])

  useEffect(() => {
    if (hayConexion()) sincronizar()       // disparador 1: montaje
    const alRecuperarRed = () => sincronizar()
    window.addEventListener('online', alRecuperarRed)   // disparador 2
    return () => window.removeEventListener('online', alRecuperarRed)
  }, [sincronizar])

  return { pendientes, sincronizando, resultado, sincronizar }
}
```

### 3.2 `marcarSincronizado(pedidoIdLocal)`
- Usa `db.pedidos.update(id, {...})` (patch parcial de Dexie) en lugar de `put` — no requiere re-leer ni re-escribir la fila completa y no puede machacar campos añadidos por una edición concurrente.

### 3.3 Cerrojo a nivel de módulo (`syncEnCurso`)
- Garantiza **no doble-envío** ante: dos instancias del hook, efecto doble de React StrictMode en dev, y disparadores simultáneos (montaje + `online`).
- Si una llamada llega con una corrida en curso, se encadena `syncEnCurso.then(() => syncPedidosPendientes())`: tras terminar se re-lee la cola (captura pedidos guardados durante la corrida) y termina porque la re-lectura ya no tiene en curso. La recursión está acotada por eventos reales de guardado, no es un bucle.

---

## 4. UI: indicador visual y mensajes

### `src/components/SyncStatus.jsx` (nuevo)
```jsx
// AVAO — Tarea #38, HU-08
// Indicador de sincronización en la barra de navegación.
import { useSincronizacion } from '../hooks/useSincronizacion'

export default function SyncStatus() {
  const { pendientes, sincronizando, resultado, sincronizar } = useSincronizacion()
  return (
    <div data-testid="sync-status" aria-label="Estado de sincronización">
      <span data-testid="sync-pendientes" data-pendientes={pendientes}>
        {pendientes > 0 ? `⏳ ${pendientes} pendiente(s) de sincronizar` : '✓ sincronizado'}
      </span>
      <button type="button" onClick={sincronizar} disabled={sincronizando || pendientes === 0}>
        {sincronizando ? 'Sincronizando…' : 'Sincronizar'}
      </button>
      {resultado?.mensaje && <p role="status">{resultado.mensaje}</p>}
    </div>
  )
}
```

### Edición `src/App.jsx`
```jsx
import SyncStatus from './components/SyncStatus'
// ... dentro de <nav>, tras los <Link>:
<SyncStatus />
```

### Edición `src/pages/CapturarPedidoPage.jsx` (disparador 3: post-guardado)
```jsx
import PedidoForm from '../components/PedidoForm'
import { useSincronizacion } from '../hooks/useSincronizacion'

export default function CapturarPedidoPage() {
  const { sincronizar } = useSincronizacion()
  return (
    <main>
      <h1>Capturar pedido</h1>
      <PedidoForm onGuardado={sincronizar} />   {/* PedidoForm ya invoca onGuardado?.() tras addPedido */}
    </main>
  )
}
```

### Comportamiento visual
| Estado | Indicador |
|---|---|
| Hay pedidos `pendiente` | Badge ámbar "⏳ N pendiente(s) de sincronizar"; botón Sincronizar habilitado |
| Todo sincronizado | "✓ sincronizado" (verde, estilo existente de `PedidosPage`) |
| Sync exitosa | Mensaje `role="status"`: "N pedido(s) sincronizado(s) con la API" |
| Sync con errores | Mensaje `role="status"`: "Error al sincronizar N pedido(s); se reintentará al recuperar la red" |
| Sin red | Mensaje "Sin conexión: los pedidos siguen guardados localmente" |

`PedidosPage.jsx` **no requiere cambios** (ya muestra badge por fila con `useLiveQuery`, que se actualiza en vivo al cambiar `estadoSync`). Opcional para el Implementador: mostrar `ultimoError` bajo la fila — no obligatorio.

---

## 5. Payload: mapeo Dexie pedido → `PedidoCreate` (Pydantic)

### 5.1 Tabla de mapeo
| Dexie (`pedidos`/`piezas`) | `PedidoCreate`/`PiezaCreate` | Transformación |
|---|---|---|
| `clienteNombre` (string) | `cliente_id: uuid.UUID` **requerido** | Vía `resolverClienteId()` — **GAP A** (§5.3) |
| `fechaEntrega` ('YYYY-MM-DD' de `<input type=date>`) | `fecha_entrega: date \| null` | Directo; `''`/`null` → `null` |
| `notas` + `telefono` | `notas: str \| null` | Plegado — **GAP C** (§5.2) |
| `piezas[].productoId` ('vidrio-claro-6') | `producto_id: uuid.UUID` **requerido** | Vía `resolverProductoId()` — **GAP B** (§5.3) |
| `piezas[].ancho_mm / largo_mm / cantidad` | `ancho_mm / largo_mm: Decimal`, `cantidad: int` | `Number()` (ya validados > 0 por `validarPedido`) |
| — | `operario_asignado` | Se omite (opcional; se asigna en Taller) |

Ejemplo de body enviado:
```json
{
  "cliente_id": "a1b2c3d4-0000-4000-8000-000000000001",
  "fecha_entrega": "2026-10-10",
  "notas": "Tel: 555-1234 — Entregar en mostrador",
  "piezas": [{ "producto_id": "a1b2c3d4-0000-4000-8000-000000000011", "ancho_mm": 100, "largo_mm": 200, "cantidad": 2 }]
}
```

### 5.2 GAP C — `telefono` no existe en `PedidoCreate`
`PedidoCreate` **no tiene** campo `telefono` (Pydantic v2 por defecto ignora claves extra: enviarlo sería **pérdida silenciosa** de dato). Decisión: plegarlo en `notas` para preservarlo:
```js
function combinarNotas(pedido) {
  const partes = []
  if (pedido.telefono) partes.push(`Tel: ${pedido.telefono}`)
  if (pedido.notas && pedido.notas.trim()) partes.push(pedido.notas.trim())
  return partes.length ? partes.join(' — ') : null
}
```
Cuando la API crezca (campo `telefono` en pedido o cliente con teléfono), se despliega y se quita el plegado — documentado en §9.

### 5.3 GAPS A y B — la brecha conocida de PLAN-#28 §10 (`clienteNombre` vs `cliente_id`)
**Problema:** `POST /pedidos` exige `cliente_id` UUID de un cliente **ya existente** en `clientes` (si no, 404) y `producto_id` UUID de `productos` (idem). Hoy:
- No existen `GET /clientes`, `POST /clientes`, `GET /productos` (HUs futuras de catálogo/clientes).
- La PWA captura `clienteNombre` libre y usa ids semánticos locales (`'vidrio-claro-6'`), **no UUIDs**.

**Decisión de diseño (no bloqueante):** capa de resolución con **directorio local manual** en `src/constants/mapeoApi.js`:
```js
// AVAO — Tarea #38, HU-08/HU-01
// Mapeo local → UUIDs de la API. RELLENAR con los UUID reales de la BD (§5.4).
// Es un placeholder hasta que existan GET /clientes y GET /productos (HU de catálogo):
// entonces este archivo se reemplaza por un caché poblado desde la API.
export const CLIENTES_POR_NOMBRE = {
  'vidriería lópez': 'a1b2c3d4-0000-4000-8000-000000000001', // nombre.trim().toLowerCase() → UUID
}
export const PRODUCTOS_POR_ID_LOCAL = {
  'vidrio-claro-6': 'a1b2c3d4-0000-4000-8000-000000000011',
  'vidrio-templado-10': 'a1b2c3d4-0000-4000-8000-000000000012',
  'vidrio-esmerilado-4': 'a1b2c3d4-0000-4000-8000-000000000013',
  'aluminio-perfil-2x1': 'a1b2c3d4-0000-4000-8000-000000000014',
  'otro-espejo-4': 'a1b2c3d4-0000-4000-8000-000000000015',
}

export function resolverClienteId(clienteNombre) {
  const clave = (clienteNombre || '').trim().toLowerCase()
  const id = CLIENTES_POR_NOMBRE[clave]
  if (!id) throw new Error(`Cliente sin UUID de API: "${clienteNombre}" (registrar cliente primero)`)
  return id
}
export function resolverProductoId(idLocal) {
  const id = PRODUCTOS_POR_ID_LOCAL[idLocal]
  if (!id) throw new Error(`Producto sin UUID de API: "${idLocal}"`)
  return id
}
```
- Si el mapeo no resuelve → `construirPayloadPedido` **lanza** → camino de error de §2 → el pedido queda `pendiente` con `ultimoError` descriptivo. Esto es exactamente el comportamiento "al error, mantener 'pendiente'" del checklist: **un pedido de cliente desconocido nunca se envía basura a la API; se queda en cola** hasta que el catálogo de clientes exista.
- Los UUIDs del ejemplo son ilustrativos: el Implementador debe copiar los UUID **reales** de la BD (§5.4) y ambos lados (SQL + constante) deben coincidir.

### 5.4 Datos iniciales en la API (seed manual, una vez en dev)
No hay script de seed; con la API corriendo y migraciones aplicadas (`alembic upgrade head`), ejecutar en `infra/`:
```bash
cd infra
docker compose exec -T db psql -U avao -d avao <<'SQL'
INSERT INTO clientes (id, nombre, telefono) VALUES
  ('a1b2c3d4-0000-4000-8000-000000000001', 'Vidriería López', '555-1234');
INSERT INTO productos (id, nombre, tipo, espesor_mm) VALUES
  ('a1b2c3d4-0000-4000-8000-000000000011', 'Vidrio claro 6mm', 'vidrio', 6),
  ('a1b2c3d4-0000-4000-8000-000000000012', 'Vidrio templado 10mm', 'vidrio', 10),
  ('a1b2c3d4-0000-4000-8000-000000000013', 'Vidrio esmerilado 4mm', 'vidrio', 4),
  ('a1b2c3d4-0000-4000-8000-000000000014', 'Perfil aluminio 2x1', 'aluminio', 20),
  ('a1b2c3d4-0000-4000-8000-000000000015', 'Espejo 4mm', 'otro', 4);
SQL
```
Verificar: `docker compose exec -T db psql -U avao -d avao -c "SELECT id, nombre FROM clientes; SELECT id, nombre FROM productos;"` → copiar los UUID reales a `mapeoApi.js`.

---

## 6. Pruebas Vitest

**Archivos:** `src/test/syncService.test.jsx` (servicio + payload, fetch mockeado) y `src/test/sincronizacionUI.test.jsx` (integración UI: guardar offline → evento `online` → se envía y cambia estadoSync).

**Estrategia de mocks:**
- `vi.stubGlobal('fetch', vi.fn())` / `vi.unstubAllGlobals()` (vitest 5).
- `navigator.onLine` se sobreescribe: `Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true })` y se restaura a `true` en `beforeEach`.
- Dexie ya corre sobre `fake-indexeddb` vía `src/test/setup.js` (existente).
- La API no se levanta en tests: todo el HTTP es mockeado.

**Casos obligatorios (checklist de testing de #38 en negrita):**

| # | Caso | Verifica |
|---|---|---|
| 1 | **Guardar pedido offline** (`onLine=false`), luego `syncPedidosPendientes()` | fetch **no** fue llamado; `estadoSync` sigue `'pendiente'` |
| 2 | **Simular recuperación de red** (`onLine=true`) + sync | fetch llamado **1 vez** con `POST ${API_URL}/pedidos`, `Content-Type: application/json`, body = payload mapeo §5; fila Dexie queda `estadoSync: 'sincronizado'` |
| 3 | **Fallo de red** (fetch rechaza `TypeError`) | `estadoSync` **se mantiene `'pendiente'**`; `ultimoError` escrito; resumen `errores: 1` |
| 4 | Error HTTP 500 (`{ ok: false, status: 500 }`) | `estadoSync` sigue `'pendiente'`; `errores: 1` |
| 5 | 404 (cliente/producto no existe) | igual que 4; mensaje contiene "API respondió 404" |
| 6 | Cola de 2 pedidos: 1 éxito + 1 fallo | el exitoso queda `sincronizado`, el fallido `pendiente`; `sincronizados: 1, errores: 1` |
| 7 | Mapeo de payload | `fechaEntrega`→`fecha_entrega`; `telefono` plegado en `notas`; `ancho_mm/largo_mm/cantidad` como números; `cliente_id`/`producto_id` son los UUID del mapeo |
| 8 | Cliente sin mapeo | `construirPayloadPedido` lanza; pedido queda `pendiente` |
| 9 | UI: guardar offline en `CapturarPedidoPage`, luego `window.dispatchEvent(new Event('online'))` | aparece `role="status"` con mensaje de sincronización; badge de `SyncStatus` pasa de "N pendiente(s)" a "✓ sincronizado" |
| 10 | UI offline: guardar con `onLine=false` | mensaje "Pedido guardado localmente"; badge muestra "1 pendiente(s) de sincronizar"; fetch no llamado |

**Esqueleto de prueba (caso 2, el central):**
```jsx
// AVAO — Tarea #38, HU-08
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { addPedido, db } from '../db/dexieDb'
import { syncPedidosPendientes } from '../services/syncService'

const API_URL = 'http://localhost:8000'

describe('syncService (HU-08)', () => {
  let fetchMock
  beforeEach(async () => {
    await db.pedidos.clear(); await db.piezas.clear()
    Object.defineProperty(window.navigator, 'onLine', { value: true, configurable: true })
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })
  afterEach(() => { vi.unstubAllGlobals() })

  it('guarda offline y, al recuperar red, envía a POST /pedidos y marca sincronizado', async () => {
    // 1) guardar OFFLINE
    Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true })
    const idLocal = await addPedido({
      clienteNombre: 'Vidriería López', telefono: '555-1234', notas: 'Entregar en mostrador',
      fechaEntrega: '2026-10-10',
      piezas: [{ productoId: 'vidrio-claro-6', ancho_mm: '100', largo_mm: '200', cantidad: '2' }],
    })
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')

    // 2) simular recuperación de red
    Object.defineProperty(window.navigator, 'onLine', { value: true, configurable: true })
    fetchMock.mockResolvedValue({ ok: true, status: 201 })
    const resumen = await syncPedidosPendientes()

    // 3) verify: API recibió el payload correcto y Dexie cambió
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe(`${API_URL}/pedidos`)
    expect(init.method).toBe('POST')
    expect(init.headers['Content-Type']).toBe('application/json')
    expect(JSON.parse(init.body)).toEqual({
      cliente_id: 'a1b2c3d4-0000-4000-8000-000000000001',
      fecha_entrega: '2026-10-10',
      notas: 'Tel: 555-1234 — Entregar en mostrador',
      piezas: [{ producto_id: 'a1b2c3d4-0000-4000-8000-000000000011', ancho_mm: 100, largo_mm: 200, cantidad: 2 }],
    })
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('sincronizado')
    expect(resumen.sincronizados).toBe(1)
  })

  it('fallo de red mantiene estadoSync pendiente', async () => {
    const idLocal = await addPedido({
      clienteNombre: 'Vidriería López', telefono: null, notas: null, fechaEntrega: null,
      piezas: [{ productoId: 'vidrio-claro-6', ancho_mm: '10', largo_mm: '20', cantidad: '1' }],
    })
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))
    const resumen = await syncPedidosPendientes()
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')   // ← checklist #38
    expect(resumen.errores).toBe(1)
    expect(resumen.erroresDetalle[0].mensaje).toBe('Failed to fetch')
  })
})
```
> Los UUIDs de las aserciones deben coincidir con `src/constants/mapeoApi.js` tal como lo escriba el Implementador.

---

## 7. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO
git checkout feature/38-sync-offline-api        # ya está, verificar con: git status

# Archivos NUEVOS en apps/ventas-pwa/src/:
#   services/syncService.js        (§3)
#   hooks/useSincronizacion.js     (§3.1)
#   constants/mapeoApi.js          (§5.3 — rellenar UUIDs reales, §5.4)
#   components/SyncStatus.jsx      (§4)
#   test/syncService.test.jsx      (§6)
#   test/sincronizacionUI.test.jsx (§6)
# Archivos a EDITAR:
#   App.jsx                        (montar <SyncStatus /> en <nav>)
#   pages/CapturarPedidoPage.jsx   (useSincronizacion + onGuardado={sincronizar})

cd apps/ventas-pwa
npm test          # vitest run — todos los tests (existinges de #28 + nuevos) deben pasar
npm run lint      # oxlint — sin errores nuevos
npm run build     # vite build — debe compilar

# Prueba manual de aceptación (checklist #38):
npm run dev                                    # Ventas PWA en :5173
#   En otra terminal: API con migraciones + seed (§5.4):
cd ../api && source .venv/bin/activate && alembic upgrade head && uvicorn main:app --reload --port 8000
#   1. DevTools → Network → Offline; capturar pedido; verificar en Application → IndexedDB → avao-ventas:
#      pedidos.estadoSync = 'pendiente'.
#   2. Quedar Offline → marcar Online: verificar request POST /pedidos en Network (201),
#      estadoSync pasa a 'sincronizado' en IndexedDB y aparece el mensaje en el badge.
#   3. Con API detenida (error de red): guardar pedido → sigue 'pendiente', mensaje de error visible.
```

Prerrequisitos de entorno: API corriendo en `http://localhost:8000` (CORS ya permite `localhost:5173`), BD con migraciones y seed (§5.4). Nota: el `Dockerfile` de `apps/api` actualmente copia solo `main.py` (no los routers) — para la prueba manual usar `uvicorn` local como arriba; el Dockerfile es deuda de DevOps, fuera de alcance de #38.

**Commit** (conventional commit + trazabilidad, según `WORKFLOWS.md` §4):
```bash
git add apps/ventas-pwa docs/planning/PLAN-#38.md
git commit -m "feat(ventas-pwa): sincronización offline→API POST /pedidos con cola en Dexie (#38, HU-08, HU-01)"
```

---

## 8. Trazabilidad

| Artefacto / decisión | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#38.md` | Tarea #38 (Subtarea 4), HU-08 (issue #10), HU-01 (issue #1) |
| Detección `navigator.onLine` + listener `online` | #38 checklist 1, HU-08 AC "sincronizarse automáticamente al recuperar la red" |
| Búsqueda de `estadoSync === 'pendiente'` en Dexie | #38 checklist 2 |
| Envío a `POST /pedidos` con payload mapeado | #38 checklist 3, HU-01, `apps/api/schemas.py` (`PedidoCreate`), `apps/api/routers/pedidos.py` |
| Marcar `estadoSync = 'sincronizado'` al éxito | #38 checklist 4 |
| Mantener `'pendiente'` + registrar mensaje al error | #38 checklist 5 |
| Test: guardar offline → simular online → verify API + `estadoSync` | #38 Testing ítem 1 (§6 casos 1-2, 9-10) |
| Test: fallo de red mantiene `'pendiente'` | #38 Testing ítem 2 (§6 casos 3-5) |
| Extensión del guardado offline-first de #28 (`addPedido` con `estadoSync:'pendiente'`) | PLAN-#28 §4, HU-01 |
| Criterio HU-08 de Service Workers (cacheo de shell) | **Fuera de alcance de #38** — tarea futura separada (§1, §9) |
| Cliente/producto por UUID (mapeo local manual) | Brecha documentada en PLAN-#28 §10; resuelve parcialmente hasta el HU de catálogo/clientes |

---

## 9. Riesgos y límites explícitos

| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **`clienteNombre` no existe en la API** (brecha conocida #28 §10): `PedidoCreate` exige `cliente_id` UUID de cliente existente; no hay `GET/POST /clientes` | Pedidos de clientes no registrados no pueden sincronizarse (404) | Directorio local `mapeoApi.js` con seed manual (§5.3-5.4); mapeo no resuelto → error controlado → queda `pendiente` (nunca se envía basura). Resolución real: futuro HU de clientes (`POST /clientes` + `GET /clientes` + selector de cliente en el formulario). **Seguir en issue propio.** |
| **Duplicados si se reenvía** un pedido (reintento tras crash entre el 201 y el `update` de Dexie, o doble disparador) | Fila duplicada en `pedidos` de la API | (a) Solo se envían filas `estadoSync='pendiente'` y se marca `sincronizado` inmediatamente tras 201; (b) cerrojo de módulo §3.3 evita corridas simultáneas; (c) **riesgo residual** (ventana de crash entre 201 y write) se acepta en esta fase: la API no tiene idempotencia (no hay `idExterno`). Futuro: agregar `id_externo`/idempotency-key en API (issue nuevo). |
| **Error 500 / API caída** durante la sync | Pedidos no sincronizados | Se mantienen `pendiente` + `ultimoError`; reintento en próximo evento `online`/montaje/manual. Sin reintentos automáticos con backoff (YAGNI en #38). |
| **`productoId` local (string) vs `producto_id` UUID** + deriva entre catálogo local y `productos` de la API | 404 al sincronizar | Mismo directorio `mapeoApi.js`; cuando exista `GET /productos`, poblar el mapeo desde la API (reemplazar constante por caché). |
| **Pérdida silenciosa de `telefono`** (no hay campo en `PedidoCreate`) | Dato de contacto perdido | Se pliega en `notas` como `Tel: …` (§5.2); despliegue cuando el esquema API crezca. |
| **`ultimoError`** es campo no indexado agregado a filas existentes de Dexie | Ninguno: Dexie permite propiedades extra sin bump de versión | No requiere `db.version(2)`; compatible con datos existentes. |
| **StrictMode (React 19) dispara efectos dos veces en dev** | Doble sync en montaje | Guardia `enCurso` por instancia en el hook + cerrojo de módulo en el servicio (§3.3). |
| **Service Workers no implementados** (segundo criterio de HU-08: cachear sesión/tareas) | PWA no funciona 100% offline (solo el guardado/sync lo hace) | Fuera de alcance de #38 por su checklist; requiere `vite-plugin-pwa` + SW — proponer como tarea/HU separada. |
| **Pruebas con fetch mockeado, no contra API real** | El contrato real (404, validaciones Pydantic) no se ejercita en CI | Prueba manual de aceptación (§7) contra API real con seed; los tests de contrato ya existen en `apps/api/test_pedidos.py`. |
| **Dockerfile de `apps/api` incompleto** (no copia `routers/`) | La API en Docker no arranca | Deuda preexistente de DevOps, fuera de #38; para pruebas manuales usar `uvicorn` local (§7). |

---

*Fin del plan. Entregado por el rol Planificador (WORKFLOWS.md §2) para ejecución por el Implementador en `feature/38-sync-offline-api`.*
