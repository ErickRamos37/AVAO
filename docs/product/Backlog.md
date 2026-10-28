# Backlog de producto AVAO

> Definición de las HU. Cuando se trasladen a GitHub Projects, allí se llevará el estado diario. Las seis HU altas son el próximo grupo de trabajo; las demás conservan solo el detalle conocido para evitar refinamiento prematuro.

## Organización y reglas

- **Área** clasifica por asunto: **Pedidos y medidas**, **Cortes y taller**, **Precios y cobros**, **Instalación**, **Materiales** o **Visibilidad**. No es una HU ni un entregable.
- **Épica** agrupa varias HU hacia un resultado amplio. No se crea para una sola HU ni se le asignan puntos. Puede representarse por un campo `Épica` en GitHub Projects; solo se crea una incidencia padre cuando seguir su progreso o decisiones propias aporte valor. El área es una clasificación temática. Véase [GuiaBacklogKanban.md](../workflow/GuiaBacklogKanban.md).
- **HU** expresa una capacidad comprobable con **Como**, **necesito** y **para**. **Quiero** puede señalar una mejora opcional expresamente clasificada así por el usuario; el verbo por sí solo no define prioridad ni MVP. Sus criterios de aceptación prueban el resultado; las subtareas describirán el trabajo del programador. Una HU próxima debe entregar un recorrido utilizable, no una capa técnica aislada.
- **Esfuerzo** usa la escala relativa `1, 2, 3, 5, 8`. Se estima solo el grupo alto próximo. Si al refinar una HU supera 8, se sustituye por dos o más HU menores que juntas cubran el alcance; se enlaza, cierra y archiva la original sin borrar su historia. Las HU lejanas esperan sin estimaciones inventadas.
- **Prioridad** y **esfuerzo** son distintos. Las seis altas forman el siguiente grupo; las medias completan el primer MVP de medidas y taller. Las HU de etapas posteriores se priorizarán cuando se acerquen.

## Épicas de resultado

| Épica | Resultado amplio | HU |
| --- | --- | --- |
| E1. Preparar ventanas California para corte | Registrar las dimensiones de fabricación indicadas por el vidriero y obtener cortes identificados por ventana. | HU-01, HU-02, HU-06, HU-22 |
| E2. Seguir la fabricación de pedidos | Saber qué aluminio, vidrio y ventanas están terminados con varios pedidos pendientes. | HU-03, HU-04, HU-05, HU-07, HU-08, HU-09, HU-10, HU-23 |
| E3. Completar un pedido desde presupuesto hasta liquidación | Comunicar total, registrar aceptación y pagos, instalar y cerrar. | HU-11 a HU-17 |
| E4. Actualizar el cálculo comercial desde insumos | Cambiar precios individuales y aplicar ganancia definida. | HU-18, HU-19 |

HU-20 y HU-21 quedan independientes hasta que su alcance justifique agruparlas. El progreso de una épica no reemplaza la aceptación de cada HU.

## Primer MVP: medidas y taller

El vidriero mide el hueco y entrega el ancho y alto **a los que debe fabricarse la ventana**, en pulgadas. El empleado captura esas dimensiones finales; AVAO no calcula una holgura adicional a partir del hueco. Se calculan cortes para la ventana California por mitad, con una hoja fija y una corrediza, y se sigue corte y ensamble. Cada pedido y ventana conserva identidad interna estable. Primero se guardan y consultan las medidas (HU-01); después se asigna el código corto de taller `A1`, `A2`, `B1` (HU-22), que el trabajador escribirá a mano en aluminio y vidrio. La etiqueta del pedido se liberará solo cuando esté **instalado y pagado por completo**; automatizar esa liberación depende del registro posterior de instalación y pagos.

### Seis HU altas para preparar ahora

#### HU-01 — Registrar ventanas medidas en un pedido

- **Área:** Pedidos y medidas · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**. Alcance acotado a guardar y consultar medidas sin datos del cliente ni generación de códigos; revisar al preparar la implementación.
- **Historia:** **Como** empleado que mide, **necesito** registrar y volver a consultar el ancho y alto indicados para fabricar una o más ventanas California dentro de un pedido, **para** conservar las medidas de cada trabajo.
- **Criterios de aceptación:**
  1. Desde un formulario sencillo se puede crear un pedido con una o más ventanas California, cada una con el ancho y alto de fabricación indicados por el vidriero en pulgadas. La entrada admite entero solo o una suma de fracciones como `26 1/2` y `24 1/4 1/16`.
  2. Durante la captura se pueden añadir filas de ventana y descartar una fila **antes de guardar**. Una fila adicional completamente vacía no se guarda; una fila parcialmente llena se señala para que el empleado la complete o descarte. Se requiere al menos una ventana con ambas medidas.
  3. Tras guardar, se pueden listar los pedidos y abrir uno para consultar sus ventanas y medidas. Una medida ingresada como `24 1/4 1/16` puede mostrarse como su fracción simplificada equivalente `24 5/16`; no es necesario conservar la escritura original. Las ventanas se distinguen dentro del pedido y conservan su identidad.
- **Subtareas técnicas propuestas, aún sin crear en el tablero:** cada paso debe producir un resultado comprobable, no una capa aislada.
  1. **Guardar y reabrir un pedido con una ventana:** capturar, guardar y volver a abrir desde la web un pedido con **una** ventana California y sus medidas, incorporando la persistencia, el backend y la interfaz necesarios.
  2. **Capturar varias ventanas y descartar filas antes de guardar:** ampliar ese recorrido para varias ventanas y permitir añadir o descartar filas antes de guardar, sin enviar filas vacías.
  3. **Listar pedidos y consultar sus ventanas:** listar los pedidos y abrir cualquiera para comprobar desde la web sus ventanas y medidas, si esa consulta no quedó cubierta en el primer paso.
- **Fuera de alcance y por decidir:** los datos de cliente y las especificaciones o notas del pedido permanecen en HU-13; el código corto es HU-22; el cálculo es HU-02; corregir o descartar una ventana **ya guardada** es HU-06. Se posponen preferencias avanzadas de presentación de fracciones. Falta decidir el comportamiento de la numeración si más adelante se corrige o descarta una ventana persistida. SQLite es el motor inicial de la primera entrega; no se define aquí un catálogo de productos ni reglas adicionales para las especificaciones.

#### HU-22 — Identificar pedidos y ventanas con códigos cortos de taller

- **Área:** Pedidos y medidas · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**. Incluye asignación y consulta estable de etiquetas y números sin repetir etiquetas entre pedidos activos; la liberación automática requiere HU-16 y HU-17.
- **Historia:** **Como** trabajador del taller, **necesito** ver un código corto para cada ventana de los pedidos activos, **para** escribirlo a mano en sus piezas y distinguirlas durante la fabricación.
- **Criterios de aceptación:**
  1. Al guardar pedidos nuevos se asigna una etiqueta en orden de creación: `A`, `B`, …, `Z`, `AA`, `AB` y así sucesivamente. Cada ventana muestra esa etiqueta seguida de su número existente dentro del pedido, como `A1`, `A2` y `B1`; no se crea una segunda numeración de ventanas.
  2. Los códigos se muestran al consultar el pedido y permanecen iguales al reabrirlo; pedido y ventana conservan identidades internas independientes del código visible. Dos pedidos activos no comparten etiqueta.
  3. Mientras no exista el registro de instalación y liquidación, una etiqueta asignada no se reutiliza. Al integrar HU-16 y HU-17, la liberación seguirá la regla confirmada: pedido instalado **y** pagado por completo.
- **Subtarea técnica propuesta — Asignar y mostrar códigos cortos al guardar pedidos:** integrar en el guardado de un pedido nuevo la asignación de su etiqueta y mostrar el código de cada ventana en la aplicación, usando el número ya guardado. Comprobar con dos pedidos y varias ventanas que aparecen `A1`, `A2` y `B1`, que permanecen al reabrirlos y que la secuencia continúa de `Z` a `AA`. Es un recorrido vertical único; no se separa la asignación de su consulta.
- **Fuera de alcance y por decidir:** los ocho pedidos y 17 ventanas de la base local son datos de prueba y pueden reiniciarse; no se requiere migrarlos ni reiniciarlos automáticamente. La liberación automática espera HU-16 y HU-17. Quedan por decidir el manejo de piezas o papeles remanentes y la numeración tras correcciones de ventanas ya guardadas.

#### HU-02 — Obtener el plan de corte de una ventana California

- **Área:** Cortes y taller · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **8**.
- **Historia:** **Como** trabajador del taller, **necesito** obtener la lista de cortes de aluminio y vidrio a partir de las medidas registradas, **para** preparar las piezas sin repetir los cálculos a mano.
- **Criterios de aceptación:**
  1. Para cada ventana, se muestran perfil, longitud y cantidad de **17 piezas de aluminio** y **dos vidrios iguales** según [Medidas.md](../domain/Medidas.md).
  2. Guía y riel son perfiles físicos distintos aunque compartan longitud. El screen muestra dos piezas de ancho y dos de alto.
  3. Los tres ejemplos de [Medidas.md](../domain/Medidas.md) coinciden; el centro calculado en treintaidosavos se sube al siguiente dieciseisavo antes de obtener cortes dependientes.
  4. Al guardar el pedido se confirman sus ventanas y se calcula y guarda el plan de cortes de cada una. Al reabrir el pedido se consulta ese plan guardado, sin volver a calcularlo por el solo hecho de consultarlo.
- **Subtareas de la HU, ya creadas como subissues #19 y #20:**
  1. **#19 — Plan de aluminio de una ventana confirmada:** al guardar el pedido, calcular y guardar los cortes de aluminio de cada ventana; desde el pedido, mostrar cada tipo de perfil, longitud legible y cantidad requerida conforme a `Medidas.md`, distinguiendo guía de riel. Comprobar que el plan siga disponible al reabrir. Es la primera subtarea preparada para trabajar.
  2. **#20 — Plan de vidrio de esa ventana:** al guardar el pedido, calcular y guardar las medidas y cantidad de dos vidrios iguales de cada ventana; completar la consulta del plan con ancho × alto. Comprobar el resultado integral con los tres ejemplos de `Medidas.md`.
- **Límites confirmados:** las dimensiones registradas ya incorporan el criterio del vidriero al medir el hueco; AVAO no aplica una holgura previa. En esta etapa, confirmar una ventana equivale a guardar el pedido. Cuando HU-06 permita corregir una medida antes de registrar cortes, se mostrará únicamente el plan actualizado con la medida nueva; HU-02 no necesita implementar esa edición. Las marcas de piezas cortadas son HU-03 y HU-04; el ensamble es HU-05; las correcciones después de cortar y sus piezas corresponden a HU-07.

#### HU-03 — Registrar cortes de aluminio

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**.
- **Historia:** **Como** quien corta aluminio, **necesito** marcar las piezas realizadas de cada perfil y medida, **para** ver cuántas faltan sin tachar una hoja.
- **Criterios de aceptación:**
  1. Cada corte muestra cantidad requerida, cortada físicamente y pendiente de corte, asociado al pedido y al código corto de su ventana generado en HU-22, como `A1` o `A2`.
  2. Puede registrarse avance parcial para piezas repetidas; guía y riel se marcan por separado.
  3. El avance permanece al cambiar de ventana o reabrir el pedido y no se mezcla con otra ventana.
  4. Una marca hecha por error de registro puede deshacerse y restaura el conteo anterior sin afectar otra pieza o ventana.
- **Subtarea #22 — Registrar y deshacer marcas de corte de aluminio por ventana:** desde el plan guardado de HU-02, permitir marcar cada corte físico, ver cantidades requeridas, cortadas y pendientes, conservar el avance y corregir una marca accidental. Comprobar el avance parcial con una de dos piezas requeridas y su persistencia al reabrir.
- **Límite confirmado:** «cortada» significa que se hizo el corte físico, aunque aún no se sepa si la pieza es utilizable. Deshacer solo corrige un registro accidental; daños, descartes y retrabajo quedan para otra historia. No incluye ensamble (HU-05). En el caso habitual de una sola persona se trabaja primero el aluminio; con varios trabajadores puede cortarse en paralelo con el vidrio.

#### HU-04 — Registrar cortes de vidrio

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **3**.
- **Historia:** **Como** quien corta vidrio, **necesito** marcar los dos vidrios iguales de cada ventana conforme se cortan, **para** ver cuántos faltan sin contarlos en papel.
- **Criterios de aceptación:**
  1. Se muestran el pedido y el código corto de su ventana generado en HU-22, como `A1` o `A2`, medidas `ancho × alto`, cantidad requerida `2`, cortada físicamente y pendiente de corte.
  2. Puede registrarse uno de los dos vidrios sin declarar completa la pareja.
  3. El avance permanece al cambiar de pedido o reabrirlo y no se confunde con otra ventana de igual medida.
  4. Una marca hecha por error de registro puede deshacerse y restaura el conteo anterior sin afectar otra ventana.
- **Subtarea #23 — Registrar y deshacer marcas de corte de vidrio por ventana:** desde el plan guardado de HU-02, permitir marcar por separado los dos cortes físicos, ver cantidades requeridas, cortadas y pendientes, conservar el avance y corregir una marca accidental. Comprobar la secuencia `1 de 2` → `2 de 2` → `1 de 2` y que otra ventana de igual medida no cambia.
- **Límite confirmado:** «cortada» acredita el corte físico, no que el vidrio sea utilizable. Deshacer solo corrige un registro accidental; daños, descartes y retrabajo quedan para otra historia. No incluye ensamble (HU-05). HU-04 puede trabajarse en paralelo con HU-03 y no depende técnicamente de ella.

#### HU-05 — Marcar ventanas ensambladas

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **3**.
- **Historia:** **Como** ensamblador, **necesito** indicar qué ventanas están ensambladas y cuáles faltan, **para** conocer el avance real del pedido.
- **Criterios de aceptación:**
  1. En el pedido abierto se muestran el código y el estado de ensamble de cada una de sus ventanas; se distinguen las ensambladas de las pendientes sin mostrar ventanas de otros pedidos.
  2. AVAO solo permite marcar ensamblada una ventana cuando todos sus cortes de aluminio y vidrio registrados están marcados. El ensamblador confirma físicamente que todas sus partes están ensambladas, incluidos screen, accesorios y extras aplicables, aunque AVAO no lleve un registro individual de estos últimos.
  3. El estado permanece al reabrir el pedido y no cambia el de otra ventana o pedido. Una marca de ensamble accidental puede deshacerse.
  4. Mientras una ventana esté marcada como ensamblada, AVAO impide deshacer marcas de corte de aluminio o vidrio; primero debe deshacerse la marca de ensamble.
  5. Marcar una ventana no declara instalado ni pagado el pedido, ni declara completo el ensamble de todas sus ventanas.
- **Subtarea #27 — Registrar y deshacer el ensamble de ventanas del pedido:** mostrar el estado por ventana en el pedido abierto, permitir marcarla ensamblada solo sin cortes pendientes y conservar el avance al reabrir. Permitir deshacer una marca de ensamble accidental y bloquear la reversión de marcas de corte mientras siga ensamblada. Comprobar con dos ventanas que el estado y los bloqueos afectan solo a la ventana correspondiente.
- **Límites confirmados:** AVAO comprueba las marcas de cortes registrados; el ensamblador verifica físicamente screen, accesorios y extras aplicables. No se añade seguimiento de esas partes ni se automatiza la declaración de pedido listo (HU-08). Las correcciones por retrabajo quedan fuera de esta entrega. Una sección mínima de ensamble pertenece a HU-05; separar por completo medidas, aluminio, vidrio y ensamble en vistas propias sigue como posible mejora independiente, sin prioridad asignada.

### Otras HU del primer MVP, por refinar cuando se acerquen

| ID | Área · Épica | Prioridad | Esfuerzo | Historia y límite conocido |
| --- | --- | --- | --- | --- |
| HU-06 | Pedidos y medidas · E1 | Media | Pendiente | **Como** empleado, **necesito** corregir o descartar una ventana ya guardada, **para** evitar que una medida errónea llegue al cálculo. Quitar filas antes del primer guardado forma parte de HU-01; falta decidir qué ocurre tras confirmar un pedido y cómo afecta la numeración. |
| HU-07 | Cortes y taller · E2 | Media | Pendiente | **Como** trabajador del taller, **necesito** registrar una corrección de medida y qué piezas se recortan, rehacen o reutilizan, **para** fabricar la ventana correcta sin confundirla con cortes anteriores. Un error del negocio no cambia el precio pactado. |
| HU-08 | Cortes y taller · E2 | Media | Pendiente | **Como** trabajador del taller, **necesito** señalar que todas las ventanas del pedido están ensambladas, **para** distinguir un pedido listo para coordinar instalación de una sola ventana terminada. Al refinarla, comprobar si basta derivar este dato del estado de cada ventana en HU-05, sin crear un segundo estado manual divergente. |
| HU-09 | Cortes y taller · E2 | Media | Pendiente | **Como** empleado, **necesito** consultar los pedidos del taller y sus pendientes de corte y ensamble, **para** retomar el trabajo que corresponde. La forma de la pantalla sigue abierta. |
| HU-10 | Pedidos y medidas · E2 | Media | Pendiente | **Como** empleado, **necesito** cambiar entre pedidos pendientes sin perder su avance, **para** continuar con otro cuando falta material para el actual. Un cliente puede tener varios pedidos y cada pedido varias ventanas. |
| HU-23 | Pedidos y medidas · E2 | Media | Pendiente | **Como** empleado, **necesito** consultar los pedidos en orden de llegada a AVAO, **para** reconocer cuál se registró primero y abrir el que convenga atender. La llegada ocurre al guardar el pedido. La lista muestra una posición calculada y `Pedido A`, `Pedido B`, etc.; abrir B antes que A no cambia el orden. La posición no es el ID interno ni la etiqueta reutilizable. Por ahora se muestran los pedidos guardados: retirar de la cola a uno instalado **y** pagado depende de HU-16 y HU-17; entonces se recalculan las posiciones restantes. **Prioridad Media confirmada; se trabaja después de HU-02.** |

## Siguiente etapa: precio sencillo, instalación y liquidación

Flujo final: **empleado captura ventanas → calcula precio y servicios → comunica total → registra datos del cliente y anticipo si acepta → confirma pedido → taller fabrica → se instala → se liquida saldo**. No hay interfaz del cliente prevista. La fórmula sencilla actual de precios aún debe documentarse con ejemplos; la antigua tabla de rangos de medidas no se adopta porque las ventanas varían mucho. Estas HU no reciben puntos todavía.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-11 | Precios y cobros · E3 | **Como** empleado, **necesito** calcular el precio de las ventanas registradas con el método sencillo actual, **para** comunicar al cliente el total calculado. | Fórmula, insumos y ejemplos reales. |
| HU-12 | Precios y cobros · E3 | **Como** empleado, **necesito** añadir servicios aplicables, como visita a domicilio e instalación, **para** comunicar un total que incluya el trabajo ofrecido. | Reglas de cobro por servicio. |
| HU-13 | Pedidos y medidas · E3 | **Como** empleado, **necesito** registrar nombre, teléfono, dirección simplificada y especificaciones del cliente en su pedido, **para** conservar los datos del trabajo aceptado. | Datos obligatorios y faltantes. |
| HU-14 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar anticipo y confirmar el pedido aceptado, **para** iniciar el trabajo con total y saldo visibles. | Varios anticipos, cancelación y cambios posteriores. |
| HU-15 | Instalación · E3 | **Como** empleado, **necesito** registrar día y, si se acuerda, hora de instalación, **para** coordinar la visita con el cliente. | Reprogramación e instalación parcial. |
| HU-16 | Instalación · E3 | **Como** instalador, **necesito** marcar el pedido instalado, **para** distinguir la entrega física de la liquidación del saldo. | Criterio de instalación completa. |
| HU-17 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar pagos posteriores y la liquidación final, **para** conocer el saldo y cerrar el pedido cuando esté instalado y pagado por completo. | Pagos parciales, ajustes y comprobantes. Su estado de cierre habilita la liberación de la etiqueta definida en HU-22. |

## Etapa posterior: precios flexibles y otras capacidades

Sin prioridad ni esfuerzo asignados hasta comprobar medidas, taller y cierre comercial con la fórmula sencilla.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-18 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** mantener precios de perfiles, vidrios y accesorios por medida, tramo o unidad, **para** actualizar un insumo sin rehacer manualmente todos los presupuestos. | Costo frente a venta, longitud del tramo, unidades y desperdicio. |
| HU-19 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** aplicar a cada ventana un porcentaje de ganancia elegido, **para** calcular su precio a partir de insumos actualizados. | Recargo sobre costo frente a margen sobre venta; mano de obra y servicios. |
| HU-20 | Visibilidad · Sin épica | **Como** encargado del negocio, **necesito** ver pedidos pendientes, en fabricación, listos, instalados y liquidados, **para** consultar su situación desde un lugar. | Estados confiables e indicador de avance verificable. |
| HU-21 | Materiales · Sin épica | **Como** encargado de materiales, **necesito** estimar perfiles y hojas de vidrio requeridos por los pedidos actuales, **para** anticipar compras cuando hagan falta. | Demanda frente a faltantes, existencias, unidades de compra, sobrantes y desperdicio. |

## Reglas transversales confirmadas

- Para California por mitad se usan las fórmulas, cantidades y tres ejemplos de [Medidas.md](../domain/Medidas.md): **17 piezas de aluminio y dos vidrios iguales**. Si el centro matemático cae en treintaidosavos, se **sube al siguiente dieciseisavo** antes de obtener sus cortes dependientes.
- El negocio asume sus errores de medición sin cambiar el precio acordado con el cliente. Puede recortar una ventana demasiado grande, rehacer una demasiado pequeña o reutilizar piezas cuya dimensión era correcta.
- Un pedido tiene una o más ventanas y un cliente puede tener varios pedidos. Otros tipos de ventana, puertas y productos quedan fuera del primer cálculo.
- La etiqueta corta de letras pertenece a un solo pedido activo. La secuencia sigue `A`…`Z`, `AA`, `AB`…; se libera únicamente cuando el pedido está **instalado y pagado por completo**. La identidad interna permanece única aunque una etiqueta visible vuelva a usarse. Falta decidir sobre piezas o papeles remanentes.
- La aceptación de una HU requiere comprobar su resultado. El progreso de subtareas informa trabajo terminado, pero no sustituye los criterios de aceptación. Las subtareas de HU lejanas se crean cuando se acerque su implementación.
- La implementación se hará por cortes verticales pequeños: datos, API e interfaz cuando la capacidad los necesite. La primera HU debe poder usarse para capturar y consultar medidas; no se construyen capas completas por adelantado. El usuario decide alcance y prioridad como Navigator y la IA ejecuta la entrega acordada como Driver.
- La optimización de cortes 1D de perfiles y 2D tipo guillotina de vidrio son propuestas **opcionales** para evaluar después. No forman parte de las HU del primer MVP ni se convierten en requisitos por aparecer aquí.
