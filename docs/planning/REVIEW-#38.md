# REVIEW #38 — Sincronización offline → API (Ventas PWA)

- **Tarea:** #38 — Subtarea 4: Sincronización offline → API (Ventas PWA).
- **HU:** HU-08 (trabajar sin internet, issue #10); extiende HU-01 (registrar pedido, issue #1).
- **Rama revisada:** `feature/38-sync-offline-api` @ `1eb80c3`.
- **Fecha de revisión:** 2026-10-04.
- **Revisor:** subagente de revisión de código (verificación, sin modificar código).

---

## Checklist

| # | Ítem | Estado | Evidencia |
|---|------|--------|-----------|
| 1 | `apps/ventas-pwa/src/services/syncService.js` con `syncPedidosPendientes()`, `marcarSincronizado(pedidoIdLocal)`, `hayConexion()`; envío secuencial (no `Promise.all`); cerrojo `syncEnCurso` | ✅ CUMPLE | Archivo existe (101 líneas). `hayConexion()` :10, `marcarSincronizado()` :42 (usa `db.pedidos.update` — patch parcial, §3.2), `syncPedidosPendientes()` :54. Envío secuencial: `for (const pedido of pendientes)` con `await` en el cuerpo (:74), comentario explícito "NO Promise.all"; `grep Promise.all` solo aparece en el comentario. Cerrojo a nivel de módulo: `let syncEnCurso = null` :46, encadenamiento `syncEnCurso.then(() => syncPedidosPendientes())` :63, limpieza en `.finally()` :64-66. |
| 2 | Errores mantienen `estadoSync:'pendiente'` y escriben `ultimoError` | ✅ CUMPLE | `syncService.js:86-92`: el `catch` incrementa `errores`, agrega a `erroresDetalle`, escribe `db.pedidos.update(idLocal, { ultimoError: err.message }).catch(() => {})` y **nunca** toca `estadoSync` — el 'pendiente' previo es el rollback natural (§2). Verificado por tests 3, 4, 5, 6 y 8. |
| 3 | `src/constants/mapeoApi.js` con `CLIENTES_POR_NOMBRE`/`PRODUCTOS_POR_ID_LOCAL` y `resolverClienteId`/`resolverProductoId` que lanzan si no resuelven | ✅ CUMPLE | `CLIENTES_POR_NOMBRE` :7 (clave normalizada `trim().toLowerCase()`), `PRODUCTOS_POR_ID_LOCAL` :12 (5 productos del catálogo local). `resolverClienteId` :22-29 lanza `Error('Cliente sin UUID de API: …')` si no hay mapeo; `resolverProductoId` :32-38 lanza `Error('Producto sin UUID de API: …')`. `construirPayloadPedido` (:19-31) las invoca → el lanzamiento cae en el `catch` de `ejecutarSync` → pedido queda `pendiente` (nunca se envía basura a la API). |
| 4 | Disparadores: montaje, `window.addEventListener('online')` con cleanup, post-guardado `onGuardado`; existe `src/hooks/useSincronizacion.js` | ✅ CUMPLE | Hook existe (40 líneas). Montaje: `useEffect` → `if (hayConexion()) sincronizar()` :33 (solo con red). Evento `online`: `window.addEventListener('online', alRecuperarRed)` :35 con `return () => window.removeEventListener('online', alRecuperarRed)` :36. Post-guardado: `CapturarPedidoPage.jsx:11` `<PedidoForm onGuardado={sincronizar} />` y `PedidoForm.jsx:54` invoca `onGuardado?.()` tras `addPedido`. Guardia por instancia `enCurso` (:18-29) para StrictMode. |
| 5 | `src/components/SyncStatus.jsx` con badge de pendientes y `role="status"`; integrado en `App.jsx` | ✅ CUMPLE | `SyncStatus.jsx`: badge `<span data-testid="sync-pendientes" data-pendientes={pendientes}>` :10-12 (⏳ N pendiente(s) / ✓ sincronizado), botón manual :13-15, mensaje `<p role="status">{resultado.mensaje}</p>` :16. Integrado en `App.jsx:5` (import) y `App.jsx:12` (`<SyncStatus />` dentro de `<nav>`). |
| 6 | `src/test/syncService.test.jsx` cubre: guardar offline → simular online → verify payload exacto + `estadoSync 'sincronizado'`; fallo de red y HTTP 500 mantienen `'pendiente'`; tests con `npm test` | ✅ CUMPLE | Caso 2 (:90-112): guarda vía `addPedido`, `fetchMock.mockResolvedValue({ ok: true, status: 201 })`, verifica **payload exacto** con `toEqual` (URL `${API_URL}/pedidos`, `POST`, `Content-Type: application/json`, `cliente_id`/`producto_id` UUIDs, `fecha_entrega`, `notas` con teléfono plegado, medidas como números) y `estadoSync === 'sincronizado'`. Caso 3 (:115-126): `TypeError('Failed to fetch')` → `'pendiente'` + `ultimoError` escrito. Caso 4 (:129-138): `{ ok: false, status: 500 }` → `'pendiente'`, mensaje "API respondió 500". Además casos 1, 5 (404), 6 (cola parcial), 7 (mapeo), 8 (cliente sin mapeo), 9-10 (UI con evento `online`). **`npm test` → 17/17 passed** (2 archivos: `syncService.test.jsx` 11 tests + `capturaPedido.test.jsx` 6 tests). |
| 7 | `npm run build` y `npm run lint` pasan | ✅ CUMPLE | `npm run build` → `✓ 42 modules transformed`, `✓ built in 257ms`. `npm run lint` (oxlint) → sin errores, `LINT_EXIT=0`. |
| 8 | Trazabilidad #38, HU-01, HU-08 | ✅ CUMPLE | Commit `1eb80c3`: asunto `feat(pwa): sincronización offline a API con Dexie (#38)`; cuerpo cita "HU-08 (trabajar sin internet) / HU-01 (registrar pedido)". Encabezados in-line en todos los archivos nuevos: `// AVAO — Tarea #38, HU-08 / HU-01` (syncService, mapeoApi, useSincronizacion, SyncStatus, tests); `App.jsx:1` y `CapturarPedidoPage.jsx:1` actualizados a "Tarea #28, HU-01; Tarea #38, HU-08". `docs/planning/PLAN-#38.md` incluido en el commit (§8 tabla de trazabilidad). |
| 9 | No push a `main`/`develop` | ✅ CUMPLE | `git merge-base --is-ancestor 1eb80c3 main/develop/origin/main/origin/develop` → **NO EN** ninguna de las cuatro. `main` local y remoto en `4751067`; `develop` local y remoto en `5f69565` (padre de `1eb80c3`). El commit existe solo en `feature/38-sync-offline-api`. |
| 10 | Observación de datos: consistencia del seed §5.4 con los CHECK de la BD y con `mapeoApi.js` | ✅ CUMPLE (con nota) | Ver análisis detallado abajo. El seed del PLAN-#38.md §5.4 **tal como está commiteado** es válido y `mapeoApi.js` es 1:1 consistente con él. La violación descrita (tipo `'espejo'`, espesor `0`) **no reproduce** en los artefactos del commit. |

### Análisis del ítem 10 (observación de datos)

- **Constraints reales** (migración `apps/api/alembic/versions/95354a0cc046_create_tables_for_pedidos_27.py:76-80`): `ck_productos_tipo_valido` = `tipo IN ('vidrio','aluminio','otro')` y `ck_productos_espesor_positivo` = `espesor_mm > 0`; `espesor_mm` es **nullable** (`:63`), por lo que `NULL` pasa el CHECK (en PostgreSQL `NULL > 0` es NULL, no falso) — `0` y `'espejo'` son los valores inválidos.
- **Seed del plan §5.4 commiteado** (`PLAN-#38.md:341-346`): `('…014', 'Perfil aluminio 2x1', 'aluminio', 20)` y `('…015', 'Espejo 4mm', 'otro', 4)` — **ambos válidos**: `'aluminio'` y `'otro'` ∈ tipo permitido; `20 > 0` y `4 > 0`.
- **`mapeoApi.js`** mapea `'aluminio-perfil-2x1' → …014` y `'otro-espejo-4' → …015`, coincidiendo exactamente con las filas del seed (mismo UUID). El catálogo local `catalogoProductos.js` también coincide (aluminio/espesor 20; espejo/tipo `'otro'`/espesor 4).
- **Conclusión:** si un seed manual se hubiera aplicado con tipo `'espejo'` o espesor `0`, el `INSERT` sería **rechazado** por la BD (CHECK violation); la convención correcta —espejo→tipo `'otro'`, y espesor `NULL` (no `0`) cuando el espesor no aplica— es la que usan el plan, el mapeo y el catálogo. No se encontró inconsistencia.
- **Limitación:** Docker no es accesible en este entorno (`permission denied` en `/var/run/docker.sock`), por lo que no fue posible inspeccionar la BD en vivo para confirmar las filas aplicadas; la verificación fue sobre el seed documentado (§5.4), la migración, `mapeoApi.js` y `catalogoProductos.js`.

### Casos de test verificados (`syncService.test.jsx`, 11 tests)

1. `hayConexion refleja navigator.onLine` — true/false vía `Object.defineProperty`.
2. Caso 1 — sin conexión: **fetch no llamado**, `estadoSync` sigue `'pendiente'`, mensaje "Sin conexión…".
3. Caso 2 — recuperar red: **fetch 1 vez**, URL/método/header/body exactos, `estadoSync → 'sincronizado'`, resumen `sincronizados: 1`.
4. Caso 3 — fallo de red (`TypeError`): `'pendiente'` preservado + `ultimoError` escrito + `errores: 1`.
5. Caso 4 — HTTP 500: `'pendiente'`, mensaje "API respondió 500".
6. Caso 5 — HTTP 404: `'pendiente'`, "API respondió 404".
7. Caso 6 — cola de 2 (1 con mapeo, 1 sin mapeo): `sincronizados: 1, errores: 1`, fetch solo 1 vez.
8. Caso 7 — mapeo de payload: fechas→`null` cuando vacías, teléfono plegado en `notas`, decimales, normalización de nombre con espacios.
9. Caso 8 — cliente sin mapeo: `construirPayloadPedido` **lanza**, fetch no llamado, `'pendiente'`.
10. Caso 9 — UI: guardar offline → `dispatchEvent(new Event('online'))` → badge "✓ sincronizado", mensaje `role="status"`, `estadoSync 'sincronizado'`, fetch exactamente 1 vez (ejercita el cerrojo con dos instancias del hook).
11. Caso 10 — UI offline: "Pedido guardado localmente", badge "1 pendiente(s)", sin fetch.

`capturaPedido.test.jsx` (6 tests, preexistentes de #28) se actualizó con `vi.stubGlobal('fetch', vi.fn())` en `beforeEach`/`afterEach` para aislar el disparador post-guardado de la red — cambio correcto y justificado con comentario `#38`.

## Comandos ejecutados

```bash
git log --oneline -10 && git branch -a && git status
git show --stat 1eb80c3                          # 9 archivos, +1016/-4
git diff 1eb80c3~1 1eb80c3 --name-status
# Lectura de: syncService.js, mapeoApi.js, useSincronizacion.js, SyncStatus.jsx,
#   App.jsx, CapturarPedidoPage.jsx, syncService.test.jsx, dexieDb.js,
#   catalogoProductos.js, PedidoForm.jsx (grep onGuardado), models.py,
#   schemas.py, alembic/versions/95354a0cc046_*.py, setup.js, vite.config.js
grep -n "Promise.all" apps/ventas-pwa/src/services/syncService.js   # solo comentario
grep -c "  it(" src/test/syncService.test.jsx src/test/capturaPedido.test.jsx  # 11 + 6
cd apps/ventas-pwa && npm test                   # Test Files 2 passed; Tests 17 passed (17)
cd apps/ventas-pwa && npm run lint; echo $?      # oxlint, LINT_EXIT=0
cd apps/ventas-pwa && npm run build              # ✓ 42 modules, built in 257ms
git merge-base --is-ancestor 1eb80c3 main develop origin/main origin/develop
                                                 # NO en ninguna (sin push)
docker ps                                        # permission denied (sin acceso a BD en vivo)
```

## Observaciones menores (no bloqueantes)

- **Desviación de archivo de tests:** el plan §6 mencionaba un segundo archivo `src/test/sincronizacionUI.test.jsx`; la implementación consolidó los casos de UI (9-10) dentro de `syncService.test.jsx`. Los 10 casos obligatorios del checklist de testing están cubiertos; no requiere rework.
- **Asunto del commit:** usa `feat(pwa):` en lugar del `feat(ventas-pwa):` del plan §7; la trazabilidad (#38, HU-08, HU-01) está completa en asunto+cuerpo. Cosmético.
- **Doble instancia del hook** (App.jsx vía SyncStatus + CapturarPedidoPage) es intencional y documentada (§2 nota del plan); el cerrojo de módulo evita doble envío — el test 9 lo verifica (fetch exactamente 1 vez).
- **Riesgos aceptados del plan** (§9) siguen vigentes: sin idempotencia en la API (ventana de crash entre 201 y el `update` de Dexie), mapeo manual provisional hasta el HU de catálogo/clientes, `telefono` plegado en `notas` (GAP C). Documentados, no bloqueantes para #38.

## Decisión final

**APROBADO** ✅

La implementación cumple `PLAN-#38.md` en los 10 ítems del checklist: servicio puro con envío secuencial y cerrojo de módulo, errores que preservan `'pendiente'` + `ultimoError`, mapeo local que lanza controlado, los 4 disparadores, UI con `role="status"`, 17/17 tests, lint y build verdes, trazabilidad completa y sin push a `main`/`develop`. La observación del ítem 10 (seed) verifica consistente y válida contra los CHECK de la BD. Lista para merge a `develop` vía PR.

*Fin del reporte. Entregado por el rol Revisor (WORKFLOWS.md §2) para la tarea #38.*
