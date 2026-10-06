# PLAN #35 — Medidas en pulgadas con precisión 1/16 (cambio de mm a in)

- **Tarea:** #35 — "Medidas en pulgadas con precisión 1/16 — cambio de mm a in" (issue de GitHub: <https://github.com/ErickRamos37/AVAO/issues/35>)
- **Historias de Usuario:** HU-01 (#1) — "Registrar el pedido del cliente" ("...ingresar medidas (largo y ancho) y cantidad de piezas" con *medidas exactas*); #35 es **subissue de #1**, Épica 1 (#18).
- **Rama:** `feature/35-medidas-pulgadas` (por crear desde `develop`; rama actual en esta sesión: `feature/cierre-auditoria-38`).
- **Fecha:** 2026-10-05
- **Decisiones vigentes aplicables (OBLIGATORIAS):** `docs/planning/DECISIONES-MVP-2026-10-05.md` **D2** (unidad canónica = pulgada decimal; `NUMERIC(10,4)`; precisión de corte 1/16 in; renombrar `*_mm` → `*_in`; excepción de espesor; frontera de presentación) y **D7** (toda medida de cualquier HU se maneja en pulgadas; la API no habla mm ni metros).
- **Documentos de referencia:** `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` (§1 unidad, §4 decisiones MVP), `docs/design/ERD-FASE1.md` (§1, §4, §5, §6.2), `apps/api/{models,schemas,database}.py`, `apps/api/routers/{pedidos,tareas,piezas}.py`, `apps/api/main.py`, migración `apps/api/alembic/versions/95354a0cc046_create_tables_for_pedidos_27.py`, `apps/api/test_{pedidos,tareas,piezas,main}.py`, `infra/seed.sql`, `infra/docker-compose.yml`, `apps/ventas-pwa/src/**` (db, services, utils, constants, components, test), `apps/taller-pwa/src/**` (components, services, test), `docs/planning/AUDITORIA-CIERRES-2026-10-05.md` (patrón de verificación Alembic en PostgreSQL 17 desechable), `docs/planning/PLAN-#38.md` (formato), `docs/planning/WORKFLOWS.md` (§2 roles, §4 conventional commits).
- **Estado del tablero:** la issue #35 **sí fue verificada** vía API de GitHub el 2026-10-05: abierta, sin etiquetas, `has_parent: true` → #1 "HU-01: Registrar el pedido del cliente" (abierta). El tablero GitHub Projects (#4) **no fue consultado** en esta sesión; su estado no fue verificado.

---

## 1. Objetivo y alcance exacto

### Qué hace (#35 / HU-01)

Cambia la **unidad canónica de todo el sistema** de milímetros a **pulgadas decimales**, con **precisión exacta de 1/16 in (0.0625)**, en las tres afectadas por la issue ("La precisión también afecta a Ventas, API y Taller"):

1. **API:** columnas `piezas.ancho_mm/largo_mm` y `productos.espesor_mm` → `*_in` `NUMERIC(10,4)`; renombrar en modelos SQLAlchemy, esquemas Pydantic y contratos JSON (`POST /pedidos`, `GET /tareas/pendientes`, `PATCH /piezas/{id}/completar`); cuantización de entrada al múltiplo de 1/16 in más cercano para cortes (sin rechazo; D-#35-4).
2. **Migración Alembic** nueva (después de `95354a0cc046`): conversión de datos existentes `*_mm` → `*_in` (`/25.4`) con política de redondeo definida (§4.2) y `downgrade` inverso documentado.
3. **Ventas PWA:** Dexie (schema v2 con upgrade de datos), `syncService` (payload `*_in`), `validarPedido` (reglas en pulgadas; la cuantización a 1/16 ocurre en `PiezaRow`), catálogo (`espesor_in`), formulario y etiquetas UI.
4. **Taller PWA:** `CorteCard` muestra `ancho_in x largo_in in`; tests.
5. **Seed de desarrollo** (`infra/seed.sql`) en pulgadas.
6. **Documentación viva:** `docs/design/ERD-FASE1.md`, notas de `ARCHITECTURE.md` y `MEMORY.md`.
7. **Prueba de ida y vuelta** exigida por la issue: pulgadas decimales → JSON → API → BD → respuesta = igualdad exacta (§7.1).

### Qué NO hace (YAGNI, explícito)

- **No** implementa la conversión decimal → fracción visual (`10 1/16 in`): es **post-MVP, tarea #37** (criterio de la issue: "Conversión decimal → fracción visual se implementará en tarea posterior al MVP"). El cálculo exacto y la presentación fraccionaria quedan separados.
- **No** implementa las fórmulas de descuento de Ventana California (`docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` §3) ni estimación de barras (#34/D6): consumen esta unidad canónica pero son otras tareas.
- **No** añade ventanas de compatibilidad dual (`ancho_mm` + `ancho_in` simultáneos): cambio rompiente con despliegue conjunto (§6.2). Dual-running = YAGNI en MVP sin producción.
- **No** añade versionado de API (`/v1/`), idempotencia (#39), catálogo/clientes por endpoint (#40), JWT (HU-03), ni CHECK de BD para 1/16 (§2 D-#35-9).
- **No** toca `routers/tareas.py`, `routers/piezas.py`, `main.py`, `database.py`, `tareasApi.js`, `mapeoApi.js` (no referencian medidas; §5.6).
- **No** reescribe planes/reviews históricos (`PLAN-#27`…`PLAN-#38`, `REVIEW-*`): son registro histórico; sus referencias a `*_mm` datan de sus iteraciones.

---

## 2. Decisiones de diseño

> D2 y D7 de `DECISIONES-MVP-2026-10-05.md` son **vigentes y obligatorias**; este plan las concreta y define los puntos que D2 deja explícitamente al plan #35 (política de entrada, redondeo de datos existentes, espesor).

### D-#35-1 — Nomenclatura: sufijo `_in` (vigente por D2)

`ancho_mm` → **`ancho_in`**, `largo_mm` → **`largo_in`**, `espesor_mm` → **`espesor_in`**, en esquema SQL, modelos, esquemas Pydantic, contratos JSON, Dexie y PWAs.

**Justificación:** (a) D2 lo fija ("Renombrar `*_mm` → `*_in`"); (b) conserva la convención existente de sufijo de unidad (`_mm`), que es corta, legible en código, JSON y SQL, y no colisiona con palabras reservadas de PostgreSQL ni de Python (`in` es keyword, pero `ancho_in` es un identificador válido); (c) alternativas (`_pulg`, `_inches`, `_dec`) son más largas o inconsistentes con el patrón del código.

### D-#35-2 — Unidad, escala y rango canónicos (vigente por D2)

- **Unidad canónica: pulgada decimal** en *todas* las medidas: `piezas.ancho_in/largo_in`, `productos.espesor_in` y cualquier medida futura (incluidos los tramos de #34/D6).
- **Escala de persistencia: `NUMERIC(10,4)`** (10 dígitos totales, 4 decimales). `NUMERIC(10,2)` **no** conserva `0.0625` (lo redondea a `0.06`); `NUMERIC(10,4)` conserva **exactamente** todo múltiplo de 1/16 in, porque `k × 0.0625 = k × 625 / 10000` siempre cabe en 4 decimales.
- **Rango:** máximo `999999.9999` in (≈ 25.4 m; una barra comercial de 6 m = 236.22 in cabe holgada). El **mayor múltiplo de 1/16 válido** es `999999.9375` in.
- **Factor de conversión:** 1 in = 25.4 mm (exacto, definición internacional).

### D-#35-3 — Espesor: decimal libre (excepción vigente por D2)

`productos.espesor_in` es **propiedad del material, no medida de corte**: se persiste como decimal libre a escala 4, **sin** cuantizar a 1/16. Justificación: el vidrio se comercializa por espesor nominal en mm (6 mm ≈ 0.2362 in, que **no** es múltiplo de 1/16); cuantizarlo a 0.25 in alteraría la especificación del material. Es la recomendación del Coordinador en D2 ("el plan define si se cuantiza o se deja libre" → **libre**). Consecuencia: la cuantización de 1/16 se aplica **solo** a `PiezaCreate.ancho_in/largo_in`, nunca a `espesor_in`.

### D-#35-4 — Política de entrada: **cuantizar al 1/16 más cercano** (RESUELTO por el responsable humano, 2026-10-05 — DECISIONES §Resueltas.1)

**Decisión (b), aplicada:** la API **cuantiza** `ancho_in`/`largo_in` al múltiplo de 1/16 in más cercano en lugar de rechazar con 422. Justificación (del responsable): el flexómetro del taller solo lee 1/16 in (`MEDIDAS-VENTANA-CALIFORNIA.md` §1), por lo que toda medida capturada *pretende* ser un múltiplo de 1/16; un valor como `10.51` in se interpreta como el múltiplo más cercano (`10.5` = 10 1/2) y **no** debe bloquear la captura del pedido:

1. **No hay rechazo**: la captura nunca falla por unidad; el pedido entra a la cola y sincroniza.
2. **Cuantización en dos capas (coherentes):** Ventas cuantiza **en captura** (`PiezaRow`, en `onBlur` — decisión del Coordinador: no interrumpe la escritura) y muestra el valor efectivo al operario (transparencia: ve `10.5` aunque tecleó `10.51`); la API cuantiza de nuevo como *defense-in-depth* (idempotente: cuantizar un múltiplo de 1/16 lo deja igual). Local y servidor conservan el mismo valor.
3. **Excepción de espesor intacta** (D-#35-3): `espesor_in` sigue decimal libre, sin cuantizar.
4. **Datos heredados** (migración §4.2): misma política de cuantización, ahora coherente con la entrada.

*Nota de revisión:* la propuesta original del Planificador era **(a) rechazar con 422** por HU-01 "medidas exactas"; el responsable humano la revocó el 2026-10-05 eligiendo (b). Queda documentada aquí y en `DECISIONES-MVP-2026-10-05.md` §Resueltas.1.

### D-#35-5 — Política de redondeo de datos existentes (migración)

- **Cortes (`piezas.ancho_in/largo_in`):** cuantizar al múltiplo de 1/16 **más cercano**: `ROUND(v_mm / 25.4 / 0.0625) * 0.0625` (PG: mitad se aleja de cero). Ejemplo: 24 mm → 0.94488… in → **0.9375 in** (15/16); 36 mm → 1.41732… in → **1.4375 in** (1 7/16).
- **Espesor (`productos.espesor_in`):** decimal libre; la escala 4 redondea: 6 mm → **0.2362**, 10 mm → **0.3937**, 4 mm → **0.1575**, 20 mm → **0.7874**, 2 mm → **0.0787**.
- Justificación: los datos actuales son **solo de desarrollo** (seed + pruebas locales; no hay producción — §10.1), por lo que la pérdida por cuantización es despreciable y queda documentada aquí. Los valores de ejemplo **no caen en empate** de redondeo (ninguno tiene 5ª cifra exactamente 5), así que no hay ambigüedad de modo de redondeo.

### D-#35-6 — Contrato rompiente y política de versión (detalle en §6)

El renombrado de campos JSON (`ancho_mm` → `ancho_in` en request y responses) es un **cambio rompiente**. Política: **sin versionado de API ni ventana dual**; **despliegue conjunto y atómico** de API + Ventas PWA + Taller PWA en el mismo tren de release. El modo de fallo es **seguro y ruidoso** (Pydantic ignora claves extra y exige `ancho_in`: un bundle viejo recibe 422 y el pedido queda `pendiente` en Dexie, nunca se corrompe).

### D-#35-7 — Dexie: bump de versión 1 → 2 **con upgrade de datos** (no reset)

Renombrar propiedades indexadas (`ancho_mm` → `ancho_in` en el schema de `piezas`) exige `db.version(2)`. Se decide **proveer función `upgrade()`** que convierte filas v1 (mm → in, cortes cuantizados a 1/16 vía `mmAInCorte`), en lugar de borrar la BD de dev: preserva datos de desarrollo, ejercita el camino de upgrade (patrón necesario para futuras migraciones Dexie) y cuesta ~10 líneas. En tests (fake-indexeddb) la DB nace en v2 y `beforeEach` limpia tablas.

### D-#35-8 — Nombres comerciales de productos conservan "mm" como etiqueta

`nombre` de producto (ej. "Vidrio claro 6mm") es una **etiqueta comercial**, no un dato de medida: el vidrio se vende por espesor nominal en mm. Se conservan los nombres tal cual y se convierte solo el campo `espesor_in`. Observación para #40: el catálogo local (`catalogoProductos.js`) trae `espesor_mm: 20` para el perfil mientras `infra/seed.sql` usa `NULL` — inconsistencia **preexistente** que este plan conserva (0.7874 vs NULL) y marca para resolver cuando el catálogo venga de `GET /productos`.

### D-#35-9 — Cuantización de 1/16 en capa de esquema (Pydantic), **no** como CHECK de BD

Justificación: (a) la transformación vive en el esquema, coherente con el patrón vigente del código; (b) la excepción de espesor vive en otra tabla, así que un CHECK no sería global de todas formas; (c) el CHECK `> 0` (que sí es de BD) se conserva y se reescribe solo al renombrar la columna. Un CHECK de cuantización en BD queda como opción abierta (§11.4).

### Definiciones (#35 / HU-01)

| Término | Valor |
|---|---|
| Paso mínimo (1/16 in) | `0.0625` in |
| Escala de persistencia | `NUMERIC(10,4)` — máx. `999999.9999` in |
| Mayor múltiplo de 1/16 válido | `999999.9375` in |
| Factor mm→in | `/ 25.4` (exacto) |
| Umbral de desbordamiento de datos heredados | `25,399,999.99` mm (= `999999.9999 × 25.4`); filas mayores no caben en `NUMERIC(10,4)` (§4.4, guarda) |

---

## 3. Representación, modelos y contrato

### 3.1 Modelos SQLAlchemy (`apps/api/models.py`) — antes → después (#35 / HU-01)

| Modelo | Campo ANTES | Campo DESPUÉS |
|---|---|---|
| `Piece` (`piezas`) | `ancho_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)` | `ancho_in: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)` |
| `Piece` | `largo_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)` | `largo_in: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)` |
| `Product` (`productos`) | `espesor_mm: Mapped[Decimal \| None] = mapped_column(Numeric(10, 2))` | `espesor_in: Mapped[Decimal \| None] = mapped_column(Numeric(10, 4))` |

- `__table_args__`: `CheckConstraint("ancho_in > 0", name="ancho_positivo")`, `CheckConstraint("largo_in > 0", name="largo_positivo")`, `CheckConstraint("espesor_in > 0", name="espesor_positivo")` — **los nombres de constraint no cambian** (no contienen `_mm`), solo la expresión.
- El resto del modelo (`cantidad`, `estado`, `operario_asignado`, FKs, índices, timestamps) no se toca.

### 3.2 Esquemas Pydantic (`apps/api/schemas.py`) — antes → después (#35 / HU-01)

| Esquema | Campo ANTES | Campo DESPUÉS |
|---|---|---|
| `PiezaCreate` | `ancho_mm: Decimal = Field(gt=0, max_digits=10, decimal_places=2)` | `ancho_in: Decimal = Field(gt=0, max_digits=10, decimal_places=4)` |
| `PiezaCreate` | `largo_mm` (idem) | `largo_in` (idem) + **cuantizador a 1/16** (§3.4) |
| `PiezaResponse` | `ancho_mm: Decimal`, `largo_mm: Decimal` | `ancho_in: Decimal`, `largo_in: Decimal` |
| `TareaPendienteResponse` | `ancho_mm: Decimal`, `largo_mm: Decimal` | `ancho_in: Decimal`, `largo_in: Decimal` |

`PedidoCreate` no cambia (contiene `piezas: list[PiezaCreate]`). `max_digits=10, decimal_places=4` rechaza con 422: más de 4 decimales, y valores fuera de rango (ej. `1000000.0000`).

### 3.3 Routers

- `routers/pedidos.py`: constructor `Piece(producto_id=…, ancho_in=p.ancho_in, largo_in=p.largo_in, cantidad=…, …)`.
- `routers/tareas.py`, `routers/piezas.py`, `main.py`: **sin cambios** (no referencian columnas de medidas; §5.6).

### 3.4 Cuantizador a 1/16 (nuevo en `schemas.py`) (#35 / HU-01)

```python
# apps/api/schemas.py — #35 / HU-01
PASO_PULGADA = Decimal("0.0625")  # 1/16 in: precisión mínima del taller


class PiezaCreate(BaseModel):
    producto_id: uuid.UUID
    ancho_in: Decimal = Field(gt=0, max_digits=10, decimal_places=4)
    largo_in: Decimal = Field(gt=0, max_digits=10, decimal_places=4)
    cantidad: int = Field(gt=0)
    operario_asignado: str | None = Field(default=None, max_length=100)

    @field_validator("ancho_in", "largo_in", mode="after")
    @classmethod
    def _cuantizar_1_16(cls, v: Decimal) -> Decimal:
        """#35 / HU-01 (D-#35-4): cuantiza al múltiplo de 1/16 más cercano.

        El flexómetro del taller solo lee dieciseisavos, así que toda
        medida capturada *pretende* ser múltiplo de 1/16 (decisión del
        responsable: cuantizar, no rechazar). Aritmética exacta en
        ``Decimal``: ``decimal_places=4`` ya garantizó escala ≤ 4 y
        ``v / PASO_PULGADA`` es exacto; se redondea al entero más
        cercano (``ROUND_HALF_UP``: mitad se aleja de cero, coherente
        con la migración §4.2) y se vuelve a escalar. Cuantizar un
        valor ya múltiplo de 1/16 lo deja igual (idempotente).
        """
        pasos = (v / PASO_PULGADA).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return pasos * PASO_PULGADA
```

> `espesor_in` **no** lleva este cuantizador (excepción D-#35-3). `Product` no tiene endpoint de creación en el MVP (solo seed), así que la única puerta de `espesor_in` es el CHECK `> 0` de BD.
>
> **Respuesta transparente:** como la cuantización ocurre en el validador, `PiezaResponse` devuelve el valor **ya cuantizado** (ej. entrada `"10.51"` → respuesta `"10.5000"`): el cliente ve la medida efectiva que el taller cortará. Ventas hace la misma cuantización en captura (§5.3), así que local y servidor coinciden.

---

## 4. Migración Alembic

### 4.1 Archivo y encadenamiento (#35 / HU-01)

- **Archivo nuevo:** `apps/api/alembic/versions/<rev>_pulgadas_decimales_35.py`.
- **Generación:** `./.venv/bin/alembic revision -m "medidas en pulgadas decimales #35"` (crea el esqueleto con `down_revision` correcto = head actual `95354a0cc046`) y luego editar con las operaciones de §4.3. El revision ID queda registrado por el Implementador en el commit.
- `down_revision = "95354a0cc046"`; `branch_labels = None`; `depends_on = None`.
- El archivo va bajo `alembic/versions/*`, exento de E501/UP007/UP035 en `ruff.toml` (ya configurado).

### 4.2 Política de conversión de datos existentes (D-#35-5)

| Tabla.columna | Conversión | Redondeo |
|---|---|---|
| `piezas.ancho_mm`, `piezas.largo_mm` | `v / 25.4` | **Cuantizar a 1/16 más cercano**: `ROUND(v / 25.4 / 0.0625) * 0.0625` |
| `productos.espesor_mm` | `v / 25.4` | Decimal libre; escala 4 redondea (PG: mitad alejada de cero) |

- **Guarda previa obligatoria** (§4.4, paso 0): ninguna fila puede superar `25,399,999.99` mm o el `ALTER COLUMN TYPE` a `NUMERIC(10,4)` desborda. En la práctica es imposible para piezas de vidrio, pero se verifica.
- **Downgrade con pérdida documentada:** `ancho_in * 25.4` a escala 2. Ejemplo: `24 mm → 0.9375 in → (downgrade) → 23.81 mm`. Aceptable: no hay producción (§10.1); el downgrade existe para reversibilidad de esquema, no para recuperación de datos.

### 4.3 `upgrade()` y `downgrade()` (#35 / HU-01)

```python
"""medidas en pulgadas decimales con precision 1/16 in (#35, HU-01)

Unidad canonica = pulgada decimal (DECISIONES-MVP D2/D7).
- piezas.ancho_mm/largo_mm y productos.espesor_mm -> *_in
- NUMERIC(10,2) -> NUMERIC(10,4): conserva 0.0625 in exacto (NUMERIC(10,2) no).
- Conversion: valor_mm / 25.4.
  * piezas (cortes): cuantizados al multiplo de 1/16 mas cercano (§4.2).
  * productos.espesor: decimal libre (excepcion D2: propiedad del material).
- Los CHECK (> 0) se reescriben solos al renombrar la columna en PostgreSQL;
  los nombres de constraint no contienen "_mm", no hay que renombrarlos.
- downgrade: x 25.4 con escala 2 — perdida de precisión documentada
  (ej. 10.0625 in -> 255.59 mm; 24 mm -> 0.9375 in -> 23.81 mm).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "<ID_GENERADO>"  # alembic revision -m "medidas en pulgadas decimales #35"
down_revision: str | Sequence[str] | None = "95354a0cc046"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """#35 / HU-01: migra medidas de mm a pulgadas decimales (NUMERIC(10,4))."""
    # piezas (cortes): conversion + cuantizacion a 1/16 (politica §4.2).
    # Orden: primero TYPE (el USING referencia el nombre viejo), luego RENAME.
    op.alter_column(
        "piezas", "ancho_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=False,
        postgresql_using="ROUND(ancho_mm / 25.4 / 0.0625) * 0.0625",
    )
    op.alter_column(
        "piezas", "ancho_mm",
        new_column_name="ancho_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        existing_nullable=False,
    )
    op.alter_column(
        "piezas", "largo_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=False,
        postgresql_using="ROUND(largo_mm / 25.4 / 0.0625) * 0.0625",
    )
    op.alter_column(
        "piezas", "largo_mm",
        new_column_name="largo_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        existing_nullable=False,
    )
    # productos.espesor: decimal libre (excepcion D2); la escala 4 redondea.
    op.alter_column(
        "productos", "espesor_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
        postgresql_using="espesor_mm / 25.4",
    )
    op.alter_column(
        "productos", "espesor_mm",
        new_column_name="espesor_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )


def downgrade() -> None:
    """#35 / HU-01: inverso a mm con perdida de precision documentada (§4.2)."""
    op.alter_column(
        "piezas", "ancho_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
        postgresql_using="ancho_in * 25.4",
    )
    op.alter_column(
        "piezas", "ancho_in",
        new_column_name="ancho_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        "piezas", "largo_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
        postgresql_using="largo_in * 25.4",
    )
    op.alter_column(
        "piezas", "largo_in",
        new_column_name="largo_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        "productos", "espesor_in",
        existing_type=sa.Numeric(precision=10, scale=4),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=True,
        postgresql_using="espesor_in * 25.4",
    )
    op.alter_column(
        "productos", "espesor_in",
        new_column_name="espesor_mm",
        existing_type=sa.Numeric(precision=10, scale=2),
        existing_nullable=True,
    )
```

Notas de implementación:

- **Dos `alter_column` por columna** (TYPE con `postgresql_using`, luego RENAME) para que el `USING` referencia siempre el nombre vigente; el orden es determinista.
- **Constraints:** PostgreSQL reescribe automáticamente las definiciones de CHECK al renombrar la columna (`ancho_mm > 0` → `ancho_in > 0`); los nombres (`ck_piezas_ancho_positivo`, …) no contienen `_mm` y **no** hay que renombrarlos. Se verifica con `pg_get_constraintdef` (§4.4, paso 2).
- **Índices:** ninguno indexa columnas de medidas; no hay rebuild.
- **Opcional:** `op.execute("COMMENT ON COLUMN piezas.ancho IS '…'")` — comentarios de columna, no obligatorio.
- **Portabilidad:** la migración es para **PostgreSQL** ( dialecto de producción; `postgresql_using` es ignorado por otros dialectos y SQLite no soporta `ALTER COLUMN TYPE`). Los **tests** usan `Base.metadata.create_all` sobre SQLite en memoria, no ejecutan Alembic — la verificación "en SQLite" de #35 es la suite pytest (modelos con `Numeric(10,4)`), y la migración se verifica en PG17 desechable (§4.4). Esta es la interpretación de "verificar upgrade/downgrade en PostgreSQL 17 … y en SQLite para tests".

### 4.4 Verificación de la migración (patrón `AUDITORIA-CIERRES-2026-10-05.md`) (#35 / HU-01)

Contenedor PostgreSQL 17 desechable, contraseña del compose de dev (`avao_dev`), puerto local 55433 para no colisionar con nada:

```bash
# 0) Arrancar y, OPCIONAL (escenario A: datos existentes), crear filas en mm
#    ANTES del upgrade (cliente + producto + pedido + pieza con ancho_mm=24, largo_mm=36)
#    para comprobar la conversión y cuantización (0.9375 / 1.4375) y la guarda de overflow:
docker run --rm -d --name avao-35-pg17 \
  -e POSTGRES_USER=avao -e POSTGRES_PASSWORD=avao_dev -e POSTGRES_DB=avao \
  -p 127.0.0.1:55433:5432 postgres:17
docker exec avao-35-pg17 pg_isready -U avao -d avao
docker exec avao-35-pg17 psql -U avao -d avao -Atc \
  "SELECT count(*) FROM piezas WHERE ancho_mm > 25399999.99 OR largo_mm > 25399999.99;"  # debe ser 0 (guarda)

export AVAO35_URL="postgresql+psycopg2://avao:avao_dev@127.0.0.1:55433/avao"
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic upgrade head

# 1) Esquema: columnas *_in NUMERIC(10,4)
docker exec avao-35-pg17 psql -U avao -d avao -c "\d piezas" -c "\d productos"

# 2) CHECKs reescritos con *_in (pg_get_constraintdef)
docker exec avao-35-pg17 psql -U avao -d avao -Atc \
  "SELECT conname || ' :: ' || pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype='c' ORDER BY 1;"

# 3) Seed en pulgadas y valores de espesor esperados (0.2362 / 0.3937 / 0.1575 / NULL / 0.1575)
docker exec -i avao-35-pg17 psql -U avao -d avao < ../infra/seed.sql
docker exec avao-35-pg17 psql -U avao -d avao -c "SELECT nombre, espesor_in FROM productos ORDER BY nombre;"

# 4) Escenario A: fila de prueba convertida (ancho_in=0.9375, largo_in=1.4375)
docker exec avao-35-pg17 psql -U avao -d avao -c "SELECT ancho_in, largo_in FROM piezas;"

# 5) Reversible: downgrade parcial y re-upgrade
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic downgrade 95354a0cc046
docker exec avao-35-pg17 psql -U avao -d avao -c "\d piezas"   # *_mm NUMERIC(10,2) otra vez
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic upgrade head

docker stop avao-35-pg17 && docker rm avao-35-pg17
```

**Criterios de aceptación de la migración:** (1) `\d piezas` muestra `ancho_in`/`largo_in` `numeric(10,4)` NOT NULL; (2) los CHECK `> 0` mencionan `*_in`; (3) el seed inserta sin error y los espesores son los de §4.2; (4) la fila de escenario A vale `0.9375`/`1.4375`; (5) downgrade y re-upgrade completan sin error; (6) tras el downgrade, la fila A vale `23.81`/`36.00` mm (pérdida documentada, no `24.00`/`36.00`).

---

## 5. Cambios transversales por archivo

### 5.1 API (`apps/api`) (#35 / HU-01)

| Archivo | Cambio |
|---|---|
| `models.py` | §3.1: `*_mm` → `*_in`, `Numeric(10,2)` → `Numeric(10,4)` en `Piece` (2 cols) y `Product` (1 col); CHECKs con nombres de constraint intactos. Docstring: añadir línea "#35 / HU-01: unidad canónica pulgada decimal (DECISIONES D2/D7)". |
| `schemas.py` | §3.2 y §3.4: renombrar campos en `PiezaCreate`, `PiezaResponse`, `TareaPendienteResponse`; `decimal_places=4`; `PASO_PULGADA` + `field_validator` de múltiplo 1/16; importar `field_validator`. |
| `routers/pedidos.py` | `Piece(... ancho_in=p.ancho_in, largo_in=p.largo_in ...)`. |
| `alembic/versions/<rev>_pulgadas_decimales_35.py` | **Nuevo** (§4.3). |
| `test_pedidos.py` | `payload_valido`: `"ancho_in": "48.0000"`, `"largo_in": "31.5000"` (pieza 1); `"ancho_in": "24.0000"`, `"largo_in": "16.1250"` (pieza 2) — todos múltiplos de 1/16 (768, 504, 384, 258 dieciseisavos). `seed`: `Product(nombre="Vidrio 6mm", tipo="vidrio", espesor_in=Decimal("0.2362"))`, `Product(nombre="Perfil aluminio", tipo="aluminio", espesor_in=Decimal("0.0787"))`. `test_422_ancho_negativo`: `body["piezas"][0]["ancho_in"] = "-10"`; `test_422_largo_cero`: `"largo_in": "0"`. |
| `test_tareas.py` | `CAMPOS_CONTRATO`: `ancho_in`, `largo_in`; `_pieza`: `ancho_in=Decimal("48.0000")`, `largo_in=Decimal("31.5000")`; `seed` con `espesor_in`. |
| `test_piezas.py` | `_pieza`: igual que arriba; `seed` con `espesor_in`; `test_idempotente_ya_completado`: `float(en_bd.ancho_in) == 48.0`. |
| `test_medidas.py` | **Nuevo** — casos M1–M8 de §7.2 (ida y vuelta, 1/16, límites, excepción espesor). |
| `test_main.py` | Sin cambios (no toca medidas). |

> Nota de tests en SQLite: SQLAlchemy persiste `Numeric` como FLOAT y lo recupera vía `str(float)`; los valores elegidos (múltiplos de 1/16 y espesores de 4 decimales) son exactos en ese camino, así que las aserciones `Decimal(str(v))`/`float(v)` son exactas. Patrón de aserción del código vigente (`float(en_bd.ancho_mm) == 1200.5`).

### 5.2 Infra

| Archivo | Cambio |
|---|---|
| `infra/seed.sql` | `espesor_mm` → `espesor_in` con valores en pulgadas: `0.2362`, `0.3937`, `0.1575`, `NULL` (perfil), `0.1575`. Los `nombre` conservan "6mm"/"10mm"/"4mm" como etiqueta comercial (D-#35-8). Actualizar el comentario de cabecera: "#35 / HU-01: espesores convertidos de mm a pulgadas decimales (÷25.4, escala 4)". |
| `infra/docker-compose.yml` | Sin cambios (PostgreSQL 17 ya; la migración corre con `alembic upgrade head`). |

### 5.3 Ventas PWA (`apps/ventas-pwa`) (#35 / HU-01)

| Archivo | Cambio |
|---|---|
| `src/utils/unidades.js` | **Nuevo** — constantes y convertidores puros (testeables): `MM_POR_PULGADA = 25.4`, `PASO_PULGADA = 0.0625`, `MAX_PULGADAS = 999999.9999`; `mmAIn(mm)` (escala 4, libre — espesor); `mmAInCorte(mm)` (cuantiza al 1/16 más cercano — datos heredados); `cuantizar1_16(v)` (al 1/16 más cercano, `ROUND_HALF_UP` — entrada de captura, D-#35-4); `esMultiplo1_16(v)` (tolerancia `1e-9` defensiva para floats de JS; uso de tests y diagnóstico, ya no de rechazo). |
| `src/db/dexieDb.js` | **Bump de versión 1 → 2** (D-#35-7): declarar `db.version(1).stores({...})` (intacta, para upgrade) y `db.version(2).stores({ pedidos: '++idLocal, clienteNombre, fechaEntrega, estadoSync, createdAt', piezas: '++idLocal, pedidoIdLocal, productoId, ancho_in, largo_in, cantidad' }).upgrade(tx => tx.table('piezas').toCollection().modify(p => { p.ancho_in = mmAInCorte(Number(p.ancho_mm)); p.largo_in = mmAInCorte(Number(p.largo_mm)); delete p.ancho_mm; delete p.largo_mm }))`. `addPedido`: `ancho_in: Number(p.ancho_in)`, `largo_in: Number(p.largo_in)`. |
| `src/utils/validarPedido.js` | Leer `p.ancho_in`/`p.largo_in`. Reglas por medida: `> 0`; `<= MAX_PULGADAS` ("La medida no puede exceder 999999.9999 in"). **Ya NO rechaza no-múltiplos de 1/16** (D-#35-4): la cuantización ocurre en `PiezaRow` al salir del campo (§5.3), y la API la repite como defense-in-depth. **Justificación:** la app es offline-first — con cuantización en captura, local y servidor conservan el mismo valor y ningún pedido queda atascado por unidad. |
| `src/constants/catalogoProductos.js` | `espesor_mm` → `espesor_in`: `0.2362`, `0.3937`, `0.1575`, `0.7874`, `0.1575`. Nombres sin cambios (D-#35-8). |
| `src/services/syncService.js` | `construirPayloadPedido`: `ancho_in: Number(p.ancho_in)`, `largo_in: Number(p.largo_in)` (el resto del payload intacto). |
| `src/components/PedidoForm.jsx` | `piezaVacia`: `{ _key, productoId: '', ancho_in: '', largo_in: '', cantidad: '' }`. |
| `src/components/PiezaRow.jsx` | `value`/`onChange` con `ancho_in`/`largo_in`; `placeholder="ancho_in"` / `"largo_in"`; añadir `step="0.0625"` y `max="999999.9999"` a los inputs de medida (stepper y límite nativos; la validación sigue siendo `validarPedido`). **Cuantización en captura (D-#35-4, decisión del Coordinador: en `onBlur`)** — no interrumpe la escritura, a diferencia de `onChange` vivo: al salir del campo, si el valor parseado es válido y no es múltiplo de 1/16, se escribe `cuantizar1_16(v)` y el campo muestra el valor efectivo (el operario ve la medida que se guardará; hint opcional "se ajustó al 1/16 más cercano"). `aria-label` sin cambios ("Ancho pieza N"). |
| `src/test/unidades.test.js` | **Nuevo** — casos U1–U7 de §7.3. |
| `src/test/capturaPedido.test.jsx` | `llenarFilaValida`: defaults `ancho = '10.0625'`, `largo = '20.1875'`. Verificar piezas en Dexie con `ancho_in`/`largo_in`. **Nuevos (D-#35-4):** `'10.51'` se **acepta** y se cuantiza — Dexie guarda `10.5` (`db.pedidos.count() == 1`); rechaza `'1000000'` (excede rango). El test de medidas negativas (`'-5'`) sigue válido. |
| `src/test/syncService.test.jsx` | `agregarPedido`: `ancho_in: '10.0625'`, `largo_in: '20.1875'`. Caso 2: aserción `JSON.parse(init.body).piezas[0]` = `{ producto_id: UUID, ancho_in: 10.0625, largo_in: 20.1875, cantidad: 2 }` (exactitud float demostrada). Caso 7 (`pedidoB`): `'10.5'`/`'20.25'` → números `10.5`/`20.25` (ambos múltiplos de 1/16: 168 y 324 dieciseisavos). |

Sin cambios en Ventas: `App.jsx`, `main.jsx`, `pages/CapturarPedidoPage.jsx`, `pages/PedidosPage.jsx`, `components/{ClienteFields,PiezasList,ProductoSelect,SyncStatus,ValidationMessage}.jsx`, `hooks/useSincronizacion.js`, `constants/mapeoApi.js` (UUIDs), `src/test/setup.js`.

### 5.4 Taller PWA (`apps/taller-pwa`) (#35 / HU-01)

| Archivo | Cambio |
|---|---|
| `src/components/CorteCard.jsx` | Destructuring: `const { pieza_id, ancho_in, largo_in, cantidad, estado, operario_asignado, fecha } = tarea`; medidas: `` <p data-testid="corte-medidas">{`${ancho_in} x ${largo_in} in`}</p> ``. Renderizado verbatim (string decimal de Pydantic), sin aritmética de presentación (#37). |
| `src/test/tallerPage.test.jsx` | Fixtures: `t1` `ancho_in: '48.0000'`, `largo_in: '96.0000'`; `t2` `ancho_in: '24.0000'`, `largo_in: '36.0000'`. Test de medidas: `/48\.0000 x 96\.0000 in/` y `/24\.0000 x 36\.0000 in/`. |

Sin cambios en Taller: `services/tareasApi.js` (consuma la misma URL; las claves las lee `CorteCard`), `pages/TallerPage.jsx`, `components/CorteCardList.jsx`, `App.jsx`, `main.jsx`.

### 5.5 Documentación

| Archivo | Cambio |
|---|---|
| `docs/design/ERD-FASE1.md` | Documento vivo de diseño: (a) §1 regla "Medidas (pulgadas decimales) — `NUMERIC(10, 4)` con `CHECK (> 0)`; cortes en múltiplos de 1/16 in (validación de esquema, #35)"; (b) §2 y §3 mermaid: `decimal espesor_in`, `decimal ancho_in`, `decimal largo_in`, `numeric(10_4)`; (c) §4.2 `espesor_in`: "Espesor en pulgadas decimales — propiedad del material, **decimal libre** (6 mm ≈ 0.2362 in no es múltiplo de 1/16; excepción D2)"; (d) §4.4 `ancho_in`/`largo_in`: "Ancho/Largo en pulgadas decimales (criterio HU-01 'medidas exactas'); múltiplos de 1/16 in = 0.0625 validados en esquema (#35); rango hasta 999,999.9999 in"; (e) §5 DDL: columnas `*_in` `NUMERIC(10,4)`; (f) §6.2: `mapped_column(Numeric(10, 4), CheckConstraint('ancho_in > 0'))`; (g) **nueva §6.5 "Unidad canónica y precisión (#35)"** con el resumen de D2/D7, política de entrada, excepción de espesor, política de migración y referencia a este plan; separación cálculo exacto vs presentación fraccionaria (#37). |
| `ARCHITECTURE.md` | §4 "Estado de implementación", línea de **Medidas**: sustituir por "**Medidas:** unidad canónica pulgada decimal (`*_in`, `NUMERIC(10,4)`, pasos de 1/16 in) desde #35 (DECISIONES D2/D7); la presentación fraccionaria queda para #37." — justificado: el documento señala explícitamente esta brecha como pendiente de #35. |
| `MEMORY.md` | Línea 30 de "Arquitectura y brechas abiertas": sustituir por "Negocio define pulgadas fraccionarias con precisión de 1/16; #35 migró la implementación a `*_in` y `NUMERIC(10,4)` con validación de múltiplos de 1/16. Presentación fraccionaria pendiente en #37." |
| `README.md` | **Sin cambios** (no contiene referencias de unidades; verificado por búsqueda). |
| `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md` | **Sin cambios** — ya describe el estado objetivo ("Backend procesará medidas con punto decimal en pulgadas"; fracciones post-MVP). Sus fórmulas §3 (ej. `guiaRiel = anchoVentana - 1 7/8`) serán directamente aplicables por #34/HU-Med-02 sobre decimales (`1 7/8` in = `1.875`). |

### 5.6 Sin cambios (explícito, para el Revisor)

`apps/api/{main,database}.py`, `apps/api/routers/{tareas,piezas}.py`, `apps/api/test_main.py`, `apps/ventas-pwa/src/{App,main}.jsx`, `pages/{CapturarPedidoPage,PedidosPage}.jsx`, `components/{ClienteFields,PiezasList,ProductoSelect,SyncStatus,ValidationMessage}.jsx`, `hooks/useSincronizacion.js`, `constants/mapeoApi.js`, `apps/taller-pwa/src/{App,main}.jsx`, `pages/TallerPage.jsx`, `components/CorteCardList.jsx`, `services/tareasApi.js`, `infra/docker-compose.yml`, planes/reviews históricos.

---

## 6. Contrato JSON y política de versión

### 6.1 Ejemplos del contrato (#35 / HU-01)

`POST /pedidos` (request):

```json
{
  "cliente_id": "a1b2c3d4-0000-4000-8000-000000000001",
  "fecha_entrega": "2026-10-10",
  "notas": "Tel: 555-1234 — Entregar en mostrador",
  "piezas": [
    {
      "producto_id": "a1b2c3d4-0000-4000-8000-000000000011",
      "ancho_in": "10.0625",
      "largo_in": "20.1875",
      "cantidad": 2
    }
  ]
}
```

`201 Created` (`PedidoResponse.piezas[0]`, y análogamente `GET /tareas/pendientes` con `TareaPendienteResponse`):

```json
{
  "id": "…",
  "producto_id": "a1b2c3d4-0000-4000-8000-000000000011",
  "ancho_in": "10.0625",
  "largo_in": "20.1875",
  "cantidad": 2,
  "estado": "pendiente",
  "operario_asignado": null,
  "created_at": "…", "updated_at": "…"
}
```

- Los decimales viajan como **string** (serialización de Pydantic `Decimal`), preservando exactitud; `10.0625` vuelve como `"10.0625"`. Una entrada con menos decimales (`"10.5"`) se normaliza a escala 4 (`"10.5000"`): el **valor** es exacto, la representación se normaliza (la igualdad de prueba es `Decimal`, y de string para la forma canónica de 4 decimales — §7.1).
- **Frontera de presentación (D2):** la API **solo** habla pulgadas. Ejemplos comerciales en metros se convierten al ingresar (6 m = 236.22 in; 5.5 m = 216.535 in). No se envían mm ni metros por la API (D7).

### 6.2 Cambio rompiente y despliegue conjunto (D-#35-6)

- **Es un cambio rompiente:** `ancho_mm`/`largo_mm` desaparecen de request y responses de `POST /pedidos`, `GET /tareas/pendientes` y `PATCH /piezas/{id}/completar`. Ambas PWAs y la API se despliegan **juntas** (mismo tren de release; en la topología objetivo, Nginx sirve ambas PWAs y proxy a la API del mismo despliegue).
- **Sin versión de API ni ventana dual (YAGNI):** aceptar ambos nombres violaría D7 ("no se guardan ni se envían milímetros") y añadiría estado transitorio innecesario en un MVP sin producción.
- **Modo de fallo seguro:** Pydantic ignora claves extra y **exige** `ancho_in`; un bundle viejo de Ventas contra API nueva recibe **422** (no aceptación silenciosa), el pedido queda `pendiente` en Dexie con `ultimoError` y se reintenta — nunca se corrompe ni se pierde. Taller viejo contra API nueva simplemente no renderizará medidas (campos `undefined`) hasta actualizarse; las lecturas no mutan datos.
- **Service Worker:** no existe aún (criterio de caché de HU-08 pendiente), por lo que **no hay caché de app que invalidar**; los bundles nuevos se sirven al recargar (§10.3).

---

## 7. Pruebas

### 7.1 Prueba de ida y vuelta (requerida por la issue) (#35 / HU-01)

**Definición:** pulgadas decimales → JSON → API → BD → respuesta = **igualdad exacta**. Caso canónico `10.0625` (10 1/16 in) y `20.1875` (20 3/16 in):

1. `POST /pedidos` con `ancho_in: "10.0625"`, `largo_in: "20.1875"`.
2. Esperar **201** y `body["piezas"][0]["ancho_in"] == "10.0625"` (igualdad de **string** en la forma canónica de 4 decimales).
3. `Decimal(body["piezas"][0]["ancho_in"]) == Decimal("10.0625")` (igualdad de **valor**).
4. Consultar la BD desde el test (`session.get(Piece, id)` / query) y comparar el `Decimal` persistido — exactitud en la persistencia `NUMERIC(10,4)`.
5. `GET /tareas/pendientes` (la pieza está `pendiente` → aparece) y verificar los mismos valores — ida y vuelta completa por el contrato de Taller.
6. Repetir con entrada como **número JSON** (`ancho_in: 10.0625`, no string) para cubrir el camino float→Decimal de Pydantic (caso M7).

**Por qué es exacta en todos los saltos:** (a) JSON string → `Decimal` exacto; (b) JSON float → Pydantic convierte vía `str` y los múltiplos de 1/16 son binariamente exactos en IEEE 754 (`0.0625 = 2^-4`; `k × 0.0625` con `k < 2^49` cabe exacto en float64); (c) `NUMERIC(10,4)` es decimal exacto en PostgreSQL; (d) en SQLite de tests, SQLAlchemy recupera vía `str(float)` y el shortest-round-trip de estos valores coincide con el literal. En JS (Ventas), `JSON.stringify(10.0625) === "10.0625"` por la misma razón — esto es lo que se aserce en el caso 2 de `syncService.test.jsx`.

### 7.2 Tabla de casos — API, pytest (`apps/api`)

**Nuevo `test_medidas.py`** (fijos de #35; fixtures estilo de `test_pedidos.py`: SQLite en memoria + `dependency_overrides`):

| # | Caso | Entrada | Esperado | Criterio de issue / HU |
|---|---|---|---|---|
| M1 | **Ida y vuelta exacta** | `POST /pedidos` `ancho_in: "10.0625"`, `largo_in: "20.1875"` | 201; string `"10.0625"`/`"20.1875"`; `Decimal` igual en response, BD y `GET /tareas/pendientes` (§7.1) | "prueba de ida y vuelta"; "conservar exactamente incrementos de 1/16 in" |
| M2 | Mínimo 1/16 | `"0.0625"` | 201 | "Precisión mínima: 1/16 de pulgada" |
| M3 | Límite superior | `"999999.9375"` (mayor múltiplo de 1/16 en `NUMERIC(10,4)`) | 201 | rango D-#35-2 |
| M4 | No múltiplo de 1/16 | `"10.51"` | **201**; respuesta y BD tienen `"10.5000"` (cuantizado, D-#35-4) | política de entrada (D-#35-4) |
| M5 | 5 decimales | `"10.06255"` | 422 (`decimal_places=4`) | escala |
| M6 | Excede `NUMERIC(10,4)` | `"1000000.0000"` | 422 (`max_digits=10`) | rango |
| M7 | Número JSON (float) | `ancho_in: 10.0625` (number) | 201; exacto | robustez del camino float |
| M8 | **Excepción de espesor** | `Product(espesor_in=Decimal("0.2362"))` (no múltiplo de 1/16) persiste | sin error; lectura igual | D2/D-#35-3 (espesor libre) |
| M9 | Migración reversible | PG17 desechable (§4.4, manual) | §4.4 criterios 1–6 | "conversión de datos `*_mm`"; migración |

**Actualizados** (`test_pedidos.py`, `test_tareas.py`, `test_piezas.py`): renombrar fixtures a `*_in` con valores múltiplos de 1/16 (§5.1); los 422 existentes (negativo, cero, cantidad, sin piezas, tipo erróneo) deben seguir pasando con los nuevos nombres de campo; `test_contrato_de_campos` de tareas verifica el nuevo conjunto de claves.

### 7.3 Tabla de casos — Ventas PWA, Vitest (`apps/ventas-pwa`)

**Nuevo `src/test/unidades.test.js`:**

| # | Caso | Esperado |
|---|---|---|
| U1 | `mmAIn(6)` | `0.2362` |
| U2 | `mmAIn(4)` | `0.1575` |
| U3 | `mmAInCorte(24)` | `0.9375` (15/16) |
| U4 | `mmAInCorte(36)` | `1.4375` (1 7/16) |
| U5 | `esMultiplo1_16(10.0625)` | `true` |
| U6 | `esMultiplo1_16(10.51)` | `false` |
| U7 | `esMultiplo1_16('10.5')` (string) | `true` |

**Actualizados:** `capturaPedido.test.jsx` (defaults `10.0625`/`20.1875`; nuevos rechazos de `'10.51'` y `'1000000'`; Dexie con `ancho_in`/`largo_in`) y `syncService.test.jsx` (payload con `ancho_in`/`largo_in`; caso 2 con exactitud float; caso 7 con `10.5`/`20.25`). El resto de la suite (13 tests de sync, 6 de captura) debe pasar sin más cambios.

### 7.4 Tabla de casos — Taller PWA, Vitest (`apps/taller-pwa`)

| # | Caso | Esperado |
|---|---|---|
| T1 | Fixtures con `ancho_in: '48.0000'`, `largo_in: '96.0000'` | DOM muestra `48.0000 x 96.0000 in` (`/48\.0000 x 96\.0000 in/`) |
| T2 | `t2` con `'24.0000'`/`'36.0000'` | `/24\.0000 x 36\.0000 in/` |
| T3 | Estado vacío, carga, error (existentes) | sin cambios de comportamiento |

### 7.5 Verificación manual en navegador — móvil y tablet (patrón `AUDITORIA-CIERRES`, Chromium + CDP)

La issue afecta UI de las dos PWAs; el coordinador ejecuta (o delega) la comprobación visual:

- **Ventas, emulación móvil (375×667):** capturar pedido con `10.0625` × `20.1875` → "Pedido guardado localmente"; intentar `10.51` → mensaje "múltiplo de 1/16 in" y nada persistido; DevTools → Application → IndexedDB → `avao-ventas` → `piezas` con campos `ancho_in`/`largo_in` (no `ancho_mm`); desconectar red (Network → Offline) → guardar → badge "1 pendiente(s) de sincronizar" → online → `POST /pedidos` 201 y badge "✓ sincronizado".
- **Taller, emulación tablet (768×1024 y 1024×768):** tarjetas de corte muestran medidas con sufijo `in` (`… x … in`), legibles sin scroll horizontal.
- **Nota:** sin Service Worker implementado (HU-08 pendiente), no hay caché que invalidar; cargar con vaciado de caché para servir el bundle nuevo.

---

## 8. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO
git fetch origin
git checkout -b feature/35-medidas-pulgadas origin/develop   # verificar: git status

# ---- API: pruebas y lint (comandos existentes en apps/api) ----
cd apps/api
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .

# ---- Migración en PostgreSQL 17 desechable (§4.4 completo) ----
docker run --rm -d --name avao-35-pg17 \
  -e POSTGRES_USER=avao -e POSTGRES_PASSWORD=avao_dev -e POSTGRES_DB=avao \
  -p 127.0.0.1:55433:5432 postgres:17
docker exec avao-35-pg17 pg_isready -U avao -d avao
export AVAO35_URL="postgresql+psycopg2://avao:avao_dev@127.0.0.1:55433/avao"
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic upgrade head
docker exec avao-35-pg17 psql -U avao -d avao -c "\d piezas" -c "\d productos"
docker exec avao-35-pg17 psql -U avao -d avao -Atc \
  "SELECT conname || ' :: ' || pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype='c' ORDER BY 1;"
docker exec -i avao-35-pg17 psql -U avao -d avao < ../infra/seed.sql
docker exec avao-35-pg17 psql -U avao -d avao -c "SELECT nombre, espesor_in FROM productos ORDER BY nombre;"
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic downgrade 95354a0cc046
DATABASE_URL="$AVAO35_URL" ./.venv/bin/alembic upgrade head
docker stop avao-35-pg17 && docker rm avao-35-pg17

# ---- Ventas PWA (scripts existentes en package.json: test/lint/build) ----
cd ../ventas-pwa
npm test
npm run lint
npm run build

# ---- Taller PWA ----
cd ../taller-pwa
npm test
npm run lint
npm run build

# ---- Verificación manual en navegador (§7.5) ----
cd ../ventas-pwa && npm run dev    # :5173, emulación móvil
cd ../taller-pwa && npm run dev    # :5174, emulación tablet
# API local: cd ../api && DATABASE_URL=... uvicorn main:app --reload --port 8000
```

Prerrequisitos: `apps/api/.venv` con alembic/psycopg2 (ya usado por la auditoría), Docker con imagen `postgres:17` local, Node con dependencias instaladas en ambas PWAs. El `Dockerfile` de `apps/api` copia solo `main.py` (deuda preexistente de DevOps, fuera de #35 — para la prueba manual usar `uvicorn` local, como en PLAN-#38 §7).

**Commit** (conventional commit + trazabilidad, `WORKFLOWS.md` §3-4):

```bash
git add apps/api apps/ventas-pwa apps/taller-pwa infra/seed.sql \
  docs/design/ERD-FASE1.md ARCHITECTURE.md MEMORY.md docs/planning/PLAN-#35.md
git commit -m "feat(api): medidas canónicas en pulgadas decimales con precisión 1/16 in (#35, HU-01)"
```

---

## 9. Trazabilidad

| Criterio de #35 / HU-01 | Decisión | Archivos | Prueba |
|---|---|---|---|
| "Backend procesará medidas con punto decimal en pulgadas" | D-#35-1/2 | `models.py`, `schemas.py`, `routers/pedidos.py` | M1–M3, M7 |
| "Precisión mínima: 1/16 de pulgada" | D-#35-2/4 | `schemas.py` (cuantizador), `unidades.js`, `PiezaRow` | M2, M4; U3–U7; captura `'10.51'`→`10.5` |
| "La representación y persistencia deben conservar exactamente incrementos de 1/16 in" | D-#35-2 (`NUMERIC(10,4)`) | migración, modelos | M1 (ida y vuelta), M3; migración §4.4 |
| "definir escala o unidad canónica" | D-#35-1/2 | todo el plan | — |
| "conversión de datos `*_mm`" | D-#35-5, migración §4 | migración Alembic, `seed.sql`, Dexie v2 upgrade | §4.4 (PG17); U3–U4 |
| "contrato JSON" | D-#35-6, §6 | `schemas.py`, PWAs | M1, M7; sync caso 2 |
| "prueba de ida y vuelta" | §7.1 | `test_medidas.py` | M1 |
| "`NUMERIC(10,2)` no conserva 0.0625 in" | motivación de `NUMERIC(10,4)` | migración, modelos | M1, M2 |
| "La precisión también afecta a Ventas, API y Taller" | alcance §1 | §5.1–§5.4 | suites de las tres apps |
| "Separar cálculo exacto de presentación fraccionaria (#37)" | §1 (no hace) | — | — |
| HU-01 AC "ingresar medidas (largo y ancho) y cantidad" con exactitud | D-#35-4 | `PiezaRow`, `validarPedido`, API | captura tests; M1 |
| Decisiones vigentes D2/D7 | este plan las concreta | todo | — |

---

## 10. Riesgos y límites explícitos

| Riesgo / límite | Impacto | Mitigación / decisión |
|---|---|---|
| **Datos de producción** | La migración convertiría datos reales | **No hay producción** (MVP; datos de dev y tests solamente — §4.2). Documentado; si aparecieran datos reales antes del despliegue, ejecutar la guarda de overflow (§4.4 paso 0) y un respaldo (`pg_dump`) antes de `alembic upgrade head`. |
| **Dual-running mm/in** | Complejidad y estado transitorio | **YAGNI:** no se mantienen ambos sistemas; cambio atómico (D-#35-6). |
| **Caché de Service Worker** | Bundle viejo tras el despliegue | **El SW no existe** (HU-08 pendiente): no hay nada que invalidar; los bundles nuevos se sirven al recargar (§6.2, §7.5). |
| **Contrato rompiente** | PWAs viejas contra API nueva (o viceversa) | Despliegue conjunto (D-#35-6); fallo seguro 422 en escritura; lectura degradada sin mutación en Taller. |
| **Overflow de datos heredados** > 25,399,999.99 mm | `ALTER COLUMN TYPE` a `NUMERIC(10,4)` fallaría | Guarda de pre-verificación obligatoria (§4.4 paso 0); imposible en la práctica para vidrio. |
| **Pérdida del downgrade** (×25.4, escala 2) | `24 mm → 0.9375 in → 23.81 mm` | Documentada (§4.2); aceptable sin producción; el downgrade es para reversibilidad de esquema. |
| **Deriva con #34/#36/#37** | Dependen de esta unidad | #34 (tramos y barra matriz, D6) y #36 (coordenadas Canvas) consumen `*_in`; #37 (fracciones visuales) consume la misma representación decimal sin tocarla. Las fórmulas de `MEDIDAS-VENTANA-CALIFORNIA.md` §3 aplican directamente sobre decimales (ej. `1 7/8` in = `1.875`). Este plan es la base: **no** implementar #34/#36/#37 antes de #35. |
| **Redondeo de empate** (mitad) | Ambigüedad en conversión de datos | Los valores de ejemplo no caen en empate de 5ª cifra; PG usa mitad-alejada-de-cero (determinista en SQL). Los tests no dependen de empates. |
| **Inconsistencia preexistente** catálogo local (20 mm) vs seed (NULL) para el perfil | Confusión menor | Se conserva cada cual (0.7874 vs NULL) y se marca para #40 (catálogo desde API) — D-#35-8. |
| **`Dockerfile` de `apps/api` incompleto** (copia solo `main.py`) | La API en Docker no arranca | Deuda preexistente de DevOps, fuera de #35; pruebas manuales con `uvicorn` local (§8). |
| **Tests en SQLite, no PostgreSQL** | El camino `Numeric` difiere (FLOAT + `str`) | Los valores elegidos son exactos en ambos caminos (§7.1); la migración se verifica en PG17 real (§4.4). |

---

## 11. Pendientes de decisión (Coordinador decide al integrar)

1. **Política de entrada ante no múltiplos de 1/16** (DECISIONES §Resueltas.1): **RESUELTO** por el responsable humano el 2026-10-05 — **(b) cuantizar al 1/16 más cercano** (D-#35-4). La propuesta original (a) de rechazar con 422 quedó revocada; el plan está enmendado en consecuencia (§1, §2 D-#35-4, §3.4, §5.3, §7.2 M4).
2. **Tolerancia en el validador Pydantic:** el plan propone **aritmética exacta** (`(v * 16) % 1 != 0`, sin epsilon — §3.4 justifica por qué no hace falta). Variante con epsilon `1e-9` si se prefiere defensa en profundidad. En JS (`validarPedido`) sí se usa `1e-9` defensivo.
3. **Nombres comerciales con "mm"** (D-#35-8): el plan propone conservarlos como etiqueta comercial. ¿Alinearlos a pulgadas en el futuro? (seguimiento junto a #40).
4. **CHECK de BD para 1/16** además de Pydantic (D-#35-9): el plan propone **no** añadirlo (coherencia con el patrón vigente de validación en esquema). Si el Coordinador quiere defensa en profundidad en BD, es un CHECK `ancho_in = ROUND(ancho_in/0.0625)*0.0625` en la migración (añadir antes de `down_revision` encadenado de #36).
5. **Revision ID de la migración:** generado por `alembic revision` al implementar; registrar en el commit.

---

*Fin del plan. Entregado por el rol Planificador (WORKFLOWS.md §2); **enmendado por el Coordinador el 2026-10-05** (D-#35-4: cuantizar en lugar de rechazar, por decisión del responsable humano — ver §Resueltas.1 de DECISIONES-MVP). Ejecución por el Implementador en `feature/35-medidas-pulgadas`. Decisiones obligatorias D2/D7 de `docs/planning/DECISIONES-MVP-2026-10-05.md` aplicadas; puntos que D2 delega al plan #35 resueltos en §2 y §11.*
