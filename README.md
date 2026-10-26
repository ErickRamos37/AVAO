# AVAO

AVAO busca ayudar a una MiPyME vidriera a registrar y dar seguimiento a pedidos y ventanas. El trabajo inmediato se enfoca en validar un flujo web completo con las funciones mínimas acordadas, antes de ampliar la aplicación.

## Alcance actual

El primer grupo de trabajo cubre el registro de medidas y el seguimiento básico del trabajo de taller, según el backlog vigente. El usuario es el experto del negocio y define las reglas, el alcance de cada entrega y sus prioridades.

El modo sin conexión, las capacidades PWA, los algoritmos avanzados de corte y el endurecimiento del backend quedan para etapas posteriores. La primera entrega usa FastAPI, SQLite y una página HTML/JavaScript sencilla.

## Estructura

- `apps/web/`: aplicación web.
- `apps/api/`: backend.
- `docs/domain/`: flujo del negocio y reglas de medidas.
- `docs/product/`: historias y alcance del producto.
- `docs/workflow/`: guía de trabajo Kanban.

## Ejecutar la primera entrega

Se necesita Python 3. La base SQLite se crea en `data/avao.sqlite3` (ignorada por Git) al inicializar la aplicación.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
python -m apps.api.init_db
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

Abre `http://127.0.0.1:8000`. Captura el ancho y alto del hueco de una o más ventanas California, guarda el pedido y usa la URL del pedido para volver a consultarlo incluso después de reiniciar el servidor. Puedes añadir o descartar filas antes de guardar; las filas completamente vacías se omiten y las parciales se señalan. El listado de pedidos pertenece a la siguiente subtarea de HU-01. Las medidas se guardan en dieciseisavos de pulgada y se muestran como fracción simplificada. La inicialización crea las tablas si faltan; no sustituye migraciones cuando el esquema cambie más adelante. Para usar otro archivo local, configura `AVAO_DB_PATH` antes de inicializar y arrancar la aplicación.

## Documentación

- [Contexto y decisiones del proyecto](docs/MEMORY.md)
- [Backlog de producto](docs/product/Backlog.md)
- [Flujo de trabajo de vidriería](docs/domain/FlujoDeTrabajoVidrieria.md)
- [Medidas de ventana California por mitad](docs/domain/Medidas.md)
- [Guía del backlog y Kanban](docs/workflow/GuiaBacklogKanban.md)
- [Esquema inicial de HU-01 (SQLite)](docs/technical/HU01-modelo-sqlite.sql)
- [Instrucciones para agentes](AGENTS.md) y skills del proyecto en `.agents/skills/`.

GitHub Projects es la fuente de verdad para el estado del trabajo. El backlog en `docs/product/Backlog.md` conserva el contenido de producto; no reemplaza el tablero.
