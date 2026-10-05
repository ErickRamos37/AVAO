# Especificaciones Técnicas: Medidas y Descuentos — Ventana California

**Fuente:** Especificaciones de Vidriería (AVAO)
**Trazabilidad:** Backlog MVP (referencia para futuras HU/Épicas)

---

## 1. Unidad de Medida
- Todas las medidas del taller se gestionan en **pulgadas**.
- Formato: **números fraccionarios**, no decimales (ej: `10 1/2 in`, no `10.5 in`).
- Precisión mínima/práctica: **1/16 de pulgada** (límite de flexómetros).

## 2. Reglas de Lectura de Fraccionarios
- No usar fracciones directas complejas como `9/16`.
- Expresar como `1/2 + 1/16` (equivale a `9/16`).
- Referencia principal: **medios (1/2)** y **cuartos (1/4)**.
- Máximo **dos fracciones combinadas** (ej: `3/4 + 1/16`, NO `1/2 + 1/4 + 1/16`).
- Estas reglas visuales se implementarán en tareas posteriores al MVP (personalización UI).

## 3. Fórmulas de Descuento (Ventana California)
Variables: `anchoVentana`, `altoVentana` (hueco real en pared).

| Pieza / Perfil | Fórmula |
|---|---|
| `centro` | `anchoVentana / 2` |
| `anchoVidrio` | `centro - 2` |
| `altoVidrio` | `altoVentana - 2` |
| `guiaRiel` | `anchoVentana - 1 7/8` |
| `jamba` | `altoVentana` |
| `mulio` | `altoVentana - 1` |
| `aleta` | `altoVentana - 2 1/2` |
| `verticalFijo` | `altoVentana - 1 1/4` |
| `horizontalFijo` | `centro - 2 1/2` |
| `horizontalCorredizo` | `centro - 7/8` |
| `altoScreen` | `verticalFijo` |
| `anchoScreen` | `centro - 1 5/8` |

**Nota:** `altoScreen` y `anchoScreen` se cortan del mismo perfil de aluminio.

---

## 4. Decisiones de Diseño (MVP)
- Backend procesará medidas con **punto decimal** en pulgadas.
- La conversión decimal → fracción se implementará en tareas posteriores (frontend/UI).
- `Ventana California` será la ventana base de referencia del MVP. Futuras ventanas/puertas se diseñarán después.
- Requerimientos visuales de fracciones (mostrar como `1/2 + 1/16`) quedan fuera del MVP.

---

## 5. Tareas sugeridas para GitHub (Backlog)
- `HU-Med-01`: Cambiar unidades del sistema de mm a pulgadas (backend con decimales).
- `HU-Med-02`: Implementar cálculo de descuentos para Ventana California.
- `HU-Med-03`: Visualización de medidas en formato fraccionario en UI (post-MVP).
- `HU-Med-04`: Catálogo de ventanas y soportes para futuros diseños (post-MVP).
