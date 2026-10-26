# AVAO: instrucciones para agentes

- El usuario es el único desarrollador humano, principal experto del dominio y quien decide alcance, prioridad y aceptación. Distingue reglas confirmadas de hipótesis; pregunta por reglas del taller antes de implementarlas.
- Trabaja en entregas pequeñas y utilizables que atraviesen interfaz, backend y datos **cuando el resultado lo requiera**. No planifiques ni construyas todas las capas por separado.
- En programación, el usuario navega y la IA conduce: acuerda el resultado y los límites, implementa lo mínimo suficiente, demuestra el comportamiento y expone dudas o riesgos concretos. Propón cambios de alcance o refactorizaciones significativas al usuario antes de incorporarlos.
- Conserva comprobaciones necesarias para evitar resultados erróneos, pérdida de datos o exposición de información; aplaza complejidad futura que no resuelva una necesidad actual.
- Para requisitos y HU, consulta `docs/product/Backlog.md` y `docs/workflow/GuiaBacklogKanban.md`. Para fórmulas y reglas del taller, consulta `docs/domain/` y confirma cualquier vacío con el usuario.
- GitHub Projects es la fuente de verdad del estado del trabajo; `docs/product/Backlog.md` conserva el contenido del producto mientras se traslada al tablero. No crees un tablero paralelo.
- Skills del proyecto: `avao-refinar-hu` al refinar historias y `avao-entrega-vertical` al implementar una entrega.
