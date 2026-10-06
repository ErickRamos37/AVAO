# PLAN #33 — Validación recursiva de progreso (FastAPI / PostgreSQL)

- **Tarea:** #33 — Subtarea 1: Validación recursiva de progreso (issue de GitHub #33, verificada **open** por el Planificador el 2026-10-05; checklist reproducido en §1).
- **Historia de Usuario:** HU-13 (issue #14) — *"Saber cuándo el pedido del cliente está listo"*. Criterios de aceptación: (1) el sistema debe validar recursivamente el estado de todas las piezas hijas de un pedido; (2) el estado global del pedido debe cambiar a "Listo para entrega" exclusivamente cuando el progreso alcance el 100%.
- **Decisión vigente aplicable:** `docs/planning/DECISIONES-MVP-2026-10-05.md` **D5** — "Listo para entrega" se representa con **`completado`** del vocabulario existente de `pedidos.estado` (`pendiente|en_proceso|completado|cancelado`); al completarse la **primera** pieza el pedido pasa a `en_proceso`. No hay migración de vocabulario.
- **Rama:** `feature/33-validacion-recursiva-progreso` (nace de `develop`, según WORKFLOWS.md §1; el Coordinador la prepara antes de lanzar al Implementador).
- **Fecha:** 2026-10-05.
- **Documentos de referencia:** `apps/api/routers/piezas.py` (PATCH #31 — aquí vivirá la lógica), `apps/api/models.py` (`Order`, `Piece`), `apps/api/schemas.py` (`PedidoCreate.piezas` con `min_length=1`, `PiezaResponse`, `EstadoPedido`, `EstadoPieza`), `apps/api/routers/pedidos.py` (patrón `db.get`), `apps/api/database.py` (`get_db`), `apps/api/test_piezas.py` (patrón de tests y fixtures), `apps/api/test_pedidos.py` (`test_422_sin_piezas` — pedidos vacíos no son creables), `docs/planning/PLAN-#31.md` (diseño del PATCH), `docs/planning/DECISIONES-MVP-2026-10-05.md` (D5), `docs/planning/WORKFLOWS.md` (flujo y conventional commits).
- **Stack:** FastAPI + SQLAlchemy 2.0; tests con SQLite in-memory (`StaticPool`) + `TestClient`; pytest; Ruff (`apps/api/ruff.toml`: line-length 100, select E/F/I/B/UP/RUF).
- **Medidas:** no aplica — esta tarea no manipula medidas (solo estados); `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` y la política de pulgadas de D2/D7 no se ven afectadas.
- **Interfaz:** no hay interfaz en #33 (backend puro); la revisión móvil/tablet no aplica. El vendedor "ve" el cambio cuando exista la consulta de pedidos (límite documentado en §5 y §10).

---

## 1. Objetivo y alcance exacto

### Qué hace
- Propagar el estado de las piezas al pedido: cuando el `PATCH /piezas/{id}/completar` (#31) completa una pieza, reevalúa el progreso del pedido padre **en la misma transacción** y actualiza `pedidos.estado`:
  - todas las piezas del pedido `completado` (count de pendientes == 0) → `pedido.estado = "completado"` (**"Listo para entrega"** por D5);
  - si no, y el pedido está `pendiente` → `en_proceso` (primera pieza completada, D5).
- **Checklist de #33 cubierto:**
  - [x] *"Programar un evento o función en el backend que escuche los cambios de estado de las piezas (gatillado por HU-09)"* → **función** dentro de la transacción del PATCH (§2, decisión D-33.1: el checklist ofrece "evento **o función**"; la función es la opción válida elegida).
  - [x] *"Lógica condicional: Si count(piezas_pendientes) == 0, actualizar estado_pedido = 'Listo'"* → reconteo agregado sobre las piezas hijas + transición (§3). `'Listo'` se materializa como `completado` (D5).
- **Ítems de Testing de #33 cubiertos:** "Completar N-1 piezas y verificar que el pedido siga 'En Proceso'" (§7, caso T1) y "Completar la última pieza y verificar cambio a 'Listo'" (§7, caso T2).

### Qué NO hace (YAGNI, explícito)
- **No** implementa un evento asíncrono, cola, broker, tabla de eventos ni worker (justificación en §2).
- **No** implementa recursión sobre árboles de componentes: el modelo es plano 1:N (`pedidos`→`piezas`, sin subpiezas en el ERD-FASE1); "recursivo" se interpreta como verificación exhaustiva de **todas** las piezas hijas (§2.1).
- **No** agrega endpoint `GET /pedidos`, listado de pedidos, UI del vendedor, notificaciones, WSS, ni transición de pieza a `en_corte` (fuera de #33; #32 es la UI del operario y no depende de este código).
- **No** modifica `models.py`, `schemas.py` ni migraciones Alembic: no hay cambio de esquema (los CHECKs de `pedidos.estado` ya admiten `completado`; `updated_at` ya existe con `onupdate`).
- **No** resucita pedidos `cancelado` (§3.3, decisión D-33.4).
- **No** toca `apps/ventas-pwa`, `apps/taller-pwa`, `infra/` ni `README.md`.

---

## 2. Dónde y cómo vive la lógica

### 2.0 Decisión D-33.1 — función sincrónica en la transacción del PATCH (no un evento aparte)
El checklist de #33 dice *"Programar un evento **o función**"*. Se elige **función**, ejecutada dentro de la misma transacción de `PATCH /piezas/{id}/completar` (`apps/api/routers/piezas.py`), por:
1. **Consistencia atómica:** pieza y pedido se comprometen (o revierten) juntos. Con un evento/cola habría una ventana en que la pieza está `completado` pero el pedido aún no refleja el 100% — exactamente la incertidumbre que HU-13 elimina para el vendedor.
2. **Simplicidad:** hoy existe **un único escritor** del estado `completado` de piezas (el endpoint #31). Un evento/cola añade broker, tabla outbox, worker, reintentos y puntos de fallo sin beneficio observable en esta fase.
3. **Gatillado por HU-09:** HU-09 (trazabilidad de estado de piezas) se materializa en este endpoint, que es el punto único de transición a `completado`; la propagación se dispara ahí, determinísticamente.

> Nota de diseño anticipada: si aparece un **segundo escritor** de estados de pieza (p. ej. endpoint de transición a `en_corte`, WSS del Taller en #36/#37), extraer la lógica de §3 a un servicio compartido `_sincronizar_estado_pedido(db, pedido_id)` y llamarlo desde ambos. En #33 se implementa in-line en el router, homogéneo al estilo actual de `routers/`.

### 2.1 Interpretación de "recursivo" (criterio HU-13)
La HU-13 pide "validar recursivamente el estado de todas las piezas hijas". El modelo de datos (`apps/api/models.py`, ERD-FASE1) es **plano**: `Order.pieces` es 1:N directo; `Piece` no tiene hijos. Por tanto "recursivo" se interpreta como **agregación exhaustiva sobre todas las piezas hijas del pedido** (progreso = 100% ⇔ ninguna hija sin completar), no como recorrido de árbol. Se documenta aquí para el Revisor: no hay niveles más profundos que validar. Si un ERD futuro introduce kits/subpiezas, esta función deberá generalizarse (riesgo R-33.2, §10).

---

## 3. Lógica exacta

### 3.1 Pseudocódigo (para `apps/api/routers/piezas.py`)

```python
# imports a añadir en routers/piezas.py: Order, select, func
from sqlalchemy import func, select
from models import Order, Piece

@router.patch("/piezas/{id}/completar", response_model=PiezaResponse)
def completar_pieza(id: uuid.UUID, db: Session = Depends(get_db)) -> Piece:
    pieza = db.get(Piece, id)
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")

    # #33 / HU-13: bloqueo pesimista de la fila del pedido para serializar
    # PATCH concurrentes sobre piezas del mismo pedido (§4). En SQLite es no-op.
    pedido = db.execute(
        select(Order).where(Order.id == pieza.pedido_id).with_for_update()
    ).scalar_one()

    pieza.estado = "completado"  # 31 / HU-02, HU-09 (idempotente por convergencia)
    pieza.updated_at = datetime.now(timezone.utc)
    db.flush()  # #33: persiste la pieza DENTRO de la transacción para que el
                # reconteo la vea; commit/rollback son conjuntos pieza↔pedido.

    # #33 / HU-13: progreso del pedido = 100% ⇔ 0 piezas hijas sin completar.
    pendientes = db.scalar(
        select(func.count())
        .select_from(Piece)
        .where(Piece.pedido_id == pedido.id, Piece.estado != "completado")
    )

    if pedido.estado == "cancelado":
        pass  # D-33.4: no resucitar un pedido cancelado (§3.3)
    elif pendientes == 0:
        pedido.estado = "completado"  # D5: "Listo para entrega"
    elif pedido.estado == "pendiente":
        pedido.estado = "en_proceso"  # D5: primera pieza completada
    # else: pedido en_proceso con piezas pendientes → sin cambio.
    # Asignar el mismo valor no marca dirty en SQLAlchemy: re-PATCH idempotente
    # nunca degrada ni re-escribe el pedido (§3.2).

    db.commit()
    db.refresh(pieza)
    return pieza
```

Notas:
- `pedido.updated_at` avanza solo cuando el estado cambia: el modelo ya define `onupdate=func.now()` (`models.py:113-117`), aplicado por el ORM en el UPDATE — no requiere código extra. Los tests pueden verificarlo (§7, caso T9).
- El reconteo es **agregado en BD** (`SELECT count(*) ... WHERE estado <> 'completado'`), no `len(order.pieces)` en memoria: evita depender del identity map/sesión y es idéntico en SQLite y PostgreSQL.
- `with_for_update()` sobre `select(Order)` se emite en PostgreSQL y es ignorado silenciosamente por el dialecto SQLite (portabilidad del código entre tests y producción).

### 3.2 Casos borde
| Caso | Comportamiento definido | Justificación |
|---|---|---|
| **Pieza ya `completado` (re-PATCH idempotente)** | 200; `pieza.estado` sigue `completado`; `updated_at` se refresca; el reconteo decide el pedido: si el pedido ya está `completado`, **no cambia** (asignar igual valor no genera UPDATE). **Nunca degrada** el pedido a `en_proceso`/`pendiente` — el estado del pedido solo avanza. | Idempotencia por convergencia (decisión #31): el Taller puede reintentar sin 409; la propagación es convergente, no una transición estricta. |
| **Pedido sin piezas** | Inalcanzable por la API: `PedidoCreate.piezas` tiene `min_length=1` (`schemas.py:48`) y `POST /pedidos` devuelve 422 con lista vacía (`test_pedidos.py::test_422_sin_piezas`); no existe endpoint DELETE de piezas. Si ocurriera (dato manual), la vacuidad (`count == 0`) daría `completado`. | Documentado, no se agrega caso especial (YAGNI); si un futuro endpoint borra piezas, revisar entonces. |
| **Piezas de otros pedidos** | El reconteo filtra por `Piece.pedido_id == pedido.id`; ningún otro pedido se lee ni se escribe. | Aislamiento por pedido; test T5 lo verifica. |
| **Pieza en `en_corte` completada** | Transición válida (`en_corte → completado` no se valida, decisión #31); la pieza cuenta como completada para el progreso. | El endpoint completa "desde cualquier origen". |
| **Pedido ya `completado` con pieza pendiente** (inconsistencia manual) | PATCH de esa pieza → `pendientes == 0` → `completado` (ya lo estaba; sin cambio). No degrada. | Convergencia segura. |

### 3.3 Decisión D-33.4 — pedidos `cancelado` no se resucitan
Si `pedido.estado == "cancelado"`, la pieza **sí** se completa (su transición es independiente y trazable por HU-09) pero el pedido **permanece `cancelado`**: las ramas de transición están protegidas por la guarda. Justificación: un pedido cancelado no debe volver a "listo para entrega" por una pieza tardía (riesgo de llamar al cliente por un trabajo que ya no quiere); reactivar un pedido cancelado es una operación explícita de negocio que no existe en el MVP. **Política de reactivación: decisión de negocio pendiente** (no consta en DECISIONES-MVP-2026-10-05) — se registra como pregunta no bloqueante (§10, R-33.1) porque el comportamiento conservador por defecto es seguro y el checklist de #33 no lo cubre.

---

## 4. Concurrencia (dos PATCH simultáneos sobre piezas del mismo pedido)

**Riesgo sin protección:** T1 y T2 completan las dos últimas piezas de un pedido. Si ambas transacciones cuentan antes del commit de la otra, cada una ve ≥1 pendiente → ambas dejan el pedido en `en_proceso` → el pedido queda **atascado** aunque el progreso sea 100% (nunca llega otra pieza que lo corrija).

**Garantía (diseño §3.1):**
1. **Bloqueo pesimista de fila** sobre `pedidos` (`with_for_update()`), adquirido **antes** de modificar la pieza y de contar: serializa las transacciones por pedido. El segundo PATCH espera el commit del primero.
2. En PostgreSQL con **READ COMMITTED** (aislamiento por defecto; no se requiere SERIALIZABLE), al reanudar, el segundo PATCH ejecuta sus sentencias con snapshot fresco: su `db.flush()` persiste su pieza y el `SELECT count(*)` **ve el commit del primero** → cuenta 0 → escribe `completado`.
3. **Exactamente una vez:** solo la transacción que observa `pendientes == 0` escribe el estado `completado`; asignar un estado igual al actual no marca el objeto dirty (sin UPDATE redundante). No se necesita re-lectura post-commit ni lenguaje de compensación.
4. **Sin deadlocks:** el orden de bloqueo es consistente (fila `pedidos` → fila `piezas`) en todos los PATCH. Dos PATCH sobre la **misma** pieza se serializan por el UPDATE de la fila pieza.
5. **Tests (SQLite):** `with_for_update()` es no-op y SQLite serializa escrituras a nivel de base de datos; `TestClient` con la sesión compartida es secuencial, por lo que la carrera **no se ejerce en pytest**. La garantía es de diseño; se documenta como límite (R-33.3) y, si en producción (PostgreSQL, un operario por pedido en el MVP) apareciera un pedido atascado, verificar con dos sesiones concurrentes contra PostgreSQL antes de cambiar el aislamiento.

Alternativa considerada y no elegida: `UPDATE pedidos SET estado='completado' WHERE id=:pid AND NOT EXISTS (SELECT 1 FROM piezas WHERE pedido_id=:pid AND estado <> 'completado')` — condición evaluada en BD sin bloqueo previo; correcta pero más opaca y no cubre la transición a `en_proceso` con la misma claridad. Rechazada por legibilidad y trazabilidad con la decisión D5.

---

## 5. Contrato de respuesta

**Decisión: el PATCH sigue devolviendo `PiezaResponse` sin cambios** (`schemas.py`, sin modificaciones; `response_model=PiezaResponse`). Justificación:
- **YAGNI:** el consumidor directo del PATCH es el Taller/Operario, que solo necesita la pieza confirmada (contrato ya establecido por #31 y consumido por `apps/taller-pwa`).
- El vendedor "ve" el cambio **a través del estado del pedido** (HU-13): hoy `GET /pedidos` **no existe** — la consulta de pedidos/listado del vendedor es trabajo futuro (§10, R-33.4). El cambio queda visible en BD (`pedidos.estado`, `pedidos.updated_at`) y será expuesto cuando se construya ese endpoint/UI. No se añade un campo `pedido_estado` a la respuesta de pieza: sería contrato nuevo sin consumidor.

---

## 6. Trazabilidad en código (para el Implementador)

- `apps/api/routers/piezas.py` — docstring actualizado: `Tarea #31, Historia de Usuario HU-02/HU-09 — Marcar pieza como completada. #33 / HU-13: propaga el estado del pedido al 100% de piezas.`; comentarios in-line `#33 / HU-13` junto al `with_for_update`, el `flush`, el reconteo y las transiciones; imports nuevos: `Order` (models), `func`, `select` (sqlalchemy).
- `apps/api/main.py` — docstring: añadir línea `#33 / HU-13: propagación de estado de pedido en completar pieza.` (el include de `piezas.router` ya existe).
- `apps/api/test_piezas.py` — docstring: añadir `Tarea #33, HU-13 — Propagación de estado del pedido.`; casos nuevos §7.
- **No** modificar `models.py`, `schemas.py`, `alembic/`, ni `apps/*-pwa`.

---

## 7. Pruebas (pytest, `apps/api/test_piezas.py`)

Andamiaje existente (reutilizar): engine SQLite `:memory:` + `StaticPool`, fixtures `db_session` / `client` / `seed`, helper `_pieza(pedido, producto, estado, operario)`. **Añadir** helper para sembrar N piezas de un pedido, p. ej.:

```python
def _pedido_con_piezas(db_session, seed, n, estados=None):
    """#33 / HU-13: pedido con N piezas; estados por defecto todas 'pendiente'."""
    _, p1, pedido = seed
    estados = estados or ["pendiente"] * n
    piezas = [_pieza(pedido, p1, estado=e) for e in estados]
    db_session.add_all(piezas)
    db_session.commit()
    return pedido, piezas
```

**Verificación de estado de pedido leyendo BD (transversal, ítem de testing de #33):** tras cada PATCH, `db_session.expire_all()` y luego `db_session.get(Order, pedido.id).estado` — nunca asertar solo sobre `r.json()` (la sesión compartida cachea el pedido en el identity map; `expire_all` fuerza la relectura, patrón ya usado en `test_piezas.py:93`).

| # | Test | Preparación | Acción | Aserciones (respuesta + **BD**) | Cobertura |
|---|------|-----------|--------|--------------------------------|-----------|
| T1 | `test_n_menos_1_piezas_pedido_en_proceso` | pedido con **3** piezas `pendiente` | PATCH 2 piezas cualesquiera | 200 ambas, `estado=="completado"`; **BD:** `pedido.estado == "en_proceso"` (no `completado`) | Checklist #33: "Completar N-1 piezas y verificar que el pedido siga 'En Proceso'"; D5 |
| T2 | `test_ultima_pieza_pedido_completado` | pedido con 3 piezas; completar 2 (como T1) | PATCH la **última** | 200; **BD:** `pedido.estado == "completado"` ("Listo" por D5) | Checklist #33: "Completar la última pieza y verificar cambio a 'Listo'"; HU-13 AC2 (100%) |
| T3 | `test_repatch_no_degrada_pedido_completado` | pedido con 1 pieza ya `completado` (pedido `completado`) | PATCH la misma pieza de nuevo | 200; pieza intacta (`operario_asignado`, `ancho_mm`, `cantidad`); **BD:** pedido sigue `"completado"` (no degrada a `en_proceso`) | #33 idempotencia; §3.2 |
| T4 | `test_404_no_altera_pedido` | pedido `pendiente` con 1 pieza | PATCH `uuid.uuid4()` inexistente | 404 `detail=="Pieza no encontrada"`; **BD:** pedido sigue `"pendiente"`; pieza sigue `"pendiente"` | #33; §3.1 |
| T5 | `test_pieza_de_otro_pedido_no_afecta` | pedido A (2 piezas `pendiente`) y pedido B (1 pieza `pendiente`) | PATCH la pieza de B | 200; **BD:** B `"completado"`; **A sigue `"pendiente"`** con sus 2 piezas intactas | #33 aislamiento; §3.2 |
| T6 | `test_pedido_cancelado_no_se_resucita` | pedido `cancelado` con 1 pieza `pendiente` | PATCH la pieza | 200; pieza `"completado"`; **BD:** pedido sigue `"cancelado"` | Decisión D-33.4; §3.3 |
| T7 (recomendado) | `test_primera_pieza_completada_pone_en_proceso` | pedido con 1 pieza `pendiente` | PATCH | 200; **BD:** pedido `"en_proceso"` | D5 (primera pieza → `en_proceso`) |
| T8 (recomendado) | `test_pieza_en_corte_completada_cierra_pedido` | pedido con 2 piezas: una `completado`, otra `en_corte` | PATCH la `en_corte` | 200; **BD:** pedido `"completado"` | Transición `en_corte→completado` válida; §3.2 |
| T9 (recomendado) | `test_updated_at_pedido_avanza_al_transicionar` | pedido `pendiente` con 1 pieza (guardar `pedido.updated_at` previo) | PATCH | 200; **BD:** `pedido.updated_at >= previo` (onupdate del modelo) | Trazabilidad HU-09/HU-13 |

Obligatorios por la issue: **T1 y T2** (ítems de Testing del checklist); **T3, T4, T5** y el patrón de lectura de BD (requeridos por el enunciado de la subtarea); **T6** documenta la decisión D-33.4. T7–T9 recomendados (barato, alta señal).

---

## 8. Comandos exactos para el Implementador y commit

```bash
cd /home/erick/Proyectos/AVAO/apps/api
source .venv/bin/activate        # venv verificada: pytest 9.1.1, ruff 0.16.10

# TDD: escribir/ajustar los tests §7 primero (rojo), luego implementar §3 (verde).
.venv/bin/python -m pytest test_piezas.py -v    # focalizado (T1-T9)
.venv/bin/python -m pytest -q                   # suite completa (21 actuales + nuevos)
.venv/bin/python -m ruff check .                # lint (E,F,I,B,UP,RUF; line-length 100)
.venv/bin/python -m ruff format --check .       # opcional; si falla por formato preexistente, solo reportar
```

**Commit** (conventional commit con trazabilidad, WORKFLOWS.md §3-§4):

```bash
git add apps/api/routers/piezas.py apps/api/test_piezas.py apps/api/main.py docs/planning/PLAN-#33.md
git commit -m "feat(api): propagar pedido a completado al 100% de piezas (#33, HU-13)"
```

Sin push a `main`/`develop`; merge a `develop` vía PR tras revisión (WORKFLOWS.md §1).

---

## 9. Trazabilidad

| Artefacto / decisión | Referencia |
|---|---|
| Este plan `docs/planning/PLAN-#33.md` | Tarea #33 (Subtarea 1: Validación recursiva de progreso), HU-13 (issue #14) |
| Gatillo = función en la transacción del PATCH | Checklist #33 ítem 1 ("evento o función" — se elige función, decisión D-33.1); gatillado por HU-09 (punto único de transición a `completado`, #31) |
| `count(piezas_pendientes) == 0 → estado_pedido = completado` | Checklist #33 ítem 2; HU-13 AC2; **D5** (`completado` = "Listo para entrega", sin migración de vocabulario) |
| Primera pieza → `en_proceso` | D5; checklist #33 testing ("N-1 piezas → sigue En Proceso") |
| Interpretación de "recursivo" como agregación 1:N exhaustiva | HU-13 AC1; modelo plano `Order.pieces` (`models.py:121-126`); §2.1 |
| No resucitar `cancelado` | Decisión D-33.4 (§3.3); política de reactivación pendiente de negocio |
| Concurrencia: `with_for_update` + reconteo en transacción | §4; READ COMMITTED en PostgreSQL; no-op en SQLite (tests secuenciales) |
| Contrato `PiezaResponse` sin cambios | §5 (YAGNI; el vendedor ve el estado vía futura consulta de pedidos) |
| Tests T1/T2 | Ítems de Testing de #33; T3-T5 por enunciado de la subtarea; T6 por D-33.4 |
| Comandos | WORKFLOWS.md §2 paso 5: `apps/api` → `.venv/bin/python -m pytest -q` y Ruff (verificados: pytest 9.1.1, ruff 0.16.10) |

**Dependencias:** depende de #27 (modelos), #29 (patrón router), #31 (el PATCH que se extiende). **No** depende de #32 (UI del operario, frontend). Desbloqueado para implementación inmediata.

---

## 10. Riesgos y límites explícitos

| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **R-33.1 — Política de reactivación de pedidos `cancelado`** (decisión de negocio pendiente, no consta en DECISIONES-MVP) | Si el negocio espera que completar una pieza re-active un pedido cancelado, el comportamiento actual no lo hace | Decisión conservadora D-33.4 (no resucitar). **Pregunta no bloqueante** para el Coordinador/responsable humano; si se requiere reactivación, será un endpoint explícito futuro, no efecto colateral del PATCH. |
| **R-33.2 — Interpretación de "recursivo"** | Si el ERD futuro introduce kits/subpiezas, la agregación plana no cubre niveles profundos | Documentada en §2.1; hoy no existen niveles más profundos (`Piece` no tiene hijos). Revisar al añadir subpiezas. |
| **R-33.3 — Concurrencia real no ejercida en pytest** (SQLite/no-op `FOR UPDATE`, tests secuenciales) | Una carrera en producción podría atascar el pedido en `en_proceso` si el diseño fallara | Garantía por diseño (§4: bloqueo de fila + reconteo post-flush en la misma transacción, READ COMMITTED). En el MVP hay un operario por pedido (riesgo bajo). Si aparece un pedido atascado: reproducir con dos sesiones concurrentes contra PostgreSQL antes de cambiar aislamiento. |
| **R-33.4 — Visibilidad para el vendedor** | El cambio de estado no es visible en ninguna UI/endpoint de consulta de pedidos (`GET /pedidos` no existe) | Límite de alcance: #33 cumple la HU-13 en backend (estado en BD); la consulta/listado de pedidos es trabajo futuro (#36/#37 o HU propia). Documentado en §5. |
| **R-33.5 — Alcance del checklist ("evento o función")** | Si el Revisor/Coordinador exige un evento real (tabla outbox/broker), este plan se desvía | Decisión D-33.1 justificada (atomicidad + simplicidad + escritor único). Escalable al humano antes de implementar; no bloquea (la función cumple el checklist literal). |
| **R-33.6 — Scope creep** | Tentación de agregar `GET /pedidos`, notificaciones, transición a `en_corte`, o WSS | Todos fuera de #33 (§1); resistir en revisión. |
| **R-33.7 — Segundo escritor de estados de pieza en el futuro** | La propagación debería vivir en un servicio compartido, no duplicarse | Nota de diseño §2.0: extraer `_sincronizar_estado_pedido(db, pedido_id)` cuando aparezca otro endpoint que mute estados de pieza. |

---

*Fin del plan. Entregado por el rol Planificador (WORKFLOWS.md §2) para ejecución por el Implementador en `feature/33-validacion-recursiva-progreso`. Estado del tablero verificado: issue #33 **open** (leída por API el 2026-10-05); campos de proyecto (Prioridad Media, Épica 5) según MEMORY.md — no se modificó el tablero.*
