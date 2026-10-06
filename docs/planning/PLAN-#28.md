# PLAN #28 — Interfaz de Captura PWA (Vite + React)

- **Tarea:** #28 — Subtarea 3: Interfaz de Captura PWA (Vite + React)
- **Historia de Usuario:** HU-01 — "Registrar el pedido del cliente" (como encargado de ventas quiero anotar los pedidos con medidas exactas).
- **Rama:** `feature/28-interfaz-captura-pwa` (nace de `develop`).
- **Fecha:** 2026-10-04
- **Documentos de referencia:** `apps/api/schemas.py` (`PedidoCreate`/`PiezaCreate`/`PedidoResponse`), `apps/api/models.py`, `apps/api/routers/pedidos.py`, `docs/design/ERD-FASE1.md`, `docs/planning/PLAN-#27.md`, `apps/ventas-pwa/` (scaffold Vite+React existente).
- **Stack existente:** `apps/ventas-pwa` con Vite 8.3, React 19.2, `@vitejs/plugin-react` 6.1, oxlint. **Aún sin** Dexie, sin react-router, sin formularios, sin tests.

---

## 1. Objetivo y alcance exacto

### Qué hace
- Construye en `apps/ventas-pwa` el **formulario dinámico de captura de pedido** (HU-01): datos del cliente, producto, y **N piezas** con `ancho_mm`, `largo_mm`, `cantidad`, añadibles/eliminables en tiempo de captura.
- Guarda el pedido de forma **temporal/local con Dexie.js (IndexedDB)**, estrategia **offline-first**: el pedido se persiste aunque no haya red.
- Expone una vista de listado de pedidos guardados localmente (`/pedidos`) leyendo desde Dexie.
- Prepara (sin implementar todavía) la sincronización con `POST /pedidos` de `apps/api` cuando haya conectividad.

### Qué NO hace (YAGNI, explícito)
- **No** implementa JWT ni flujo de login (HU-03, fase posterior).
- **No** implementa WebSockets ni UI de Taller/Operario.
- **No** implementa sincronización automática/background sync compleja ni reintentos con cola persistente sofisticada (se diseña, no se implementa).
- **No** crea endpoints en la API; solo consume el contrato ya existente de `POST /pedidos` cuando haya red (fetch directo sin auth por ahora).
- **No** optimiza cortes ni dibuja guías (eso es Taller/Canvas 2D, `rectpack`).
- **No** sube piezas/pedidos al servidor en esta fase salvo botón manual opcional de "sincronizar" si el implementador decide incluirlo como mínimo; la prioridad es guardar local.

---

## 2. Estructura de componentes React a crear

```
apps/ventas-pwa/src/
├── main.jsx                      (editar: envolver en <BrowserRouter> si se usa react-router)
├── App.jsx                       (editar: rutas o navegación por estado)
├── db/
│   └── dexieDb.js                (nuevo: instancia Dexie + esquema + helpers)
├── pages/
│   ├── CapturarPedidoPage.jsx    (nuevo: página /capturar)
│   └── PedidosPage.jsx           (nuevo: página /pedidos)
├── components/
│   ├── PedidoForm.jsx            (nuevo: orquestador del formulario)
│   ├── ClienteFields.jsx         (nuevo: nombre cliente requerido, teléfono opcional, notas)
│   ├── PiezaRow.jsx              (nuevo: fila editable de una pieza)
│   ├── PiezasList.jsx            (nuevo: lista dinámica + botón "Agregar pieza")
│   ├── ProductoSelect.jsx        (nuevo: select desde catálogo local)
│   └── ValidationMessage.jsx     (opcional: helper de error inline)
└── constants/
    └── catalogoProductos.js      (nuevo: catálogo estático local de productos con id/nombre/tipo)
```

### Responsabilidades
- **`PedidoForm`:** estado del formulario (cliente, notas, fecha_entrega), array `piezas` en estado React, validación antes de persistir, llamada a `dexieDb.addPedido(...)`.
- **`ClienteFields`:** `nombre` (requerido), `telefono` (opcional), `notas`/`fecha_entrega` del pedido.
- **`PiezasList`:** renderiza N `<PiezaRow>`, botón "Agregar pieza" (añade fila vacía), botón eliminar por fila. Mínimo 1 pieza.
- **`PiezaRow`:** `ProductoSelect` + inputs numéricos `ancho_mm`, `largo_mm`, `cantidad` + botón eliminar.
- **`PedidosPage`:** lista pedidos desde Dexie (`db.pedidos.toArray()` y `db.piezas.where('pedidoId').equals(id).toArray()`), badge de estado "pendiente de sincronizar".

> Decisión: catálogo de productos estático local (lista cerrada con `id`, `nombre`, `tipo`, `espesor_mm`) para no depender de endpoints aún inexistentes. Cuando exista `GET /productos`, se reemplaza por fetch.

---

## 3. Integración con Dexie.js

### Instalación
```bash
cd apps/ventas-pwa
npm install dexie dexie-react-hooks
```

### Base de datos local: `avao-ventas`

```js
// src/db/dexieDb.js
import Dexie from 'dexie'

export const db = new Dexie('avao-ventas')
db.version(1).stores({
  pedidos: '++idLocal, clienteNombre, fechaEntrega, estadoSync, createdAt',
  piezas: '++idLocal, pedidoIdLocal, productoId, ancho_mm, largo_mm, cantidad',
})
```

- `pedidos`: `{ idLocal, clienteNombre, fechaEntrega, notas, estadoSync: 'pendiente' | 'sincronizado', createdAt }`.
- `piezas`: `{ idLocal, pedidoIdLocal, productoId, ancho_mm, largo_mm, cantidad }`.

### Operaciones requeridas (checklist)
- **`add`**: insertar un pedido nuevo (`db.pedidos.add(...)`) y sus piezas (`db.piezas.bulkAdd(...)`).
- **`put`**: actualizar un pedido existente (p. ej. marcar `estadoSync: 'sincronizado'` tras POST exitoso) — `db.pedidos.put({...})` / `db.piezas.put({...})`.
- **`where`**: filtrar, p. ej. `db.piezas.where('pedidoIdLocal').equals(idLocal).toArray()` o `db.pedidos.where('estadoSync').equals('pendiente')`.
- **`toArray()`**: listar todos los pedidos/piezas para la vista `/pedidos`.
- Hook reactivo recomendado: `useLiveQuery` de `dexie-react-hooks` para que la UI se actualice al persistir.

### ¿Por qué Dexie y no localStorage?
| Criterio | localStorage | Dexie (IndexedDB) |
|---|---|---|
| Modelo de datos | clave-valor, strings | BD transaccional orientada a objetos |
| Volumen/estructura | ~5 MB, sin índices | Cientos de MB, índices y queries |
| Queries | manuales (parsear todo) | `where`, filtros, ordenamiento nativos |
| API | síncrona, bloqueante | asíncrona (Promises), no bloquea UI |
| Esquema/versionado | ninguno | `version(n).stores(...)` con migraciones |
| Tipado/relaciones | serializar a mano | tablas relacionadas (`pedidoIdLocal`) naturales |

Para pedidos con piezas (relación 1:N), offline-first con queries por estado y crecimiento de datos, localStorage es insuficiente; Dexie es el wrapper estándar de IndexedDB recomendado por el stack (Vite + React) y permite crecer sin reescribir.

---

## 4. Estrategia offline-first

### Qué se guarda cuando no hay red
1. El usuario llena el formulario en `/capturar`.
2. Al guardar, **siempre** se persiste primero en Dexie (`avao-ventas`): un registro en `pedidos` con `estadoSync: 'pendiente'` y N registros en `piezas` enlazados por `pedidoIdLocal`, dentro de una transacción Dexie (`db.transaction('rw', db.pedidos, db.piezas, ...)`).
3. La UI confirma "Pedido guardado localmente" y la fila aparece en `/pedidos` con badge "pendiente de sincronizar".

### Cómo se sincronizaría después (diseño; implementación completa opcional en esta fase)
- Al recuperar conectividad (evento `window.online` o botón "Sincronizar"):
  1. Leer pendientes: `db.pedidos.where('estadoSync').equals('pendiente').toArray()`.
  2. Por cada pedido, armar el payload `PedidoCreate` (`cliente_id`, `fecha_entrega`, `notas`, `piezas[]` con `producto_id`, `ancho_mm`, `largo_mm`, `cantidad`) y hacer `fetch(POST /pedidos)`.
  3. Si HTTP 201 → `db.pedidos.put({...pedido, estadoSync: 'sincronizado'})`.
  4. Si falla (4xx/5xx o red caída) → mantener `estadoSync: 'pendiente'` para reintento posterior.
- No se borran los registros locales: la copia en Dexie es la fuente de verdad en campo; el servidor es réplica cuando hay red.
- **Nota de brecha conocida:** hoy `POST /pedidos` exige `cliente_id` (UUID de cliente existente). El formulario captura `clienteNombre`; el mapeo nombre→`cliente_id` requiere o bien un selector de clientes sincronizados o el futuro `POST /clientes`. Se documenta en §10 y se resuelve en subtarea posterior; en esta fase el botón de sincronización puede omitirse o dejarse deshabilitado.

---

## 5. Páginas / rutas sugeridas

- **Opción A (recomendada):** instalar `react-router-dom` y definir:
  - `/capturar` → `CapturarPedidoPage` (formulario HU-01).
  - `/pedidos` → `PedidosPage` (lista desde Dexie).
  - `/` → redirige a `/capturar`.
- **Opción B (mínima):** sin dependencia nueva, navegación por estado en `App.jsx` (`vista: 'capturar' | 'pedidos'`) con dos botones de tab.

Justificación: react-router es el estándar del ecosistema y habilita deep-linking/PWA install; si se quiere cero dependencias extra en esta fase, la Opción B es aceptable. El implementador elige y justifica en el PR.

---

## 6. Validaciones de formulario

| Campo | Regla | Mensaje |
|---|---|---|
| `clienteNombre` | requerido, no vacío, trim | "El nombre del cliente es obligatorio" |
| `producto_id` (por pieza) | debe pertenecer al catálogo (`<select>` controlado) | "Selecciona un producto del catálogo" |
| `ancho_mm` | número > 0 | "La medida debe ser mayor que 0" |
| `largo_mm` | número > 0 | "La medida debe ser mayor que 0" |
| `cantidad` | entero > 0 | "La cantidad debe ser mayor que 0" |
| `piezas` | al menos 1 pieza válida | "Agrega al menos una pieza" |

- Validación en cliente antes de escribir en Dexie; los mismos límites que `PiezaCreate` de la API (`gt=0`, `cantidad gt=0`) para que el payload futuro sea válido.
- Medidas negativas o cero → error inline por fila y **no** se persiste el pedido.

---

## 7. Plan de pruebas (Vitest + Testing Library)

### Instalación de tooling de test
```bash
cd apps/ventas-pwa
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom fake-indexeddb
```
- `vitest` + `jsdom` como environment en `vite.config.js` (`test: { environment: 'jsdom', setupFiles: './src/test/setup.js' }`).
- `fake-indexeddb` para que Dexie funcione en tests (`import 'fake-indexeddb/auto'` en el setup).
- Script en `package.json`: `"test": "vitest run"`.

### Casos obligatorios

| # | Caso | Qué se verifica |
|---|---|---|
| 1 | Renderiza el formulario | `/capturar` muestra campos de cliente, al menos 1 fila de pieza, botón "Agregar pieza" |
| 2 | Agregar N piezas dinámicamente | Click en "Agregar pieza" N veces → existen N+1 filas con sus inputs; eliminar una fila reduce el conteo |
| 3 | Guardar en Dexie (offline simulado) | Con `navigator.onLine = false` (o sin mockear fetch), rellenar formulario válido, guardar → `db.pedidos.toArray()` tiene 1 registro con `estadoSync: 'pendiente'` y `db.piezas.where('pedidoIdLocal').equals(id).toArray()` tiene las N piezas |
| 4 | Validación: medidas negativas | `ancho_mm = -5` → mensaje de error visible, `db.pedidos.count()` sigue en 0 |
| 5 | Validación: cantidad 0 / vacía, nombre de cliente vacío, producto no seleccionado | Errores inline, sin persistencia |
| 6 | Listado `/pedidos` | Tras guardar, la página lista el pedido con su cliente y badge "pendiente de sincronizar" |

### Prueba manual de aceptación (checklist de la tarea)
1. `npm run dev`, abrir DevTools → Network → **Offline**.
2. Capturar un pedido con 3 piezas y guardar.
3. Verificar en DevTools → Application → IndexedDB → `avao-ventas` que existen filas en `pedidos` y `piezas`.
4. Recargar la página (sigue offline) → `/pedidos` muestra el pedido guardado.

---

## 8. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO/apps/ventas-pwa

# 1) Dependencias de runtime
npm install dexie dexie-react-hooks
# (opcional) npm install react-router-dom

# 2) Dependencias de test
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom fake-indexeddb

# 3) Desarrollo
npm run dev

# 4) Tests
npm run test

# 5) Build de producción
npm run build

# 6) Lint (oxlint ya configurado)
npm run lint
```

> Añadir `"test": "vitest run"` en `apps/ventas-pwa/package.json` (scripts), ya que hoy no existe el script `test`.

---

## 9. Trazabilidad

| Artefacto | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#28.md` | #28, Subtarea 3, HU-01 |
| Formulario dinámico de piezas (N piezas, agregar/eliminar) | #28 checklist 1, HU-01 |
| `avao-ventas` en Dexie con tablas `pedidos` y `piezas` (`add`, `put`, `where`, `toArray()`) | #28 checklist 2, HU-01 |
| Prueba DevTools offline + verificación IndexedDB | #28 Testing |
| Payload compatible con `POST /pedidos` (`PedidoCreate`/`PiezaCreate`) | HU-01, `apps/api/schemas.py`, PLAN-#27.md |
| Catálogo local de productos, `clienteNombre` capturado | Brecha documentada: pendiente `POST /clientes`/`GET /productos`; ver §10 |

---

## 10. Riesgos y límites explícitos

| Riesgo / límite | Mitigación |
|---|---|
| **No implementar JWT todavía** | Sin login, sin headers `Authorization`; cuando exista HU-03 se añade fastapi-users en API y el interceptor fetch en PWA. |
| **No implementar WebSocket** | Ningún `WebSocket`/WSS en esta subtarea; pertenece a Taller (HU-02, #31+). |
| **No crear UI de Taller** | `apps/taller-pwa` queda intacto; no tocarlo. |
| **Sin sincronización automática compleja** | Solo diseño (§4); a lo sumo botón manual "Sincronizar" o listener `online` básico. Sin colas persistentes con backoff, sin idempotencia, sin resolución de conflictos. |
| **Brecha cliente_id**: la API exige `cliente_id` UUID de cliente existente y hoy no hay `POST /clientes` ni selector de clientes sincronizados | El formulario captura `clienteNombre`; marcar `estadoSync: 'pendiente'` y documentar que el mapeo a `cliente_id` se habilita cuando exista el endpoint de clientes. No inventar UUIDs en cliente. |
| **Sin catálogo remoto**: no hay `GET /productos` | Catálogo estático local (`constants/catalogoProductos.js`) alineado a los enums de `TipoProducto`; reemplazar por fetch cuando exista el endpoint. |
| **Tests con fake-indexeddb**, no IndexedDB real de navegador | Aceptable para unitario; la aceptación manual DevTools→IndexedDB cubre el caso real. |
| **Dexie en jsdom** | Requiere `fake-indexeddb`; olvidar el import en el setup rompe todos los tests de `db/`. |
| **Naming**: repo llama al sistema AVAO (README) y VidriCalc (ARCHITECTURE) | Usar "AVAO" y nombre de BD `avao-ventas` según convención del README/PLAN-#27. |
| **No editar código de la API ni de `apps/taller-pwa`** en esta subtarea | Cambios limitados a `apps/ventas-pwa` + este documento. |
