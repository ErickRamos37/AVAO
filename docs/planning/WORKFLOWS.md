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
- `feature/*` → `develop`: tras PR revisada, pruebas pertinentes y decisión del Coordinador; ninguna aprobación del Revisor hace un merge automático por sí sola.
- `develop` → `main`: requiere luz verde del humano tras probar en `develop`.

---

## 2. Flujo Multiagente (por tarea)

```
Coordinador → Planificador → Implementador → Revisor → Coordinador → GitHub Projects
```

| Rol | Agente | Función |
|-----|--------|---------|
| **Coordinador** | Agente coordinador y responsable humano | Organiza fases, transmite contexto, gestiona ramas y tablero; consulta al humano para pasar a `main` |
| **Planificador** | Subagente (general) | Analiza HU/tarea, lee código existente, diseña la solución (archivos a tocar, modelos de datos, endpoints, pruebas). Entrega plan detallado sin escribir código |
| **Implementador** | Subagente (general) | Ejecuta el plan en la rama preparada, escribe código, ejecuta pruebas pertinentes (TDD). Reporta al Coordinador |
| **Revisor** | Subagente (general) | Comprueba código, documentación y pruebas contra el plan, la HU y el checklist; aprueba o solicita corrección |

### Flujo paso a paso por tarea
1. **Coordinador** lee la issue y su estado; mueve la tarea a "En proceso" cuando comienza trabajo autorizado, si dispone de acceso al tablero.
2. **Coordinador** lanza al **Planificador** con la HU, checklist y diseño vigente relevante.
3. **Planificador** entrega plan de implementación con archivos, criterios, pruebas y migraciones cuando correspondan.
4. **Coordinador** lanza al **Implementador** con el plan, rama `feature/*` ya creada desde `develop`.
5. **Implementador** codifica y corre pruebas. Verifica comandos existentes y reporta los ejecutados: en `apps/api`, `./.venv/bin/python -m pytest -q` y Ruff; en cada PWA, `npm test`, `npm run lint` y `npm run build`.
6. **Coordinador** lanza al **Revisor** con plan vs implementación vs pruebas.
7. **Revisor** aprueba → Coordinador prepara PR a `develop` y decide su integración tras comprobar pruebas y revisión.
   **Revisor** rechaza → Coordinador devuelve al Implementador con comentarios.
8. **Coordinador** marca "Finalizado" cuando cumple criterios de la subtarea, pruebas verificadas, revisión registrada, integración a `develop`, issue coherente y comunicación al responsable. El paso de `develop` a `main` es independiente y requiere luz verde humana explícita.

---

## 3. Prohibiciones estrictas
- Ningún subagente puede pushear directo a `main` o `develop`.
- Ninguna tarea se marca "Finalizado" sin criterios comprobados, revisión, integración a `develop` y comunicación al responsable.
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

## 5. Estado observado (2026-10-05)

- #26–#31 figuran cerradas y en Finalizado. #38 estuvo cerrada durante la auditoría, pero se **reabrió y pasó a En proceso** hasta integrar a `develop` la corrección que exige HTTP 201. La comprobación independiente se registra en `AUDITORIA-CIERRES-2026-10-05.md`.
- `develop` contiene el MVP de API, captura Ventas, tarjetas Taller y sincronización #38. Antes de iniciar una tarea, verificar rama, historial y estado remoto; las referencias a commits de iteraciones anteriores son históricas.
- Política de Prioridad del tablero: sólo las HUs rectoras #1/HU-01, #2/HU-02, #11/HU-09, #14/HU-13 y #24/HU-05.1 llevan **Alta**; subtareas usan **Media** o **Baja**. Orden MVP: HU-01 (incluidas #35/#39/#40) → HU-02 (incluida #41) → HU-09/#32 → HU-13/#33 → HU-05.1/#34 → #36/#37, sujeto a dependencias técnicas y de negocio.
