# REVIEW #28 — Interfaz de Captura PWA

- **Rama revisada:** `feature/28-interfaz-captura-pwa`
- **Commit:** `aaaf50b` — `feat(pwa): interfaz de captura de pedidos con Dexie offline-first (#28)`
- **Plan de referencia:** `docs/planning/PLAN-#28.md`
- **HU:** HU-01 — Registrar el pedido del cliente
- **Fecha de revisión:** 2026-10-04
- **Revisor:** subagente de revisión de código (sin modificación de código)

---

## Checklist de verificación

| # | Ítem | Estado | Evidencia |
|---|---|---|---|
| 1 | `src/db/dexieDb.js` con BD `avao-ventas`, tablas `pedidos`/`piezas`, funciones `addPedido`, `getPiezasDePedido` | ✅ CUMPLE | `apps/ventas-pwa/src/db/dexieDb.js`: `new Dexie('avao-ventas')`, stores `pedidos`/`piezas` con índices, `addPedido` (transacción rw, estadoSync 'pendiente', bulkAdd de piezas), `getPiezasDePedido` con `where('pedidoIdLocal')` |
| 2 | Formulario dinámico `PedidoForm` con `ClienteFields`, `PiezasList`, `PiezaRow`, `ProductoSelect` | ✅ CUMPLE | Todos los componentes existen en `apps/ventas-pwa/src/components/`; `PiezasList` renderiza N `PiezaRow` con botón "Agregar pieza" y mínimo 1 fila (`canRemove`) |
| 3 | Validaciones + archivo `utils/validarPedido.js` | ✅ CUMPLE | `src/utils/validarPedido.js`: cliente requerido (trim), `piezas.length >= 1`, `ancho_mm`/`largo_mm` > 0, `cantidad` entero > 0, `productoId` no vacío. Medidas negativas → error y `db.pedidos.count()` permanece 0 (cubierto por test) |
| 4 | Offline-first: `estadoSync 'pendiente'` al guardar con Dexie, piezas enlazadas por `pedidoIdLocal` | ✅ CUMPLE | `addPedido` siempre persiste con `estadoSync: 'pendiente'` dentro de `db.transaction('rw', ...)`; piezas con `pedidoIdLocal` |
| 5 | Rutas `/capturar` y `/pedidos` con react-router-dom en `App.jsx`; `PedidosPage` con `useLiveQuery` | ✅ CUMPLE | `App.jsx` usa `BrowserRouter`/`Routes`/`Route` con `/` → redirect a `/capturar`, `/capturar`, `/pedidos`; `PedidosPage` usa `useLiveQuery(() => db.pedidos.toArray(), [])` de `dexie-react-hooks` |
| 6 | Pruebas Vitest en `src/test/capturaPedido.test.jsx` con los 6 casos | ✅ CUMPLE | 6 tests: render del formulario, agregar/eliminar piezas, guardado Dexie offline (estadoSync 'pendiente', 2 piezas enlazadas), medidas negativas rechazadas sin persistir, cantidad 0/cliente vacío/producto sin seleccionar, listado con badge "pendiente de sincronizar" |
| 7 | `fake-indexeddb` en `src/test/setup.js` | ✅ CUMPLE | `import 'fake-indexeddb/auto'` presente; `vite.config.js` define `test.environment 'jsdom'` y `setupFiles` |
| 8 | `npm run test`, `npm run build`, `npm run lint` | ✅ TODOS PASAN | Ver sección de comandos |
| 9 | Trazabilidad `#28` y `HU-01` en archivos nuevos | ✅ CUMPLE | Cabeceras `// AVAO — Tarea #28, HU-01` en dexieDb, PedidoForm, ClienteFields, PiezasList, PiezaRow, ProductoSelect, ValidationMessage, dexieDb, paginas, test, validarPedido, catalogoProductos, App.jsx |
| 10 | Sin push a `main` ni `develop` | ✅ CUMPLE | `git branch -r --contains aaaf50b` → vacío; `origin/main` en `4751067`, `origin/develop` en `50a97f4`, ninguno contiene `aaaf50b` |

---

## Resultado de comandos

Ejecutados en `apps/ventas-pwa`:

```
$ npm run test
 Test Files  1 passed (1)
      Tests  6 passed (6)
   Duration  1.79s

$ npm run build
vite v8.3.2 building client environment for production...
✓ 38 modules transformed.
dist/index.html                   0.46 kB
dist/assets/index-nqMpL4T3.css    1.78 kB
dist/assets/index-Dx29G2Rw.js   362.42 kB
✓ built in 281ms

$ npm run lint
> oxlint
(sin hallazgos; exit 0)
```

---

## Decisión final

**APROBADO** — La implementación cumple el plan §1–§10: formulario dinámico con N piezas, persistencia offline-first en Dexie (`avao-ventas`, `pedidos`/`piezas` enlazadas, transacción), validaciones previas a persistir, rutas con react-router-dom, `useLiveQuery`, 6 tests Vitest con fake-indexeddb, tooling de test configurado, trazabilidad `#28`/`HU-01` en todos los archivos nuevos, y el commit permanece solo en la rama de feature (sin push a `main`/`develop`).

Recomendación: **sí se recomienda merge de `feature/28-interfaz-captura-pwa` a `develop`** tras el PR correspondiente.

---

## Recomendaciones menores (no bloqueantes)

1. **`put` no usado como helper**: el plan menciona operaciones `put` para futuras actualizaciones (p. ej. `estadoSync: 'sincronizado'`); hoy no hay función `putPedido` en `dexieDb.js`. Aceptable en esta fase (YAGNI documentado), pero conviene un helper `marcarSincronizado(idLocal)` cuando se implemente §4.
2. **Validación por pieza prioriza el primer error**: en `validarPedido.js`, si una pieza tiene producto vacío **y** medida negativa, solo se muestra el de producto (`msg || ...`). Considerar mostrar todos los errores por fila en una iteración futura.
3. **Badge de estado**: el badge se colorea por valor literal `'pendiente'`/`'sincronizado'`; si el enum crece conviene un mapa de estilos. No bloqueante.
4. **PiezaRow sin `type="number"` con `min="0"`/`step`**: la UI no impide escribir negativos; la defensa real está en `validarPedido` + tests. Menor mejora de UX.
5. **`_key` incremental en `PedidoForm`**: clave de filas suficiente para esta fase; al editar no persiste, por lo que no hay riesgo de colisión en Dexie.
6. **Brecha conocida (documentada en el plan §10)**: `clienteNombre` capturado no mapea aún a `cliente_id` UUID exigido por `POST /pedidos`; queda pendiente de `POST /clientes`. Correcto que esta fase no suba al servidor.

---

*Revisión realizada sin modificar código del commit `aaaf50b`. Rama de trabajo: `feature/28-interfaz-captura-pwa`.*
