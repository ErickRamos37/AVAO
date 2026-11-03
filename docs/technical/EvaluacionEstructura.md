# Evaluación de la estructura del proyecto

**Revisión:** 28 de octubre de 2026. **Estado:** diagnóstico; no autoriza por sí mismo una refactorización. Revisar cuando una entrega concreta muestre dificultades de mantenimiento.

## Hallazgos verificables

- `apps/api/main.py` tiene 256 líneas. Contiene modelos y rutas FastAPI, conexión SQLite y asignación de etiquetas, guardado y consulta de pedidos, construcción de respuestas y registro del avance de cortes. El punto que más puede crecer es `get_order`, donde conviven consultas y armado del detalle de cada ventana.
- `apps/web/app.js` tiene 285 líneas y concentra captura y consulta. La propuesta de vistas de aluminio, vidrio y ensamble se evaluará como requisito de producto antes de decidir cómo dividir ese código.
- Las reglas de medidas y planes ya están separadas en `medidas.py`, `plan_aluminio.py` y `plan_vidrio.py`. La inicialización y las migraciones condicionales están en `init_db.py`; el esquema SQL en `docs/technical/HU01-modelo-sqlite.sql` es ejecutable y está en uso.
- `mark_aluminum` y `mark_glass` repiten un ciclo corto de leer, comprobar límites, actualizar y responder. Operan sobre tablas y respuestas diferentes; una función genérica ahora reduciría poco código y podría ocultar esas diferencias.
- Las pruebas de persistencia y marcas cubren validación, transacciones, límites, aislamiento de ventanas, conservación del avance y migración de bases anteriores. Varias llaman directamente a funciones de `main.py`: no sustituyen por completo una comprobación HTTP y de interfaz de la entrega afectada.

## Decisión actual

**No reestructurar por el número de líneas.** La separación necesaria para calcular medidas y cortes ya existe. Dividir ahora todo en routers, servicios y repositorios aumentaría archivos y coordinación sin resolver una dificultad observada. Tampoco se justifica incorporar un framework de migraciones mientras las alteraciones condicionales sigan siendo claras e idempotentes.

## Cuándo reconsiderarlo

Revisar al preparar una HU si localizar o modificar su comportamiento exige tocar varias responsabilidades no relacionadas dentro de `main.py`, si `get_order` se vuelve difícil de comprobar, o si una nueva migración hace ambiguo el orden de actualización de bases existentes. Registrar el problema concreto antes de proponer cambios.

Si aparece esa necesidad, extraer **una responsabilidad a la vez** y conservar inicialmente los imports públicos de `main.py` que usan las pruebas. Mantener el mismo contrato HTTP, el esquema de datos y el comportamiento visible; ejecutar las pruebas existentes y comprobar por HTTP y desde la web el flujo afectado. Una refactorización significativa requiere propuesta al usuario antes de implementarla, según `AGENTS.md`.
