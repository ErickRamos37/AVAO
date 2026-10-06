# PLAN #32 — Interfaz de Operario: botón "Completado" (PWA Taller)

- **Tarea:** #32 — Subtarea 2: Interfaz de Operario (issue [abierta](https://github.com/ErickRamos37/AVAO/issues/32), verificada vía API de GitHub el 2026-10-05).
- **Historia de Usuario:** HU-09 — "Marcar cortes terminados" (issue #11, abierta, 1/2 subtareas: #31 cerrada). Extiende HU-02 (tarjetas de cortes pendientes, implementada en #30).
- **Rama:** `feature/32-interfaz-operario` (nace de `develop`; el Coordinador la crea antes de lanzar al Implementador).
- **Fecha:** 2026-10-05
- **Estado del tablero:** **no verificado** — no hay acceso a GitHub Projects (`users/ErickRamos37/projects/4`) desde las herramientas disponibles; el estado de las issues #32/#11 sí fue verificado (ambas OPEN, sin PRs que las cierren).
- **Documentos de referencia:** `docs/planning/PLAN-#30.md` (vista Taller, §3 componentes), `docs/planning/PLAN-#31.md` (contrato y decisiones del PATCH, incluida idempotencia), `docs/planning/PLAN-#38.md` (estilo de plan y patrones: servicio puro, cerrojo `useRef`, mocks con `vi.stubGlobal`), `docs/planning/DECISIONES-MVP-2026-10-05.md` (D2/D7 unidades; D4 #41 identidad de operario), `apps/api/routers/piezas.py` (implementado, cerrado), `apps/api/schemas.py` (`PiezaResponse`), `apps/taller-pwa/src/**` (código actual), `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` (consultada; ver §9 sobre medidas).
- **Stack:** Vite 8 + React 19 (JSX), Vitest 5 + jsdom + Testing Library + user-event 14 (ya en `devDependencies`), oxlint. **No se requieren dependencias nuevas** (fetch nativo).

---

## 1. Objetivo y alcance exacto

### Qué hace
- Habilita el botón **"Marcar completado"** de `CorteCard.jsx` (hoy `disabled` con TODO #31) y lo conecta a `PATCH /piezas/{id}/completar` del API (implementada y cerrada en #31).
- **Checklist de #32 cubierto:**
  1. Botón touch-friendly en cada tarjeta de la HU-02: `min-height/min-width: 44px`, padding generoso, `touch-action: manipulation` (§4).
  2. Feedback visual al presionar: mientras la petición vuela, el botón pasa a "Marcando…" (deshabilitado); al éxito (HTTP 200), la tarjeta se **oscurece y se tacha** (`data-estado="completado"` + CSS) y el estado muestra "completado" (§3).
- **Ítem de Testing de #32 cubierto:** 3 toques rápidos seguidos producen **exactamente 1 petición HTTP** mediante cerrojo síncrono (`useRef`) + `disabled` durante la petición + guardia en el handler (§2.2).
- Añade la función cliente `completarPieza(piezaId)` al servicio puro `src/services/tareasApi.js` (§2.1).
- Manejo de errores visible por tarjeta: red, 404, 5xx (§5).

### Qué NO hace (YAGNI, explícito)
- **No** implementa cola offline de completados ni Dexie en el Taller: #32 es **online-only**; la cola offline es trabajo futuro ligado a HU-08 (hoy HU-08 solo existe en `apps/ventas-pwa`). Ver §5.3 y §9.
- **No** implementa optimistic UI con rollback: se aplica la respuesta del servidor (decisión §3).
- **No** hace refetch de `GET /tareas/pendientes` tras completar: el endpoint filtra solo pendientes, así que el refetch **eliminaría** la tarjeta y destruiría el tachado que HU-09 exige como criterio de aceptación (decisión §3).
- **No** implementa debounce temporal (retardo por temporizador): la issue usa "Debounce" coloquialmente; el requisito verificable es anti-doble envío y se resuelve con cerrojo — decisión justificada en §2.2.
- **No** toca `apps/api`: el contrato `PATCH /piezas/{id}/completar` → 200 `PiezaResponse` / 404 está fijo por #31 (cerrada).
- **No** implementa auth/JWT (HU-03), WSS/push (futuro), asignación de operario (#41), transición a `en_corte`, Canvas 2D, paginación ni filtros.
- **No** cambia unidades ni precisión de medidas (el contrato vigente usa `*_mm`; la migración a pulgadas es #35 — ver §9).
- **No** reorganiza el scaffold CSS existente: solo se agregan reglas nuevas al final de `src/index.css`.

---

## 2. Diseño

### 2.1 Servicio — `src/services/tareasApi.js` (módulo puro, sin React)

Patrón idéntico a `getTareasPendientes` (módulo puro testeable en aislamiento, como exige el patrón de #30 y #38):

```js
// AVAO — Tarea #32, HU-09 (extiende HU-02)
// Cliente HTTP de PATCH /piezas/{id}/completar (contrato fijado en #31).
/** Marca una pieza como completada. #32 / HU-09.
 *  Devuelve la PiezaResponse (estado "completado", updated_at).
 *  Lanza Error("API respondió <status>") si !res.ok; propaga errores de red. */
export async function completarPieza(piezaId) {
  const res = await fetch(`${API_URL}/piezas/${piezaId}/completar`, {
    method: 'PATCH',
  })
  if (!res.ok) {
    throw new Error(`API respondió ${res.status}`)
  }
  return res.json()
}
```

- Sin body (el endpoint no lo exige — `routers/piezas.py` no lee body).
- El `Error` con el status incrustado permite a la UI distinguir 404 de 5xx sin mapear códigos.

### 2.2 Anti-doble envío (checklist "Debounce" de #32) — decisión y diseño

**Decisión: cerrojo (lock), no debounce temporal.** El criterio verificable de la issue es *"pulsar el botón rápido 3 veces seguidas y verificar que no dispare múltiples peticiones HTTP"*. Un debounce de tiempo (ej. esperar 300 ms) (a) añade latencia al feedback que HU-09 pide inmediato, y (b) no bloquea toques que caigan fuera de la ventana temporal. El cerrojo garantiza **exactamente 1 envío por pieza mientras la petición está en vuelo**, con latencia cero, y es la semántica que realmente se prueba.

Doble defensa en `CorteCard.jsx`:

1. **Cerrojo síncrono con `useRef`** — `enviandoRef.current = true` se asigna **antes** de cualquier `await`, por lo que 3 clics síncronos en el mismo tick de evento (el peor caso, reproducible con `fireEvent.click` ×3 en jsdom) no pasan la guardia aunque React aún no haya re-renderizado.
2. **`disabled` durante la petición + guardia al inicio del handler** — en el caso real de tablet, el re-render ocurre entre toques y el botón físico queda deshabilitado; la guardia `if (enviandoRef.current || tarea.estado === 'completado') return` es la red para el mismo tick.

Red de seguridad residual: el endpoint es **idempotente** (PLAN-#31: un PATCH repetido devuelve 200 sin corromper), de modo que incluso un envío duplicado hipotético (ej. retry del navegador) es inofensivo.

```jsx
// AVAO — Tarea #32, HU-09
// Tarjeta de una pieza pendiente de corte (HU-02) con acción Completado (#32).
import { useRef, useState } from 'react'
import { completarPieza } from '../services/tareasApi'

export default function CorteCard({ tarea, onCompletado }) {
  const { pieza_id, ancho_mm, largo_mm, cantidad, estado, operario_asignado, fecha } = tarea
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)
  const enviandoRef = useRef(false) // cerrojo síncrono — #32 / HU-09 (§2.2)
  const completado = estado === 'completado'

  async function onMarcarCompletado() {
    if (enviandoRef.current || completado) return        // guardia #32 / HU-09
    enviandoRef.current = true                            // antes del await: 3 toques → 1 fetch
    setEnviando(true)
    setError(null)
    // #32 es online-only: sin red, no se intenta el PATCH (§5.3).
    if (typeof navigator !== 'undefined' && navigator.onLine === false) {
      enviandoRef.current = false
      setEnviando(false)
      setError('Sin conexión. La pieza sigue pendiente.')
      return
    }
    try {
      const pieza = await completarPieza(pieza_id)        // PATCH /piezas/{id}/completar
      onCompletado?.(pieza_id, pieza)                     // aplica PiezaResponse a la lista (§3)
    } catch (err) {
      setError(clasificarError(err))                      // §5
    } finally {
      enviandoRef.current = false
      setEnviando(false)                                  // re-habilita: reintento manual es seguro (idempotencia #31)
    }
  }

  // ... render (§3, §4): article data-estado, botón .btn-completar, p role="alert"
}
```

### 2.3 Contrato de consumo

| Campo | Detalle |
|---|---|
| Petición | `PATCH ${VITE_API_URL}/piezas/{pieza_id}/completar`, sin body, sin headers de auth (HU-03 pendiente) |
| Éxito | `200` + `PiezaResponse` (`apps/api/schemas.py`): `id`, `estado: "completado"`, `updated_at`, etc. |
| Error | `404` (pieza no existe), `422` (id no UUID — no ocurre desde la UI), `5xx`; red: `fetch` rechaza `TypeError` |
| Idempotencia | Repetir el PATCH es seguro (200 de nuevo) — habilita el reintento manual |

---

## 3. Feedback visual — decisión: actualización por respuesta (no optimista, no refetch)

**Decisión:** al **200**, la tarjeta aplica `estado: "completado"` tomado de la `PiezaResponse` (vía `onCompletado(pieza_id, pieza)` que actualiza el estado de `TallerPage`).

| Alternativa | Por qué se descarta |
|---|---|
| **Refetch** de `/tareas/pendientes` tras el PATCH | El endpoint **filtra solo pendientes**: el refetch eliminaría la tarjeta de la lista y con ella el tachado/oscurecido que HU-09 exige como criterio de aceptación. Además añade una segunda petición y un parpadeo de carga. |
| **Optimista** (marcar antes del 200, rollback al fallar) | En una pantalla de taller con pocas piezas, el feedback tras una sola petición (~RTT de LAN) es imperceptible; el optimista añade estado dual y código de rollback sin beneficio. Si el PATCH falla, **nada cambió**: no hay rollback que hacer. |
| **Elegida: actualización por respuesta** | Feedback inmediato de dos niveles: (1) al tocar, el botón ya muestra "Marcando…" (el toque se registró al instante); (2) al 200, la tarjeta se oscurece y tacha con el estado confirmado por el servidor — sin riesgo de divergencia. |

**Visual concreto (HU-09: "oscurecerse o tacharse"):**

```jsx
<article
  className="corte-card"
  data-testid="corte-card"
  data-estado={estado}                    // "pendiente" | "completado" — gancho CSS §4
  aria-busy={enviando}
>
  <h2>Pieza {String(pieza_id).slice(0, 8)}…</h2>
  {/* ...datos existentes sin cambios (testids de #30 se conservan)... */}
  <p>
    Estado: <span data-testid="corte-estado" aria-live="polite">{estado}</span>
  </p>
  <button
    type="button"
    className="btn-completar"
    data-testid="btn-completar"
    onClick={onMarcarCompletado}
    disabled={enviando || completado}
  >
    {enviando ? 'Marcando…' : completado ? 'Completado ✓' : 'Marcar completado'}
  </button>
  {error && <p role="alert" data-testid="card-error">Error al completar: {error}</p>}
</article>
```

- El cambio **no es solo de color**: opacidad + tachado + texto de estado distinto + botón distinto (cumple WCAG 1.4.1 *Use of Color*).
- `aria-live="polite"` en el span de estado anuncia el cambio a lectores de pantalla; `aria-busy` comunica la petición en curso; el error usa `role="alert"` (patrón ya usado en `TallerPage.jsx`).
- El TODO #31 de `CorteCard.jsx` se elimina (cumplido aquí, como preveía PLAN-#31 §4).

### 3.1 `TallerPage.jsx` — actualización de la lista

```jsx
// AVAO — Tarea #32, HU-09 — aplica la PiezaResponse a la tarjeta correspondiente.
function handleCompletada(piezaId, pieza) {
  setTareas((prev) => prev.map((t) =>
    t.pieza_id === piezaId ? { ...t, estado: pieza.estado } : t))
}
// ...
<CorteCardList tareas={tareas} onCompletado={handleCompletada} />
```

`CorteCardList` pasa `onCompletado` a cada `CorteCard`. Solo cambia `estado` (el único campo relevante para la UI de la tarjeta; la tarjeta **permanece visible y tachada**, no se re-filtra).

---

## 4. Accesibilidad y CSS (touch-friendly, HU-09)

Reglas nuevas al final de `src/index.css` (no tocar el scaffold existente):

```css
/* AVAO — Tarea #32, HU-09: tarjeta completada y botón touch-friendly */
/* Oscurecido + tachado: feedback visual de pieza completada (no solo color, WCAG 1.4.1) */
.corte-card[data-estado='completado'] {
  opacity: 0.6;
}
.corte-card[data-estado='completado'] h2 {
  text-decoration: line-through;
}
/* Botón grande y fácil de presionar (HU-09): objetivo táctil ≥ 44px (iOS HIG / WCAG 2.2 AA).
   touch-action: manipulation evita el retardo de doble toque en móvil/tablet. */
.btn-completar {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 20px;
  font-size: 1rem;
  border-radius: 8px;
  cursor: pointer;
  touch-action: manipulation;
}
.btn-completar:disabled {
  cursor: default;
}
```

- **44 px** es el tamaño mínimo de objetivo táctil recomendado (Apple HIG; WCAG 2.2 AA 2.5.8 usa 24 px como mínimo absoluto — 44 px cubre ambos y responde al "botón grande" de HU-09). Es un tamaño de control de UI, **no** una medida de ventana: `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` (pulgadas, fracciones de 1/16) no aplica a #32 — ver §9.
- Revisión **móvil/tablet** (el Taller corre en tablet): verificación manual en §7 con emulación de dispositivo; el layout existente es de ancho fluido y el botón es de bloque, por lo que no se esperan quiebres.

---

## 5. Manejo de errores y estado offline

### 5.1 Clasificación (`clasificarError(err)` en `CorteCard.jsx`)

| Escenario | Mensaje visible (`role="alert"` dentro de la tarjeta) | Estado de la pieza |
|---|---|---|
| Sin red (`navigator.onLine === false`) | `Sin conexión. La pieza sigue pendiente.` | pendiente; **no se llama a fetch** (pre-check, §5.3) |
| `fetch` rechaza (`TypeError: Failed to fetch`, CORS, DNS) | `Error de red. Intente de nuevo.` | pendiente |
| HTTP 404 | `Pieza no encontrada (quizá fue eliminada).` | pendiente; tarjeta permanece |
| HTTP 5xx / otro | `Error del servidor (500). Intente de nuevo.` | pendiente |

- El error es **local por tarjeta**: el operario ve exactamente qué pieza falló sin buscar un banner global (decisión de UI para pantalla de taller en tablet).
- `finally` siempre re-habilita el botón: el reintento manual es seguro por la **idempotencia** del endpoint (PLAN-#31).
- Ante 404 la tarjeta **no se elimina**: la lista es el contexto de trabajo del operario; una pieza 404 real desaparecerá en el próximo montaje/carga de página. Decisión documentada (alternativa rechazada: eliminar en caliente, que ocultaría información sin confirmación).

### 5.2 Estado de la pieza ante error
Al no haber optimistic UI (§3), ante cualquier error **el estado nunca salió de `pendiente`**: no hay rollback que ejecutar; el criterio "el estado vuelve a pendiente si se usó optimista" se satisface por construcción.

### 5.3 Límite explícito: offline (fuera de alcance)
#32 es **online-only**: el PATCH requiere red. El pre-check de `navigator.onLine` (§2.2) solo mejora el mensaje; **no** hay cola de completados offline. La cola offline de completados queda como trabajo futuro ligado a **HU-08** ("Trabajar sin internet", hoy implementada solo en `apps/ventas-pwa`): requiere Dexie en Taller + sincronización, y es otra tarea/distinta, no extensión de #32 (YAGNI).

---

## 6. Pruebas Vitest (obligatorias, `apps/taller-pwa`)

**Estrategia de mocks:** `vi.mock('../services/tareasApi', ...)` con ambas funciones (el mock existente en `tallerPage.test.jsx` se extiende con `completarPieza: vi.fn()`); `Object.defineProperty(window.navigator, 'onLine', { value, configurable: true })` para el caso offline (patrón de #38); la API no se levanta en tests. `user-event` ya está en `devDependencies` (14.6.7).

### 6.1 Archivo nuevo `src/test/tareasApi.test.js` (servicio puro)

| # | Caso | Verifica |
|---|---|---|
| S1 | `completarPieza('uuid')` con 200 | `fetch` llamado **1 vez** con URL `${API_URL}/piezas/uuid/completar` y `method: 'PATCH'`, sin body; devuelve la `PiezaResponse` parseada |
| S2 | Respuesta 404 | lanza `Error` con texto `API respondió 404` |
| S3 | Respuesta 500 | lanza `Error` con `API respondió 500` |
| S4 | `fetch` rechaza `TypeError` | el error se propaga (no se traga) |

### 6.2 `src/test/tallerPage.test.jsx` (extender; mock ampliado)

| # | Caso (checklist/HU) | Verifica |
|---|---|---|
| U1 | **Ítem de Testing de #32: 3 toques rápidos** — `userEvent` `tripleClick` sobre `btn-completar` (y variante agresiva: `fireEvent.click` ×3 síncronos en el mismo tick) | `completarPieza` llamado **exactamente 1 vez** (cerrojo `useRef` §2.2) |
| U2 | **Éxito con feedback visual (HU-09 AC2)** — `completarPieza` resuelve `PiezaResponse` con `estado: 'completado'` | tarjeta queda con `data-estado="completado"`, `corte-estado` muestra "completado", botón deshabilitado con texto `Completado ✓`; **otra tarjeta de la lista sigue `pendiente`** (actualización selectiva §3.1) |
| U3 | **Error de red** — `completarPieza` rechaza `TypeError('Failed to fetch')` | aparece `role="alert"` con `Error de red`; `corte-estado` sigue `pendiente`; botón **re-habilitado** (reintento posible) |
| U4 | **404** — rechaza `Error('API respondió 404')` | alerta con `Pieza no encontrada`; la tarjeta permanece visible |
| U5 | **Offline** — `navigator.onLine = false` | alerta `Sin conexión`; `completarPieza` **no** fue llamado |
| U6 | **Touch-friendly (HU-09 AC1)** | `btn-completar` existe con `getByRole('button', { name: /marcar completado/i })` y `className` contiene `btn-completar` (clase que define ≥44px; jsdom no aplica CSS, se verifica la clase) |
| U7 | Tarjeta con `estado: 'completado'` de entrada | botón deshabilitado desde el montaje (defensa del handler §2.2) |
| U8 | Regresiones de #30 | los 5 tests existentes (vacío, datos válidos, medidas, carga, error de carga) **siguen pasando sin modificación** (los `data-testid` se conservan) |

> Nota de implementación para el Implementador: en U1 usar `await user.click(btn)` ×3 con `delay: null` **y** `fireEvent.click(btn)` ×3 síncrono, para cubrir tanto el caso real (re-render entre toques → `disabled`) como el peor caso (mismo tick → solo el `useRef` lo detiene). El caso debe ser verde en ambas variantes.

---

## 7. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO
git checkout feature/32-interfaz-operario   # rama creada por el Coordinador desde develop

# Archivos a EDITAR:
#   apps/taller-pwa/src/services/tareasApi.js      (completarPieza — §2.1)
#   apps/taller-pwa/src/components/CorteCard.jsx   (botón, cerrojo, feedback, error — §2.2/§3)
#   apps/taller-pwa/src/components/CorteCardList.jsx (pasa onCompletado — §3.1)
#   apps/taller-pwa/src/pages/TallerPage.jsx       (handleCompletada — §3.1)
#   apps/taller-pwa/src/index.css                  (estilos — §4)
#   apps/taller-pwa/src/test/tallerPage.test.jsx   (mock ampliado + casos U1-U8 — §6.2)
# Archivo NUEVO:
#   apps/taller-pwa/src/test/tareasApi.test.js     (§6.1)

cd apps/taller-pwa
npm test      # vitest run — U1-U8 + S1-S4 + regresiones #30 en verde
npm run lint  # oxlint — sin errores nuevos
npm run build # vite build — compila

# Prueba manual de aceptación (checklist #32 + revisión tablet):
npm run dev                                    # Taller PWA en :5173
#   API corriendo en :8000 (apps/api, con BD migrada y al menos 1 pieza pendiente)
#   1. DevTools → Network: pulsar "Marcar completado" 3 veces rápido
#      → exactamente 1 PATCH /piezas/{id}/completar (200).
#   2. La tarjeta se oscurece y tacha; estado muestra "completado"; botón queda "Completado ✓".
#   3. DevTools → Device toolbar → tablet (p. ej. iPad 1024×768): botón ≥44px, sin quiebre de layout.
#   4. Detener la API → pulsar → alerta "Error de red"; tarjeta sigue pendiente; botón reintenta.
```

**Commit** (conventional commit + trazabilidad, WORKFLOWS.md §3-4):
```bash
git add apps/taller-pwa docs/planning/PLAN-#32.md
git commit -m "feat(taller-pwa): botón Completado con PATCH /piezas/{id}/completar, anti-doble envío y feedback visual (#32, HU-09, HU-02)"
```

---

## 8. Trazabilidad

| Artefacto / decisión | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#32.md` | Tarea #32 (Subtarea 2), HU-09 (issue #11), extiende HU-02 (issue #2) |
| `completarPieza()` en `services/tareasApi.js` | #32 checklist (habilitar acción), consume `PATCH /piezas/{id}/completar` de #31 (`apps/api/routers/piezas.py`, cerrada) |
| Cerrojo `useRef` + `disabled` + guardia | #32 Testing ítem (3 toques rápidos → 1 petición HTTP); decisión §2.2 |
| Feedback oscurecido/tachado (`data-estado`, CSS) | HU-09 AC "al presionarlo, el estado visual de la pieza debe actualizarse (ej. oscurecerse o tacharse)" |
| Botón ≥44px, `touch-action: manipulation` | HU-09 AC "botón accesible (touch-friendly)"; #32 checklist "botón touch-friendly" |
| Actualización por respuesta (no refetch, no optimista) | Decisión §3; el refetch destruiría el tachado exigido por HU-09 |
| Manejo de red/404/5xx con `role="alert"` | #32 (implícito: la acción no debe fallar silenciosamente); patrón de `TallerPage.jsx` (#30) |
| Pre-check `navigator.onLine` + límite online-only | #32 (PATCH requiere red); cola offline = HU-08 futura (§5.3) |
| Tests U1-U8 / S1-S4 | #32 Testing ítem (U1), HU-09 AC (U2, U6), robustez (U3-U5, U7), regresiones #30 (U8) |
| Dependencia #41 (filtro por operario) | Nota §9: el botón funciona sobre cualquier tarjeta que la lista muestre; #32 no depende del filtro |
| Unidades: sin cambio en #32 | DECISIONES-MVP D2/D7 y `MEDIDAS-VENTANA-CALIFORNIA.md`: la migración mm→pulgadas es #35 (§9) |
| Sin auth en el PATCH | HU-03, fase posterior |

---

## 9. Riesgos y límites explícitos

| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **"Debounce" de la issue es término coloquial** | Si se implementa como temporizador, se añade latencia y no se cumple el criterio en todas las ventanas | Se implementa **cerrojo** (§2.2): cumple el criterio verificable (3 toques → 1 fetch) con latencia cero; decisión documentada aquí y en el docstring del handler |
| **Dependencia con #41 (identidad/filtrado por operario, D4)** | Si #41 cambia la forma en que la lista se puebla, el botón podría parecer "desconectado" | **No hay acoplamiento**: `CorteCard` actúa sobre la `tarea` que recibe; el botón funciona sobre cualquier tarjeta que la lista muestre, venga de `?operario=` o no. #41 no altera este plan |
| **Contrato de medidas vigente (`*_mm`, `NUMERIC(10,2)`) vs especificación de pulgadas (D2/D7, `MEDIDAS-VENTANA-CALIFORNIA.md`)** | Riesgo de confusión: mostrar `1200.00 x 2400.00 mm` hoy vs pulgadas después | #32 **no define unidad, precisión ni redondeo** de medidas: renderiza verbatim el contrato vigente (como #30). La conversión mm→pulgadas es cambio de diseño y migración de **#35**, no cosmético (AGENTS.md). El único tamaño nuevo en #32 (44px) es de control de UI, no medida de ventana |
| **404 deja "tarjeta fantasma"** | El operario ve una pieza que el servidor ya no tiene | Decisión: mantenerla visible con mensaje de error (§5.1); desaparece en la próxima carga. Eliminarla en caliente ocultaría información sin confirmación del operario |
| **Sin cola offline (online-only)** | Si la red cae, el completado no se registra | Límite explícito de #32 (§5.3): mensaje visible, pieza sigue pendiente, reintento manual. La cola offline de completados es HU-08 futura (issue nuevo cuando corresponda) |
| **Sin auth/JWT** | El PATCH viaja sin credenciales | Hu-03, fase posterior; el endpoint público es el estado vigente del MVP (PLAN-#31 §2) |
| **Sin WSS**: otras tablets no ven el completado en vivo | Divergencia visual entre dispositivos hasta recargar | Fuera de alcance (comunicación WSS es objetivo de arquitectura, tarea futura); cada carga de página refleja el servidor |
| **`useRef` vs StrictMode** | En dev, React 19 no re-dispara handlers de eventos (solo efectos), así que el cerrojo no se ve afectado | No requiere mitigación; los tests U1 cubren el peor caso síncrono |
| **Pruebas con fetch mockeado** | El contrato real (404/422/500, idempotencia) no se ejercita en CI | Prueba manual de aceptación (§7) contra API real; los tests de contrato ya existen en `apps/api` (#31) |
| **Scope creep** | Tentación de agregar `en_corte`, asignación, reintentos automáticos | Todos fuera de alcance (§1); el reintento es manual y seguro por idempotencia |

---

*Fin del plan. Entregado por el rol Planificador (WORKFLOWS.md §2) para ejecución por el Implementador en `feature/32-interfaz-operario`. Estado del tablero de GitHub Projects no verificado (sin acceso); issues #32 y #11 verificadas OPEN vía API el 2026-10-05.*
