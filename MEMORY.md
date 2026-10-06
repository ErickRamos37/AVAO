# MEMORY.md — Contexto AVAO

## Identidad y fuentes

- Producto: **AVAO** (Asistente para Vidrieras Administrativo y Operativo), repositorio [ErickRamos37/AVAO](https://github.com/ErickRamos37/AVAO).
- Fuente principal del estado: [tablero AVAO / Desarrollo Principal](https://github.com/users/ErickRamos37/projects/4); los cuerpos de las issues y sus checklists delimitan cada subtarea. No confundir cierre de subtarea con HU completa.
- `README.md` fija trazabilidad inline a HU. `AGENTS.md` y `docs/planning/WORKFLOWS.md` describen convenciones y coordinación; `ARCHITECTURE.md` distingue objetivo y avance. Los planes/revisiones anteriores son registros históricos.

## Rol y flujo

- Coordinador: organiza fases, transmite contexto, contrasta evidencia y gobierna el tablero.
- Planificador: analiza HU y diseña. Implementador: cambia código con pruebas. Revisor: comprueba contra plan, checklist y resultados. El coordinador integra la decisión.
- Orden: planificación → análisis/diseño → implementación con TDD → verificación → integración. No considerar una prueba verde suficiente para completar una HU.
- Ramas: `feature/*` hacia `develop` tras revisión; `main` requiere aprobación humana explícita, según `WORKFLOWS.md`.

## Estado verificado al 2026-10-05

- Existen `apps/api` (FastAPI, SQLAlchemy, Alembic, pytest, Ruff), `apps/ventas-pwa` (React/Vite, Dexie, Vitest), `apps/taller-pwa` (React/Vite, Vitest), `infra/docker-compose.yml` y documentación de diseño.
- API: `POST /pedidos` (#27), `GET /tareas/pendientes` (#29), `PATCH /piezas/{id}/completar` (#31), migración de cuatro tablas (#26). Ventas: formulario y almacenamiento Dexie (#28), sincronización offline → API (#38). Taller: tarjetas de cortes pendientes por REST (#30).
- Instantánea del tablero autenticado: **35 elementos**. En Finalizado y cerradas: #26–#31; **#38 reabierta, En proceso**, hasta integrar a `develop` la corrección HTTP 201; Por hacer: #32–#33; Backlog: #34–#37, #39–#41 y HUs. #40 resuelve cliente/producto reales en captura y sincronización de Ventas; #41 filtra cortes por operario activo. Ambas son Backlog, Prioridad Media, Épica 1, con Esfuerzo pendiente.
- Política: sólo cinco HUs rectoras están en **Alta** (#1 HU-01, #2 HU-02, #11 HU-09, #14 HU-13, #24 HU-05.1); las subtareas usan Media/Baja. Prioridad actual: Media #26–#35 y #38–#41; Baja #36–#37. Épica: #26–#30→1, #31–#32→3, #33→5, #34–#35→1, #38→3, #39–#41→1. #35, #39 y #40 están vinculadas como subissues de #1/HU-01; #41 es subissue de #2/HU-02; #38 de #10/HU-08. Sólo #36/#37 carecen de parent y Épica hasta definir flujo/HU dueño. Esfuerzo permanece vacío en cerradas para no inventar estimaciones históricas y en abiertas hasta acordar escala/refinamiento. Los cuerpos #34–#38 se ampliaron con decisiones pendientes; #35 identifica HU-01 como principal y #38 enlaza #39. Véase `docs/planning/CONSERVACION-TABLERO-2026-10-05.md`.
- Orden MVP: HU-01 (incluidas #35/#39/#40) → HU-02 (incluida #41) → HU-09/#32 → HU-13/#33 → HU-05.1/#34 → #36/#37; las dependencias técnicas y decisiones de negocio pueden ajustar la secuencia.
- Posición global verificada del tablero: primeros 18 **#1, #26, #27, #28, #35, #39, #40, #2, #29, #30, #41, #11, #31, #32, #14, #33, #24, #34**; últimos dos **#36, #37**. Las vistas agrupadas por Status muestran columnas y pueden diferir visualmente de este orden global.
- Las pruebas de esta iteración y sus límites constan en `docs/planning/AUDITORIA-CIERRES-2026-10-05.md`. La migración Alembic se verificó con upgrade/downgrade en PostgreSQL 17 desechable.

## Arquitectura y brechas abiertas

- Objetivo: dos PWAs (Ventas móvil y Taller tablet), Dexie/IndexedDB offline-first, Canvas 2D en Taller; backend FastAPI/PostgreSQL, `fastapi-users` JWT, `rectpack`; Ventas HTTPS REST + JWT, Taller WSS, Nginx/Oracle Cloud. Resultado de optimización: JSON de coordenadas 2D para Canvas.
- El flujo actual de Taller usa REST y tarjetas. JWT, WSS, Canvas, optimización y Service Workers todavía no están implementados. HU-02 requiere tareas filtradas por operario activo (#41); HU-08 requiere caché offline adicional a #38; HU-09 necesita interfaz táctil; HU-13 requiere actualización del pedido al 100%.
- Negocio define pulgadas fraccionarias con precisión de 1/16 (`docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md`); implementación conserva `*_mm` y `NUMERIC(10,2)`. #35 necesita diseño de unidad canónica y migración sin pérdida.
- #38 carece de idempotencia del POST en servidor: una respuesta 201 perdida puede duplicar un pedido al reintentar; **#39** quedó abierta para resolverlo. El mapeo de cliente/producto a UUID sigue siendo manual y se sigue en **#40**; teléfono se coloca en notas. Son brechas específicas para seguimiento, no prueba de HU-08 completa.
- `README.md` pide scripts Docker local en raíz tras definición DevOps; el compose de desarrollo existente está en `infra/`. Resolver ubicación antes de añadir scripts.

## Conexiones

- `opencode.json` define MCP remoto GitHub con `GITHUB_TOKEN` por variable de entorno y Chrome DevTools. El tablero se consultó por GraphQL autenticado en la iteración previa; no registrar credenciales en documentos ni salida de herramientas.
- Los roles `.opencode/agents` fueron adaptados a AVAO, pero en esta sesión el coordinador usa subagentes nativos. La configuración de OpenCode no activa automáticamente esos roles en este entorno.
