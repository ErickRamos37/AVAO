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

Abre `http://127.0.0.1:8000`. Captura el ancho y alto a los que el vidriero decidió fabricar una o más ventanas California tras evaluar el hueco; AVAO no resta otra holgura. Guarda el pedido y usa la lista de pedidos para abrir cualquiera y consultar sus ventanas, incluso después de reiniciar el servidor. La lista se muestra por ID ascendente: es una decisión técnica para mantener un orden estable, no una prioridad de negocio. Los pedidos nuevos reciben etiquetas `A`…`Z`, `AA`… y sus ventanas muestran códigos como `A1` y `A2`. Puedes añadir o descartar filas antes de guardar; las filas completamente vacías se omiten y las parciales se señalan. Las medidas se guardan en dieciseisavos de pulgada y se muestran como fracción simplificada. Para usar otro archivo local, configura `AVAO_DB_PATH` antes de inicializar y arrancar la aplicación.

Al guardar un pedido nuevo se calcula y guarda el plan de aluminio y de dos vidrios iguales de cada ventana. El detalle muestra los perfiles de aluminio con longitud y cantidad, y las medidas ancho × alto de los vidrios. Se consulta el plan guardado sin recalcularlo al abrir el pedido. Los pedidos guardados antes de este cambio conservan sus medidas, pero no tienen un plan generado.

Desde el plan de aluminio de una ventana se puede marcar un corte físico o deshacer una marca accidental. La pantalla muestra cantidad requerida, cortada y pendiente por perfil; el avance queda guardado al reabrir el pedido. Guía y riel se marcan por separado.

Cada ventana también muestra las medidas y el avance de sus dos vidrios iguales. Se puede marcar cada corte físico y deshacer una marca accidental; el conteo queda guardado por ventana.

El pedido muestra el estado de ensamble de cada ventana. Solo se puede confirmar tras registrar todos sus cortes de aluminio y vidrio; el ensamblador verifica físicamente screen, accesorios y extras aplicables. Puede deshacer una marca de ensamble accidental. Mientras una ventana figure ensamblada, primero hay que deshacer esa marca para poder deshacer un corte. Este estado no declara listo, instalado ni pagado el pedido.

Si ya tienes una base SQLite de la entrega anterior, ejecuta de nuevo `python -m apps.api.init_db` antes de iniciar la aplicación. Conserva los pedidos existentes sin etiqueta y los muestra como «sin etiqueta»; solo los pedidos creados después reciben códigos. No borra ni reinicia los datos de prueba.

## Documentación

- [Contexto y decisiones del proyecto](docs/MEMORY.md)
- [Backlog de producto](docs/product/Backlog.md)
- [Flujo de trabajo de vidriería](docs/domain/FlujoDeTrabajoVidrieria.md)
- [Medidas de ventana California por mitad](docs/domain/Medidas.md)
- [Guía del backlog y Kanban](docs/workflow/GuiaBacklogKanban.md)
- [Esquema inicial de HU-01 (SQLite)](docs/technical/HU01-modelo-sqlite.sql)
- [Evaluación de la estructura del proyecto](docs/technical/EvaluacionEstructura.md)
- [Instrucciones para agentes](AGENTS.md) y skills del proyecto en `.agents/skills/`.

GitHub Projects es la fuente de verdad para el estado del trabajo. El backlog en `docs/product/Backlog.md` conserva el contenido de producto; no reemplaza el tablero.
