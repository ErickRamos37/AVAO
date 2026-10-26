# Contexto breve de AVAO para continuar el trabajo

> Índice de decisiones y fuentes, no backlog paralelo. Antes de cambiar requisitos, leer los documentos enlazados y confirmar con el usuario cualquier regla operativa incierta. El usuario es el experto principal del negocio, el único desarrollador humano y quien decide el MVP y las prioridades.

## Dónde está cada cosa

- [Medidas.md](domain/Medidas.md): ventana California por mitad, fórmulas, cantidades, fracciones y tres referencias.
- [FlujoDeTrabajoVidrieria.md](domain/FlujoDeTrabajoVidrieria.md): recorrido del pedido, varios pedidos pendientes, tareas actuales, ideas y preguntas.
- [Backlog.md](product/Backlog.md): backlog de producto con 22 HU, cuatro épicas de resultado y seis prioridades altas vigentes. `HU-01` y `HU-22` tienen estimación inicial de 5 puntos cada una, revisable al implementar.
- [GuiaBacklogKanban.md](workflow/GuiaBacklogKanban.md): formato de historias, esfuerzo numérico, prioridad y forma propuesta de usar GitHub Projects.
- El borrador anterior fue retirado después de consolidar sus ideas en `Backlog.md`; no mantener un segundo backlog.
- [README.md](../README.md) resume el alcance y la estructura actuales; las reglas de producto se mantienen en los documentos de `docs/`.
- [AGENTS.md](../AGENTS.md) conserva instrucciones generales. Las Skills `avao-refinar-hu` y `avao-entrega-vertical` en `.agents/skills/` guían cada tipo de trabajo.

## Decisiones de producto expresadas

- Primer MVP: **medidas y taller** para California por mitad, cálculo de cortes, marcas de aluminio y vidrio y ventanas ensambladas. Más adelante: fórmula sencilla actual de precios y recorrido hasta la liquidación; después: catálogo y precios avanzados.
- El flujo final de la aplicación es operado por empleados, sin interfaz del cliente prevista.
- Un cliente puede tener varios **pedidos** y cada pedido una o más ventanas. Puede haber pedidos pendientes en paralelo y el empleado puede cambiar entre ellos, incluso cuando a uno le falta material.
- Cada pedido y ventana tendrán identificador lógico interno. La primera entrega guarda y consulta medidas; `HU-22` añade después, con prioridad alta, el código corto de taller (`A1`, `A2`, `B1`) que se escribe a mano sobre aluminio y vidrio. Su letra **se liberará cuando el pedido esté instalado y pagado por completo**; automatizarlo depende de instalación y pagos posteriores. La identidad interna permanece estable. Falta definir el comportamiento de números al corregir o descartar una ventana guardada, así como piezas o papeles remanentes y más de 26 pedidos activos.
- Una equivocación de medida del negocio no cambia el precio acordado con el cliente. El material correcto puede reutilizarse y el incorrecto recortarse o rehacerse según el caso.
- La preferencia de esfuerzo es `1, 2, 3, 5, 8`; una historia estimada por encima de 8 se divide en historias menores que conserven valor comprobable. Las seis HU altas tienen estimación inicial revisable.
- Refinar, estimar y crear subtareas solo para las HU altas próximas. Una HU que supere 8 puntos se sustituye por dos o más HU menores; se cierra y archiva la original con enlaces a las sucesoras, conservando el historial. Las subtareas de implementación son sub-issues en el tablero; los criterios de aceptación quedan en la HU.
- Las áreas clasifican historias por tema; las épicas agrupan varias HU hacia un resultado amplio. Un campo `Épica` puede agruparlas en Projects; crear una incidencia padre solo si se necesita seguir ese resultado por separado. Las subtareas son hijas de cada HU.

## Forma de trabajo

- Kanban es el método principal. Una vez adoptado GitHub Projects, las HU quedan visibles en una vista de backlog con progreso de sub-issues y sus subtareas viajan por una vista de tablero: máximo cinco Por hacer y una En proceso, sujeto a revisión. Cerrar la HU solo tras comprobar sus criterios de aceptación. Este archivo solo orienta a quien retome el contexto.
- Distinguir **hecho confirmado**, **idea**, **regla abierta**, **recomendación** y **prioridad propuesta**. No convertir hipótesis del README o de investigación externa en requisitos del taller.
- El primer intento sufrió sobreingeniería y supuestos prematuros. Comprobar primero la conexión entre medidas capturadas y cortes calculados; ampliar robustez y diseños a partir de pruebas reales.
- Desarrollar entregas verticales pequeñas, utilizables desde la web e integradas con backend y datos cuando la aceptación lo exija. El usuario navega y decide alcance y verdad del negocio; la IA conduce la implementación acotada y muestra evidencia. Véanse la guía y las skills del proyecto.
- La plantilla de HU preferida usa «necesito»; «quiero» puede expresar un extra, pero el verbo no determina prioridad ni inclusión en MVP. La optimización de cortes 1D/2D es posterior al cálculo básico de cortes. El usuario eligió guardar y volver a consultar medidas como primera entrega y elevar `HU-22` a prioridad alta para añadir después los códigos visibles. Los datos del cliente siguen en `HU-13`; el descarte antes de guardar entra en `HU-01` y la corrección o eliminación posterior queda en `HU-06`.
- En `HU-01` se exige al menos una ventana con ancho y alto completos. Una fila vacía adicional no se guarda y una parcial se señala. El backend convierte la entrada fraccionaria a dieciseisavos enteros, que se guardan sin el texto original; al reabrir se muestra la fracción equivalente simplificada (`24 1/4 1/16` → `24 5/16`). El ascenso de resultados en treintaidosavos al siguiente dieciseisavo corresponde al cálculo de HU-02, no al almacenamiento de HU-01. La personalización de la escritura se aplaza. PostgreSQL es el dialecto elegido para el [borrador de esquema](technical/HU01-modelo-postgresql.sql), no una instalación ni decisión del resto del stack.
