# Plan de corrección de contexto, verificación y conservación del tablero — AVAO

**Iteración:** 1, planificación. **Fecha:** 2026-10-05. **Responsable:** planificador. **Trazabilidad:** HU-01, HU-02, HU-03, HU-08; subtareas #26–#38. **Fuente principal de estado:** [tablero AVAO / Desarrollo Principal](https://github.com/users/ErickRamos37/projects/4). Este documento no cambia issues, campos ni código.

## 1. Punto de partida y límites de evidencia

El coordinador leyó los 32 elementos del tablero: 7 subtareas cerradas y en **Finalizado** (#26–#31 y #38), 2 en **Por hacer** (#32–#33), 4 en **Backlog** (#34–#37) y 19 HUs. Las 13 subtareas #26–#38 carecen de **Prioridad**, **Esfuerzo** y **Épica**; las 19 HUs sí tienen valores. Es una instantánea del tablero, no una asignación propuesta. Antes de escribir en GitHub, volver a leer IDs de campos, opciones y valores para evitar sobrescribir cambios concurrentes. No se han cotejado aquí los cuerpos completos de las 13 issues con el tablero.

El repositorio **sí contiene código** (`apps/api`, `apps/ventas-pwa`, `apps/taller-pwa`), manifests y pruebas. Por ello [AGENTS.md](../../AGENTS.md), [MEMORY.md](../../MEMORY.md) y el apartado de estado de [WORKFLOWS.md](WORKFLOWS.md) están desactualizados. [README.md](../../README.md) nombra AVAO; [ARCHITECTURE.md](../../ARCHITECTURE.md) aún dice VidriCalc. La especificación vigente de negocio fija pulgadas con pasos de 1/16 en [MEDIDAS-VENTANA-CALIFORNIA.md](../specs/MEDIDAS-VENTANA-CALIFORNIA.md), pero modelo, API y PWAs todavía emplean `*_mm` y `NUMERIC(10,2)`.

Los reportes `REVIEW-#27.md` a `REVIEW-#31.md` y `REVIEW-#38.md` son **evidencia histórica declarada**. No sustituyen una ejecución independiente en esta iteración. #26 tiene ERD y validación declarada con PGlite; no se encontró `REVIEW-#26.md` ni prueba documentada de `upgrade`/`downgrade` de Alembic contra PostgreSQL 17. #27 registra explícitamente que esa ejecución quedó sin verificar. El cierre de una subtarea tampoco certifica toda su HU.

## 2. Resultado esperado y reglas de trabajo

1. Contexto único y vigente: corregir los cuatro roles de `.opencode/agents` para AVAO, retirar referencias de otros proyectos, comandos inexistentes y dependencias de archivos/skills ausentes. El planificador documenta criterios; el implementador ejecuta diseño y TDD; el revisor contrasta evidencia; el coordinador gobierna estado, trazabilidad y decisiones. Confirmar que las herramientas disponibles en esta sesión pueden invocar esos roles; la configuración OpenCode por sí sola no los activa en otros agentes.
2. Instrucciones y arquitectura coherentes: actualizar hechos observables de AGENTS/MEMORY/WORKFLOWS, resolver el nombre del producto con README y el tablero como referencia, y distinguir **arquitectura objetivo** de **implementación actual**. Conservar la regla de referencias inline a HU. No cambiar scripts Docker hasta decisión DevOps sobre su ubicación, que contradice la estructura `infra/` actual.
3. Auditoría reproducible de #26–#31 y #38: criterio de aceptación → archivo/commit/PR → prueba ejecutada → resultado → brecha. Un resultado de reporte previo se rotula “histórico”; un criterio sin prueba queda “no verificado”. Corregir redacción o estado de una issue solo después de leer su texto actual y preservar la trazabilidad de la decisión.
4. Tablero conservable: cada subtarea vinculada a HU/épica y con metadatos pertinentes o una excepción documentada; estados con significado único; la descripción de cada tarea permite verificar cuándo termina. No asignar prioridad ni esfuerzo por intuición: usar urgencia, dependencia, impacto y alcance observado.

## 3. Auditoría prevista de las siete tareas finalizadas

| Issue | Evidencia localizada | Verificación de segunda iteración | Redacción a cotejar en GitHub |
|---|---|---|---|
| [#26](https://github.com/ErickRamos37/AVAO/issues/26) | `ERD-FASE1.md` declara DDL y 13 comprobaciones en PGlite. Migración existe en `apps/api/alembic/versions/`. | Comparar ERD, modelo y migración; verificar primero el entorno y ejecutar `alembic upgrade head`, inspeccionar tablas/restricciones/índices y `alembic downgrade base` en PostgreSQL 17 desechable. Registrar diferencias y revisión propia. | Precisar que el diseño y la migración son entregables distintos; no afirmar “migración PostgreSQL validada” por PGlite. |
| [#27](https://github.com/ErickRamos37/AVAO/issues/27) | `REVIEW-#27.md` declara 10 pruebas API y observa Alembic sin prueba real. | POST válido 201, 404, 422, transacción sin datos parciales; contrato `cliente_id`/`producto_id` y prueba con DB real. | Describir requisitos observables y dependencia de #26 y catálogo/clientes. |
| [#28](https://github.com/ErickRamos37/AVAO/issues/28) | `REVIEW-#28.md` declara 6 pruebas Vitest y guardado Dexie. | Captura sin red, persistencia y recarga, validaciones; revisar móvil. Aclarar que en esta fase el nombre de cliente no resolvía el UUID API. | Distinguir captura local de sincronización #38. |
| [#29](https://github.com/ErickRamos37/AVAO/issues/29) | `REVIEW-#29.md` declara 7 pruebas de `GET /tareas/pendientes`. | Filtro, orden, paginación, contrato y visibilidad por operario con datos reales; identificar falta de autenticación/autorización. | Aclarar si “pendientes” es global o por operario y cómo se prueba. |
| [#30](https://github.com/ErickRamos37/AVAO/issues/30) | `REVIEW-#30.md` declara 5 pruebas Vitest; Taller renderiza tarjetas por REST. | Carga, vacío, error y medidas en tablet; cotejar alcance con WSS/Canvas objetivo. | Nombrar explícitamente “vista de tarjetas por REST” si ese fue su alcance; no declarar WSS/Canvas completos. |
| [#31](https://github.com/ErickRamos37/AVAO/issues/31) | `REVIEW-#31.md` declara 4 pruebas específicas, suite API de 21, idempotencia de completar pieza. | PATCH 200/404/422, persistencia, reintento y concurrencia; comprobar que pedido completo pertenece a #33. | Separar estado de pieza de estado de pedido. |
| [#38](https://github.com/ErickRamos37/AVAO/issues/38) | `REVIEW-#38.md` declara 17 pruebas Ventas; documenta mapeo manual e idempotencia de POST pendiente. | Sin red, retorno de red, 500/404, recarga y respuesta perdida después de 201: detectar pedidos duplicados. Confirmar persistencia de error y UUID de servidor. | Expresar “sincronización básica con riesgos conocidos”; vincular una tarea de idempotencia y sustitución del mapeo manual. |

**Regla de decisión:** si un criterio de aceptación original no se cumple, documentar la discrepancia y corregir issue, implementación o estado según corresponda. No cerrar una nueva brecha mediante una nota vaga ni reabrir automáticamente una tarea por trabajo futuro fuera de su alcance original. Para cada # registrar URL de issue/PR, commit, versión de entorno, comando exacto, resultado y fecha. El revisor decide “cumple”, “cumple con límite de alcance” o “requiere corrección”, con motivo reproducible.

## 4. Conservación del tablero y calidad de issues

Usar una plantilla breve para cada subtarea: **objetivo y HU**, contexto, alcance y exclusiones, criterios observables, dependencias, evidencia requerida y criterio de cierre. Para las HUs mantener valor para usuario, escenario y aceptación; evitar copiar detalles técnicos de la subtarea. Consultar la descripción existente antes de reescribir: edición mínima, historial preservado y enlaces a PR/pruebas. Los [formularios de issue de GitHub](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms) pueden exigir campos de captura; los [campos personalizados de Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) gestionan prioridad/esfuerzo/épica en el tablero.

Primero leer las opciones reales de **Prioridad**, la escala de **Esfuerzo** y la taxonomía de **Épica**. Luego evaluar #26–#38 y completar los campos aplicables con justificación breve por item. Propuesta de criterio, sujeta a los valores existentes: prioridad por impacto, urgencia y bloqueo de otras tareas; esfuerzo por trabajo restante estimado y riesgo técnico; épica por HU o flujo principal, sin inventar una nueva agrupación. Para las cerradas, registrar esfuerzo histórico solo si el campo pretende medirlo y existe evidencia suficiente; en otro caso dejarlo vacío con motivo «N/A: esfuerzo histórico no estimable» en el registro de auditoría. No poner “0” ni un valor ficticio para hacer desaparecer celdas vacías. Las 19 HUs se revisan por consistencia, sin alterar valores válidos.

Crear una vista de triage con filtros de campos vacíos y otra de **Finalizado** con issues cerradas; revisar semanalmente nuevas entradas y discrepancias issue/estado. GitHub permite [filtrar vistas](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects) y [automatizar cambios de estado](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations); comprobar las reglas activas antes de habilitar automatismos que puedan cerrar issues sin la revisión humana definida en WORKFLOWS. Adoptar una sola definición de **Finalizado**: criterios de la subtarea y pruebas verificadas, revisión registrada, integración a `develop`, estado de issue coherente y comunicación al dueño. `main` mantiene su aprobación humana separada. Resolver la contradicción actual de WORKFLOWS que combina integración a `develop` con aprobación previa al merge a `main` en el mismo paso.

### Issues abiertas que requieren precisión

- **#32 y #33:** comprobar alcance y dependencia de #30/#31; definir interfaz de operario y regla de pedido completo, respectivamente, con pruebas observables. No asumir que #33 ya está cubierta por el PATCH de pieza.
- **#34:** el ejemplo `5.5 m / 6 m` contradice la decisión de pulgadas para medidas de fabricación. Leer el cuerpo; separar longitud comercial de barra y medidas de corte, decidir unidad canónica y conversión explícita antes de estimar. No editar el ejemplo como si la equivalencia fuese obvia.
- **#35:** `1/16 in = 0.0625 in`; `NUMERIC(10,2)`, `decimal_places=2` y campos `*_mm` no preservan ese paso. Definir representación canónica (por ejemplo entero de dieciseisavos, o decimal exacto de escala suficiente), redondeo, migración de datos, nombres del contrato y compatibilidad offline. La selección requiere diseño y prueba de ida/vuelta.
- **#36 y #37:** conectar fórmulas California y presentación fraccionaria a #35; validar ejemplos con negocio y casos límite (resultado no positivo, mitad de pasos, perfil compartido). La visualización no debe decidir la precisión de cálculo.
- **#38:** crear o vincular seguimiento específico para idempotencia del alta de pedidos tras una respuesta 201 perdida. HTTP no da idempotencia automática a POST; ver [RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2). Diseñar clave estable por pedido local y restricción única/recuperación en servidor antes de activar reintentos no controlados.

## 5. Verificación por componente en la segunda iteración

| Componente | Criterios y herramientas existentes | Evidencia mínima |
|---|---|---|
| API + datos | En `apps/api`: pytest, Ruff y Alembic según archivos del árbol. PostgreSQL 17 desechable para migración y contratos con FKs/CHECKs; verificar `upgrade` y `downgrade` mediante [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html). | Salida de comandos, esquema observado y casos HTTP/DB reales. No confundir PGlite con ejecución real de migración. |
| Ventas PWA | `npm run test`, `npm run lint`, `npm run build` definidos en `apps/ventas-pwa/package.json`; IndexedDB/Dexie sin red, recuperación, recarga, reintento y medidas. | Resultados Vitest, revisión móvil y evidencia de persistencia/duplicados. |
| Taller PWA | Los mismos scripts definidos en `apps/taller-pwa/package.json`; contrato con API, estados, errores y medidas en tablet. | Resultados Vitest, revisión tablet y brecha WSS/Canvas registrada contra arquitectura. |
| Integración | Ventas → API → PostgreSQL → Taller con pedido y piezas de ejemplo, JWT/WSS/optimización solo cuando existan tareas para implementarlos. | IDs correlacionados y transición observable de estados; distinguir alcance MVP de arquitectura futura. |

La semántica de `NUMERIC(p,s)` y su redondeo está documentada por [PostgreSQL](https://www.postgresql.org/docs/17/datatype-numeric.html). Para #35, un caso con `0.0625` y otro con fracción compuesta debe atravesar UI, Dexie, JSON, Pydantic, SQLAlchemy y PostgreSQL sin cambio de valor no autorizado.

## 6. Secuencia de ejecución propuesta para la iteración 2

1. Reconectar y congelar una instantánea de las 32 tarjetas y sus campos; leer cuerpos completos de #26–#38 y HUs relacionadas. Guardar tabla de diferencias antes de cualquier edición.
2. Validar que los roles limpios de `.opencode/agents` se invocan con el contexto correcto; corregir AGENTS, MEMORY, ARCHITECTURE y WORKFLOWS con hechos comprobados y fechas, manteniendo la arquitectura objetivo identificada.
3. Auditar #26–#31 y #38 en orden de dependencia. Ejecutar comandos definidos y PostgreSQL 17 real; registrar resultados por criterio, sin dar por repetidos los resultados históricos.
4. Corregir descripciones y vínculos de issues de alcance inequívoco. Documentar brechas como #34/#35/#38 en tareas precisas, sin cambiar el cierre de otra tarea sin evidencia de incumplimiento original.
5. Evaluar Prioridad/Esfuerzo/Épica de #26–#38 según opciones y significado reales; completar valores justificables y registrar excepciones N/A, revisar las 19 HUs, crear vista de triage y reconciliar estado de issue con columna.
6. Releer el tablero y comprobar: 32 elementos salvo altas justificadas, ningún valor inventado, 13 subtareas evaluadas, 7 cierres con matriz de evidencia, descripciones trazables y automatismos sin conflictos. Entregar diferencias y decisiones de negocio pendientes.

## 7. Riesgos y decisiones pendientes

- **Datos existentes en mm:** migrar a pulgadas exige política de conversión y redondeo; no cambiar campos ni datos sin respaldo y prueba de reversibilidad. El paso de 1/16 hace inadecuada la escala actual de dos decimales.
- **Cierre de #26/#27:** el DDL probado en PGlite y la migración Alembic son evidencias diferentes. El resultado en PostgreSQL puede obligar a corregir código o la afirmación de cierre.
- **Duplicados por sincronización:** #38 deja una ventana entre alta en servidor y marca local; definir idempotencia antes de considerar seguro el reintento automático.
- **Prioridad y esfuerzo:** las escalas del tablero y la intención histórica de “Esfuerzo” aún no constan aquí. Se consultan antes de asignar valores; si faltan, registrar decisión explícita.
- **Autenticación y canal Taller:** JWT, WSS, Canvas 2D y optimización están en arquitectura, mientras el flujo observado usa REST y tarjetas. Planificar por HU/épica sin atribuir esos entregables a #29/#30.
- **Trazabilidad de cambios:** `.opencode/` y varios planes aparecen sin seguimiento Git; verificar con el coordinador qué artefactos entran en el PR de contexto antes de preparar integración.

## Referencias de prácticas aplicables

- [GitHub Docs: Projects y campos](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects): metadatos, vistas y triage.
- [GitHub Docs: formularios de issues](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms): estructura y datos obligatorios al crear tareas.
- [GitHub Docs: automatización del tablero](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations): sincronía de estado y cierre, sujeta a la política del proyecto.
- [Alembic: tutorial oficial](https://alembic.sqlalchemy.org/en/latest/tutorial.html): ejecución y consulta de revisiones reales.
- [PostgreSQL 17: tipos numéricos](https://www.postgresql.org/docs/17/datatype-numeric.html): precisión, escala y redondeo.
- [RFC 9110: idempotencia HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2): base de la estrategia de reintentos de POST.
