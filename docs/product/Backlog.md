# Backlog de producto AVAO

> Definición y registro histórico de las HU. GitHub Projects conserva el estado diario; este archivo conserva ciclos, historias, estimaciones de esfuerzo y resultados. Al cerrar un ciclo, se retira la prioridad operativa, pero se mantienen sus HU y estimaciones como historial.

## Organización y reglas

- **Área** clasifica por asunto: **Pedidos y medidas**, **Cortes y taller**, **Precios y cobros**, **Instalación**, **Materiales** o **Visibilidad**. No es una HU ni un entregable.
- **Épica** agrupa varias HU hacia un resultado amplio. No se crea para una sola HU ni se le asignan puntos. Puede representarse por un campo `Épica` en GitHub Projects; solo se crea una incidencia padre cuando seguir su progreso o decisiones propias aporte valor. El área es una clasificación temática. Véase [GuiaBacklogKanban.md](../workflow/GuiaBacklogKanban.md).
- **HU** expresa una capacidad comprobable con **Como**, **necesito** y **para**. **Quiero** puede señalar una mejora opcional expresamente clasificada así por el usuario; el verbo por sí solo no define prioridad ni MVP. Sus criterios de aceptación prueban el resultado; las subtareas describirán el trabajo del programador. Una HU próxima debe entregar un recorrido utilizable, no una capa técnica aislada.
- **Esfuerzo** usa la escala relativa `1, 2, 3, 5, 8`. Las estimaciones ya registradas se conservan como dato histórico aunque el ciclo termine. Si al refinar una HU supera 8, se sustituye por dos o más HU menores que juntas cubran el alcance; se enlaza, cierra y archiva la original sin borrar su historia.
- **Prioridad** y **esfuerzo** son distintos. La prioridad se usa para ordenar trabajo pendiente dentro del ciclo actual; al terminar el ciclo se limpia ese campo, sin borrar el ciclo ni la estimación histórica.

## Épicas de resultado

| Épica | Resultado amplio | HU |
| --- | --- | --- |
| E1. Preparar ventanas California para corte | Registrar las dimensiones de fabricación indicadas por el vidriero y obtener cortes identificados por ventana. | HU-01, HU-02, HU-06, HU-22 |
| E2. Seguir la fabricación de pedidos | Saber qué aluminio, vidrio y ventanas están terminados con varios pedidos pendientes. | HU-03, HU-04, HU-05, HU-07, HU-08, HU-09, HU-10, HU-23 |
| E3. Completar un pedido desde presupuesto hasta liquidación | Comunicar total, registrar aceptación y pagos, instalar y cerrar. | HU-11 a HU-17 |
| E4. Actualizar el cálculo comercial desde insumos | Cambiar precios individuales y aplicar ganancia definida. | HU-18, HU-19 |

HU-20, HU-21 y HU-24 quedan independientes hasta que su alcance justifique agruparlas. El progreso de una épica no reemplaza la aceptación de cada HU.

## Ciclo 1 completado: medidas y taller

El vidriero mide el hueco y entrega el ancho y alto **a los que debe fabricarse la ventana**, en pulgadas. El empleado captura esas dimensiones finales; AVAO no calcula una holgura adicional a partir del hueco. Se calculan cortes para la ventana California por mitad, con una hoja fija y una corrediza, y se sigue corte y ensamble. Cada pedido y ventana conserva identidad interna estable. Primero se guardan y consultan las medidas (HU-01); después se asigna el código corto de taller `A1`, `A2`, `B1` (HU-22), que el trabajador escribirá a mano en aluminio y vidrio. La etiqueta del pedido se liberará solo cuando esté **instalado y pagado por completo**; automatizar esa liberación depende del registro posterior de instalación y pagos.

### Resumen histórico del Ciclo 1

| Orden | HU | Épica | Prioridad actual | Esfuerzo histórico | Resultado |
| --- | --- | --- | --- | ---: | --- |
| 1 | HU-01 | E1 | — | 5 | Completada |
| 2 | HU-22 | E1 | — | 5 | Completada |
| 3 | HU-02 | E1 | — | 8 | Completada |
| 4 | HU-03 | E2 | — | 5 | Completada |
| 5 | HU-04 | E2 | — | 3 | Completada |
| 6 | HU-05 | E2 | — | 3 | Completada |

Las HU completas se conservan a continuación como especificación e historial del ciclo.

#### HU-01 — Registrar ventanas medidas en un pedido

- **Área:** Pedidos y medidas · **Épica:** E1 · **Esfuerzo histórico:** **5**. Alcance acotado a guardar y consultar medidas sin datos del cliente ni generación de códigos.
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

- **Área:** Pedidos y medidas · **Épica:** E1 · **Esfuerzo histórico:** **5**. Incluye asignación y consulta estable de etiquetas y números sin repetir etiquetas entre pedidos activos; la liberación automática requiere HU-16 y HU-17.
- **Historia:** **Como** trabajador del taller, **necesito** ver un código corto para cada ventana de los pedidos activos, **para** escribirlo a mano en sus piezas y distinguirlas durante la fabricación.
- **Criterios de aceptación:**
  1. Al guardar pedidos nuevos se asigna una etiqueta en orden de creación: `A`, `B`, …, `Z`, `AA`, `AB` y así sucesivamente. Cada ventana muestra esa etiqueta seguida de su número existente dentro del pedido, como `A1`, `A2` y `B1`; no se crea una segunda numeración de ventanas.
  2. Los códigos se muestran al consultar el pedido y permanecen iguales al reabrirlo; pedido y ventana conservan identidades internas independientes del código visible. Dos pedidos activos no comparten etiqueta.
  3. Mientras no exista el registro de instalación y liquidación, una etiqueta asignada no se reutiliza. Al integrar HU-16 y HU-17, la liberación seguirá la regla confirmada: pedido instalado **y** pagado por completo.
- **Subtarea técnica propuesta — Asignar y mostrar códigos cortos al guardar pedidos:** integrar en el guardado de un pedido nuevo la asignación de su etiqueta y mostrar el código de cada ventana en la aplicación, usando el número ya guardado. Comprobar con dos pedidos y varias ventanas que aparecen `A1`, `A2` y `B1`, que permanecen al reabrirlos y que la secuencia continúa de `Z` a `AA`. Es un recorrido vertical único; no se separa la asignación de su consulta.
- **Fuera de alcance y por decidir:** los ocho pedidos y 17 ventanas de la base local son datos de prueba y pueden reiniciarse; no se requiere migrarlos ni reiniciarlos automáticamente. La liberación automática espera HU-16 y HU-17. Quedan por decidir el manejo de piezas o papeles remanentes y la numeración tras correcciones de ventanas ya guardadas.

#### HU-02 — Obtener el plan de corte de una ventana California

- **Área:** Cortes y taller · **Épica:** E1 · **Esfuerzo histórico:** **8**.
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

- **Área:** Cortes y taller · **Épica:** E2 · **Esfuerzo histórico:** **5**.
- **Historia:** **Como** quien corta aluminio, **necesito** marcar las piezas realizadas de cada perfil y medida, **para** ver cuántas faltan sin tachar una hoja.
- **Criterios de aceptación:**
  1. Cada corte muestra cantidad requerida, cortada físicamente y pendiente de corte, asociado al pedido y al código corto de su ventana generado en HU-22, como `A1` o `A2`.
  2. Puede registrarse avance parcial para piezas repetidas; guía y riel se marcan por separado.
  3. El avance permanece al cambiar de ventana o reabrir el pedido y no se mezcla con otra ventana.
  4. Una marca hecha por error de registro puede deshacerse y restaura el conteo anterior sin afectar otra pieza o ventana.
- **Subtarea #22 — Registrar y deshacer marcas de corte de aluminio por ventana:** desde el plan guardado de HU-02, permitir marcar cada corte físico, ver cantidades requeridas, cortadas y pendientes, conservar el avance y corregir una marca accidental. Comprobar el avance parcial con una de dos piezas requeridas y su persistencia al reabrir.
- **Límite confirmado:** «cortada» significa que se hizo el corte físico, aunque aún no se sepa si la pieza es utilizable. Deshacer solo corrige un registro accidental; daños, descartes y retrabajo quedan para otra historia. No incluye ensamble (HU-05). En el caso habitual de una sola persona se trabaja primero el aluminio; con varios trabajadores puede cortarse en paralelo con el vidrio.

#### HU-04 — Registrar cortes de vidrio

- **Área:** Cortes y taller · **Épica:** E2 · **Esfuerzo histórico:** **3**.
- **Historia:** **Como** quien corta vidrio, **necesito** marcar los dos vidrios iguales de cada ventana conforme se cortan, **para** ver cuántos faltan sin contarlos en papel.
- **Criterios de aceptación:**
  1. Se muestran el pedido y el código corto de su ventana generado en HU-22, como `A1` o `A2`, medidas `ancho × alto`, cantidad requerida `2`, cortada físicamente y pendiente de corte.
  2. Puede registrarse uno de los dos vidrios sin declarar completa la pareja.
  3. El avance permanece al cambiar de pedido o reabrirlo y no se confunde con otra ventana de igual medida.
  4. Una marca hecha por error de registro puede deshacerse y restaura el conteo anterior sin afectar otra ventana.
- **Subtarea #23 — Registrar y deshacer marcas de corte de vidrio por ventana:** desde el plan guardado de HU-02, permitir marcar por separado los dos cortes físicos, ver cantidades requeridas, cortadas y pendientes, conservar el avance y corregir una marca accidental. Comprobar la secuencia `1 de 2` → `2 de 2` → `1 de 2` y que otra ventana de igual medida no cambia.
- **Límite confirmado:** «cortada» acredita el corte físico, no que el vidrio sea utilizable. Deshacer solo corrige un registro accidental; daños, descartes y retrabajo quedan para otra historia. No incluye ensamble (HU-05). HU-04 puede trabajarse en paralelo con HU-03 y no depende técnicamente de ella.

#### HU-05 — Marcar ventanas ensambladas

- **Área:** Cortes y taller · **Épica:** E2 · **Esfuerzo histórico:** **3**.
- **Historia:** **Como** ensamblador, **necesito** indicar qué ventanas están ensambladas y cuáles faltan, **para** conocer el avance real del pedido.
- **Criterios de aceptación:**
  1. En el pedido abierto se muestran el código y el estado de ensamble de cada una de sus ventanas; se distinguen las ensambladas de las pendientes sin mostrar ventanas de otros pedidos.
  2. AVAO solo permite marcar ensamblada una ventana cuando todos sus cortes de aluminio y vidrio registrados están marcados. El ensamblador confirma físicamente que todas sus partes están ensambladas, incluidos screen, accesorios y extras aplicables, aunque AVAO no lleve un registro individual de estos últimos.
  3. El estado permanece al reabrir el pedido y no cambia el de otra ventana o pedido. Una marca de ensamble accidental puede deshacerse.
  4. Mientras una ventana esté marcada como ensamblada, AVAO impide deshacer marcas de corte de aluminio o vidrio; primero debe deshacerse la marca de ensamble.
  5. Marcar una ventana no declara instalado ni pagado el pedido, ni declara completo el ensamble de todas sus ventanas.
- **Subtarea #27 — Registrar y deshacer el ensamble de ventanas del pedido:** mostrar el estado por ventana en el pedido abierto, permitir marcarla ensamblada solo sin cortes pendientes y conservar el avance al reabrir. Permitir deshacer una marca de ensamble accidental y bloquear la reversión de marcas de corte mientras siga ensamblada. Comprobar con dos ventanas que el estado y los bloqueos afectan solo a la ventana correspondiente.
- **Límites confirmados:** AVAO comprueba las marcas de cortes registrados; el ensamblador verifica físicamente screen, accesorios y extras aplicables. No se añade seguimiento de esas partes ni se automatiza la declaración de pedido listo (HU-08). Las correcciones por retrabajo quedan fuera de esta entrega. Una sección mínima de ensamble pertenece a HU-05; separar por completo medidas, aluminio, vidrio y ensamble en vistas propias sigue como posible mejora independiente, sin prioridad asignada.

## Ciclo 2: correcciones y seguimiento del taller

HU-07 y HU-09 se completaron; HU-08 y HU-10 quedaron cubiertas por el flujo implementado. HU-13, HU-23 y HU-24 también se incorporaron para completar la captura y consulta del flujo. La única subtarea pendiente de este ciclo es la #52, dependiente de las funciones de precios y registro comercial; por ello HU-06 queda funcionalmente aceptada, con ese ajuste aplazado.

### Resumen histórico del Ciclo 2

| HU | Épica | Prioridad actual | Esfuerzo histórico | Resultado |
| --- | --- | --- | ---: | --- |
| HU-06 | E1 | — | 3 | Implementada; subtarea #52 pendiente por dependencia de precios |
| HU-07 | E2 | — | 8 | Completada y aceptada |
| HU-08 | E2 | — | No consta en el backlog | Cubierta por el ensamble de HU-05 |
| HU-09 | E2 | — | No consta en el backlog | Completada y aceptada (#53) |
| HU-10 | E2 | — | No consta en el backlog | Cubierta por el flujo actual |
| HU-13 | E3 | — | No consta en el backlog | Completada y probada por el usuario |
| HU-23 | E2 | — | No consta en el backlog | Implementada en el flujo de pedidos |
| HU-24 | Sin épica | — | No consta en el backlog | Vistas por área implementadas y aceptadas |

Las HU completas y sus criterios permanecen en las secciones siguientes y en sus apartados específicos; los esfuerzos que no aparecen en el registro disponible se identifican como no documentados, sin estimarlos retrospectivamente.

### HU del primer MVP incorporadas o completadas en el Ciclo 2

| ID | Área · Épica | Prioridad actual | Esfuerzo histórico | Historia y límite conocido |
| --- | --- | --- | --- | --- |
| HU-06 | Pedidos y medidas · E1 | — | 3 | **Como** empleado, **necesito** corregir las medidas de una ventana guardada antes de iniciar sus cortes, o descartarla mientras el pedido siga activo, **para** mantener correctos el plan y el precio del pedido. La corrección, el descarte y la reincorporación están aceptados; queda pendiente el ajuste de precio en la subtarea [#52](https://github.com/ErickRamos37/AVAO/issues/52). Véase [#45](https://github.com/ErickRamos37/AVAO/issues/45). |
| HU-07 | Cortes y taller · E2 | — | 8 | **Como** trabajador del taller, **necesito** corregir las medidas de una ventana después de iniciar sus cortes, **para** continuar su fabricación con el plan actualizado y conservar las marcas que aún aplican. **Terminada:** el usuario aceptó la subtarea [#49](https://github.com/ErickRamos37/AVAO/issues/49); no incluye registrar daños ni decidir si se reutiliza una pieza. Véase [#47](https://github.com/ErickRamos37/AVAO/issues/47). |
| HU-08 | Cortes y taller · E2 | — | Cubierta | **Como** trabajador del taller, **necesito** señalar que todas las ventanas del pedido están ensambladas, **para** distinguir un pedido listo para coordinar instalación de una sola ventana terminada. El flujo actual deriva este resultado del ensamble registrado en sus ventanas (HU-05); el usuario confirmó que está cubierto. |
| HU-09 | Cortes y taller · E2 | — | Terminada | **Como** empleado, **necesito** consultar el avance de los pedidos activos del taller, **para** identificar rápidamente qué trabajo sigue pendiente. Tarjetas por pedido, progreso general con tres áreas de igual peso y desglose; subtarea [#53](https://github.com/ErickRamos37/AVAO/issues/53) aceptada e integrada. |
| HU-10 | Pedidos y medidas · E2 | — | Cubierta | **Como** empleado, **necesito** cambiar entre pedidos pendientes sin perder su avance, **para** continuar con otro cuando falta material para el actual. El flujo actual permite abrir otro pedido y conserva el avance; el usuario confirmó que está cubierto. |
| HU-23 | Pedidos y medidas · E2 | — | Pendiente | **Como** empleado, **necesito** consultar los pedidos en orden de llegada a AVAO, **para** reconocer cuál se registró primero y abrir el que convenga atender. [Issue #17](https://github.com/ErickRamos37/AVAO/issues/17); alcance de esta entrega debajo. |

### HU-06 — Corrección, descarte y reincorporación de ventanas guardadas

- **Subtarea [#48](https://github.com/ErickRamos37/AVAO/issues/48), aceptada — Corregir medidas guardadas antes del primer corte:** cambiar las medidas de cualquiera de las ventanas de un pedido, recalcular su plan y conservar código y posición. La edición puede cancelarse sin guardar. El usuario comprobó el recorrido con varias ventanas.
- **Subtarea [#51](https://github.com/ErickRamos37/AVAO/issues/51), aceptada — Descartar y reincorporar una ventana guardada:** mientras el pedido siga activo, pedir confirmación antes de descartar e indicar si hay cortes marcados o ensamble. Conservar la ventana en una sección de descartadas con sus medidas, plan, marcas, código y posición; permitir reincorporarla con la misma identidad. Una ventana descartada se excluye de cortes, ensamble y progreso pendientes, pero conserva sus marcas. Puede quedar un pedido con cero ventanas activas. El usuario comprobó el recorrido; no incluye borrar definitivamente la ventana ni ajustar el precio.
- **Trabajo futuro [#52](https://github.com/ErickRamos37/AVAO/issues/52) — Actualizar total y saldo al descartar o reincorporar:** restar o sumar el precio de la ventana y actualizar total y saldo del pedido. Depende de disponer del cálculo de precio y el registro comercial en HU-11/HU-14; queda fuera del Ciclo 2 y no es ejecutable hasta que esas capacidades existan. El trato con el cliente corresponde al encargado; no se fija aquí una fórmula de precio.
- **Límite:** HU-07 cubre correcciones después de iniciar cortes. La corrección, descarte y reincorporación están aceptados; el ajuste de precio permanece diferido por su dependencia comercial. El descarte no elimina piezas o marcas de trabajo ya realizado.

### HU-07 — Corrección después de iniciar cortes

- **Subtarea [#49](https://github.com/ErickRamos37/AVAO/issues/49), aceptada — Actualizar el plan y las marcas de corte al corregir medidas:** recalcular aluminio y vidrio; conservar marcas solo para piezas requeridas del mismo tipo y dimensión, hasta la cantidad nueva requerida; desmarcar las que cambien. Si la ventana estaba ensamblada, quitar esa marca. Conservar el código de la ventana. El encargado decide si recorta o sustituye una pieza; no se lleva historial de daños o retrabajo.

### HU-09 — Consulta del avance entre pedidos

- **Subtarea [#53](https://github.com/ErickRamos37/AVAO/issues/53), aceptada — Mostrar avance de pedidos activos en la cola:** presentar una tarjeta por pedido en orden de llegada, con avance general y desglose desplegable de aluminio, vidrio y ensamble. Para cada área, mostrar cantidad terminada frente a cantidad requerida: piezas de aluminio cortadas / piezas de aluminio requeridas; vidrios cortados / vidrios requeridos; ventanas ensambladas / ventanas activas del pedido. El progreso general combina esas tres proporciones con igual peso, sin sumar directamente unidades distintas. Excluir las ventanas descartadas de los pendientes y denominadores de progreso sin perder sus marcas. Identificar los pedidos con todas sus ventanas activas ensambladas como listos para instalación. La subtarea se integró y se cerró.
- **Dependencia y caso sin ventanas activas:** excluir pedidos solo cuando estén instalados y liquidados depende de HU-16/HU-17. Si un pedido tiene cero ventanas activas, mostrar «Sin ventanas activas», sin porcentaje general ni marca de listo para instalación.

### HU-23 — Orden de llegada visible

- **Reglas confirmadas:** un pedido llega al guardarlo en AVAO. La lista muestra una posición calculada y su etiqueta (`1. Pedido A`, `2. Pedido B`, etc.). La posición no reemplaza al ID interno ni a la etiqueta de taller; abrir o trabajar otro pedido no cambia el orden de llegada.
- **Criterios de aceptación:** al guardar A y después B, aparecen en ese orden y cada entrada abre el pedido correcto; al abrir B, volver a la lista o recargar, A sigue primero y B segundo. El detalle identifica el pedido por su etiqueta, por ejemplo `Pedido A`.
- **Subtarea [#41](https://github.com/ErickRamos37/AVAO/issues/41) — Mostrar pedidos con posición de llegada y etiqueta de taller:** adaptar la lista y el encabezado del pedido usando los datos ya guardados; comprobar el recorrido con al menos dos pedidos y el regreso desde el segundo. No persistir una segunda posición si basta calcularla al consultar.
- **Límites:** por ahora se muestran todos los pedidos guardados. Sacar uno de la cola solo cuando esté instalado **y** pagado depende de HU-16 y HU-17; entonces se recalcularán las posiciones visibles. No incluye reordenación manual, resumen de pendientes de corte o ensamble (HU-09) ni cambios al avance al abrir otro pedido (HU-10).

### HU-24 — Consultar un pedido por área de trabajo, completada en Ciclo 2

### HU-24 — Consultar un pedido por área de trabajo

- **Issue:** [AVAO #30](https://github.com/ErickRamos37/AVAO/issues/30).
- **Área:** Visibilidad · sin épica asignada. Esfuerzo no documentado en la versión histórica disponible.
- **Historia:** **Como** empleado que trabaja en un pedido, **necesito** consultar por separado sus medidas, cortes de aluminio, cortes de vidrio y ensamble, **para** concentrarme en la información pertinente a la tarea que realizo.
- **Alcance de esta entrega:** las cuatro vistas pertenecen solo al pedido abierto. «Medidas» consulta las ventanas ya guardadas; la captura de un pedido nuevo sigue en el flujo actual. Los datos del cliente y las notas del pedido deben seguir accesibles, en particular las notas compartidas con los trabajadores; su ubicación exacta no se fija aquí.
- **Criterios de aceptación propuestos:**
  1. Dentro del mismo pedido se puede pasar entre «Medidas», «Aluminio», «Vidrio» y «Ensamble». Cada vista muestra las ventanas de ese pedido, sin mezclar datos de otro.
  2. «Medidas» muestra código y dimensiones de fabricación; «Aluminio» muestra perfiles, longitudes, cantidades y marcas existentes; «Vidrio» muestra código, `ancho × alto`, cantidad y avance, por ejemplo `1 de 2`; «Ensamble» muestra código, estado y acciones existentes. La presentación puede ser una lista o tabla sencilla.
  3. Marcar o deshacer un corte o ensamble conserva las reglas ya aceptadas. Cambiar de vista y reabrir el pedido no altera medidas, planes ni avances; los datos del cliente y las notas siguen disponibles.
- **Subtarea [#43](https://github.com/ErickRamos37/AVAO/issues/43) — Separar la consulta del pedido en cuatro vistas de trabajo:** reorganizar la información y los controles existentes por área dentro del pedido abierto, mantener el acceso a cliente y notas y comprobar navegación y marcas con dos ventanas. No añadir estados, cálculos ni pasos de captura.
- **Límites:** no reúne pendientes de todos los pedidos (HU-09), no agrega cálculos, marcas o estados nuevos a HU-01, HU-03, HU-04 y HU-05, no introduce permisos por área ni fija un diseño visual detallado. Mantener visibles los avisos existentes si un pedido anterior carece de plan de corte.

## Ciclo 3 propuesto: costos y precios de ventanas

El usuario decidió omitir la fórmula sencilla. Este ciclo prepara el costo real de materiales desde el inventario flexible, aplica ganancia al costo total de materiales de cada ventana y muestra el total de ventanas activas del pedido. La aceptación del presupuesto, anticipos y otros cobros quedan para un ciclo posterior. Las prioridades y esfuerzos siguientes son **propuestas iniciales**, no compromisos definitivos.

| Orden | HU | Prioridad propuesta | Esfuerzo inicial propuesto | Dependencias y límites |
| --- | --- | --- | ---: | --- |
| 1 | HU-18 — Mantener costos de compra de insumos de California por mitad | Alta | 3 | Perfiles, vidrio y accesorios ya utilizados en el plan. Registrar/consultar/actualizar costo de compra. Sin existencias, órdenes de compra ni otros productos. |
| 2 | HU-11 — Calcular costo exacto de materiales por ventana | Alta | 5 | Usa cantidades y medidas del plan de corte y costos de HU-18. Valora medidas exactas usadas, sin redondear a tramos comerciales. No recupera desperdicio ni optimiza cortes. |
| 3 | HU-19 — Aplicar ganancia al costo de materiales de una ventana | Alta | 3, provisional | Aplica el porcentaje definido por el usuario sobre el costo total de materiales de la ventana, no por perfil. No incluye servicios ni cobros. Un ejemplo numérico debe confirmar la interpretación antes de fijar aceptación. |
| 4 | HU-25 — Mostrar total de ventanas activas del pedido | Alta | 2 | Suma los precios por ventana y excluye descartadas. No incluye aceptar presupuesto, registrar anticipo o calcular saldo. |
| 5 | HU-12 — Agregar servicios opcionales al pedido | Media, propuesta | Por estimar | Instalación y visita a domicilio como conceptos separados de materiales, asociados al pedido. La visita depende principalmente de distancia. No incluye cotización independiente, mantenimiento, reparaciones ni cobro de recorte/ensamble por separado. Sin regla de importe no está lista para estimarse. |
| 6 | HU-26 — Recuperar desperdicio de perfiles de aluminio según umbral | Media, propuesta | 3, provisional | Depende de HU-18/HU-11. Regla configurable y cobro distribuido entre ventanas del pedido; se limita a aluminio y no implementa optimización 1D. Falta fijar longitud comercial y aplicación del umbral. |

### Fuera del Ciclo 3

| HU | Prioridad | Alcance conocido y dependencia |
| --- | --- | --- |
| HU-27 — Recuperar y distribuir costo de desperdicio de vidrio entre ventanas | Futura, sin asignar | Depende de los costos de HU-18/HU-11. Usa umbrales configurables de consumo de hoja y distribuye el costo recuperado entre ventanas del pedido. No implementa optimización 2D. Quedan por definir dimensiones comerciales de hoja, medida de consumo y ejemplos del umbral. |
| HU-14 — Registrar anticipo y confirmar pedido; HU-15 a HU-17 — instalación y liquidación | Ciclo posterior, sin estimar | Cierre comercial después de que precio y total estén disponibles. |

**Reglas confirmadas:** el inventario guarda costo real de compra; se calcula material por ventana y se aplica ganancia al costo total de materiales de esa ventana; el total suma ventanas activas; el error humano lo asume el negocio y no se cobra como desperdicio. Para perfiles y vidrio se valora la medida exacta utilizada, sin redondear a barras u hojas enteras. Los porcentajes/umbrales de desperdicio son ajustables por el usuario, incluido 0 % para no recuperar desperdicio. El costo que se recupere se distribuye equitativamente entre las ventanas del pedido e integra su costo/precio; no aparece como concepto independiente para el cliente.

**Pendiente de concretar antes de cerrar criterios:** ejemplo numérico del porcentaje de ganancia; qué longitud comercial de perfil se usa para evaluar sobrantes aunque no se optimicen cortes; qué medida comercial de hoja y cálculo de consumo aplican al umbral del vidrio; cómo se asigna recuperación cuando no todas las ventanas comparten el mismo tipo de material. No convertir estos vacíos en reglas supuestas.

HU-13 contiene datos del cliente y notas ya trabajados. No se implementan en este ciclo algoritmos 1D/2D, PWA/aplicación móvil, mantenimiento, reparación, aceptación del presupuesto ni anticipo.

### HU-18 — Mantener costos reales de compra de insumos

- **Área:** Precios y cobros · **Épica:** E4 · **Prioridad/esfuerzo:** Alta / 3 propuestos para Ciclo 3.
- **Historia:** **Como** encargado del negocio, **necesito** registrar, consultar y actualizar el costo real de compra de los insumos usados por la ventana California por mitad, **para** calcular sus costos de materiales con valores vigentes.
- **Criterios de aceptación propuestos:**
  1. El encargado puede consultar y actualizar el costo de cada insumo que usa el plan vigente de California por mitad, incluidos perfiles, vidrio y accesorios definidos para esa ventana.
  2. El sistema conserva para cada valor el insumo al que pertenece y la unidad en que se registra, de modo que HU-11 pueda valorar la cantidad exacta usada.
  3. Cambiar un costo no cambia los cortes ni las marcas de fabricación.
- **Dependencias/límites:** habilita HU-11; no incluye existencias, compras, proveedores, otros tipos de ventana/producto ni el precio final del cliente.
- **Preguntas abiertas:** unidad de compra registrada por cada tipo de insumo y conversión a costo por unidad de cálculo. En perfiles por longitud y vidrio por hoja/área se necesitan datos del proveedor antes de fijar criterios completos.

### HU-11 — Calcular costo exacto de materiales por ventana

- **Área:** Precios y cobros · **Épica:** E3 · **Prioridad/esfuerzo:** Alta / 5 propuestos para Ciclo 3.
- **Historia:** **Como** empleado, **necesito** consultar el costo de los materiales requeridos por cada ventana según su plan de corte y los costos de compra vigentes, **para** conocer la base del precio de esa ventana.
- **Criterios de aceptación propuestos:**
  1. Para una ventana California por mitad con plan de HU-02, el sistema valora las cantidades y longitudes requeridas de perfiles, vidrios y los accesorios que se confirmen en HU-18.
  2. El costo por perfil y vidrio corresponde a la medida exacta usada, sin redondear a un tramo o una hoja comercial entera.
  3. El resultado presenta un desglose de costo de materiales por ventana y el subtotal de materiales.
  4. El cambio de costo de un insumo afecta los cálculos nuevos; no altera plan de corte, medidas ni avance del taller.
- **Dependencias/límites:** depende de unidades y costos configurados en HU-18. No aplica ganancia (HU-19), recupera desperdicio (HU-26/HU-27), incluye servicios ni optimiza cortes 1D/2D.
- **Preguntas abiertas:** conversión de unidades de compra de perfiles/vidrio al costo de medida consumida; ejemplo real para validar costo de una ventana.

### HU-19 — Aplicar ganancia al costo de materiales de la ventana

- **Área:** Precios y cobros · **Épica:** E4 · **Prioridad/esfuerzo:** Alta / 3 propuestos para Ciclo 3.
- **Historia:** **Como** encargado del negocio, **necesito** aplicar un porcentaje de ganancia al costo total de materiales de cada ventana, **para** obtener su precio antes de agregar servicios.
- **Criterios de aceptación propuestos:**
  1. El porcentaje se aplica al costo total de materiales de la ventana obtenido por HU-11, no a cada perfil por separado.
  2. El resultado muestra costo de materiales, ganancia aplicada y precio de la ventana de forma distinguible.
  3. Cambiar el porcentaje configura cálculos posteriores y no altera las medidas ni planes de corte.
- **Dependencias/límites:** depende de HU-11. No incorpora servicios, aceptación, anticipos ni pagos.
- **Pregunta abierta:** ejemplo numérico aprobado por el usuario para validar cómo se aplica el porcentaje y el redondeo monetario.

### HU-25 — Consultar el total de ventanas activas del pedido

- **Área:** Precios y cobros · **Épica:** E3 · **Prioridad/esfuerzo:** Alta / 2 propuestos para Ciclo 3.
- **Historia:** **Como** empleado, **necesito** consultar el total de los precios de ventana de un pedido, **para** conocer el importe de los productos antes de agregar servicios o registrar pagos.
- **Criterios de aceptación propuestos:**
  1. Muestra el precio de cada ventana activa y la suma del pedido.
  2. Las ventanas descartadas no se suman; reincorporarlas vuelve a incluirlas conforme a HU-06.
  3. Si no hay ventanas activas, no presenta un importe como si hubiera productos vigentes.
- **Dependencias/límites:** depende de HU-19; no incluye servicios (HU-12), aceptación de presupuesto, anticipo ni saldo.

### HU-12 — Agregar servicios opcionales al pedido

- **Área:** Precios y cobros · **Épica:** E3 · **Prioridad/esfuerzo:** Media propuesta / por estimar en Ciclo 3.
- **Historia:** **Como** empleado, **necesito** agregar visita a domicilio e instalación como conceptos separados de los materiales en un pedido, **para** mostrar por separado el importe de esos servicios.
- **Criterios de aceptación propuestos:**
  1. El empleado puede indicar los servicios aplicables al pedido y verlos separados del precio de las ventanas.
  2. El total presenta los servicios aplicados junto al total de ventanas.
- **Dependencias/límites:** depende de HU-25 y de reglas de tarifa confirmadas. No permite cotizaciones de visita independientes del pedido. Recorte y ensamble son parte del precio de ventana y no se agregan como servicios separados. Mantenimiento y reparaciones quedan fuera.
- **Preguntas abiertas:** regla o ejemplos de tarifa de instalación y de visita según distancia; si se requiere capturar la distancia o solo seleccionar el importe calculado por el encargado.

### HU-26 — Recuperar costo de desperdicio de perfiles de aluminio

- **Área:** Precios y cobros · **Épica:** E4 · **Prioridad/esfuerzo:** Media propuesta / 3 provisional para Ciclo 3.
- **Historia:** **Como** encargado del negocio, **necesito** configurar un umbral de recuperación de sobrantes de aluminio y distribuir su costo permitido entre las ventanas del pedido, **para** reflejar el desperdicio de material sin cobrar los errores humanos del negocio.
- **Criterios de aceptación propuestos:**
  1. El encargado puede configurar el umbral para perfiles de aluminio.
  2. El usuario puede ajustar el umbral, incluido 0 % para no recuperar desperdicio.
  3. Cuando la regla de recuperación aplica, el importe se distribuye equitativamente entre ventanas activas y forma parte del costo/precio de cada ventana; no se presenta al cliente como concepto separado. Puede mostrarse en un desglose interno comprobable.
  4. Un error de medición o fabricación del negocio no aumenta el importe cobrado al cliente.
- **Dependencias/límites:** depende de HU-18, HU-11 y HU-25. Solo valoración de aluminio; no incluye optimización 1D, reutilización automática de sobrantes ni vidrio.
- **Preguntas abiertas:** longitud comercial de cada perfil y ejemplo concreto que defina cómo se interpreta el umbral sin optimizar cortes.

### HU-27 — Recuperar y distribuir desperdicio de hojas de vidrio (futura)

- **Área:** Precios y cobros · **Épica:** E4 · **Prioridad/esfuerzo:** Sin asignar; fuera del Ciclo 3.
- **Historia:** **Como** encargado del negocio, **necesito** configurar un umbral para recuperar el costo de desperdicio de vidrio y distribuirlo entre ventanas del pedido, **para** reflejar el uso de hojas comerciales sin cobrar errores humanos del negocio.
- **Criterios de aceptación propuestos:**
  1. El sistema permite configurar el umbral y presenta el costo recuperado separado del material exacto utilizado.
  2. El umbral puede ajustarse, incluido 0 % para no recuperar desperdicio.
  3. Cuando la regla de recuperación aplica, el importe se distribuye equitativamente entre ventanas activas y forma parte del costo/precio de cada ventana; no se presenta al cliente como concepto separado. Puede mostrarse en un desglose interno comprobable.
  4. Los errores del negocio no se cobran como desperdicio.
- **Dependencias/límites:** depende de HU-18, HU-11 y HU-25; futuro respecto del Ciclo 3. No incluye algoritmo de optimización 2D ni reutilización automática de sobrantes.
- **Preguntas abiertas:** dimensiones comerciales de hoja, medida de consumo contra el umbral y ejemplo numérico que determine la regla.

## Secuencia comercial prevista: datos, precios, aceptación y liquidación

Secuencia funcional prevista: **empleado captura medidas → completa datos de cliente → calcula precio de ventanas e incorpora servicios opcionales → comunica total → si cliente acepta, registra anticipo y confirma pedido → taller fabrica → se instala → se liquida saldo**. El Ciclo 3 cubre solo el precio de las ventanas, el total de pedido y servicios opcionales acotados; la aceptación, anticipo y cierre comercial siguen para después. No hay interfaz del cliente prevista.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-13 | Pedidos y medidas · E3 | **Como** empleado, **necesito** completar, consultar y corregir los datos del cliente y las notas del pedido cuyas ventanas ya guardé, **para** conservar la información de contacto y las especificaciones de trabajo antes de calcular el precio. | Nombre, primer apellido y celular obligatorios; segundo apellido, dirección y notas opcionales. Las notas pertenecen al pedido y las consultan los trabajadores. |
| HU-11 | Precios y cobros · E3 | **Como** empleado, **necesito** calcular el costo de los materiales requeridos por cada ventana según sus medidas y el inventario, **para** conocer la base del precio de venta. | HU-18, unidades y exactitud del valor de insumo. |
| HU-12 | Precios y cobros · E3 | **Como** empleado, **necesito** añadir servicios opcionales al pedido, como visita e instalación, **para** presentar por separado su importe junto al precio de las ventanas. | Importe de visita por distancia, tarifa de instalación y vigencia del servicio. |
| HU-14 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar anticipo y confirmar el pedido aceptado, **para** iniciar el trabajo con total y saldo visibles. | Varios anticipos, cancelación y cambios posteriores. |
| HU-15 | Instalación · E3 | **Como** empleado, **necesito** registrar día y, si se acuerda, hora de instalación, **para** coordinar la visita con el cliente. | Reprogramación e instalación parcial. |
| HU-16 | Instalación · E3 | **Como** instalador, **necesito** marcar el pedido instalado, **para** distinguir la entrega física de la liquidación del saldo. | Criterio de instalación completa. |
| HU-17 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar pagos posteriores y la liquidación final, **para** conocer el saldo y cerrar el pedido cuando esté instalado y pagado por completo. | Pagos parciales, ajustes y comprobantes. Su estado de cierre habilita la liberación de la etiqueta definida en HU-22. |

### HU-13 — Datos del cliente y notas del pedido, cubierta

- **Issue:** [AVAO #33](https://github.com/ErickRamos37/AVAO/issues/33); **subtarea:** [#34](https://github.com/ErickRamos37/AVAO/issues/34).
- **Secuencia y campos confirmados:** primero se guardan las medidas del pedido; después se completan los datos del cliente y, más adelante, se mostrará el precio. Nombre, primer apellido y celular son obligatorios; segundo apellido y dirección son opcionales. Según la definición previa, el celular tiene diez dígitos. Las notas son especificaciones **del pedido** para los trabajadores, como horarios o teléfono alternativo, y son opcionales. En esta entrega solo se crea un cliente nuevo; elegir uno ya registrado queda fuera.
- **Criterios de aceptación propuestos:**
  1. Desde un pedido ya guardado, incluso uno anterior sin cliente, se pueden registrar nombre, primer apellido y celular de un cliente nuevo; segundo apellido y dirección pueden omitirse. Las notas opcionales se guardan en ese pedido y se muestran al consultar el trabajo.
  2. Tras guardar, el empleado puede corregir los datos del cliente y las notas del pedido. Al reabrirlo se muestran los valores corregidos, sin alterar sus ventanas, planes de corte ni marcas.
  3. Los datos del cliente y las notas de un pedido no aparecen como datos de otro. Los pedidos todavía sin cliente siguen siendo consultables mientras se completa la captura.
- **Subtarea vertical propuesta — Registrar, consultar y corregir datos del cliente y notas del pedido:** incorporar captura y consulta en el pedido ya guardado, con corrección posterior y campos obligatorios acordados; comprobar persistencia y separación entre dos pedidos sin alterar medidas ni avances.
- **Fuera de alcance:** cálculo o visualización de precios, anticipo, selección de clientes existentes y diseño detallado de la dirección. No convertir la secuencia futura en un bloqueo del flujo actual de taller.
- **Detalle aún abierto:** cómo introducir y validar el celular de diez dígitos y qué formato de dirección resulta útil; no se define una estructura o regla adicional por anticipación.

## Etapa posterior: precios flexibles y otras capacidades

La recuperación de desperdicio de vidrio se registra en HU-27 para un ciclo posterior, separada de la futura optimización de cortes. No duplicar las capacidades del Ciclo 3 en esta sección.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-18 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** mantener y actualizar el costo real de compra de los perfiles, vidrio y accesorios usados por California por mitad, **para** calcular el costo de sus materiales con valores vigentes. | Catálogo y unidades mínimas del primer caso; otros productos y existencias quedan fuera. |
| HU-19 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** aplicar un porcentaje de ganancia al costo total de materiales de cada ventana, **para** obtener su precio antes de agregar servicios. | Ejemplo del porcentaje; no aplicar ganancia independiente por perfil. |
| HU-20 | Visibilidad · Sin épica | **Como** encargado del negocio, **necesito** ver pedidos pendientes, en fabricación, listos, instalados y liquidados, **para** consultar su situación desde un lugar. | Estados confiables e indicador de avance verificable. |
| HU-21 | Materiales · Sin épica | **Como** encargado de materiales, **necesito** estimar perfiles y hojas de vidrio requeridos por los pedidos actuales, **para** anticipar compras cuando hagan falta. | Demanda frente a faltantes, existencias, unidades de compra, sobrantes y desperdicio. |
| HU-25 | Precios y cobros · E3 | **Como** empleado, **necesito** consultar el total de las ventanas activas de un pedido, **para** comunicar el importe de sus productos antes de agregar servicios o registrar pagos. | Excluir ventanas descartadas; no implica aceptación del presupuesto ni saldo. |
| HU-26 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** definir una regla configurable para recuperar costo de sobrantes de aluminio, **para** distribuir el desperdicio permitido entre las ventanas del pedido. | Longitud de perfil comercial, umbral y ejemplo de distribución; sin optimización 1D. Ciclo 3, prioridad menor propuesta. |
| HU-27 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** definir una regla configurable para recuperar costo de sobrantes de vidrio y distribuirlo entre ventanas, **para** reflejar el desperdicio según el uso de hojas. | Tamaño comercial de hoja, métrica del umbral y ejemplo numérico; ciclo posterior, sin prioridad ni esfuerzo asignados. Sin optimización 2D. |

## Reglas transversales confirmadas

- Para California por mitad se usan las fórmulas, cantidades y tres ejemplos de [Medidas.md](../domain/Medidas.md): **17 piezas de aluminio y dos vidrios iguales**. Si el centro matemático cae en treintaidosavos, se **sube al siguiente dieciseisavo** antes de obtener sus cortes dependientes.
- El negocio asume sus errores de medición sin cambiar el precio acordado con el cliente. Puede recortar una ventana demasiado grande, rehacer una demasiado pequeña o reutilizar piezas cuya dimensión era correcta.
- Un pedido tiene una o más ventanas y un cliente puede tener varios pedidos. Otros tipos de ventana, puertas y productos quedan fuera del primer cálculo.
- La etiqueta corta de letras pertenece a un solo pedido activo. La secuencia sigue `A`…`Z`, `AA`, `AB`…; se libera únicamente cuando el pedido está **instalado y pagado por completo**. La identidad interna permanece única aunque una etiqueta visible vuelva a usarse. Falta decidir sobre piezas o papeles remanentes.
- La aceptación de una HU requiere comprobar su resultado. El progreso de subtareas informa trabajo terminado, pero no sustituye los criterios de aceptación. Las subtareas de HU lejanas se crean cuando se acerque su implementación.
- La implementación se hará por cortes verticales pequeños: datos, API e interfaz cuando la capacidad los necesite. La primera HU debe poder usarse para capturar y consultar medidas; no se construyen capas completas por adelantado. El usuario decide alcance y prioridad como Navigator y la IA ejecuta la entrega acordada como Driver.
- La optimización de cortes 1D de perfiles y 2D tipo guillotina de vidrio son propuestas **opcionales** para evaluar después. No forman parte de las HU del primer MVP ni se convierten en requisitos por aparecer aquí.
