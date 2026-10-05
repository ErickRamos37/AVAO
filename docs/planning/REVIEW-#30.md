# REVIEW #30 — Vista de Taller PWA

- **Fecha:** 2026-10-04
- **Rama:** `feature/30-vista-taller-pwa`
- **Commit revisado:** `dd017b1 feat(pwa): vista de taller con tarjetas de cortes pendientes (#30)`
- **Plan:** `docs/planning/PLAN-#30.md`

## Checklist

| # | Ítem | Estado |
|---|------|--------|
| 1 | Existe `apps/taller-pwa/src/pages/TallerPage.jsx` | ✅ OK |
| 2 | `src/components/CorteCard.jsx` con medidas, cantidad, operario, fecha | ✅ OK (también `estado`, `pieza_id` y botón "Marcar completado" deshabilitado con `TODO #31`) |
| 3 | Servicio `tareasApi.js` con fetch a `/tareas/pendientes` | ✅ OK (`getTareasPendientes()`, throw si `!res.ok`, fallback `VITE_API_URL` → `http://localhost:8000`) |
| 4 | `App.jsx` usa react-router-dom con ruta `/` o `/taller` | ✅ OK (`BrowserRouter`, `Routes`, `Route path="/"`, `Route path="/taller"` con `Navigate to="/"`) |
| 5 | Estado vacío muestra "No hay cortes pendientes hoy" | ✅ OK (texto exacto en `TallerPage.jsx`) |
| 6 | Pruebas Vitest en `src/test/tallerPage.test.jsx`, 5/5 pasan | ✅ OK |
| 7 | `npm run build` y `npm run lint` pasan | ✅ OK |
| 8 | Trazabilidad #30 y HU-02 en archivos nuevos | ✅ OK (comentario `// AVAO — Tarea #30, HU-02` en App, TallerPage, CorteCard, CorteCardList, tareasApi, setup.js, test, y README) |
| 9 | No push a `main`/`develop` | ✅ OK (`dd017b1` solo presente en rama local `feature/30-vista-taller-pwa`; `git branch -r --contains dd017b1` vacío; remoto no contiene el commit) |

## Comandos ejecutados

```bash
git branch --show-current                       # feature/30-vista-taller-pwa
git log --oneline -3                            # dd017b1 en HEAD
git branch -r --contains dd017b1                # (vacío → no pusheado)
cd apps/taller-pwa
npm run test                                    # Test Files 1 passed (1), Tests 5 passed (5)
npm run lint                                    # oxlint, exit code 0
npm run build                                   # ✓ built in 179ms, dist/ generado
```

## Observaciones

- Tests: 5/5 en verde — estado vacío, datos válidos (2 cards), medidas `1200.00 x 2400.00 mm`, loading, error.
- Cumple límites del plan: sin PATCH funcional, sin Dexie, sin WebSocket, sin auth, sin Canvas 2D, sin cambios al backend.
- `.env.example` con `VITE_API_URL=http://localhost:8000` presente y documentado en README.
- `CorteCard` renderiza `ancho_mm`/`largo_mm` verbatim (string decimal), sin aritmética.

## Decisión final

**APROBADO** — la implementación cumple el plan #30 en su totalidad. Merge de `feature/30-vista-taller-pwa` a `develop` puede proceder (tras revisión/aprobación del equipo).
