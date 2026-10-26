# AVAO

AVAO busca ayudar a una MiPyME vidriera a registrar y dar seguimiento a pedidos y ventanas. El trabajo inmediato se enfoca en validar un flujo web completo con las funciones mínimas acordadas, antes de ampliar la aplicación.

## Alcance actual

El primer grupo de trabajo cubre el registro de medidas y el seguimiento básico del trabajo de taller, según el backlog vigente. El usuario es el experto del negocio y define las reglas, el alcance de cada entrega y sus prioridades.

El modo sin conexión, las capacidades PWA, los algoritmos avanzados de corte y el endurecimiento del backend quedan para etapas posteriores. El stack tecnológico y las instrucciones para ejecutar la aplicación se documentarán cuando estén decididos y disponibles.

## Estructura

- `apps/web/`: aplicación web.
- `apps/api/`: backend.
- `docs/domain/`: flujo del negocio y reglas de medidas.
- `docs/product/`: historias y alcance del producto.
- `docs/workflow/`: guía de trabajo Kanban.

Las carpetas de aplicación están preparadas; todavía no contienen una implementación inicial.

## Documentación

- [Contexto y decisiones del proyecto](docs/MEMORY.md)
- [Backlog de producto](docs/product/Backlog.md)
- [Flujo de trabajo de vidriería](docs/domain/FlujoDeTrabajoVidrieria.md)
- [Medidas de ventana California por mitad](docs/domain/Medidas.md)
- [Guía del backlog y Kanban](docs/workflow/GuiaBacklogKanban.md)
- [Borrador de esquema relacional de HU-01 (PostgreSQL)](docs/technical/HU01-modelo-postgresql.sql)
- [Instrucciones para agentes](AGENTS.md) y skills del proyecto en `.agents/skills/`.

GitHub Projects es la fuente de verdad para el estado del trabajo. El backlog en `docs/product/Backlog.md` conserva el contenido de producto; no reemplaza el tablero.
