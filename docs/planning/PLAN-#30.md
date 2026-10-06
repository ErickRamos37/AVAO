# PLAN #30 — Vista de Taller PWA (Vite + React)

- **Tarea:** #30 — Subtarea 2: Vista de Taller PWA (Vite + React)
- **Historia de Usuario:** HU-02 — Taller/Operario debe ver las piezas pendientes de corte.
- **Rama:** `feature/30-vista-taller-pwa` (nace de `develop`)
- **Fecha:** 2026-10-04
- **Documentos de referencia:** `apps/taller-pwa/` (scaffold Vite+React), `apps/ventas-pwa/` (estructura react-router-dom, vitest, testing-library), `apps/api/routers/tareas.py`, `apps/api/schemas.py`, `docs/planning/PLAN-#29.md`, `docs/planning/PLAN-#28.md`.
- **Stack:** Vite 8 + React 19, JSX (no TypeScript en el taller por ahora, alineado al scaffold), Vitest + Testing Library + jsdom.

---

## 1. Objetivo y alcance exacto

### Qué hace
- Reemplazar el scaffold de `apps/taller-pwa` por una vista de taller que consume `GET /tareas/pendientes` y muestra las piezas pendientes como lista de tarjetas (Cards) con sus medidas de corte.
- Cada Card muestra: `pieza_id`, medidas `ancho_mm x largo_mm`, `cantidad`, `estado`, `operario_asignado`, `fecha`.
- Estado vacío: cuando la API devuelve `[]`, mostrar el mensaje "No hay cortes pendientes hoy".
- Estados de UI mínimos: cargando y error de red (mensaje simple), para que la vista no rompa silenciosamente.

### Qué NO hace (límites explícitos)
- **No** marca piezas como completadas — botón placeholder/deshabilitado, anotado para #31.
- **No** implementa sincronización bidireccional ni cola offline con Dexie (la vista es esencialmente read; se instala Dexie solo si el Implementador detecta una necesidad concreta, no por defecto).
- **No** implementa WebSocket/WSS ni push en tiempo real.
- **No** implementa auth/JWT (HU-03, fase posterior).
- **No** implementa guías de corte sobre Canvas 2D (tarea posterior del Taller).
- **No** modifica el backend ni el contrato `TareaPendienteResponse`.

---

## 2. Endpoint API a consumir

`GET /tareas/pendientes` (implementado en #29, `apps/api/routers/tareas.py`).

Query params opcionales: `limit` (1–200, default 50), `offset` (default 0). La UI usa defaults; paginación no es objetivo de esta subtarea.

### Respuesta: `list[TareaPendienteResponse]`

```json
[
  {
    "pieza_id": "uuid",
    "pedido_id": "uuid",
    "product_id": "uuid",
    "ancho_mm": "1200.00",
    "largo_mm": "2400.00",
    "cantidad": 2,
    "estado": "pendiente",
    "operario_asignado": "string | null",
    "fecha": "2026-10-04T10:15:30Z"
  }
]
```

Notas de consumo:
- `ancho_mm` y `largo_mm` llegan como string decimal (Pydantic `Decimal` serializado); renderizar verbatim, p. ej. `1200.00 x 2400.00 mm`. No hacer aritmética de presentación.
- `fecha` es ISO 8601; se puede formatear con `toLocaleDateString`/`toLocaleString` de forma defensiva, pero los tests deben verificar el dato presente y formateado de manera determinista (preferible `new Date(fecha).toLocaleString()` con regex o fecha fija conocida).
- `operario_asignado` puede ser `null`: mostrar "Sin asignar" o equivalente.
- `estado` siempre será `"pendiente"` por el filtro del backend.

Base URL: configurar `import.meta.env.VITE_API_URL` con fallback a `http://localhost:8000` (el repo no tiene esta variable definida aún; el Implementador la documenta en `apps/taller-pwa/README.md` o `.env.example`).

---

## 3. Componentes

```
apps/taller-pwa/src/
  App.jsx                  # router (ver §5)
  main.jsx                 # sin cambios de estructura
  pages/
    TallerPage.jsx         # fetch + estados loading/error/vacío/lista
  components/
    CorteCard.jsx          # una Card por pieza
    CorteCardList.jsx      # lista de CorteCard (o map directo en TallerPage)
  services/
    tareasApi.js           # getTareasPendientes(): fetch wrapper
  test/
    setup.js               # jest-dom (+ fake-indexeddb solo si se usa Dexie)
    tallerPage.test.jsx    # pruebas de la vista
```

### `TallerPage.jsx`
- Al montar: `getTareasPendientes()` → `setTareas(data)`.
- Renderiza:
  - `loading` → mensaje/indicador "Cargando...".
  - `error` → mensaje de error simple.
  - `tareas.length === 0` → **"No hay cortes pendientes hoy"**.
  - else → `CorteCardList` con las Cards.
- Acepta una prop opcional `tareas` (inyección para tests, igual patrón que las páginas de ventas) **o** expone `fetchTareas` mockeable vía `vi.mock('../services/tareasApi')`. Decidir una sola estrategia; preferencia: mock del servicio `vi.mock` + componente puro.

### `CorteCard.jsx`
Recibe una `tarea` y muestra:
- `pieza_id` (o prefijo visible, p. ej. `Pieza abc123…`).
- Medidas: `ancho_mm x largo_mm mm` (formato exacto a acordar: `${ancho_mm} x ${largo_mm} mm`).
- `cantidad`.
- `estado` (texto, p. ej. badge).
- `operario_asignado` (fallback "Sin asignar").
- `fecha`.
- Botón **"Marcar completado" deshabilitado o placeholder**, anotado `TODO #31`, sin lógica de PATCH.

### `services/tareasApi.js`
- `export async function getTareasPendientes()` → `fetch(`${API_URL}/tareas/pendientes`)`, throw si `!res.ok`, retorna `res.json()`.

Trazabilidad in-line: cada archivo inicia con comentario `// AVAO — Tarea #30, HU-02`.

---

## 4. Estado vacío

- Cuando `getTareasPendientes()` resuelve `[]`, la página muestra exactamente el texto **"No hay cortes pendientes hoy"** (verificar en test con regex `/No hay cortes pendientes hoy/i` y que no haya Cards en el DOM).
- Aplica también como criterio de aceptación de la tarea #30.

---

## 5. Rutas

- Rutas: `/` (lista de taller). Se instala y usa **react-router-dom** para mantener paridad con `apps/ventas-pwa` (que ya lo usa con `BrowserRouter`, `Routes`, `Route`, `Navigate`), de modo que futuras subvistas (#31, guías de corte, detalle de pieza) se agreguen como rutas sin reestructurar.
- Estructura mínima propuesta (espejo de ventas-pwa):
  ```jsx
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<TallerPage />} />
      <Route path="/taller" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
  ```
- **Justificación vs estado local:** una sola pantalla cabría en estado local, pero la decisión del repo es react-router-dom en ambas PWAs; #31 añadirá una vista de detalle/guía de corte que es una ruta natural. Se acepta el peso de la dependencia por consistencia.

---

## 6. Pruebas (Vitest + Testing Library + jsdom)

Archivo `apps/taller-pwa/src/test/tallerPage.test.jsx`:

1. **Array vacío** — mockear `getTareasPendientes()` para resolver `[]`; render de `<TallerPage />`; `await screen.findByText(/No hay cortes pendientes hoy/i)`; verificar que no existe ningún elemento de Card.
2. **Datos válidos** — resolver con 2 tareas válidas (UUIDs fijadas, anchos/largos conocidos, operario `null` en una); verificar que se renderizan 2 Cards, y que cada Card muestra su `pieza_id` (o prefijo), `cantidad`, `estado`, `fecha` y operario/fallback.
3. **Medidas visibles** — verificar con `getByText(/1200\.00 x 2400\.00 mm/)` (o regex equivalente) que las medidas del fixture son visibles en el DOM.
4. **Loading** (opcional pero recomendado) — verificar mensaje de carga mientras la promesa no resuelve.
5. **Error** (opcional) — la promesa rechaza; verificar mensaje de error.

Setup: añadir bloque `test: { environment: 'jsdom', setupFiles: './src/test/setup.js', globals: true }` a `apps/taller-pwa/vite.config.js` (copiando el patrón de `apps/ventas-pwa/vite.config.js`), `setup.js` con `import '@testing-library/jest-dom/vitest'` (+ `fake-indexeddb/auto` solo si se decide usar Dexie). Script `"test": "vitest run"` en `package.json`.

---

## 7. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO/apps/taller-pwa

# Dependencias de runtime
npm install react-router-dom

# (OPCIONAL — NO obligatorio; solo si se materializa una necesidad offline)
# npm install dexie dexie-react-hooks

# Tooling de pruebas
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
# npm install -D fake-indexeddb   # solo si se instala dexie

# Verificación
npm run lint
npm run test
npm run build
```

Notas:
- `oxlint` ya está configurado en el scaffold; mantener `npm run lint` en verde.
- No tocar `apps/api`; el contrato ya está fijado por #29.
- Añadir `.env.example` (o documentar en README) con `VITE_API_URL=http://localhost:8000`.

---

## 8. Trazabilidad

- Tarea: **#30** — Subtarea 2: Vista de Taller PWA.
- Historia de Usuario: **HU-02** — Taller/Operario debe ver las piezas pendientes de corte.
- Depende de: **#29** (`GET /tareas/pendientes`, `TareaPendienteResponse`).
- Relaciona con: **#31** (marcar completado — solo dejar placeholder), futuras tareas de guías de corte Canvas 2D y WSS.
- Documentar cada archivo/componente con comentario in-line: `// AVAO — Tarea #30, HU-02`.

---

## 9. Riesgos y límites

- **CORS**: la API FastAPI debe permitir el origen de la PWA (`localhost:5173`); si fetch falla en desarrollo, verificar middleware CORS en `apps/api/main.py` (documentar, no rediseñar).
- **Decimal como string**: no parsear `ancho_mm`/`largo_mm` a número para mostrar; pueden perderse ceros de formato.
- **Offset/paginación**: la vista consume defaults (50). Si un día hay más de 50 piezas, agregar paginación sería otra subtarea.
- **Backend sin auth**: la vista no debe enviar headers de Authorization todavía.
- **Fuera de alcance** (explícito, no implementar): PATCH para completar pieza (#31), sincronización bidireccional/cola offline completa, WebSockets, cambios en `schemas.py`/routers, auth.
- **Riesgo de scope creep**: el botón "Marcar completado" debe quedar deshabilitado/TODO, no funcional.
