# MEMORY.md — Contexto AVAO

## Rol
Arquitecto principal / orquestador de agentes del proyecto AVAO. Abogado del diablo: contradecir cuando haga falta, investigar antes de asumir, cero huecos de información.
Delegar a subagentes especializados cuando sea beneficioso; proponer crearlos si faltan.

## Proyecto
- Nombre oficial: **AVAO** (Asistente para Vidrieras Administrativo y Operativo). OJO: ARCHITECTURE.md lo llama "VidriCalc" (pendiente resolver).
- PWA B2B para MiPyMEs vidrieras. Repo: https://github.com/ErickRamos37/AVAO (público, rama main).
- Stack estricto: Vite+React (2 PWAs: Ventas/Medidor y Taller/Operario), FastAPI + PostgreSQL (SQLAlchemy/Alembic, fastapi-users JWT, rectpack, UUIDs), Nginx, Docker.
- Ventas→HTTPS REST+JWT; Taller→WSS; backend envía payload JSON de coordenadas 2D a PWA Taller (Canvas 2D).
- Convenciones: toda componente/API/modelo referencia su HU, documentado in-line. Scripts Docker en raíz (pendiente DevOps).

## Estado actual (2026-10-04)
- Local: solo README.md, ARCHITECTURE.md, AGENTS.md, MEMORY.md. Sin código; sin node/npm/docker/gh/pip instalados.
- GitHub: repo público, issues = HUs. GitHub Projects pendiente de acceso.
- MCP GitHub: pendiente configurar con PAT del usuario (PAT recibido 2026-10-04).
- "Stack": herramienta externa sin nombre confirmado aún.

## Reglas SDLC
- Orden: Planificación → Análisis → Diseño (ERD LMD/PMD) → Implementación → Pruebas (TDD obligatorio) → Despliegue.
- No escribir código de implementación sin diseño previo y entorno configurado.
- Actualizar MEMORY.md cuando el contexto cambie.

## MCP GitHub (2026-10-04)
- opencode.json creó MCP remoto github (https://api.githubcopilot.com/mcp/), token vía env GITHUB_TOKEN (guardado en ~/.config/fish/config.fish). Requiere reiniciar opencode para cargarlo.
- Probado el handshake initialize: OK. Issues/HUs legibles vía API (lista completa obtenida, 30 issues, 2 épicas, HU-01..HU-15, subtareas 25-34).
- BLOCKER: el PAT no tiene permiso de Projects (fine-grained PAT necesita "Projects: Read/Write" a nivel cuenta). GitHub Projects V2 devuelve FORBIDDEN → regenerar PAT con ese permiso.
- Hubo un dir MEMORY.md fantasma; ya eliminado; MEMORY.md es archivo.

## Iteración 1 (2026-10-04) completada
- Herramientas instaladas vía sudo(1923): node v26.10.0, npm 12.2.0, docker 29.8.2, compose 5.6.0, python-pip. Docker service habilitado; grupo docker agregado a erick (requiere re-login para que aplique sin sudo).
- Estructura monorepo: apps/ventas-pwa + apps/taller-pwa (Vite+React, build OK en ambas, lint=oxlint), apps/api (FastAPI, venv, test_health pytest OK, Dockerfile), packages/shared, infra/docker-compose.yml (postgres:17, api, nginx), docs/.
- docker run hello-world OK.
- opencode.json con MCP GitHub remoto (env GITHUB_TOKEN, guardado en fish config).
- PAT actual aún sin permiso Projects → tablero Projects V2 sigue FORBIDDEN; requiere PAT clásico con scope `project` o fine-grained con Projects:RW a nivel cuenta.
- Git repo aún sin commits nuevos (todo untracked).

## Conexión a GitHub Projects (2026-10-04) - CONFIRMADA
- Token clásico (ghp_d3BDWzys...) con scopes completos (project, repo, user, etc.) funcionando.
- Tablero: "AVAO / Desarrollo Principal" (`PVT_kwHOCXTPGc4BkXAI`, URL https://github.com/users/ErickRamos37/projects/4).
- 28 items leídos directamente del tablero:
  * Subtareas activas: #26 (Diseño LMD/PMD + Migración), #27 (API REST Pedidos), #28 (Captura PWA), #29 (Endpoint Listado), #30 (Vista Taller PWA), #31 (Actualización estado), #32 (Interfaz Operario), #33 (Validación progreso), #34 (Sumatoria lineal).
  * HUs: HU-01 a HU-15 (con subtareas HU-05.1/2 y HU-10.1/2/3/4).
- GITHUB_TOKEN actualizado en ~/.config/fish/config.fish.

## Avance Tareas (2026-10-04)
- #26 (Diseño LMD/PMD + Migración) → **Finalizado**. Documento `docs/design/ERD-FASE1.md` validado con PGlite (DDL + 13 pruebas OK). Commit `5a9e83b`.
- #27 (API REST Recepción de Pedidos) → **En proceso** (listo para siguiente agente).
- Marker: #28 también en "Por hacer", #29/#30/#31 en Backlog (por confirmar).

## Avance Tareas (2026-10-05) - PRUEBAS HUMANAS PENDIENTES
- #27 finalizado, código en `develop`.
- #28 finalizado, código en `develop` (apps/ventas-pwa).
- #29 finalizado, código en `develop` (API GET /tareas/pendientes).
- #30 finalizado, código en `develop` (apps/taller-pwa).
- #31 finalizado, código en `develop` (PATCH /piezas/{id}/completar).
- Branch `develop` ahora contiene MVP: API con POST /pedidos, GET /tareas/pendientes, PATCH /piezas/{id}/completar; Ventas con formulario Dexie; Taller con cards.
- Todo en develop pendiente de tu luz verde para merge a main.

## Especificaciones de Medidas (2026-10-05)
- Todas las medidas se manejan en **pulgadas fraccionarias** (no mm, no decimales). Precisión 1/16.
- Reglas de lectura: referencias 1/2 y 1/4, máximo dos fracciones combinadas (ej: `3/4 + 1/16`).
- Variables clave: `anchoVentana`, `altoVentana` (hueco real).
- Fórmulas de descuento para Ventana California documentadas en `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md`.
- Decisión MVP: backend procesa pulgadas con punto decimal; fracción visual y ventana California como base documentada quedan para post-MVP.
- Issues creados: #35 (pulgadas/cambio mm), #36 (fórmulas California), #37 (visualización fracciones UI post-MVP).
