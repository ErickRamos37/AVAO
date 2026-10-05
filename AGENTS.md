# AGENTS.md

## Estado del repositorio

- Solo existen `README.md` y `ARCHITECTURE.md` (diseño). **No hay código, manifests, ni comandos de build/test definidos aún.** No inventes comandos: si necesitas ejecutar algo, verifica primero qué existe en el árbol.
- `ARCHITECTURE.md` llama al sistema "VidriCalc" mientras `README.md` lo llama AVAO — inconsistencia de nombre en los docs, no asumas que una es la correcta.

## Convenciones obligatorias (de README.md)

- Todo componente, API o modelo de base de datos debe referenciar su Historia de Usuario (HU) y documentarse in-line.
- Scripts de despliegue local Docker van en la raíz del repositorio (pendiente de definición por DevOps — no crear estructura hasta que se defina).

## Decisiones de arquitectura (no negociables al implementar)

- Frontend: dos PWAs separadas — **Ventas/Medidor** (móvil) y **Taller/Operario** (tablet). Vite + React + Dexie.js (IndexedDB, offline-first). Taller usa Canvas 2D para guías de corte.
- Backend: FastAPI + PostgreSQL (SQLAlchemy + Alembic), `fastapi-users` (JWT), `rectpack` para optimización de guillotina 2D, UUIDs.
- Comunicación: Ventas → HTTPS REST + JWT; Taller → WSS (WebSockets). Nginx como proxy/SSL en Oracle Cloud (Docker).
- El flujo de optimización termina con un payload JSON de coordenadas 2D enviado del backend a la PWA Taller (lo dibuja Canvas 2D).
