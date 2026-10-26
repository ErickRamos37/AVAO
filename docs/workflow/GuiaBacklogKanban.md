# Guía ligera para historias y GitHub Projects en AVAO

> Propuesta de trabajo para un desarrollador humano con apoyo de IA. No sustituye las decisiones del usuario sobre procesos de vidriería, alcance ni prioridad. **GitHub Projects será la fuente de verdad del estado del trabajo cuando se trasladen allí las historias**; los archivos locales son borradores y contexto, no un segundo tablero.

## 1. Escribir historias que describan valor

La [ISO/IEC/IEEE 29148:2018](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A29148%3Aed-2%3Av1%3Aen) orienta la ingeniería de requisitos y la redacción de requisitos precisos y sin ambigüedad; **no exige** una plantilla «Como / necesito / para» ni puntos de historia. Para AVAO se puede aplicar proporcionalmente: registrar necesidad, condiciones, ejemplos verificables y dudas sin crear una especificación extensa. La [Agile Alliance](https://agilealliance.org/glossary/user-stories/) describe las historias como incrementos de valor y advierte que una pantalla, API o sección de documento no es automáticamente una historia.

**Forma elegida para el borrador de AVAO:**

> **Como** [empleado o papel real], **necesito** [capacidad o resultado observable], **para** [beneficio en el trabajo].

Las palabras **Como**, **necesito** y **para** van en negrita para facilitar la lectura. La plantilla es una ayuda, no una condición de la norma. «Necesito» favorece preguntar por una necesidad real; **no demuestra que la HU sea obligatoria para el MVP**. Si «quiero» ayuda a expresar un extra, puede usarse, pero la decisión de incluirlo o posponerlo debe figurar por separado y la toma el usuario. Usar el papel que necesita el resultado sin fingir permisos separados; una misma persona puede desempeñar varios. Preferir un verbo de resultado («consultar cortes pendientes») frente a «crear API», «agregar botón» o «hacer pantalla». Revisar cada candidata con [INVEST](https://agilealliance.org/glossary/invest/) cuando se acerque a desarrollo: valor, tamaño, posibilidad de estimar y de comprobar, entre otros criterios. La idea de [tarjeta, conversación y confirmación](https://agilealliance.org/glossary/three-cs/) recuerda que el texto breve se completa con diálogo y ejemplos.

Una incidencia de HU lista para trabajar podría contener solo:

1. **Título** con resultado observable.
2. **Historia** en la forma anterior.
3. **Criterios o ejemplos de aceptación suficientes** con entrada, acción y resultado esperado. Pueden escribirse como «Dado / Cuando / Entonces» si ayudan, pero no es obligatorio. Una checklist de aceptación en la HU sirve para comprobar el resultado, no para describir cada paso de programación.
4. **Reglas y límites confirmados**, dependencias, preguntas todavía abiertas y enlace a la fuente pertinente.
5. **Prioridad, fase y esfuerzo estimado**, separados entre sí.

No existe un máximo universal de criterios de aceptación. Usar los necesarios para demostrar el camino principal y límites relevantes; si la lista crece porque aparecen varios resultados independientes, proponer dividir la HU. «Registrar ventanas», «calcular cortes» y «asignar códigos de taller» son capacidades distintas que pueden tener aceptación propia, aunque se encadenen en un mismo flujo. El usuario confirmó separar la captura de `HU-01` del código visible de `HU-22`: primero se guardan y consultan medidas; después se añaden los códigos A1/A2 con prioridad alta. El cálculo de cortes de `HU-02` no equivale a optimizar material con algoritmos 1D o 2D, que queda para otra etapa.

## Entregas verticales y programación en pareja con IA

La unidad de entrega es un **resultado pequeño, completo y observable desde la web**, útil para el trabajo real dentro de un escenario delimitado. Integrar interfaz, backend y persistencia cuando ese resultado las necesite: por ejemplo, si la aceptación exige reabrir medidas, guardarlas es parte de la misma entrega. No convertir frontend, API y base de datos en tres entregas de negocio independientes ni exigir que toda HU toque forzosamente las tres capas. Una HU puede depender de otra sin dejar de ofrecer un nuevo resultado utilizable.

Antes de programar, el usuario como **Navigator** fija el objetivo, las reglas conocidas, lo excluido y cómo reconocerá que funciona. La IA como **Driver** contrasta ese encargo con el código, señala contradicciones y propone el siguiente paso técnico mínimo. Durante la implementación toma decisiones técnicas pequeñas y reversibles, muestra el resultado integrado y la evidencia de comprobación; eleva decisiones de negocio, expansión de alcance o refactorización significativa al usuario. El usuario valida el flujo de vidriería; la IA no transforma fuentes externas en reglas del negocio.

**Ramas desde la segunda entrega:** crear una rama corta desde `develop` para cada subtarea. Revisar e integrar por PR a `develop`, ejecutar allí las pruebas pertinentes y comprobar el flujo web con el usuario. Tras su aceptación, integrar `develop` en `main`, que conserva el código estable. La rama `develop` permite integración previa, pero no simula producción por sí sola; configurar un entorno equivalente se decidirá cuando exista un despliegue real. La primera subtarea de HU-01 llegó a `main` antes de adoptar esta política.

Comenzar con el código y las validaciones **mínimos suficientes**, no con todo el endurecimiento futuro. Mantener desde la primera entrega las comprobaciones que eviten medidas o cortes incorrectos, pérdida de información exigida por la HU y exposición innecesaria de datos. Para cálculos, contrastar con ejemplos independientes confirmados en `docs/domain/Medidas.md`; para guardar y reabrir, comprobar el recorrido completo. Incorporar abstracciones y robustez adicional cuando un caso real, repetición o fallo lo justifique. Lo que se aprenda del uso puede originar otra HU, bug o mejora; no se añade silenciosamente a la entrega activa.

Este proceso toma de [hola-ai](https://github.com/nschurmann/hola-ai) sus ideas de historia vertical, alcance explícito y humano al mando. Sus límites fijos de 10–15 HU, 2–3 criterios, 50 líneas y pausas después de cada prueba no son reglas de AVAO: podrían fragmentar trabajo sin beneficio o hacer impráctica una sola persona asistida por IA. El [concepto de historias de Agile Alliance](https://agilealliance.org/glossary/user-stories/) respalda los incrementos de valor, y su [descripción de pair programming](https://agilealliance.org/glossary/pair-programming/) inspira los papeles Driver/Navigator; en AVAO se adaptan porque uno de los participantes es una IA.

La información lejana puede permanecer breve. Refinar con más detalle solo las HU que se acercan al trabajo. Una **épica** agrupa varias historias. En AVAO, las **subtareas de implementación** serán sub-issues vinculadas a la HU: describen qué hará el desarrollador y podrán tener su propio estado en el tablero. Los **criterios de aceptación** permanecen en la HU y se revisan al terminar las subtareas. Si una parte entrega valor comprobable por sí misma, puede ser otra historia; dividir un tema solo por «frontend» y «backend» puede dejar resultados incompletos. [Agile Alliance sobre historias](https://agilealliance.org/glossary/user-stories/) y [división de historias](https://agilealliance.org/agile101/agile-glossary/) respaldan la distinción.

## 2. Esfuerzo numérico sin falsa precisión

Adoptar la preferencia del usuario como **regla local**: escala relativa `1, 2, 3, 5, 8`; al preparar una HU para trabajar, si parece **mayor que 8**, dividirla en dos o más HU menores que, juntas, cubran el alcance original y tengan resultados comprobables. Por ejemplo, `HU5.1` y `HU5.2` pueden sustituir a `HU5`. La HU original se cierra como reemplazada y se archiva del Project tras enlazar las nuevas; no se borra el historial. Las HU lejanas pueden quedar sin estimar y sin subdividir hasta que se acerquen al trabajo. Esta escala es una elección de AVAO, no un mandato de IEEE o Kanban. [Agile Alliance explica la estimación relativa](https://agilealliance.org/glossary/relative-estimation/) y ofrece escalas numéricas como ejemplo en su [material de prácticas](https://www.agilealliance.org/wp-content/uploads/2018/12/08.031.17-Agile-Playbook-2.1-v12-One-Per-Student.pdf).

Comparar cada historia con una referencia pequeña ya terminada, considerando cambios, integración, comprobación e incertidumbre. Los números **no son horas ni prioridades**. Tras varias entregas, revisar cuánto tardaron realmente las historias y ajustar la referencia si deja de ser útil. Las seis HU altas de [Backlog.md](../product/Backlog.md) tienen estimación inicial revisable; `HU-01` y `HU-22` están en 5 cada una. Si alguna pasa de 8, se divide entonces. El resto permanece sin puntos hasta acercarse a su turno.

## 3. Prioridad y alcance

**Áreas y épicas.** «Medidas», «Taller», «Precios» e «Inventario» funcionan como **áreas temáticas**: sirven para filtrar HU por asunto, pero no expresan un resultado que pueda darse por terminado. Una **épica** representa un resultado amplio compuesto por varias HU, por ejemplo «Obtener cortes de aluminio y vidrio a partir de las medidas capturadas» o «Completar el pedido desde el presupuesto hasta la liquidación». No se crea una épica por cada área ni se estiman las épicas ahora. Un campo `Épica` puede clasificar las HU; las subtareas sí pueden ser incidencias hijas de su HU. La [Agile Alliance](https://agilealliance.org/glossary/epic/) distingue las épicas grandes de los temas usados para agrupar historias y advierte contra jerarquías demasiado elaboradas.

En **AVAO-OLD**, el campo de selección llamado `Épica` contiene opciones como «Organizar el Trabajo» y «Ahorrar Material». Esas opciones describen **temas u objetivos generales**, no las épicas de resultado definidas para el nuevo backlog. El tablero vigente puede usar un campo `Épica` con E1–E4 para agrupar HU; una etiqueta `Área` se añade si ayuda a filtrar. Crear incidencias padre de épica se deja para cuando se necesite seguimiento propio de decisiones o progreso. No hace falta cambiar el tablero antiguo ni copiar automáticamente sus opciones.

- **Fase:** primer MVP de medidas y taller; cierre comercial con fórmula sencilla; control de precios posterior; otras ideas.
- **Prioridad:** seis **Altas** para preparar a continuación; otras del primer MVP en **Media**; las etapas posteriores quedan por priorizar. Una nueva necesidad puede cambiar ese orden. Alta no significa que las seis se ejecuten a la vez: sigue vigente el límite de una subtarea En proceso.
- **Esfuerzo:** campo numérico independiente. Una historia de poco esfuerzo no se vuelve prioritaria por eso solo; una de alto valor puede necesitar dividirse antes de empezar.

El usuario decide valor y prioridades. Las dependencias ayudan a decidir el orden de implementación, pero no sustituyen esa decisión. `HU-10` —cambiar entre pedidos cuando falta material— permanece en prioridad Media; se puede subir si las pruebas del primer grupo muestran que es indispensable para avanzar con varios pedidos.

## 4. HU en backlog y subtareas en el tablero

Mantener `docs/product/Backlog.md` como lista y contexto de producto mientras se trasladan las HU. No abrir una carpeta con un Markdown por cada historia por anticipado: dividiría un documento aún manejable y duplicaría información frente a GitHub. Al activar una HU, sus criterios y subtareas pueden vivir en su incidencia y sub-issues del Project; enlazar desde allí anexos duraderos de dominio o diseño, como el esquema SQL de HU-01, cuando aporten detalle real. Evitar copiar manualmente el estado o el texto completo en dos lugares.

La [Guía Kanban de mayo de 2025](https://kanbanguides.org/the-kanban-guide) pide definir qué elemento fluye, cuándo empieza y termina y cómo se controla el trabajo en curso; no obliga a que la unidad del tablero sea siempre una HU. Para AVAO, el usuario prefiere dos vistas del mismo GitHub Project: **Backlog de HU** en tabla y **Tablero de subtareas**. La HU es una incidencia padre de sus subtareas y permanece en `Backlog` con su [progreso de sub-issues](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-parent-issue-and-sub-issue-progress-fields). Al cumplir sus criterios de aceptación pasa a `Finalizado`. Las subtareas son incidencias hijas que recorren el tablero. Las épicas pueden ser un campo de clasificación; no requieren incidencias padre hasta que su seguimiento aporte valor. GitHub Projects permite [filtrar por incidencia padre](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects) y configurar [vistas de tabla y tablero](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/changing-the-layout-of-a-view).

**Tablero de subtareas acordado:** Por hacer → En proceso → Finalizado. Mantener como máximo **cinco subtareas preparadas en Por hacer** y **una En proceso** para el desarrollador individual. El límite de cinco es para una cola preparada, no equivale a cinco tareas en curso. Si una subtarea se bloquea, registrar causa y siguiente acción antes de seleccionar otra; se puede usar una etiqueta «Bloqueada» sin ocultar su estado. Revisar el límite si la experiencia real lo pide. La guía Kanban permite definir estas políticas según el contexto.

**Responsabilidad de actualización:** el usuario mueve las tarjetas del Project y confirma la aceptación funcional. El agente comprueba que la subtarea seleccionada corresponde al momento del flujo y cierra la issue después de esa aprobación; no mueve el estado del Project por su cuenta.

**Relación entre HU y subtareas:**

- **Checklist de aceptación en la HU:** comprueba lo que debe observar el usuario. No sustituye las subtareas de desarrollo.
- [Sub-issues de GitHub](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues): tareas concretas para construir, integrar o verificar la HU; su estado viaja por el tablero. La barra de progreso cuenta subtareas terminadas, **no garantiza que el resultado ya cumpla la HU**.
- Al cerrar las subtareas, comprobar los criterios de aceptación de la HU. Si faltan, añadir la subtarea necesaria o corregir el trabajo; cerrar la HU solo después de aceptar el resultado. Una solicitud de cambio (PR) enlazada aporta evidencia, pero su cierre tampoco basta por sí solo.
- Si una HU se divide en `HU5.1` y `HU5.2`, esas nuevas incidencias son **HU**, no subtareas técnicas de `HU5`; cada una tendrá sus propios criterios y subtareas cuando llegue su turno.

## 5. Mantener el tablero legible

Los campos observados en la referencia y su uso propuesto para el tablero nuevo son:

| Campo | Configuración del nuevo tablero |
| --- | --- |
| `Épica` | Selección única con E1–E4 para agrupar historias por resultado. Un campo de área o etiquetas se añade solo si facilita una vista útil. |
| `Status` | Selección única: `Backlog`, `Por hacer`, `En proceso`, `Finalizado`. Las HU permanecen en `Backlog` mientras estén abiertas; las subtareas pasan por los tres estados de ejecución. Una HU aceptada pasa a `Finalizado`. |
| `Prioridad` | Selección única: `Alta`, `Media`, `Baja`. Puede quedar sin valor para HU futuras aún no priorizadas. |
| `Esfuerzo` | Número relativo `1`, `2`, `3`, `5` u `8` en las HU listas para trabajar. No se asigna a épicas ni se fuerza para HU futuras. |
| `Sub-issues progress` | Campo integrado de progreso, con barra segmentada y valor numérico (`2 / 5`, `40 %`). En una HU refleja subtareas cerradas; no equivale a aceptación automática. El campo `Épica` no tiene barra de progreso propia. |

Distinguir HU y subtareas con un tipo de incidencia o etiquetas sencillas para filtrar. Usar una vista **Backlog** en tabla para HU, con progreso, prioridad y esfuerzo, y una vista **Trabajo activo** en tablero para subtareas. El mismo Project ofrece ambas vistas sin duplicar tarjetas. Crear incidencias de épica solo si el campo ya no alcanza para seguir decisiones o progreso. No se necesita un campo adicional `Fase`: la etapa del plan está descrita en el backlog. GitHub Projects admite [campos numéricos](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-text-and-number-fields), [campos de selección](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields) y [progreso de sub-issues](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-parent-issue-and-sub-issue-progress-fields).

Revisar periódicamente que cada subtarea activa tenga siguiente paso, que las bloqueadas indiquen causa, que los duplicados se relacionen y que lo descartado no parezca trabajo pendiente. Al completar una HU, cerrar su incidencia tras comprobar la aceptación; se puede [archivar su tarjeta del Project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/archiving-items-from-your-project) para despejar la vista conservando el registro. Una HU reemplazada por varias se cierra con enlaces a sus sucesoras y se archiva, sin eliminar su historia. Evitar copiar manualmente el mismo estado a Markdown, Slack y Projects: Projects debe contener el estado vigente una vez adoptado.

## 6. Enlaces externos, Slack y otras fuentes

El tablero no necesita una tarjeta llamada «Slack» ni una integración solo para poder abrirlo. Los elementos nativos de Projects son incidencias, PR y borradores. Cuando un mensaje de Slack, fotografía, dibujo, documento, diseño o cálculo externo **justifica una decisión, contiene un ejemplo de aceptación o es necesario para realizar una historia**, poner un enlace en la **incidencia concreta**, acompañado de un resumen de la decisión o del dato. GitHub admite [enlaces Markdown y URLs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax). Un enlace por sí solo puede dejar el contexto inaccesible si cambia el permiso o desaparece el mensaje.

Conviene enlazar: la hoja de medidas validada para una historia de cálculo, el ejemplo de precio cuando se confirme, una decisión de negocio sobre redondeo o una evidencia de prueba. No conviene crear tarjetas para conversaciones generales, todos los mensajes de Slack o material sin relación con una decisión. Evitar colocar datos personales de clientes en incidencias visibles a personas que no deban acceder a ellos.

## Fuentes principales consultadas

- [ISO/IEC/IEEE 29148:2018, plataforma ISO](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A29148%3Aed-2%3Av1%3Aen)
- [Agile Alliance: historias de usuario](https://agilealliance.org/glossary/user-stories/), [INVEST](https://agilealliance.org/glossary/invest/), [estimación relativa](https://agilealliance.org/glossary/relative-estimation/) y [tres C](https://agilealliance.org/glossary/three-cs/)
- [Kanban Guide, mayo de 2025](https://kanbanguides.org/the-kanban-guide)
- [GitHub Docs: Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects), [sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues), [automatizaciones](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations) y [archivo](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/archiving-items-from-your-project)
