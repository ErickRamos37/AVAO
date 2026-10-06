# AGENTS.md — AVAO

## Fuente de verdad y estado

- El producto se llama **AVAO**. El tablero [AVAO / Desarrollo Principal](https://github.com/users/ErickRamos37/projects/4) contiene el estado de HUs y subtareas; cotejar issue, checklist y código antes de declarar un cierre.
- Política de Prioridad vigente: sólo cinco HUs rectoras están en **Alta** (#1 HU-01, #2 HU-02, #11 HU-09, #14 HU-13 y #24 HU-05.1); las subtareas se clasifican **Media** o **Baja**. El orden MVP se guía por HU-01 (incluidas #35, #39 y #40), HU-02 (incluida #41), HU-09/#32, HU-13/#33 y HU-05.1/#34; #36/#37 siguen después, ajustando la secuencia por dependencias reales.
- El repositorio ya tiene `apps/api`, `apps/ventas-pwa`, `apps/taller-pwa`, migración Alembic, pruebas y `infra/docker-compose.yml`. Verificar scripts y entorno en los manifests antes de ejecutarlos.
- `docs/planning/WORKFLOWS.md` define roles, revisión y ramas. `MEMORY.md` resume contexto; los planes y reportes previos son evidencia histórica, no sustituyen pruebas propias.

## Convenciones obligatorias

- Todo componente, API o modelo de base de datos nuevo debe referenciar su Historia de Usuario (HU) y documentarse in-line, como pide `README.md`.
- Diseñar antes de implementar y probar el comportamiento verificable. En la API existen pytest y Ruff; en ambas PWAs, Vitest, oxlint y build de Vite. Ejecutar solo comandos definidos y pertinentes.
- `README.md` reserva los scripts de despliegue Docker local para la raíz, pendiente de definición por DevOps. Existe `infra/docker-compose.yml` para desarrollo; no moverlo ni crear scripts nuevos sin resolver esa decisión.

## Arquitectura objetivo y alcance implementado

- Objetivo: dos PWAs separadas, Ventas/Medidor (móvil) y Taller/Operario (tablet), con Vite, React y Dexie.js/IndexedDB offline-first; Taller dibujará guías de corte con Canvas 2D.
- Objetivo backend: FastAPI, PostgreSQL, SQLAlchemy, Alembic, UUIDs, `fastapi-users`/JWT y `rectpack` para optimización de guillotina 2D.
- Objetivo de comunicación: Ventas por HTTPS REST + JWT; Taller por WSS; Nginx proxy/SSL en Oracle Cloud con Docker. La optimización terminará en JSON de coordenadas 2D para Canvas 2D.
- Implementado a 2026-10-05: API de pedidos, tareas pendientes y finalización de piezas; Ventas captura con Dexie y sincroniza pedidos; Taller muestra tarjetas consultadas por REST. JWT, WSS, Canvas, optimización y caché Service Worker aún requieren trabajo. No atribuirlos a subtareas ya cerradas sin evidencia.
- La especificación de negocio actual pide pulgadas con precisión de 1/16; contratos y datos implementados aún usan campos `*_mm` y `NUMERIC(10,2)`. Tratar la conversión como cambio de diseño y migración de #35, no como ajuste cosmético.
