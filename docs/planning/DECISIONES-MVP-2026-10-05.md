# Registro de decisiones del MVP — AVAO

- **Fecha:** 2026-10-05
- **Autor:** Coordinador (con decisiones del responsable humano)
- **Alcance:** Decisiones de diseño para las subtareas abiertas de las HUs Altas (#1 HU-01, #2 HU-02, #11 HU-09, #14 HU-13, #24 HU-05.1). Cada plan `PLAN-#NN.md` debe citar aquí su decisión aplicable.
- **Estado:** Decisiones vigentes hasta que el responsable humano las revoque. No sustituyen los checklists de las issues.

---

## D1 — Secuencia: diseño primero

Se planifica **todo** antes de implementar: los planes `PLAN-#NN.md` de las subtareas abiertas se entregan y revisan antes de lanzar al Implementador. Orden de planificación: #32, #33, #35, #39+#40, #41, #34. Orden de implementación se define al integrar los planes.

## D2 — #35: unidad canónica = pulgada decimal

- **Todas las medidas** del sistema se expresan en **pulgadas decimales**: `piezas.ancho/largo`, `productos.espesor` y cualquier medida futura. Renombrar `*_mm` → `*_in` en esquema, contratos y PWAs.
- **Persistencia:** `NUMERIC(10,4)` (conserva 0.0625 = 1/16 exacto; `NUMERIC(10,2)` no).
- **Precisión de corte:** incrementos de **1/16 in (0.0625)**, límite del flexómetro. **Política de entrada (RESUELTA 2026-10-05, §Resueltas.1):** los valores no múltiplos de 1/16 se **cuantizan al 1/16 más cercano** (sin rechazo) en Ventas (captura, con el valor efectivo visible) y en la API (defense-in-depth, idempotente).
- **Excepción de espesor:** el espesor es propiedad del material, no una medida de corte; puede ser decimal libre (ej. 6 mm ≈ 0.236 in no es múltiplo de 1/16). El plan #35 define si se cuantiza o se deja libre.
- **Migración de datos:** convertir mm → in dividiendo 25.4; política de redondeo de datos existentes la define el plan #35.
- **Frontera de presentación:** los ejemplos comerciales en metros (ej. barra de 6 m) se convierten a pulgadas en la UI o al ingresar; **la API solo habla pulgadas**. 6 m = 236.22 in; 5.5 m = 216.535 in.

## D3 — #40: catálogo y clientes por endpoints mínimos

- `POST /clientes` con **find-or-create** por **`(nombre_normalizado, discriminador)`** — discriminador = `telefono` (o `email` si no hay teléfono), **al menos uno obligatorio** (§Resueltas.2): dos clientes homónimos con distinto discriminador **no se fusionan**.
- `GET /productos` para listar el catálogo real.
- No hay CRUD completo en el MVP (YAGNI). La PWA Ventas reemplaza el mapeo manual `mapeoApi.js` por resolución desde la API con caché local en Dexie.

## D4 — #41: identidad de operario interina

- `GET /tareas/pendientes?operario=<identificador>` — **filtro en la API**, no en la UI. Parámetro obligatorio en el contrato Taller.
- Mecanismo **interino** hasta JWT/`fastapi-users` (HU-03): no es autorización real; se documenta como limitación.

## D5 — #33: "Listo para entrega" = `completado`

- Cuando todas las piezas de un pedido están `completado`, `pedidos.estado` pasa a **`completado`** (vocabulario existente; sin migración de estados).
- Cuando se completa la **primera** pieza, el pedido pasa a `en_proceso` (satisface el checklist de #33: "N-1 piezas → el pedido sigue En Proceso").

## D6 — #34: estimación de barras

- Se suma **solo el `largo`** de cada tramo (× cantidad).
- **Unidad: pulgadas** para tramos y para la medida estándar de la barra matriz (D2/D7).
- `barras = ceil(total_tramos / medida_barra)`; validar que ningún tramo supere la barra matriz (422 claro).
- La medida de barra matriz es un estándar comercial: decimal libre, no cuantizado a 1/16.

## D7 — Aclaración global (2026-10-05)

**Toda medida mencionada por cualquier HU se maneja en pulgadas**, incluidos los tramos de #34, el espesor de productos y las medidas de pieza de HU-01. No se guardan ni se envían milímetros ni metros por la API.

---

## Resueltas (2026-10-05, por el responsable humano salvo nota)

1. **#35 — Entrada de cortes:** **cuantizar al 1/16 más cercano** (no rechazar con 422). Cuantización en Ventas (captura, con el valor efectivo visible al operario) y en la API (defense-in-depth, idempotente). El espesor sigue decimal libre. PLAN-#35 enmendado por el Coordinador.
2. **#40 — Homónimos:** find-or-create exige **discriminador** (`telefono`, o `email` si no hay teléfono; al menos uno obligatorio, 422 si no hay ninguno). Unicidad compuesta `(nombre_normalizado, teléfono)` + `UNIQUE (email)` existente. Dos homónimos con distinto discriminador → dos clientes. El **teléfono pasa a ser obligatorio en la captura** de Ventas. PLAN-#40 enmendado por el Coordinador.
3. **#39 — Idempotencia:** header **`Idempotency-Key` obligatorio** (422 si falta); UUID v4 generada por Ventas y persistida en Dexie; replay con mismo payload → **201** con el mismo `id`; misma clave con payload distinto → **409**; clave permanente (sin limpieza, YAGNI); concurrencia resuelta por la UNIQUE + recuperación del ganador. (Resuelto por el Coordinador, técnico.)
4. **#41 — Asignación:** **opción B aprobada** — `PATCH /piezas/{id}/asignar` (body `{operario_asignado: string|null}`, normaliza `.strip()`, 404/422) + selector de asignación por tarjeta en Taller. Interino sin auth (misma limitación que D4; HU-03 lo protegerá).
5. **#41 — Contrato:** `?operario=` **requerido** (422 si falta) y comparación **exacta** (case-sensitive). (Resuelto por el Coordinador, técnico.)
6. **#34 — Alcance:** `POST /estimacion/barras` **stateless** (opción a); la variante por pedido (b) queda post-MVP. (Resuelto por el Coordinador, técnico.)
7. **#32 — Anti-doble envío:** **cerrojo** (guardia síncrona + `disabled` durante la petición), no debounce temporal. (Resuelto por el Coordinador, técnico.)
8. **#33 — Pedidos cancelados:** el PATCH de completar **no resucita** un pedido `cancelado` (política conservadora; la reactivación es decisión de negocio futura). (Resuelto por el Coordinador, técnico.)
9. **Orden de integración confirmado:** **#35 → #39 → #40 → #41 → #32 → #33 → #34**. Las migraciones Alembic encadenan `down_revision` en ese orden; versiones de Dexie: #35 = v2, #40 = v3.

## Pendientes de decisión (se elevan al responsable cuando corresponda)

- Ninguno bloqueante para la fase de implementación. Seguimiento conocido: reactivación de pedidos cancelados (#33), protección real del interino D4/opción B (HU-03) y la ambigüedad de "tramo de barra" para la variante por pedido de #34 (post-MVP).
