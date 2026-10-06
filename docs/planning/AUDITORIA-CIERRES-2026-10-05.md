# Auditoría de subtareas que figuraban en Finalizado — 2026-10-05

**Alcance:** [#26](https://github.com/ErickRamos37/AVAO/issues/26)–[#31](https://github.com/ErickRamos37/AVAO/issues/31) y [#38](https://github.com/ErickRamos37/AVAO/issues/38), según el tablero AVAO / Desarrollo Principal. **Base de comparación:** checklists actuales de esas issues y HUs #1 (HU-01), #2 (HU-02), #10 (HU-08), #11 (HU-09) y #14 (HU-13), comunicados por el coordinador desde GitHub; planes `PLAN-#27` a `PLAN-#38`, ERD y código local. `REVIEW-#*.md` se usaron sólo como antecedente. Rama de auditoría: `feature/auditoria-cierres-contexto`, base `0743c4d`.

**Estado posterior a la auditoría:** #38, cerrada durante esta revisión, fue reabierta y movida a **En proceso** hasta integrar a `develop` la corrección del contrato HTTP 201. El resto de los cierres auditados no cambió. Esta matriz conserva el estado histórico de partida y distingue evidencia de pruebas de integración completada.

## Comprobaciones ejecutadas

| Entorno/comando | Resultado y límite |
|---|---|
| `apps/api/.venv/bin/python -m pytest -q` en `apps/api` | **21 passed, 1 warning** (deprecación TestClient/httpx), Python 3.14.7. El comando quedó bloqueado dentro del sandbox en la primera prueba; ejecutado fuera del aislamiento terminó en 0.59 s. Usa SQLite en memoria, no PostgreSQL. |
| `apps/api/.venv/bin/python -m ruff check .` | **All checks passed**. |
| `npm test -- --reporter=dot`, `npm run lint`, `npm run build` en `apps/ventas-pwa` | **19 passed** tras corrección de #38; lint y build OK. Vitest/jsdom + fake-indexeddb y fetch simulado. Persisten avisos React `act(...)` en tests existentes y mocks sin respuesta en dos tests de captura; no impiden el paso. |
| Mismos tres comandos en `apps/taller-pwa` | **5 passed**, lint y build OK. API simulada, sin prueba visual en tablet real. |
| PostgreSQL 17 desechable + `alembic upgrade head`/`downgrade base` | Upgrade a `95354a0cc046` OK; tablas `clientes`, `productos`, `pedidos`, `piezas` y `alembic_version`; 16 restricciones y 13 índices totales observados. Downgrade OK; sólo quedó `alembic_version`. Contenedor `--rm` detenido. No se ejecutaron pruebas HTTP integradas contra esa instancia. |
| Chromium 153.0.8010.52 con DevTools/CDP y Vite local; #28 | El coordinador emuló red offline (`Network.emulateNetworkConditions`), comprobó `navigator.onLine === false`, guardó un pedido desde la UI y leyó IndexedDB `avao-ventas` con `Runtime.evaluate`: una fila `pendiente` y una pieza vinculada con medidas/cantidad correctas. Se verificó persistencia en la misma sesión; no se hizo recarga offline. |

Para #28, la secuencia CDP fue habilitar `Network`, invocar `Network.emulateNetworkConditions` con `offline: true`, evaluar `navigator.onLine`, llenar y guardar el formulario de Vite local, y consultar con `Runtime.evaluate` las tablas `pedidos` y `piezas` de `avao-ventas`. La evidencia visual mostró «Pedido guardado localmente» y «1 pendiente(s)»; la consulta devolvió un pedido `estadoSync: pendiente` y una pieza asociada (24 × 36, cantidad 2). El navegador fue **Chromium 153.0.8010.52**. Esta secuencia no prueba recarga de la página ni persistencia tras cerrar el navegador.

### Reproducción de la comprobación PostgreSQL 17

Imagen local `postgres:17`, `PG_VERSION=17.11-1.pgdg13+2`, ID `sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f` (metadatos de `docker image inspect`). La prueba se ejecutó fuera del sandbox tras autorizar acceso al socket Docker y a `127.0.0.1:55432`; dentro del sandbox `docker info` devolvió «permission denied while trying to connect to the docker API». La contraseña usada era temporal y se omite. Estos comandos reproducen los pasos con una contraseña nueva, apta para una URL, en `AVAO_AUDIT_PASSWORD` (establecerla en el entorno antes de empezar):

```bash
docker image inspect postgres:17 --format '{{.Id}}'
docker image inspect postgres:17 --format '{{range .Config.Env}}{{println .}}{{end}}'
docker run --rm -d --name avao-audit-pg17 -e POSTGRES_USER=avao_audit -e POSTGRES_PASSWORD="$AVAO_AUDIT_PASSWORD" -e POSTGRES_DB=avao_audit -p 127.0.0.1:55432:5432 postgres:17
docker exec avao-audit-pg17 pg_isready -U avao_audit -d avao_audit

# En apps/api, con su .venv existente:
AVAO_AUDIT_DATABASE_URL="postgresql+psycopg2://avao_audit:${AVAO_AUDIT_PASSWORD}@127.0.0.1:55432/avao_audit"
DATABASE_URL="$AVAO_AUDIT_DATABASE_URL" ./.venv/bin/alembic upgrade head
docker exec avao-audit-pg17 psql -U avao_audit -d avao_audit -Atc "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name; SELECT count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace; SELECT count(*) FROM pg_indexes WHERE schemaname='public';"
DATABASE_URL="$AVAO_AUDIT_DATABASE_URL" ./.venv/bin/alembic downgrade base
docker exec avao-audit-pg17 psql -U avao_audit -d avao_audit -Atc "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
docker stop avao-audit-pg17
```

Salida observada: `pg_isready` informó «accepting connections»; upgrade informó `Running upgrade  -> 95354a0cc046`; la consulta devolvió `alembic_version`, `clientes`, `pedidos`, `piezas`, `productos`, luego `16` y `13`; downgrade informó `Running downgrade 95354a0cc046 ->`; la última consulta devolvió únicamente `alembic_version`. Los conteos incluyen claves primarias, unique y sus índices, por lo que no equivalen al número de índices secundarios definido en el ERD. No se ensayó integridad de filas ni reversión con datos.

## Matriz criterio → evidencia → resultado → limitación

| Issue / HU / integración | Criterio del checklist | Evidencia propia | Resultado | Limitación y decisión |
|---|---|---|---|---|
| **#26** HU-01/02/03; `5a9e83b`, migración en `a58b9ff` | ERD para clientes, productos, pedidos y piezas; modelos; generar y ejecutar Alembic | `docs/design/ERD-FASE1.md`, `apps/api/models.py`, migración `95354a0cc046`; upgrade/downgrade en PostgreSQL 17 y esquema observado | **Cumple el entregable estructural** | La comprobación previa PGlite no probaba Alembic real; esta auditoría la completa. No se ensayaron aquí casos de integridad negativos ni actualización sobre datos existentes. El modelo todavía usa mm y escala 2, brecha de #35 posterior. |
| **#27** HU-01; `a58b9ff`, merge `55dbecc` | Pydantic, POST `/pedidos`, 422 para medidas inválidas, 201 para válido | `schemas.py`, `routers/pedidos.py`; `test_pedidos.py`: 201, 422, 404 y piezas/estado inicial; suite API 21/21 | **Cumple con límite de entorno** | Tests HTTP usan SQLite; no se hizo POST completo en PostgreSQL. Requiere cliente/producto UUID preexistentes; resolverlos desde captura y sincronización corresponde a [#40](https://github.com/ErickRamos37/AVAO/issues/40). Medidas exactas en pulgadas 1/16 siguen pendientes (#35). |
| **#28** HU-01; `aaaf50b`, merge `aae5973` | Formulario de N piezas y guardado Dexie sin red; comprobar en DevTools almacenamiento | `PedidoForm.jsx`, `PiezasList.jsx`, `dexieDb.js`; seis tests de captura; Ventas 19/19. En Chromium 153 DevTools, con red emulada offline, el coordinador capturó «Cliente Offline 28», producto `vidrio-claro-6`, ancho 24, largo 36, cantidad 2: UI mostró «Pedido guardado localmente» y «1 pendiente(s)»; IndexedDB tuvo 1 pedido `pendiente` y 1 pieza vinculada con esos valores | **Cumple el checklist de captura offline** | La comprobación DevTools fue en una misma sesión; no incluyó recarga offline ni reinicio del navegador. HU-01 completa depende también de catálogo/clientes y unidad correcta. |
| **#29** HU-02; `5e30a40`, merge `66751dd` | GET `/tareas/pendientes` sólo incluye estado `pendiente`, JSON omite completadas | `routers/tareas.py`; siete pruebas de tareas en suite API: filtro, vacío, contrato, orden y paginación | **Cumple la subtarea** | El endpoint no filtra por operario activo y no hay identidad/JWT. La prueba `test_respeta_operario_asignado` confirma exposición del campo, no filtrado. HU-02 pide lista asignada al operario activo; se sigue en [#41](https://github.com/ErickRamos37/AVAO/issues/41): **HU incompleta**. |
| **#30** HU-02; `dd017b1`, merge `53791ac` | Tarjetas muestran medidas; array vacío dice «No hay cortes pendientes hoy» | `TallerPage.jsx`, `CorteCard.jsx`; cinco tests de vacío, tarjetas, medidas, carga y error; Taller 5/5 | **Cumple la subtarea de tarjetas** | Taller obtiene datos por REST y muestra `mm`; no se validó vista física tablet. Botón «Marcar completado» permanece deshabilitado y corresponde a #32/HU-09. WSS/Canvas son arquitectura futura. HU-02 sigue sin filtro por operario. |
| **#31** HU-02/HU-09; `ba7f620`, merge `0493265` | PATCH `/piezas/{id}/completar`, persistencia y 404 para ID inexistente | `routers/piezas.py`; cuatro tests: 200, 404, 422 e idempotencia, con lectura posterior del estado en BD SQLite | **Cumple la subtarea API** | No hay prueba de concurrencia ni integración con Taller. HU-09 exige botón táctil y cambio visual (#32); HU-13 exige pedido «Listo para entrega» al 100% (#33). Ninguna queda cumplida por el PATCH. |
| **#38** HU-08/HU-01; `1eb80c3`, `25661a0`, merge histórico `0743c4d` | Detectar conexión, cola Dexie pendiente, POST con payload, marcar sincronizado al éxito, conservar pendiente/error al fallo | `syncService.js`, `useSincronizacion.js`; 13 tests de sync (19 Ventas total), incluidos reconexión, 404/500, mapeo y UI. Pruebas nuevas demostraron fallo con HTTP 200/204; se corrigió para exigir 201 | **Corrección probada; En proceso hasta integración** | El ajuste HTTP 201 sigue en rama `feature/*`, sin integrar a `develop`. Fetch y IndexedDB simulados; no hubo integración navegador → API → PostgreSQL. POST carece de clave idempotente: si el servidor crea el pedido y se pierde el 201, el reintento puede duplicarlo (#39). El mapeo manual cliente/producto se sigue en [#40](https://github.com/ErickRamos37/AVAO/issues/40). HU-08 también pide Service Worker/caché de sesión y tareas: **HU incompleta**. |

## Decisiones y seguimiento

- Las siete subtareas tienen evidencia técnica de sus checklists dentro de los límites indicados; #28 incluye la comprobación de guardado y lectura de IndexedDB con Chromium DevTools en una misma sesión. #38 permanece abierta y En proceso hasta integrar la corrección HTTP 201. La recarga offline sigue sin verificarse y no se debe inferir que HU-01 esté completa. No marcar nuevas tareas como cerradas por esta auditoría.
- Para #38 se añadió prueba de contrato 201 exacto antes del cambio: con 200 y 204 falló porque el pedido quedaba `sincronizado`; tras el ajuste permanece `pendiente` y registra el error. El caso de respuesta 201 perdida requiere idempotencia en servidor, una tarea separada de la sincronización básica.
- Las brechas del MVP ya tienen seguimiento: HU-01 cliente/producto reales en [#40](https://github.com/ErickRamos37/AVAO/issues/40), HU-02 filtro por operario activo en [#41](https://github.com/ErickRamos37/AVAO/issues/41), medidas en #35, idempotencia en #39, interfaz de HU-09 en #32 y pedido listo de HU-13 en #33. HU-08 aún requiere Service Worker/caché; revisar que #32 tenga botón táctil y estado visual, y que #33 actualice pedido sólo al 100%.
- Conservar `Finalizado` como criterio de subtarea verificada, revisada e integrada a `develop`; aprobación humana para `main` queda separada en `WORKFLOWS.md`. La matriz no modifica issues ni campos del tablero.
