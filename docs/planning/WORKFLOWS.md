# Flujo Multiagente y Estrategia de Ramas — AVAO

**Proyecto:** AVAO (PWA B2B para talleres vidrieros)
**Estándar de referencia:** GitHub Flow + prácticas Trunk-Based (PR cortos, main siempre desplegable), adaptado para equipo pequeño y revisión humana.

---

## 1. Estrategia de Ramas (GitHub Flow modificado)

| Rama | Propósito | Reglas |
|------|-----------|--------|
| `main` | Producción estable. **Código probado y aprobado por el humano (luz verde)** | Solo merge desde `develop` vía Pull Request aprobada por el coordinador humano |
| `develop` | Integración / staging. Lugar donde el humano **visualiza y prueba** las funcionalidades terminadas | Recibe merges solo desde ramas `feature/*` vía Pull Request con pruebas pasadas |
| `feature/<#tarea>-<descripcion>` | Rama de trabajo por tarea HU/subtarea | Nace de `develop`, merge a `develop` tras pruebas y revisión |

### Nomenclatura de ramas
- `feature/27-api-recepcion-pedidos`
- `feature/28-interfaz-captura-pwa`
- `hotfix/32-fix-crash-operario`

### PR y merge
- Todo cambio pasa por Pull Request (no push directo a `main` o `develop`).
- `feature/*` → `develop`: automático tras PR del Revisor (multiagente) aprobada por el Coordinador.
- `develop` → `main`: requiere luz verde del humano tras probar en `develop`.

---

## 2. Flujo Multiagente (por tarea)

```
Coordinador (Tú/Yo) → Planificador → Implementador → Revisor → Coordinador → GitHub Projects
```

| Rol | Agente | Función |
|-----|--------|---------|
| **Coordinador** | Erick / AI Orquestador | Organiza fases, transmite contexto, gestiona ramas, actualiza GitHub Projects, pide luz verde al humano |
| **Planificador** | Subagente (general) | Analiza HU/tarea, lee código existente, diseña la solución (archivos a tocar, modelos de datos, endpoints, pruebas). Entrega plan detallado sin escribir código |
| **Implementador** | Subagente (general) | Ejecuta el plan: crea rama `feature/*` desde `develop`, escribe código, ejecuta pruebas (TDD). Reporta al Coordinador |
| **Revisor** | Subagente (general) | Comprueba el código contra el plan: LMD/PMD, estándares IEEE, nombres, tests. Aprueba o rechaza |

### Flujo paso a paso por tarea
1. **Coordinador** mueve la tarea a "En proceso" en GitHub Projects.
2. **Coordinador** lanza al **Planificador** con el contexto del ERD Fase 1 y la HU.
3. **Planificador** entrega plan de implementación (archivos, schemas Pydantic, tests, migraciones Alembic necesarias).
4. **Coordinador** lanza al **Implementador** con el plan, rama `feature/*` ya creada desde `develop`.
5. **Implementador** codifica y corre pruebas. Reporta comando: `pytest apps/api/tests/`, `npm run build`, etc.
6. **Coordinador** lanza al **Revisor** con plan vs implementación vs pruebas.
7. **Revisor** aprueba → Coordinador crea PR a `develop` y la merge.
   **Revisor** rechaza → Coordinador devuelve al Implementador con comentarios.
8. **Coordinador** mueve la tarea a "Finalizado" en GitHub Projects **solo** tras merge a `develop` y luz verde del humano en `develop` → merge a `main`.

---

## 3. Prohibiciones estrictas
- Ningún subagente puede pushear directo a `main` o `develop`.
- Ninguna tarea se marca "Finalizado" sin merge a `develop` y notificación al humano.
- Ningún código se mergea a `main` sin luz verde explícita del usuario.
- Todo código nuevo debe tener trazabilidad a HU/tarea en commits (conventional commits + referencia a issue).

---

## 4. Conventional Commits
```
feat(api): agregar endpoint POST /pedidos con validación Pydantic (#27)
docs(design): ERD Fase 1 LMD/PMD (#26, HU-01, HU-02, HU-03)
test(api): agregar pruebas de rechazo 422 para medidas negativas (#27)
fix(pwa): corregir estado offline en Dexie (#28)
```

---

## 5. Estado actual de ramas (2026-10-04)
- `main`: commit `4751067` (incluye #26 finalizado y docs de planificación)
- `develop`: creada desde `main` (4751067)
- Próxima rama de trabajo: `feature/27-api-recepcion-pedidos`
