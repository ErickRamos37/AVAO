# PLAN #34 — Algoritmo de sumatoria lineal (FastAPI)

- **Tarea:** #34 — Subtarea 1: Algoritmo de sumatoria lineal.
- **Historia de Usuario:** HU-05.1 (Calcular estimación básica de barras de aluminio, MVP).
- **Rama:** `feature/34-algoritmo-sumatoria-lineal` (nace de `develop`).
- **Fecha:** 2026-10-05.
- **Documentos de referencia:** `apps/api/main.py`, `apps/api/schemas.py` (Pydantic v2), `apps/api/models.py` (`Piece.largo`, `Product.tipo` — solo contexto), `apps/api/routers/piezas.py` (estilo de router), `apps/api/test_piezas.py` (patrón de tests), `docs/planning/DECISIONES-MVP-2026-10-05.md` (**D2, D6, D7 — obligatorias**), `docs/planning/PLAN-#31.md` (estilo), `docs/specs/MEDIDAS-VENTANA-CALIFORNIA.md`, issue #34 (requisito original 5.5 m / barra 6 m).
- **Stack:** FastAPI + Pydantic v2, `decimal.Decimal`, pytest, ruff (`line-length = 100`).
- **Estado del tablero verificado:** issue #34 abierta (2026-10-05), checklist con un ítem ("Crear endpoint que reciba tramos, los sume y los divida entre la medida estándar").

---

## 1. Objetivo y alcance exacto

### Qué hace
- Implementar `POST /estimacion/barras` en `apps/api`: recibe la medida estándar de la barra matriz y una lista de tramos (cada uno con `largo_in` y `cantidad`), **todo en pulgadas decimales** (D2/D7), suma `Σ(largo_in × cantidad)` (D6) y devuelve `barras = ceil(total / barra_medida_in)` redondeando **hacia arriba** (criterio HU-05.1).
- Validar que ningún tramo supere la barra matriz → **422** con mensaje claro (criterio HU-05.1: "validar que no se puedan ingresar tramos individuales más largos que la barra matriz").
- Endpoint **stateless**: sin acceso a BD, sin `Depends(get_db)`, sin migraciones, sin cambios en `models.py`.
- Tests pytest en `apps/api/test_estimacion.py` con el caso de la HU (tramos por 216.535 in sobre barra de 236.22 in → **1 barra**).

### Qué NO hace (límites explícitos)
- **No** calcula sobre piezas de un pedido ni filtra `productos.tipo='aluminio'`: la opción (b) `GET /pedidos/{id}/estimacion-barras` se descarta en el MVP (ver §2.3, YAGNI) y queda como extensión post-MVP.
- **No** convierte unidades: la API solo habla pulgadas (D7); la conversión metro→pulgada es responsabilidad de la UI futura si el negocio insiste en ingresar metros (ver §8).
- **No** cuantiza tramos a múltiplos de 1/16: la barra matriz es decimal libre (D6) y la política de entrada de piezas (rechazar vs cuantizar) es pendiente de #35; este endpoint solo valida `largo_in > 0` y `largo_in <= barra_medida_in`.
- **No** persiste nada: el resultado no se guarda en BD (no hay modelo ni migración; `total_largo_in` es un cálculo en memoria).
- **No** implementa auth/JWT (HU-03), ni residuo en la respuesta (YAGNI, ver §3), ni WSS.

---

## 2. Endpoint

### 2.1 Ruta y método

```
POST /estimacion/barras
```

- **Body (JSON):** `EstimacionBarrasRequest` (§3). Los `Decimal` se envían como **strings** (ej. `"216.535"`) para preservar exactitud; Pydantic v2 los acepta así.
- **Dependencias:** ninguna (stateless — decisión de alcance, ver 2.3).
- **Respuesta 200:** `EstimacionBarrasResponse` (§3).
- **Errores:** `422` por validación de esquema (Pydantic) y por tramo que supere la barra matriz (levitado explícitamente en el router).

### 2.2 Lógica (diseño, no código final)

```python
# apps/api/routers/estimacion.py — esqueleto de diseño. #34 / HU-05.1.
from decimal import ROUND_CEILING

from fastapi import APIRouter, HTTPException

from schemas import EstimacionBarrasRequest, EstimacionBarrasResponse

router = APIRouter()


@router.post("/estimacion/barras", response_model=EstimacionBarrasResponse)
def estimar_barras(request: EstimacionBarrasRequest) -> EstimacionBarrasResponse:
    """Algoritmo de sumatoria lineal. #34 / HU-05.1.

    Suma el ``largo`` de cada tramo multiplicado por su cantidad (D6),
    divide entre la medida de la barra matriz y redondea hacia arriba
    (criterio HU-05.1). Unidad canónica: pulgadas (D2/D7). La barra
    matriz es decimal libre, no cuantizada a 1/16 (D6).
    """
    for tramo in request.tramos:  # 34 / HU-05.1: criterio HU, tramo <= barra
        if tramo.largo_in > request.barra_medida_in:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"El tramo de {tramo.largo_in} in supera la medida de "
                    f"la barra matriz ({request.barra_medida_in} in)"
                ),
            )
    total = sum(t.largo_in * t.cantidad for t in request.tramos)
    cociente = total / request.barra_medida_in
    barras = int(cociente.to_integral_value(rounding=ROUND_CEILING))
    return EstimacionBarrasResponse(
        total_largo_in=total,
        barra_medida_in=request.barra_medida_in,
        barras_estimadas=barras,
    )
```

Notas de implementación:
- **`Decimal` no tiene `ceil` directo.** La forma correcta es `cociente.to_integral_value(rounding=ROUND_CEILING)` (importar `ROUND_CEILING` de `decimal`). `math.ceil(total / barra)` también funciona (`Decimal` implementa `__ceil__`), pero `to_integral_value` es explícito y autodocumentado; **no usar `float` en ningún paso**.
- **Seguridad de la división Decimal:** la división usa la precisión del contexto (28 dígitos por defecto); con operandos de ≤ 10 dígitos el error de redondeo del cociente (≤ ~1e-24) es despreciable frente al residuo mínimo significativo (≥ 1e-4 in sobre una barra de ~236 in), y un cociente exactamente entero se representa sin error. Alternativa totalmente exacta si el Revisor la prefiere: `residuo = total % barra_medida_in; barras = int(total // barra_medida_in) + (1 if residuo > 0 else 0)` (`//` y `%` de `Decimal` son exactos). Cualquiera de las dos debe pasar los tests 3 y 4 de §5 (múltiplo exacto y residuo mínimo), que son los guardias del redondeo.
- **Validación de tramo > barra en el router, no en el esquema:** compara dos campos del request (validación de negocio), por lo que `Field` no puede expresarla; se levanta `HTTPException(422, ...)` con mensaje claro y estable (el test 5 de §5 afirma el `detail`).
- **`sum(...)` inicia en `0` (int):** `0 + Decimal` es válido; el resultado es `Decimal`.
- **Serialización:** Pydantic v2 serializa `Decimal` como string en JSON. La escala del string depende de la entrada (ej. `"216.535"`); los tests deben comparar con `Decimal(body[...])`, no por igualdad de strings, salvo donde se indique.

### 2.3 Alcance del endpoint — decisión (a) recomendada, (b) descartada en MVP

- **(a) `POST /estimacion/barras` stateless — RECOMENDADA (núcleo).** Cumple 100% los criterios de HU-05.1 (ingresar barra matriz, sumar tramos, dividir con ceil, mostrar total, validar tramo ≤ barra), es testeable sin fixtures de BD y sin dependencia de datos.
- **(b) `GET /pedidos/{id}/estimacion-barras` — NO en el MVP (YAGNI):**
  1. HU-05.1 no menciona pedidos ni BD: pide ingresar medidas y mostrar un total.
  2. **Bloqueo técnico real:** hoy `Piece.largo_mm` está en mm `NUMERIC(10,2)` (migración #35 pendiente); calcular sobre BD mezclaría unidades y acoplaría #34 a #35 sin aportar al criterio de la HU.
  3. **Ambigüedad de negocio no resuelta:** no existe en el modelo la noción de "tramo de una barra" (una pieza no equivale necesariamente a un tramo, ni hay agrupación por barra); definir qué piezas `tipo='aluminio'` sumar es decisión de negocio pendiente, no implementable sin supuestos (AGENTS.md: no suponer detalles del dominio).
- **Decisión pendiente para el Coordinador** (pendiente #5 de `DECISIONES-MVP-2026-10-05.md`): confirmar (a) como alcance de #34. Si el Coordinador exige (b) también, debe resolverse primero la ambigüedad del punto 3 y el orden con #35 — en ese caso este plan se reabre; no se implementa (b) por defecto.
- **Filtrado por `tipo='aluminio'`:** documentado aquí como extensión; **no** se implementa en el endpoint stateless (ver §6).

---

## 3. Esquemas Pydantic (`apps/api/schemas.py`, agregar al final)

```python
class TramoEstimacion(BaseModel):
    """Tramo de corte para estimación de barras. #34 / HU-05.1.

    ``largo_in`` en pulgadas decimales (D2/D7). Proviene de piezas de
    corte con precisión 1/16 según #35, pero este endpoint stateless no
    cuantiza: la política de entrada la define #35.
    """

    largo_in: Decimal = Field(gt=0, max_digits=10, decimal_places=4)
    cantidad: int = Field(gt=0)


class EstimacionBarrasRequest(BaseModel):
    """Petición de estimación de barras matriz de aluminio. #34 / HU-05.1."""

    barra_medida_in: Decimal = Field(
        gt=0, max_digits=10, decimal_places=4
    )  # estándar comercial, decimal libre (D6): 6 m = 236.22 in
    tramos: list[TramoEstimacion] = Field(min_length=1)  # 34 / HU-05.1: al menos un tramo


class EstimacionBarrasResponse(BaseModel):
    """Resultado de la sumatoria lineal. #34 / HU-05.1."""

    total_largo_in: Decimal
    barra_medida_in: Decimal
    barras_estimadas: int  # ceil(total / barra), redondeo hacia arriba (criterio HU)
```

- **`max_digits=10, decimal_places=4`** — coherentes con `NUMERIC(10,4)` de #35 (D2): 216.535 (3 decimales) y 236.22 caben sobrados; 0.0625 (1/16) es exacto.
- **`gt=0`** en `barra_medida_in`, `largo_in` y `cantidad` → 422 automático de Pydantic (tests 7 y 8).
- **`min_length=1`** en `tramos` → 422 si la lista viene vacía (test 10), mismo patrón que `PedidoCreate.piezas`.
- **Residuo en la respuesta: NO** (YAGNI). El criterio HU solo exige el total de barras; si una futura HU lo pide, es un campo aditivo.

**Ejemplo del caso de la HU** (requisito original conservado y convertido según D2: 5.5 m = 216.535 in; 6 m = 236.22 in):

```json
POST /estimacion/barras
{"barra_medida_in": "236.22", "tramos": [{"largo_in": "216.535", "cantidad": 1}]}

200 OK
{"total_largo_in": "216.535", "barra_medida_in": "236.22", "barras_estimadas": 1}
```

---

## 4. Archivos previstos y trazabilidad en código

| Archivo | Cambio | Trazabilidad |
|---|---|---|
| `apps/api/schemas.py` | Agregar `TramoEstimacion`, `EstimacionBarrasRequest`, `EstimacionBarrasResponse` (§3) | docstrings `#34 / HU-05.1` |
| `apps/api/routers/estimacion.py` | **Nuevo** — router con docstring `Tarea #34, HU-05.1 — Estimación básica de barras de aluminio.` y comentario in-line `#34 / HU-05.1` junto a la ruta y la validación de tramo | estilo de `routers/piezas.py` |
| `apps/api/main.py` | `from routers import estimacion, pedidos, piezas, tareas` + `app.include_router(estimacion.router)` + línea de docstring `#34 / HU-05.1: include router de estimación de barras.` | in-line |
| `apps/api/test_estimacion.py` | **Nuevo** — docstring `Tests pytest para POST /estimacion/barras. Tarea #34, HU-05.1.` | §5 |

- **No** se tocan `models.py`, `alembic/`, `apps/ventas-pwa`, `apps/taller-pwa` ni `infra/docker-compose.yml`.

---

## 5. Pruebas (pytest, `apps/api/test_estimacion.py`)

**Andamiaje:** el endpoint es stateless → **no** requiere engine SQLite ni fixtures `db_session`/`seed`. Basta `client = TestClient(app)` (importar `from main import app`). Los bodies se envían con Decimals como strings para evitar float.

| # | Caso (trazabilidad) | Request (`barra_medida_in`, tramos) | Esperado |
|---|---|---|---|
| 1 | **Caso HU / ítem de testing de #34**: tramos que suman 5.5 m sobre barra de 6 m (convertido D2) | `236.22`; `[{216.535, cantidad 1}]` | 200; `Decimal(body["total_largo_in"]) == 216.535`; `barras_estimadas == 1` |
| 2 | **Conversión explícita** (el issue exige "probar explícitamente la conversión"): 5.5 m → pulgadas redondeado a 3 decimales | — | assertion de trazabilidad: `(Decimal("5.5") / Decimal("0.0254")).quantize(Decimal("0.001"), ROUND_HALF_UP) == Decimal("216.535")` — documenta que el valor del caso 1 es la conversión del requisito original, no magia |
| 3 | Total múltiplo exacto de la barra (sin residuo) | `236.22`; `[{118.11, 1}, {118.11, 1}]` | 200; total `236.22`; **`barras_estimadas == 1`** (no 2) |
| 4 | Residuo mínimo → redondeo hacia arriba | `236.22`; `[{118.115, 1}, {118.115, 1}]` (total 236.23) | 200; **`barras_estimadas == 2`** |
| 5 | Tramo individual > barra matriz (criterio HU) | `236.22`; `[{236.23, 1}]` | **422**; `detail` contiene "supera la medida de la barra matriz" |
| 6 | `cantidad > 1` (D6: largo × cantidad) | `236.22`; `[{100, 2}, {100, 2}]` (total 400) | 200; total `400`; `ceil(400/236.22) == 2` barras |
| 7 | `barra_medida_in` cero / negativa | `0` y `-236.22` | **422** (validación `gt=0` del esquema) |
| 8 | `largo_in` cero / negativo; `cantidad` cero | `[{0, 1}]`, `[{-1, 1}]`, `[{1, 0}]` | **422** |
| 9 | Aritmética **Decimal exacta** (sin float) | `1`; dieciséis tramos `{0.0625, 1}` (1/16 exacto); y `236.22` con dos tramos `{236.22, 1}` | 200; total exacto `"1"` y `"472.44"`; `barras_estimadas == 1` y `== 2` respectivamente (un float podría dar 3 en el segundo caso si se redondea mal) |
| 10 | Lista de tramos vacía | `236.22`; `[]` | **422** (`min_length=1`) |

**Contradicción identificada y resuelta (para el Implementador):** el ejemplo literal "residuo mínimo: 236.23 in → 2 barras" **como tramo único es incompatible con el caso 5** (un tramo de 236.23 supera la barra de 236.22 y debe dar 422). Se implementa como **dos tramos de 118.115 in** (caso 4), que alcanza el mismo total 236.23 sin violar la validación de la HU. No "corregir" el caso 5: ambos casos deben coexistir.

---

## 6. Alcance de tramos y aluminio (documentación obligatoria)

- El endpoint recibe **tramos explícitos** en el body; no lee piezas ni pedidos (stateless).
- La relación con piezas de `tipo='aluminio'` (filtrado por pedido, opción (b)) **queda como extensión post-MVP**: no se implementa filtrado por tipo en el endpoint stateless (YAGNI, §2.3). Si se eligiera (b) después, el nuevo endpoint sumaría los `largo_in` de las piezas `tipo='aluminio'` del pedido y reutilizaría la misma función de cálculo — motivo por el cual el cálculo debe vivir en una función pura y testeable, no en el handler acoplado a la ruta.
- Docstring del router debe dejarlo explícito: "Endpoint stateless: no filtra por tipo de producto ni accede a BD (extensión post-MVP si se adopta la variante por pedido)."

---

## 7. Comandos exactos para el Implementador

```bash
cd /home/erick/Proyectos/AVAO/apps/api
# venv del repo (verificado: .venv/bin/pytest y .venv/bin/ruff existen)

# Pruebas (foco y totales; WORKFLOWS.md §2 prescribe -q para el reporte)
./.venv/bin/python -m pytest test_estimacion.py -v
./.venv/bin/python -m pytest -q

# Lint
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .   # si falla por formato preexistente, solo reportar

# Smoke manual opcional (sin BD: el endpoint es stateless)
./.venv/bin/uvicorn main:app --reload --port 8000
curl -X POST http://localhost:8000/estimacion/barras \
  -H 'Content-Type: application/json' \
  -d '{"barra_medida_in": "236.22", "tramos": [{"largo_in": "216.535", "cantidad": 1}]}'
```

**Commit (conventional, con trazabilidad — WORKFLOWS.md §4):**

```
feat(api): agregar POST /estimacion/barras — sumatoria lineal de tramos (#34, HU-05.1)
```

---

## 8. Riesgos, dependencias y decisiones pendientes

- **Riesgo — confusión de unidades (alto, ya ocurrió):** el input es **pulgadas** (D6/D7: "la API no habla metros"). El ejemplo métrico de la HU (5.5 m / 6 m) se preserva **convertido** (216.535 in / 236.22 in, D2). Si el negocio insiste en ingresar metros en la UI, la conversión se hace **en la UI futura**, no aquí. El test 2 fija la conversión como evidencia.
- **Dependencia con #35 — independencia defendida:** el endpoint es stateless y no lee `Piece`, por lo que **no depende del orden de integración de #35**. Si #34 se integra antes, el repo tendrá temporalmente `*_mm` en BD y `*_in` en el endpoint nuevo — aceptable porque no hay persistencia ni reutilización de modelos; los nombres `_in` y `decimal_places=4` ya asumen D2/D7 (vigentes). Si #35 se integra primero, #34 no cambia. Recomendación: cualquier orden funciona; por política D1 la planificación fue #35 antes que #34.
- **Precisión del ejemplo métrico:** 216.535 in (3 decimales) y 118.115 in caben en `max_digits=10, decimal_places=4` y en `NUMERIC(10,4)` de #35; 0.0625 (1/16) es exacto en decimal.
- **`Decimal` vs float:** ningún paso del cálculo puede tocar `float`; los tests envían strings. El test 9 es el guardia.
- **Decisiones pendientes para el Coordinador (no bloquear la implementación de (a)):**
  1. Confirmar alcance (a) stateless vs (b) por pedido (pendiente #5 de `DECISIONES-MVP-2026-10-05.md`); recomendación: (a).
  2. Confirmar que no se requiere parámetro de unidad en el API (D7 lo fija: pulgadas).
- **Scope creep a resistir:** agregar residuo a la respuesta, persistir estimaciones, cuantizar tramos a 1/16 aquí, o filtrar por tipo de producto — todos fuera de este PR.
