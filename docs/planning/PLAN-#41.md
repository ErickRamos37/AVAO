# PLAN #41 — Filtro por operario activo (API + Taller PWA)

- **Tarea:** #41 — "HU-02 · Mostrar sólo cortes asignados al operario activo" (issue [abierta](https://github.com/ErickRamos37/AVAO/issues/41), verificada vía GitHub MCP el 2026-10-05; subissue de #2 HU-02 "Saber qué hacer hoy", OPEN, épica #18).
- **Historia de Usuario:** HU-02 (issue #2) — *"Las tareas mostradas deben estar filtradas y asignadas específicamente al operario activo"* (criterio de aceptación pendiente hasta #41).
- **Rama:** `feature/41-filtro-operario-activo` (nace de `develop`; la crea el Coordinador antes de lanzar al Implementador).
- **Fecha:** 2026-10-05
- **Estado del tablero:** issues #41/#2 verificadas OPEN vía `issue_read` (GitHub MCP). **GitHub Projects (`users/ErickRamos37/projects/4`) no fue accesible** desde las herramientas disponibles: el estado de columna/checklist del tablero **no fue verificado** en esta sesión.
- **Documentos de referencia:** `docs/planning/DECISIONES-MVP-2026-10-05.md` (**D4** vigente: filtro en la API, parámetro obligatorio, mecanismo interino hasta HU-03; **pendiente #4**: mecanismo mínimo de asignación), `docs/planning/PLAN-#29.md` (endpoint y contrato `TareaPendienteResponse`), `docs/planning/PLAN-#30.md` (vista Taller), `docs/planning/PLAN-#31.md` y `apps/api/routers/piezas.py` (patrón PATCH), `docs/planning/PLAN-#32.md` (botón Completado — dependencia futura), `docs/planning/PLAN-#38.md` (estilo de plan), `apps/api/routers/tareas.py`, `apps/api/models.py` (`Piece.operario_asignado` VARCHAR(100) nullable, índice `idx_piezas_operario`), `apps/api/schemas.py`, `apps/api/test_tareas.py`, `apps/taller-pwa/src/**`, `apps/ventas-pwa/src/**` (evaluada para la opción A de asignación), `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` (ver §10).
- **Stack:** FastAPI + SQLAlchemy 2.0 (pytest con SQLite en memoria, Ruff); Vite 8 + React 19, Vitest 5 + jsdom + Testing Library + user-event 14, oxlint. **No se requieren dependencias nuevas** ni migraciones (la columna y el índice ya existen desde #26/#27).

---

## 1. Objetivo y alcance exacto

### Qué hace
- Completa el criterio pendiente de HU-02: la lista de Taller corresponde al **operario activo**.
- **Checklist de #41 cubierto:**
  1. Define cómo se identifica al operario activo (§3: selector + `localStorage`, interino) y documenta el contrato API/Taller (§2).
  2. `GET /tareas/pendientes?operario=<identificador>` devuelve **solo** piezas `pendiente` con `operario_asignado = <identificador>` (filtro en la API, D4).
  3. No expone piezas de otro operario al consultar la lista de uno (aislamiento verificado con dos operarios en pytest y Vitest).
  4. Taller PWA muestra la lista filtrada, su estado vacío y errores de carga de forma coherente, con el operario activo visible en la cabecera.
  5. Pruebas con al menos dos operarios (**Ana** y **Juan**) en API (pytest) y vista (Vitest).

### Qué NO hace (YAGNI, explícito)
- **No** implementa JWT/`fastapi-users` ni autorización real (HU-03). El filtro es un **filtro de lista, no una protección** (D4; §9.1).
- **No** implementa WSS/push, Canvas 2D, optimización de corte ni Service Workers.
- **No** cambia el contrato `TareaPendienteResponse`, el modelo `Piece`, ni migraciones Alembic.
- **Sí** implementa la asignación de operarios por **opción B aprobada** por el Coordinador (decisión #4 de `DECISIONES-MVP` §Resueltas.4, 2026-10-05): `PATCH /piezas/{id}/asignar` (§5.3) + selector de asignación por tarjeta en Taller (§6.4) son **alcance de #41**.
- **No** cambia unidades ni precisión de medidas: el contrato vigente sigue en `*_mm` / `NUMERIC(10,2)`; la migración a pulgadas es #35 (§10).
- **No** toca `apps/ventas-pwa` (la asignación en captura, opción A, se evalúa y rechaza en §4.2 salvo decisión contraria del Coordinador).

---

## 2. Contrato API: `GET /tareas/pendientes?operario=`

### 2.1 Decisión: parámetro **requerido** (cambio rompiente, documentado)

**Decisión (ratifica D4):** `operario` es query param **obligatorio**, `str`, `min_length=1`, `max_length=100` (alineado a `VARCHAR(100)`). Si falta o está vacío → **422** (validación automática de FastAPI).

**Justificación (vs. opcional con back-compat):**
- El criterio de HU-02 exige que la lista **corresponda al operario activo**. Un parámetro opcional invita a llamar sin él y devolvería *todas* las piezas pendientes — exactamente el comportamiento pre-#41 que esta tarea elimina. Requerido hace imposible llamar "por accidente" sin filtro.
- El contrato es autodocumentado: todo caller debe declarar *de quién* quiere la lista.
- **Rompiendo:** sí. Único consumidor conocido es la Taller PWA del mismo repositorio, que **se actualiza en el mismo despliegue** (§6). No hay consumidores externos en el MVP (producto de despliegue único, Nginx/Oracle Cloud). Los tests propios de #29 se actualizan en esta misma tarea (§5.2).
- El Coordinador puede revocar a "opcional"; en ese caso el plan exige al menos: si se omite, devolver `[]` (no todas) para no recrear la exposición total. **Marcado como decisión pendiente #1 para el Coordinador** (la recomendación es requerido, per D4).

### 2.2 Semántica del filtro y piezas sin asignar

```
WHERE estado = 'pendiente' AND operario_asignado = :operario
ORDER BY created_at ASC
LIMIT :limit OFFSET :offset
```

- El filtro de estado (#29) **se conserva** y se combina con el de operario; la paginación `limit`/`offset` se aplica **sobre el conjunto ya filtrado** (sin cambios de contrato).
- **Piezas con `operario_asignado IS NULL` no aparecen en la lista de ningún operario** (la comparación SQL `= :operario` nunca coincide con NULL). Decisión: **no** mostrarlas a nadie. Justificación: "Sin asignar" es un **estado de captura pendiente de asignación**, no un operario; mostrarlas en todas las listas recrearía el ruido pre-#41 y ocultaría la brecha de asignación (§4) en lugar de hacerla visible. Si el negocio quisiera una vista de "sin asignar", es un filtro explícito futuro (p. ej. `?operario=` con valor centinela), **no** comportamiento por defecto.

### 2.3 Política de comparación de nombres (deriva "Juan" vs "juan")

**Decisión: comparación exacta** (case-sensitive, sin `trim` ni `lower()` en la lectura). Justificación:
- La UI envía nombres canónicos desde una lista fija (§3), así que la deriva no puede originarse en el selector.
- El comparador exacto hace **visible** un dato mal escrito (lista vacía → alguien investiga) en lugar de enmascararlo con un `LOWER()` que ocultaría deriva real de datos.
- La escritura se normaliza en el único path de escritura nuevo (el PATCH de asignación, opción B, hace `.strip()`); la lectura queda pura.
- **Riesgo residual:** `POST /pedidos` acepta `operario_asignado` libre sin normalizar (path cerrado en #27). Si el Coordinador lo considera, agregar `.strip()` ahí es un endurecimiento de una tarea cerrada — fuera de #41, documentado en §9.2.
- **Decisión pendiente #2 para el Coordinador:** exacta (recomendada) vs. case-insensitive (`func.lower()` en ambos lados). El test `test_coincidencia_exacta` (§5.2) **documenta la política elegida** y se invierte si el Coordinador revoca.

### 2.4 Código — `apps/api/routers/tareas.py`

```python
"""Router de tareas — GET /tareas/pendientes.

Tarea #29, HU-02 — listado de piezas pendientes.
Tarea #41, HU-02 — filtro por operario activo (D4): el parámetro
``operario`` es obligatorio; el endpoint devuelve solo las piezas
pendientes asignadas a ese operario. Es un filtro de lista, NO
autorización (mecanismo interino hasta JWT/fastapi-users, HU-03).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Piece
from schemas import TareaPendienteResponse

router = APIRouter()


@router.get("/tareas/pendientes", response_model=list[TareaPendienteResponse])
def listar_tareas_pendientes(
    operario: str = Query(
        ...,  # requerido: falta o vacío → 422 (#41 / HU-02, D4)
        min_length=1,
        max_length=100,
        description="Operario activo; solo se devuelven sus piezas pendientes",
    ),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Piece]:
    """Piezas pendientes asignadas al operario activo. #41 / HU-02.

    Filtro compuesto: ``estado='pendiente' AND operario_asignado = :operario``.
    Las piezas sin asignar (NULL) no aparecen en la lista de nadie:
    "Sin asignar" es un estado de captura, no un operario.
    """
    return (
        db.query(Piece)
        .filter(Piece.estado == "pendiente")
        .filter(Piece.operario_asignado == operario)  # #41 / HU-02 (exacto, NULL no coincide)
        .order_by(Piece.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
```

Sin cambios en `schemas.py` (`TareaPendienteResponse` ya expone `operario_asignado`), sin migración (`idx_piezas_operario` ya existe). Verificar con `alembic check` que no hay deriva de esquema.

---

## 3. Identidad del operario activo (interina, D4)

### 3.1 Mecanismo en Taller PWA

1. **`src/constants/operarios.js`** (nuevo): lista interina de nombres conocidos, `OPERARIOS_CONOCIDOS = ['Ana', 'Juan']`. Hasta HU-03 no hay catálogo de usuarios en la API; esta constante se reemplaza por usuarios resueltos desde la API cuando exista auth.
2. **`src/services/operarioActivo.js`** (nuevo, módulo puro): `getOperarioActivo()` lee `localStorage['avao-taller:operario-activo']` y lo devuelve si está en la lista conocida (si no, devuelve `OPERARIOS_CONOCIDOS[0]`); `setOperarioActivo(nombre)` lo persiste.
3. **`TallerPage`**: `<select data-testid="selector-operario">` en la cabecera con `OPERARIOS_CONOCIDOS`; al cambiarlo, persiste y pone el nombre en el estado, lo que re-dispara el `useEffect` (dependencia `[operario]`) y recarga la lista filtrada. El operario activo es **visible** en la cabecera ("Operario: …").
4. **`tareasApi.getTareasPendientes(operario)`** envía `?operario=<encodeURIComponent(operario)>` (vía `URLSearchParams`).

### 3.2 Por qué `localStorage` es suficiente para el MVP — y sus límites

**Suficiente porque:** (a) el patrón de uso es **un dispositivo-estación por operario** (tablet/celular del cortador, HU-02: "en mi celular o tableta"); la identidad del dispositivo es, en la práctica, la identidad del operario; (b) no existe nada más fuerte hasta HU-03 — no hay usuarios, sesiones ni tokens que persistir; (c) sobrevive recargas y siestas del tablet (a diferencia de `sessionStorage`), que es el caso de uso real; (d) costo cero de backend y despliegue.

**Límites explícitos (documentar en código y en §9):**
- **No es autenticación ni autorización:** cualquiera con el dispositivo puede seleccionar otro operario y ver (y, con opción B, reasignar) sus piezas. El parámetro `?operario=` es **dato del cliente**, no una credencial (D4).
- No hay revocación de sesión, auditoría ni caducidad.
- Borrar datos del sitio reinicia la identidad al primer operario conocido; el `localStorage` es por-origen-por-navegador (no viaja entre dispositivos).

### 3.3 Relación con HU-03 (exigida por la issue)

HU-03 (JWT / `fastapi-users`) **reemplaza** este mecanismo: el operario se identificará por el token (server-side), el selector y el `localStorage` desaparecerán, y el parámetro `?operario=` se volverá redundante (el servidor deriva el operario del token). #41 deja el contrato y la UI preparados para esa sustitución: el filtro ya está en la API (donde luego se aplicará el principal del token), no en la UI. **Hasta HU-03, la limitación de §3.2 queda aceptada y documentada** — no se construye auth media en #41 (YAGNI y separación de tareas).

---

## 4. Brecha de asignación — dilema y propuesta (DECISIÓN PENDIENTE #4 de DECISIONES-MVP)

### 4.1 Estado actual verificado (por qué la lista filtrada estaría vacía en producción)

- `Piece.operario_asignado` existe (VARCHAR(100) nullable, indexada) pero **solo se escribe** opcionalmente en `POST /pedidos` (`PiezaCreate.operario_asignado`, default `None`).
- **`apps/ventas-pwa` nunca lo envía:** `PedidoForm`/`PiezaRow` no tienen campo de operario (`piezaVacia()` solo lleva `productoId`, `ancho_mm`, `largo_mm`, `cantidad`); el store Dexie `piezas` (v1) no tiene el campo; `syncService.construirPayloadPedido` lo omite explícitamente (PLAN-#38 §5.1: *"Se omite (opcional; se asigna en Taller)"*).
- **No existe endpoint de asignación posterior.** El único PATCH de piezas es `/piezas/{id}/completar` (#31).
- **Consecuencia:** con el filtro de §2 desplegado, toda lista real de Taller estaría **vacía** — la funcionalidad sería formalmente completa (los tests pasarían sembrando `operario_asignado` directo en la BD de prueba) pero **inútil en producción**. Ese es el riesgo de falsa completitud que esta sección obliga a resolver antes de implementar.

### 4.2 Opciones: costo y riesgo

| Opción | Qué implica | Costo | Riesgo |
|---|---|---|---|
| **A) Asignación en la captura** (Ventas elige operario al agregar pieza) | `PiezaRow`/`PedidoForm`: selector de operario por pieza; bump de Dexie a `version(2)` con índice `operario_asignado`; `syncService` lo envía en el payload; tests de Ventas actualizados | Alto y transversal: **4+ archivos en `apps/ventas-pwa`** (app con #28/#38 recién cerradas), migración de IndexedDB, carga UX sobre el vendedor | Cae en órbita de #40 (que ya toca la captura de Ventas para cliente/producto); semánticamente discutible — la asignación es decisión de taller, no de mostrador; reabre trabajo cerrado |
| **B) Endpoint mínimo `PATCH /piezas/{id}/asignar`** (recomendada) | Nuevo endpoint en `routers/piezas.py` (patrón #31) + selector de asignación por tarjeta en Taller (§5.3, §6.4) | Bajo y contenido: **1 endpoint + tests en `apps/api`** (mismo patrón de fixtures), **1 select + 1 función cliente en Taller**; **no toca Ventas** | Amplía Taller más allá de read-only (YAGNI de #30) — se mitiga manteniendo la UI mínima y marcándola interina (sin auth, igual que D4); es un path de escritura nuevo que HU-03 deberá proteger |
| **C) Fuera de alcance — deuda documentada** | #41 entrega filtro + identidad + pruebas; las pruebas siembran `operario_asignado` en la BD directamente | Cero ahora | La funcionalidad es **vacía en producción** (todas las listas vacías hasta que alguien corra SQL a mano); cerrar #41 así oculta la brecha; la asignación habrá que construirla después con otro cambio de Taller igualmente |

### 4.3 Propuesta del Planificador

**Opción B**, con alcance mínimo:
- `PATCH /piezas/{id}/asignar` con body `{ "operario_asignado": "Ana" | null }` (`null` desasigna), 404 si la pieza no existe, 422 si el nombre está vacío o supera 100 caracteres; normaliza con `.strip()` al escribir; responde `PiezaResponse`.
- Selector de asignación por tarjeta en Taller (§6.4), consistente con el selector de operario activo y con la misma lista interina.
- Flujo real que habilita: la oficina/supervisor (o cualquier usuario de la tablet, sin auth aún) asigna piezas desde la misma vista donde el operario ve su lista; la pieza aparece en la lista del destinatario al recargar.

**RESUELTO por el Coordinador el 2026-10-05 (DECISIONES-MVP §Resueltas.4): opción B APROBADA.** §5.3 y §6.4 **entran en el alcance de #41** y el Implementador los ejecuta. (Opción A evaluada y no recomendada; opción C descartada — la deuda de asignación quedaría abierta y la lista filtrada estaría vacía en producción.)

---

## 5. API: cambios y pruebas pytest

### 5.1 Archivos

| Archivo | Cambio |
|---|---|
| `apps/api/routers/tareas.py` | Editar: param `operario` requerido + filtro (§2.4) |
| `apps/api/test_tareas.py` | Editar: actualizar los 7 tests existentes (hoy llaman sin `?operario` → recibirían 422) y añadir los casos de #41 |
| `apps/api/routers/piezas.py`, `apps/api/schemas.py`, `apps/api/test_piezas.py` | **Opción B aprobada** (§5.3): `PATCH /piezas/{id}/asignar` |

### 5.2 Tabla de casos pytest (`test_tareas.py`) — dos operarios: Ana y Juan

| # | Caso | Verifica (AC #41) |
|---|---|---|
| 1 | `test_requiere_operario_422` — `GET /tareas/pendientes` sin param y con `?operario=` vacío | Contrato requerido (AC1, D4) → 422 en ambos |
| 2 | `test_filtra_por_operario_aislado` — sembrar 2 piezas de Ana + 1 de Juan (todas pendientes) | `?operario=Ana` → solo las 2 de Ana; `?operario=Juan` → solo la de Juan; **ninguna pieza de Juan aparece en la respuesta de Ana y viceversa** (AC2/AC3: aislamiento cruzado) |
| 3 | `test_pieza_sin_asignar_invisible` — pieza `operario_asignado=None` | No aparece ni para Ana ni para Juan (§2.2) |
| 4 | `test_coincidencia_exacta` — pieza de "Juan"; consulta `?operario=juan` | `[]` — documenta la política de comparación exacta (§2.3) |
| 5 | `test_solo_pendientes_del_operario` — Juan tiene pendiente + `en_corte` + `completado` | `?operario=Juan` → solo la pendiente (filtro compuesto `estado AND operario`) |
| 6 | `test_paginacion_con_filtro` — 3 piezas de Ana; `?operario=Ana&limit=1&offset=1` → la 2ª de Ana; `limit=0`/`limit=500`/`offset=-1` → 422 | La paginación sigue funcionando sobre el conjunto filtrado |
| 7 | `test_orden_creado_at_con_filtro` — 2 piezas de Ana con `created_at` distinto | Orden ascendente dentro del operario |
| 8 | **Actualizar los 7 tests existentes de #29** (`test_lista_vacia_sin_pendientes`, `test_solo_incluye_pendientes`, `test_respeta_operario_asignado`, `test_formato_fecha_iso`, `test_orden_por_created_at`, `test_paginacion_limit_offset`, `test_contrato_de_campos`): pasar `?operario=<nombre>` y sembrar `operario_asignado` acorde (el helper `_pieza` ya acepta `operario=`) | Regresión del contrato de campos, formato ISO, orden y paginación bajo el nuevo contrato. `test_respeta_operario_asignado` se reenfoca: el campo `operario_asignado` sigue viajando en la respuesta filtrada |

### 5.3 (Opción B APROBADA — alcance de #41) `PATCH /piezas/{id}/asignar`

```python
# apps/api/routers/piezas.py — #41 / HU-02 (opción B aprobada)
from pydantic import ...  # schemas.py: class PiezaAsignar(BaseModel):
#   operario_asignado: str | None = Field(default=None, min_length=1, max_length=100)

@router.patch("/piezas/{id}/asignar", response_model=PiezaResponse)
def asignar_pieza(id: uuid.UUID, body: PiezaAsignar, db: Session = Depends(get_db)) -> Piece:
    """Asigna (o desasigna con null) una pieza a un operario. #41 / HU-02.

    Interino sin auth (D4/HU-03): cualquier caller puede asignar.
    """
    pieza = db.get(Piece, id)
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")
    pieza.operario_asignado = (  # escritura normalizada; la lectura es exacta (§2.3)
        body.operario_asignado.strip() if body.operario_asignado else None
    )
    pieza.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pieza)
    return pieza
```

Tests añadidos a `test_piezas.py` (mismo patrón de fixtures): asignación exitosa (200 + campo persistido en BD + **la pieza pasa a aparecer en `?operario=Ana`** — verificación end-to-end del filtro), 404 pieza inexistente, 422 nombre vacío/>100, desasignación con `null` (desaparece de todas las listas), y que el `PATCH /piezas/{id}/completar` (#31) no altera `operario_asignado`.

---

## 6. Taller PWA: cambios y pruebas Vitest

### 6.1 Archivos

| Archivo | Cambio |
|---|---|
| `src/constants/operarios.js` | **Nuevo** — `OPERARIOS_CONOCIDOS` (§3.1), comentario `#41 / HU-02` con la advertencia de reemplazo en HU-03 |
| `src/services/operarioActivo.js` | **Nuevo** — `getOperarioActivo()` / `setOperarioActivo()` sobre `localStorage` (§3.1–3.2) |
| `src/services/tareasApi.js` | Editar — `getTareasPendientes(operario)` envía `?operario=`; (con opción B) añadir `asignarPieza(piezaId, operario)` |
| `src/pages/TallerPage.jsx` | Editar — estado `operario`, selector en cabecera, `useEffect` con dependencia `[operario]` |
| `src/test/tallerPage.test.jsx` | Editar — casos nuevos de #41 (§6.2); los 5 existentes siguen pasando (el mock ahora recibe el operario como argumento) |
| `src/components/CorteCard.jsx`, `src/components/CorteCardList.jsx` | **Solo con opción B** (§6.4); `CorteCard` ya muestra `operario_asignado` con fallback "Sin asignar" |

### 6.2 Código principal

```js
// src/services/tareasApi.js — AVAO — Tarea #30/#41, HU-02
/** Lista de piezas pendientes del operario activo. #41 / HU-02 (D4).
 *  ``operario`` es obligatorio en el contrato API: sin él la API responde 422. */
export async function getTareasPendientes(operario) {
  const params = new URLSearchParams({ operario })
  const res = await fetch(`${API_URL}/tareas/pendientes?${params}`)
  if (!res.ok) {
    throw new Error(`Error al obtener tareas: ${res.status}`)
  }
  return res.json()
}
```

```jsx
// src/pages/TallerPage.jsx — AVAO — Tarea #30/#41, HU-02
import { useEffect, useState } from 'react'
import { getTareasPendientes } from '../services/tareasApi'
import { getOperarioActivo, setOperarioActivo } from '../services/operarioActivo'
import { OPERARIOS_CONOCIDOS } from '../constants/operarios'
import CorteCardList from '../components/CorteCardList'

export default function TallerPage() {
  // #41 / HU-02: identidad interina del operario activo (D4) — localStorage, no auth.
  const [operario, setOperario] = useState(getOperarioActivo)
  const [tareas, setTareas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let activo = true
    setLoading(true)
    setError(null)
    getTareasPendientes(operario) // #41 / HU-02: ?operario= siempre presente
      .then((data) => {
        if (activo) {
          setTareas(Array.isArray(data) ? data : [])
          setLoading(false)
        }
      })
      .catch((err) => {
        if (activo) {
          setError(err?.message || 'Error de red')
          setLoading(false)
        }
      })
    return () => {
      activo = false
    }
  }, [operario])

  const onCambioOperario = (e) => {
    setOperarioActivo(e.target.value)
    setOperario(e.target.value)
  }

  return (
    <main>
      <h1>Cortes pendientes</h1>
      <label>
        Operario:{' '}
        <select data-testid="selector-operario" value={operario} onChange={onCambioOperario}>
          {OPERARIOS_CONOCIDOS.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>
      {loading && <p>Cargando...</p>}
      {error && <p role="alert">Error al cargar cortes: {error}</p>}
      {!loading && !error && tareas.length === 0 && <p>No hay cortes pendientes hoy</p>}
      {!loading && !error && tareas.length > 0 && <CorteCardList tareas={tareas} />}
    </main>
  )
}
```

Notas de coherencia (AC3): el texto de estado vacío **se conserva idéntico** al de #30 ("No hay cortes pendientes hoy") para no romper su criterio; el contexto del operario vive en la cabecera. Al cambiar de operario se resetean `loading`/`error` y se recarga. `CorteCard` no cambia (ya muestra medidas, cantidad, estado, operario y fecha).

### 6.3 Tabla de casos Vitest (`src/test/tallerPage.test.jsx`)

Mocks: `vi.mock('../services/tareasApi')` (patrón existente); `beforeEach` limpia `window.localStorage` y mocks. Operarios de los tests: **Ana** (default, `OPERARIOS_CONOCIDOS[0]`) y **Juan**.

| # | Caso | Verifica (AC #41) |
|---|---|---|
| 1 | Lista filtrada: mock resuelve `[t1, t2]`; render | `getTareasPendientes` fue llamado con `'Ana'`; se renderizan las Cards (AC1/AC4) |
| 2 | **Aislamiento por operario:** mock resuelve `[]` para Juan (`mockResolvedValueOnce`) | Cambiar el `<select>` a Juan → `getTareasPendientes` se vuelve a llamar con `'Juan'`; aparece "No hay cortes pendientes hoy" y 0 Cards (AC2/AC3: la vista corresponde al operario activo) |
| 3 | **Persistencia:** `localStorage.setItem('avao-taller:operario-activo','Juan')` antes del render | El select vale "Juan" y la primera llamada usa `'Juan'` (identidad del operario activo sobrevive recargas) |
| 4 | Estado vacío: mock `[]` | /No hay cortes pendientes hoy/ + `queryAllByTestId('corte-card')` = 0 (AC3, heredado de #30) |
| 5 | Error de carga: mock rechaza | `role="alert"` con /Error al cargar cortes/ (AC3) |
| 6 | Loading: promesa pendiente | /Cargando/ (AC3) |
| 7 | Valor guardado inválido en `localStorage` (p. ej. `'Luis'`, no está en la lista) | Caer al default `'Ana'` (defensa §3.1) |

Esqueleto (caso 2, el central):

```jsx
// AVAO — Tarea #41, HU-02
import userEvent from '@testing-library/user-event'

it('recarga la lista del operario al cambiar el selector', async () => {
  getTareasPendientes.mockResolvedValue([t1]) // Ana
  render(<TallerPage />)
  await screen.findAllByTestId('corte-card')
  expect(getTareasPendientes).toHaveBeenCalledWith('Ana')

  getTareasPendientes.mockResolvedValueOnce([]) // Juan no tiene piezas
  await userEvent.selectOptions(screen.getByTestId('selector-operario'), 'Juan')
  expect(await screen.findByText(/No hay cortes pendientes hoy/i)).toBeInTheDocument()
  expect(screen.queryAllByTestId('corte-card')).toHaveLength(0)
  expect(getTareasPendientes).toHaveBeenLastCalledWith('Juan')
})
```

### 6.4 (Opción B APROBADA — alcance de #41) Asignación desde Taller

- `tareasApi.asignarPieza(piezaId, operario)`: `PATCH /piezas/{id}/asignar` con `{ operario_asignado: operario }` (`null` para desasignar); lanza `Error("API respondió <status>")` si `!res.ok`.
- `CorteCard` gana `<select data-testid="asignar-select" value={operario_asignado ?? ''}>` con opciones "Sin asignar" + `OPERARIOS_CONOCIDOS`; al cambiar: cerrojo `useRef` anti-doble envío (patrón #32), `disabled` durante la petición, mensaje de error por tarjeta (`role="alert"`), y al éxito llama `onAsignada()` que provoca el refetch en `TallerPage` (la pieza puede salir de la lista del operario activo — comportamiento correcto).
- Vitest (añadir a `tallerPage.test.jsx` o `corteCard.test.jsx`): cambiar el select de una tarjeta llama `asignarPieza(pieza_id, 'Juan')` exactamente 1 vez; error del PATCH muestra alerta por tarjeta; éxito dispara refetch.

### 6.5 Revisión móvil/tablet (manual, hay navegador)

Con `npm run dev` y DevTools → device toolbar: **teléfono 360×800** y **tablet 768×1024**. Verificar: el `<select>` de operario es utilizable sin desbordamiento horizontal (control nativo), las Cards apilan sin corte, el estado vacío y el `role="alert"` son legibles, y el selector de asignación (si aplica opción B) es táctil (≥44px, heredado del patrón #32). Registrar capturas en la PR.

---

## 7. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO
git checkout feature/41-filtro-operario-activo   # la crea el Coordinador desde develop

# --- API (verificados el 2026-10-05: .venv presente, pytest y Ruff pasan) ---
cd apps/api
./.venv/bin/python -m pytest -q                     # toda la API (regresión: test_tareas, test_piezas, test_pedidos, test_main)
./.venv/bin/python -m pytest test_tareas.py -v      # foco #41
./.venv/bin/python -m ruff check .                  # sin errores nuevos (line-length 100)
./.venv/bin/python -m alembic check                 # sin deriva de esquema (no hay migración nueva)

# --- Taller PWA (verificado el 2026-10-05: node_modules presente, npm test pasa 5/5) ---
cd ../taller-pwa
npm test          # vitest run — existentes + nuevos de #41
npm run lint      # oxlint — sin errores nuevos
npm run build     # vite build — debe compilar

# --- Prueba manual de aceptación (checklist #41) ---
# API corriendo: cd ../api && ./.venv/bin/uvicorn main:app --reload --port 8000
curl -i "http://localhost:8000/tareas/pendientes"                     # → 422 (falta operario)
curl -i "http://localhost:8000/tareas/pendientes?operario=Ana"        # → 200, solo piezas de Ana
# Taller: npm run dev (:5173) → selector de operario en cabecera; cambiar a Juan recarga;
#   con API detenida → role="alert"; sin piezas → "No hay cortes pendientes hoy".
#   Revisión móvil/tablet según §6.5.
```

**Commit** (conventional commit + trazabilidad, `WORKFLOWS.md` §4):

```bash
git add apps/api apps/taller-pwa docs/planning/PLAN-#41.md
git commit -m "feat(taller): filtrar /tareas/pendientes por operario activo (#41, HU-02)"
# Opción B aprobada — commit aparte:
git commit -m "feat(api): asignar pieza a operario via PATCH /piezas/{id}/asignar (#41, HU-02)"
```

**Breaking change:** el commit y la PR deben declarar explícitamente que `GET /tareas/pendientes` sin `?operario` ahora responde 422, y que la Taller PWA se actualiza en el mismo despliegue (§2.1).

---

## 8. Trazabilidad

| Criterio de aceptación de #41 / HU-02 | Dónde se cumple | Prueba |
|---|---|---|
| AC1: se define cómo se identifica al operario activo y se documenta el contrato API/Taller | §2 (contrato), §3 (identidad interina) | pytest caso 1; Vitest casos 1, 3, 7 |
| AC2: `GET /tareas/pendientes` devuelve solo piezas pendientes asignadas a ese operario | §2.2, §5 | pytest casos 2, 5, 6, 7 |
| AC3: no expone piezas de otro operario al consultar su lista | §2.2 (filtro en API, no en UI) | pytest caso 2 (aislamiento cruzado Ana↔Juan); Vitest caso 2 |
| AC4: Taller muestra la lista, su estado vacío y errores de carga de forma coherente | §6.1–6.2 | Vitest casos 1, 2, 4, 5, 6 |
| AC5: pruebas con al menos dos operarios en API y vista | §5.2, §6.3 (Ana y Juan) | pytest casos 2–5; Vitest casos 1–3 |
| HU-02: "las tareas mostradas deben estar filtradas y asignadas específicamente al operario activo" | Todo el plan | conjunto de §5.2 + §6.3 |
| D4 (DECISIONES-MVP): filtro en la API, parámetro obligatorio, interino hasta HU-03 | §2.1, §3 | pytest caso 1; §3.3 |
| Pendiente #4 (DECISIONES-MVP): mecanismo mínimo de asignación | §4 (dilema), §5.3/§6.4 | **RESUELTO: opción B aprobada (Coordinador, 2026-10-05)** |
| Depende de #29 y #30 (cerradas/Finalizado) | contrato `TareaPendienteResponse`, vista base | regresión §5.2 caso 8, §6.3 casos 4–6 |
| Relación con #32 (futuro): botón Completado sobre tarjetas filtradas | §9.3 | verificación manual en PR |

---

## 9. Riesgos y límites explícitos

| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **1. Falso sentido de seguridad:** el filtro **no es autorización**; cualquier cliente puede pasar `?operario=<cualquier nombre>` y ver esa lista. El AC "no expone piezas de otro operario" se cumple como *filtro de lista*, no como *protección de datos* | Alto si se interpreta como seguridad | Documentado en D4, §2.4, §3.2 y en el docstring del endpoint. Ruta: HU-03 (JWT/`fastapi-users`) — el operario vendrá del token, no del query param |
| **2. Deriva de nombre** (`VARCHAR(100)` libre: "Juan" vs "juan" vs "Juan "): lista vacía silenciosa | Medio | Comparación exacta en lectura (§2.3) + escritura normalizada (`.strip()`) en el PATCH de asignación + selector de lista fija en la UI. El test `test_coincidencia_exacta` documenta la política. Pendiente #2 para el Coordinador (exacta vs. case-insensitive). Residual: `POST /pedidos` acepta texto libre sin normalizar (tarea cerrada #27; endurecimiento fuera de #41) |
| **3. Dependencia con #32** (botón Completado): `PATCH /piezas/{id}/completar` opera por `id`, sin filtro de operario — coherente con la fase sin auth, pero cualquiera puede completar cualquier pieza | Medio (aceptado en fase interina) | #32 debe seguir funcionando sobre las tarjetas filtradas: verificación manual en la PR (completar una pieza de la lista de Ana con el selector en Ana). La protección real llega con HU-03 |
| **4. Breaking change del contrato** (`422` sin `?operario`) | Bajo en MVP (consumidor único, despliegue conjunto) | Declarado en PR y commit (§7); si el Coordinador prefiere back-compat, exigir al menos `[]` al omitirlo (§2.1) |
| **5. Lista de operarios hardcodeada** (`OPERARIOS_CONOCIDOS`): un operario nuevo ("Luis") requiere editar la constante | Medio | Constante única y comentada; reemplazo planeado por usuarios de la API en HU-03 (§3.1) |
| **6. `localStorage`**: borrar datos del sitio reinicia la identidad; dispositivo compartido permite suplantación | Bajo/Medio | Aceptado para MVP (D4 interino, §3.2); documentado en código y aquí |
| **7. Orden de integración con #35** (unidades): si #35 (mm→pulgadas, `*_in`) aterriza antes, los fixtures y contratos de este plan deben renombrarse (`ancho_mm`→`ancho_in`, etc.) | Medio | #41 no introduce medidas nuevas (§10); el Implementador debe verificar qué versión del contrato está en `develop` al crear la rama y ajustar nombres de campos en fixtures/tests |
| **8. Falsa completitud si el Coordinador rechaza la opción B** | — | **Moot: opción B aprobada**; §5.3/§6.4 son alcance de #41 |

---

## 10. Medidas (unidad, precisión, redondeo) — sin cambios en #41

Consultada `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` y `DECISIONES-MVP` D2/D7: la unidad canónica vigente en diseño es la **pulgada decimal** (precisión 1/16), pero la **migración es alcance de #35** y los contratos implementados aún usan `*_mm` con `NUMERIC(10,2)` (AGENTS.md lo ordena explícitamente: tratarlo como cambio de diseño de #35, no cosmético). #41 **no introduce medidas nuevas ni aritmética**: la API filtra y devuelve `ancho_mm`/`largo_mm` verbatim (sin redondeo, sin conversión) y la UI los renderiza verbatim (`${ancho_mm} x ${largo_mm} mm`, convención de #30). Si #35 ya está integrado en `develop` al crear la rama (riesgo §9.7), los fixtures de tests usan los nombres y la unidad de entonces.

---

*Fin del plan. Entregado por el rol Planificador (WORKFLOWS.md §2) para revisión del Coordinador y ejecución por el Implementador en `feature/41-filtro-operario-activo`. Decisiones pendientes para el Coordinador: (1) `operario` requerido vs. opcional — recomendado requerido; (2) comparación exacta vs. case-insensitive — recomendada exacta; (3) brecha de asignación: opción B propuesta (endpoint + UI mínima), A evaluada y no recomendada, C como fallback con deuda explícita.*
