# Backlog de producto AVAO

> Definición y registro histórico de las HU. GitHub Projects conserva el estado diario; este archivo conserva ciclos, historias, estimaciones de esfuerzo y resultados. Al cerrar un ciclo, se retira la prioridad operativa, pero se mantienen sus HU y estimaciones como historial.

## Organización y reglas

- **Área** clasifica por asunto: **Pedidos y medidas**, **Cortes y taller**, **Precios y cobros**, **Instalación**, **Materiales** o **Visibilidad**. No es una HU ni un entregable.
- **Épica** agrupa varias HU hacia un resultado amplio. No se crea para una sola HU ni se le asignan puntos. Puede representarse por un campo `Épica` en GitHub Projects; solo se crea una incidencia padre cuando seguir su progreso o decisiones propias aporte valor. El área es una clasificación temática. Véase [GuiaBacklogKanban.md](../workflow/GuiaBacklogKanban.md).
- **HU** expresa una capacidad comprobable con **Como**, **necesito** y **para**. **Quiero** puede señalar una mejora opcional expresamente clasificada así por el usuario; el verbo por sí solo no define prioridad ni MVP. Sus criterios de aceptación prueban el resultado; las subtareas describirán el trabajo del programador. Una HU próxima debe entregar un recorrido utilizable, no una capa técnica aislada.
- **Esfuerzo** usa la escala relativa `1, 2, 3, 5, 8`. Las estimaciones ya registradas se conservan como dato histórico aunque el ciclo termine. Si al refinar una HU supera 8, se sustituye por dos o más HU menores que juntas cubran el alcance; se enlaza y cierra la original como reemplazada, manteniéndola en Backlog sin borrar su historia.
- **Prioridad** y **esfuerzo** son distintos. La prioridad se usa para ordenar trabajo pendiente dentro del ciclo actual; al terminar el ciclo se limpia ese campo, sin borrar el ciclo ni la estimación histórica.

## Épicas de resultado

| Épica | Resultado amplio | HU |
| --- | --- | --- |
| E1. Preparar ventanas California para corte | Registrar las dimensiones de fabricación indicadas por el vidriero y obtener cortes identificados por ventana. | HU-01, HU-02, HU-06, HU-22 |
| E2. Seguir la fabricación de pedidos | Saber qué aluminio, vidrio y ventanas están terminados con varios pedidos pendientes. | HU-03, HU-04, HU-05, HU-07, HU-08, HU-09, HU-10, HU-23 |
| E3. Completar un pedido desde presupuesto hasta liquidación | Comunicar total, registrar aceptación y pagos, instalar y cerrar. | HU-11 a HU-17 |
| E4. Actualizar el cálculo comercial desde insumos | Cambiar precios individuales y aplicar ganancia definida. | HU-18, HU-19 |
| E5. Conocer el desempeño del taller para tomar decisiones | Consultar eventos y resultados del taller a lo largo del tiempo para apoyar decisiones. | HU-28 a HU-33 |
| E6. Facilitar el trabajo cotidiano del taller | Mejorar navegación, edición y comprensión de presupuestos y cambios. | HU-35 a HU-38 |

HU-20, HU-21 y HU-24 quedan independientes hasta que su alcance justifique agruparlas. El progreso de una épica no reemplaza la aceptación de cada HU.

## Ciclos de trabajo

En AVAO, un ciclo agrupa trabajo con un objetivo común dentro del flujo Kanban; no implica un sprint Scrum ni duración fija. Antes de empezar se acuerdan objetivo, prioridad, esfuerzo, dependencias y criterios suficientes. Al terminar se conservan las HU, resultados y esfuerzos históricos; se retira la prioridad de las terminadas. Las HU permanecen en Backlog incluso al cerrar sus incidencias; solo las subtareas recorren el tablero y el usuario mueve sus tarjetas.

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

> **Regla posterior confirmada:** el presupuesto sin anticipo mínimo se identifica por ID y no ocupa etiqueta de letras. La etiqueta y los códigos de sus ventanas se asignan al aceptar el pedido mediante el anticipo mínimo. Si una anulación devuelve el pedido a presupuesto, se libera la etiqueta; al aceptarlo de nuevo se asigna una letra disponible. Se conservan el ID, las ventanas y los eventos. Esta actualización no modifica el registro histórico de la entrega.

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

HU-07 y HU-09 se completaron; HU-08 y HU-10 quedaron cubiertas por el flujo implementado. HU-13, HU-23 y HU-24 también se incorporaron para completar la captura y consulta del flujo. HU-06 quedó funcionalmente aceptada. La subtarea #52 se cerró por decisión del usuario: HU-25 cubre el ajuste del total al descartar o reincorporar; el saldo sigue pendiente del registro comercial en HU-14.

### Resumen histórico del Ciclo 2

| HU | Épica | Prioridad actual | Esfuerzo histórico | Resultado |
| --- | --- | --- | ---: | --- |
| HU-06 | E1 | — | 3 | Implementada y aceptada; #52 cerrada por decisión del usuario, saldo pendiente de HU-14 |
| HU-07 | E2 | — | 8 | Completada y aceptada |
| HU-08 | E2 | — | No consta en el backlog | Cubierta por el ensamble de HU-05 |
| HU-09 | E2 | — | 5 | Completada y aceptada (#53) |
| HU-10 | E2 | — | No consta en el backlog | Cubierta por el flujo actual |
| HU-13 | E3 | — | 5 | Completada y probada por el usuario |
| HU-23 | E2 | — | 2 | Implementada en el flujo de pedidos |
| HU-24 | Sin épica | — | 3 | Vistas por área implementadas y aceptadas |

Las HU completas y sus criterios permanecen en las secciones siguientes y en sus apartados específicos. Se recuperaron las estimaciones históricas de HU-09 (5), HU-13 (5), HU-23 (2) y HU-24 (3) de la copia anterior del backlog; no se estiman retrospectivamente las HU cubiertas sin estimación propia.

### HU del primer MVP incorporadas o completadas en el Ciclo 2

| ID | Área · Épica | Prioridad actual | Esfuerzo histórico | Historia y límite conocido |
| --- | --- | --- | --- | --- |
| HU-06 | Pedidos y medidas · E1 | — | 3 | **Como** empleado, **necesito** corregir las medidas de una ventana guardada antes de iniciar sus cortes, o descartarla mientras el pedido siga activo, **para** mantener correctos el plan y el precio del pedido. La corrección, el descarte y la reincorporación están aceptados; HU-25 cubre el total y la subtarea [#52](https://github.com/ErickRamos37/AVAO/issues/52) se cerró por decisión del usuario. El saldo queda para HU-14. Véase [#45](https://github.com/ErickRamos37/AVAO/issues/45). |
| HU-07 | Cortes y taller · E2 | — | 8 | **Como** trabajador del taller, **necesito** corregir las medidas de una ventana después de iniciar sus cortes, **para** continuar su fabricación con el plan actualizado y conservar las marcas que aún aplican. **Terminada:** el usuario aceptó la subtarea [#49](https://github.com/ErickRamos37/AVAO/issues/49); no incluye registrar daños ni decidir si se reutiliza una pieza. Véase [#47](https://github.com/ErickRamos37/AVAO/issues/47). |
| HU-08 | Cortes y taller · E2 | — | Cubierta | **Como** trabajador del taller, **necesito** señalar que todas las ventanas del pedido están ensambladas, **para** distinguir un pedido listo para coordinar instalación de una sola ventana terminada. El flujo actual deriva este resultado del ensamble registrado en sus ventanas (HU-05); el usuario confirmó que está cubierto. |
| HU-09 | Cortes y taller · E2 | — | Terminada | **Como** empleado, **necesito** consultar el avance de los pedidos activos del taller, **para** identificar rápidamente qué trabajo sigue pendiente. Tarjetas por pedido, progreso general con tres áreas de igual peso y desglose; subtarea [#53](https://github.com/ErickRamos37/AVAO/issues/53) aceptada e integrada. |
| HU-10 | Pedidos y medidas · E2 | — | Cubierta | **Como** empleado, **necesito** cambiar entre pedidos pendientes sin perder su avance, **para** continuar con otro cuando falta material para el actual. El flujo actual permite abrir otro pedido y conserva el avance; el usuario confirmó que está cubierto. |
| HU-23 | Pedidos y medidas · E2 | — | Pendiente | **Como** empleado, **necesito** consultar los pedidos en orden de llegada a AVAO, **para** reconocer cuál se registró primero y abrir el que convenga atender. [Issue #17](https://github.com/ErickRamos37/AVAO/issues/17); alcance de esta entrega debajo. |

### HU-06 — Corrección, descarte y reincorporación de ventanas guardadas

- **Subtarea [#48](https://github.com/ErickRamos37/AVAO/issues/48), aceptada — Corregir medidas guardadas antes del primer corte:** cambiar las medidas de cualquiera de las ventanas de un pedido, recalcular su plan y conservar código y posición. La edición puede cancelarse sin guardar. El usuario comprobó el recorrido con varias ventanas.
- **Subtarea [#51](https://github.com/ErickRamos37/AVAO/issues/51), aceptada — Descartar y reincorporar una ventana guardada:** mientras el pedido siga activo, pedir confirmación antes de descartar e indicar si hay cortes marcados o ensamble. Conservar la ventana en una sección de descartadas con sus medidas, plan, marcas, código y posición; permitir reincorporarla con la misma identidad. Una ventana descartada se excluye de cortes, ensamble y progreso pendientes, pero conserva sus marcas. Puede quedar un pedido con cero ventanas activas. El usuario comprobó el recorrido; no incluye borrar definitivamente la ventana ni ajustar el precio.
- **Subtarea [#52](https://github.com/ErickRamos37/AVAO/issues/52), cerrada por decisión del usuario — Actualizar total y saldo al descartar o reincorporar:** HU-25 cubre la exclusión y reincorporación del precio de la ventana en el total. El saldo aún no está implementado y queda pendiente del registro comercial de HU-14. El trato con el cliente corresponde al encargado.
- **Límite:** HU-07 cubre correcciones después de iniciar cortes. La corrección, descarte y reincorporación están aceptados; el total de ventanas se ajusta mediante HU-25; el saldo depende del registro comercial de HU-14. El descarte no elimina piezas o marcas de trabajo ya realizado.

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

- **Issue:** [AVAO #30](https://github.com/ErickRamos37/AVAO/issues/30).
- **Área:** Visibilidad · sin épica asignada · **Esfuerzo histórico:** 3, recuperado del registro del Ciclo 2.
- **Historia:** **Como** empleado que trabaja en un pedido, **necesito** consultar por separado sus medidas, cortes de aluminio, cortes de vidrio y ensamble, **para** concentrarme en la información pertinente a la tarea que realizo.
- **Alcance de esta entrega:** las cuatro vistas pertenecen solo al pedido abierto. «Medidas» consulta las ventanas ya guardadas; la captura de un pedido nuevo sigue en el flujo actual. Los datos del cliente y las notas del pedido deben seguir accesibles, en particular las notas compartidas con los trabajadores; su ubicación exacta no se fija aquí.
- **Criterios de aceptación propuestos:**
  1. Dentro del mismo pedido se puede pasar entre «Medidas», «Aluminio», «Vidrio» y «Ensamble». Cada vista muestra las ventanas de ese pedido, sin mezclar datos de otro.
  2. «Medidas» muestra código y dimensiones de fabricación; «Aluminio» muestra perfiles, longitudes, cantidades y marcas existentes; «Vidrio» muestra código, `ancho × alto`, cantidad y avance, por ejemplo `1 de 2`; «Ensamble» muestra código, estado y acciones existentes. La presentación puede ser una lista o tabla sencilla.
  3. Marcar o deshacer un corte o ensamble conserva las reglas ya aceptadas. Cambiar de vista y reabrir el pedido no altera medidas, planes ni avances; los datos del cliente y las notas siguen disponibles.
- **Subtarea [#43](https://github.com/ErickRamos37/AVAO/issues/43) — Separar la consulta del pedido en cuatro vistas de trabajo:** reorganizar la información y los controles existentes por área dentro del pedido abierto, mantener el acceso a cliente y notas y comprobar navegación y marcas con dos ventanas. No añadir estados, cálculos ni pasos de captura.
- **Límites:** no reúne pendientes de todos los pedidos (HU-09), no agrega cálculos, marcas o estados nuevos a HU-01, HU-03, HU-04 y HU-05, no introduce permisos por área ni fija un diseño visual detallado. Mantener visibles los avisos existentes si un pedido anterior carece de plan de corte.

## Ciclo 3 cerrado: costos y precios de ventanas

El usuario decidió omitir la fórmula sencilla. Este ciclo prepara el costo real de materiales desde el inventario flexible, aplica ganancia al costo total de materiales de cada ventana y muestra el total de ventanas activas del pedido. La aceptación del presupuesto, anticipos y otros cobros quedan para un ciclo posterior. Las seis historias fueron implementadas y aprobadas por el usuario. Se conserva su esfuerzo histórico; la prioridad deja de aplicar a las historias cerradas.

| Orden | HU | Esfuerzo histórico | Dependencias y límites |
| --- | --- | ---: | --- |
| 1 | HU-18 — Mantener costos de compra de insumos de California por mitad | 3 | Registrar costos documentados de perfiles, moldura de screen, vidrio, tela, consumibles lineales y artículos contables. Guardado único y aviso de cambios pendientes aprobados por el usuario. Sin compras, existencias, rollos, sets, silicón, vistas ni accesorios aún no identificados. |
| 2 | HU-11 — Calcular costo exacto de materiales por ventana | 5 | Usa cantidades y medidas del plan de corte y costos de HU-18. Valora medidas exactas usadas, sin redondear a tramos comerciales. No recupera desperdicio ni optimiza cortes. |
| 3 | HU-19 — Aplicar ganancia al costo de materiales de una ventana | 3 | Aplica el porcentaje definido por el usuario sobre el costo total de materiales de la ventana, no por perfil. Porcentaje común configurable en inventario (25 % inicial, entero de 1 a 100), aplicado a cada ventana. Los precios guardados cambian solo con Recalcular. Subtarea implementada y aprobada por el usuario. No incluye servicios ni cobros. |
| 4 | HU-25 — Mostrar total de ventanas activas del pedido | 2 | Implementada y aprobada por el usuario; subtarea #71. Suma precios guardados de ventanas activas, excluye descartadas y distingue total parcial, precios pendientes y avisos de desactualización. No incluye aceptar presupuesto, anticipo ni saldo. |
| 5 | HU-12 — Agregar traslado opcional al pedido | 3 | Un único importe opcional por pedido para traslados de visita o entrega a domicilio, estimado manualmente según ubicación y gasolina. Se suma separado del total de ventanas, sin aplicar ganancia al traslado. Implementada y aprobada por el usuario; subtarea #74. Depende de HU-25; sin tarifas automáticas ni instalación como servicio. |
| 6 | HU-26 — Recuperar merma de perfiles de aluminio según umbral | 3 | Consumo por tipo de perfil en el pedido; umbral común editable, inicialmente 80 %. Cargo separado y desmarcable, sin ganancia sobre la merma. Se evalúa el último tramo de cada perfil, incluida moldura de screen; vidrio continúa en HU-27 del Ciclo 4. Implementada y aprobada por el usuario; subtarea #77. Tabla de merma y nombres aprobados por el usuario. |

### Fuera del Ciclo 3

| HU | Prioridad | Alcance conocido y dependencia |
| --- | --- | --- |
| HU-27 — Recuperar desperdicio de vidrio | Ciclo 4, prioridad propuesta | Depende de HU-18/HU-11; reglas confirmadas en HU-27. |
| HU-14 — Registrar anticipo y confirmar pedido; HU-15 a HU-17 — instalación y liquidación | Ciclo 4 propuesto | Cierre comercial después de que precio y total estén disponibles. |

**Reglas confirmadas:** el inventario guarda costo real de compra; se calcula material por ventana y se aplica ganancia al costo total de materiales de esa ventana; el total suma ventanas activas; el error humano lo asume el negocio y no se cobra como desperdicio. Para perfiles y vidrio se valora la medida exacta utilizada, sin redondear a barras u hojas enteras. En HU-18, los perfiles de aluminio se registran por tramo de 21 pies y la moldura de screen por tramo de 12 pies, mostrando costo por pie lineal; el vidrio doble fuerza de 1/8″ se registra por hoja de 71″ × 102″, mostrando costo por pie cuadrado; la tela se registra directamente por pie cuadrado; los demás insumos usan su unidad documentada. Los precios aún no informados quedan pendientes, no equivalen a cero. Actualizar un costo afecta cálculos nuevos, no los ya consultados. Se incluyen los accesorios ya identificados en la documentación; los que no estén identificados quedan fuera hasta que se definan. Los porcentajes/umbrales de desperdicio son ajustables por el usuario, incluido 0 % para no recuperar desperdicio. Para aluminio, la decisión más reciente sustituye el reparto oculto entre ventanas por un cargo de merma separado y desmarcable, sin ganancia sobre ese cargo. La regla confirmada de vidrio se describe en HU-27.

**Vidrio:** la regla confirmada del Ciclo 4 usa área y cargo separado; véase HU-27.

HU-13 contiene datos del cliente y notas ya trabajados. No se implementan en este ciclo algoritmos 1D/2D, PWA/aplicación móvil, mantenimiento, reparación, aceptación del presupuesto ni anticipo.

### HU-18 — Mantener costos reales de compra de insumos

- **Estado:** implementada y aprobada por el usuario.
- **Área:** Precios y cobros · **Épica:** E4 · **Esfuerzo histórico:** 3.
- **Historia:** **Como** encargado del negocio, **necesito** registrar, consultar y actualizar el costo real de compra de los insumos usados por la ventana California por mitad, **para** calcular sus costos de materiales con valores vigentes.
- **Criterios de aceptación propuestos:**
  1. El encargado puede consultar e ingresar o actualizar los costos de compra de los insumos documentados para California por mitad, usando la presentación y unidad indicadas en [Insumos y costos de California por mitad](../domain/CostosInsumosCalifornia.md). Los precios no informados permanecen pendientes y no se interpretan como cero.
  2. El costo por pie lineal de cada perfil y de la moldura de screen se deriva del costo de su tramo (21 pies para perfiles y 12 pies para moldura). El costo por pie cuadrado del vidrio se deriva del precio de una hoja de 71″ × 102″. La tarifa de tela se registra directamente por pie cuadrado; los demás insumos conservan su costo por unidad documentada.
  3. Los costos ingresados permanecen al volver a consultar el catálogo. Actualizar un costo solo afecta cálculos nuevos; no modifica planes de corte, marcas de fabricación ni resultados ya consultados.
- **Subtarea propuesta — Registrar y consultar costos de compra de los insumos de California por mitad:** permitir consultar e ingresar o actualizar cada costo con la presentación documentada: tramo con su longitud para perfiles y moldura de screen; hoja para vidrio; pie cuadrado para tela; pie lineal para insumos lineales; y unidad para artículos contables, incluida la pasta. Mostrar los costos derivados por pie lineal de perfil y moldura, y por pie cuadrado de vidrio; registrar directamente la tarifa de tela por pie cuadrado. Comprobar que persistan al volver a consultar y que sus cambios afecten solo cálculos nuevos. No incluye costo consumido por ventana (HU-11), rollos o su acomodo, compras en set o paquetes, accesorios aún no identificados, silicón ni vistas.
- **Subtarea de mejora, implementada y aprobada — Guardar los cambios del inventario en una sola acción:** sustituir los botones individuales por un único botón **Guardar** o **Aplicar**, detectar los campos modificados y persistir esos cambios, incluido el porcentaje de ganancia de HU-19 cuando esté disponible. Al intentar navegar dentro de AVAO con cambios sin guardar, advertir y ofrecer guardar o descartar. Al recargar o cerrar la pestaña con cambios pendientes, activar la advertencia estándar del navegador para salir o permanecer; no guardar automáticamente ni prometer botones personalizados en ese aviso. Comprobar que se conservan los valores al volver a consultar, que descartar no guarda las modificaciones y que la advertencia aparece únicamente cuando hay cambios pendientes.
- **Clasificación:** subtarea de mejora de HU-18, aprobada por el usuario. Cambia la interacción de una capacidad ya entregada; no es un fallo del comportamiento acordado anteriormente ni requiere una HU independiente. Conservar la subtarea original y su aceptación como historial.
- **Dependencias/límites:** habilita HU-11; no incluye existencias, compras, proveedores, otros tipos de ventana/producto ni el precio final del cliente.

### HU-11 — Calcular costo exacto de materiales por ventana

- **Estado:** implementada y aprobada por el usuario.
- **Área:** Precios y cobros · **Épica:** E3 · **Esfuerzo histórico:** 5.
- **Historia:** **Como** empleado, **necesito** consultar el costo de los materiales requeridos por cada ventana según su plan de corte y los costos de compra vigentes, **para** conocer la base del precio de esa ventana.
- **Criterios de aceptación propuestos:**
  1. Para una ventana California por mitad con plan de HU-02, el sistema valora las cantidades y longitudes requeridas de perfiles, vidrios y los accesorios que se confirmen en HU-18.
  2. El costo por perfil y vidrio corresponde a la medida exacta usada, sin redondear a un tramo o una hoja comercial entera.
  3. El resultado presenta un desglose de costo de materiales por ventana y el subtotal de materiales.
  4. El cambio de costo de un insumo afecta los cálculos nuevos; no altera plan de corte, medidas ni avance del taller.
- **Subtarea — Calcular y consultar el costo base completo de una ventana California por mitad:** usar el plan de corte guardado y los costos vigentes para valorar longitudes exactas de perfiles y moldura, áreas exactas de vidrios y tela, consumibles según las fórmulas documentadas y artículos por unidad, incluida la pasta. Mostrar el desglose de cantidades, medidas y costo base solo cuando estén configurados todos los costos requeridos; si falta alguno, indicar cuáles faltan y no mostrar importes ni subtotal parcial. No redondear a tramos u hojas comerciales ni modificar medidas, planes o avances. No incluye ganancia (HU-19), servicios, recuperación de desperdicio ni optimización 1D/2D.
- **Dependencias/límites:** depende de unidades y costos configurados en HU-18. No aplica ganancia (HU-19), recupera desperdicio (HU-26/HU-27), incluye servicios ni optimiza cortes 1D/2D.
- **Referencia histórica:** conversión de unidades de compra y ejemplo para validar el costo de una ventana, considerados durante la entrega aprobada.

### HU-19 — Aplicar ganancia al costo de materiales de la ventana

- **Estado:** implementada y aprobada por el usuario.
- **Área:** Precios y cobros · **Épica:** E4 · **Esfuerzo histórico:** 3.
- **Historia:** **Como** encargado del negocio, **necesito** aplicar un porcentaje de ganancia al costo total de materiales de cada ventana, **para** obtener su precio antes de agregar servicios.
- **Criterios de aceptación propuestos:**
  1. Un único porcentaje común se configura al final de los materiales del inventario, con valor inicial de 25 %. Se aplica a cada ventana y no se edita individualmente por ventana. Admite únicamente enteros de 1 a 100, ambos incluidos; rechaza valores vacíos, decimales, cero, negativos y mayores que 100.
  2. El cálculo aplica ese porcentaje al costo total de materiales de cada ventana obtenido por HU-11, no a cada perfil por separado. Presenta costo, porcentaje, ganancia y precio distinguibles.
  3. Guardar un porcentaje nuevo afecta cálculos nuevos y conserva los precios de las ventanas ya calculadas. El botón **Recalcular** permite actualizar explícitamente el cálculo con la configuración vigente, sin alterar medidas, planes de corte ni avances.
  4. El precio de cada ventana se muestra en pesos enteros: una fracción de peso menor que $0.50 baja al entero inferior; desde $0.50 sube al siguiente peso.
- **Subtarea implementada y aprobada — Aplicar y consultar la ganancia en el precio de una ventana:** incorporar al final del inventario un único porcentaje común editable, con valor inicial de 25 %, sin edición individual por ventana y persistirlo mediante el guardado del inventario. Aplicarlo al costo completo de materiales de cada ventana y mostrar costo, porcentaje utilizado, ganancia y precio redondeado. Conservar los precios ya calculados al cambiar la configuración; actualizarlos solo mediante **Recalcular**. Comprobar límites, persistencia, conservación del precio previo y recálculo explícito, sin perder medidas, planes ni marcas de fabricación.
- **Dependencias/límites:** depende de HU-11. Comparte el guardado del inventario con la mejora de HU-18; no incorpora servicios, aceptación, anticipos ni pagos.
- **Ejemplo de comprobación propuesto:** materiales por $1,000 con el 25 % inicial producen $250 de ganancia y $1,250 de precio. La ganancia es un recargo sobre costo.

### HU-25 — Consultar el total de ventanas activas del pedido
- **Área:** Precios y cobros · **Épica:** E3 · **Esfuerzo histórico:** 2.
- **Historia:** **Como** empleado, **necesito** consultar el total de los precios de ventana de un pedido, **para** conocer el importe de los productos antes de agregar servicios o registrar pagos.
- **Estado:** implementada y aprobada por el usuario, incluida la regla de total parcial; no requiere una nueva subtarea para ese comportamiento.
- **Criterios de aceptación:**
  1. Muestra el precio de cada ventana activa y la suma del pedido.
  2. Las ventanas descartadas no se suman; reincorporarlas vuelve a incluirlas conforme a HU-06.
  3. Si no hay ventanas activas, no presenta un importe como si hubiera productos vigentes.
  4. Si faltan precios de ventanas activas, muestra la suma parcial de las que sí tienen precio y señala las pendientes; si ninguna tiene precio, indica que no hay precios calculados. Si algún precio guardado está desactualizado por cambios en medidas o planes, advierte de ello. Los cambios de costos o ganancia del inventario no invalidan por sí solos precios guardados.
- **Subtarea [#71](https://github.com/ErickRamos37/AVAO/issues/71), implementada y aprobada — Consultar el total de precios de las ventanas activas del pedido:** mostrar el precio de cada ventana activa calculado en HU-19 y sumar esos precios ya redondeados. Excluir las ventanas descartadas y volver a incluirlas al reincorporarlas, conservando su identificación. Comprobar el total con varias ventanas, precios pendientes o desactualizados y cambios al descartar o reincorporar, sin presentar un importe vigente si no quedan ventanas activas. No incluye servicios, anticipos ni saldo.
- **Dependencias/límites:** depende de HU-19; no incluye servicios (HU-12), aceptación de presupuesto, anticipo ni saldo.

### HU-12 — Agregar traslado opcional al pedido

- **Área:** Precios y cobros · **Épica:** E3 · **Esfuerzo histórico:** 3. El esfuerzo considera capturar, conservar, modificar y quitar el importe, e integrarlo al total existente; es una estimación relativa sujeta a revisión.
- **Historia:** **Como** empleado, **necesito** agregar al pedido un importe opcional de traslado para visita o entrega a domicilio, **para** presentar ese cargo separado del precio de las ventanas y conocer el total del pedido.
- **Reglas confirmadas:** el usuario estima manualmente el importe variable según ubicación y gasolina. Un único importe opcional por pedido reúne los traslados. Si no se agrega, no hay cargo. La ganancia de las ventanas no se aplica al traslado.
- **Estado:** implementada y aprobada por el usuario; subtarea #74.
- **Criterios de aceptación:**
  - [x] Permite agregar un único importe de traslado en pesos a un pedido y consultar lo guardado.
  - [x] El campo de traslado aparece al final, bloqueado por defecto; su botón **Editar** permite cambiar el importe. Permite quitarlo y deja de incluir el cargo al hacerlo.
  - [x] Presenta por separado el total de ventanas y el traslado, y muestra su suma como total del pedido. Sin traslado, no agrega cargo.
  - [x] Conserva la distinción de HU-25 para precios pendientes o desactualizados y no presenta una suma parcial como total completo del pedido.
  - [x] No aplica al traslado el porcentaje de ganancia de ventanas.
- **Subtarea [#74](https://github.com/ErickRamos37/AVAO/issues/74), implementada y aprobada — Registrar y consultar el traslado opcional de un pedido:** permitir agregar un único importe manual en pesos, consultarlo, editarlo o quitarlo; mostrar el traslado al final, con su campo bloqueado por defecto y un botón **Editar** que habilite cambiarlo; mostrar por separado total de ventanas y traslado y su suma como total del pedido, conservando los avisos y límites de HU-25. Comprobar persistencia, edición, eliminación, ausencia de cargo cuando no se agrega y que no se aplique ganancia de ventanas al traslado. No incluye instalación como servicio ni cálculo automático del importe.
- **Dependencias/límites:** depende de HU-25. Visita y entrega a domicilio se reúnen en el importe de traslado del pedido; no hay cotización de visita independiente. No incluye mapas, kilómetros ni tarifas automáticas, instalación como servicio, mantenimiento, reparaciones ni cobros separados por recorte o ensamble.

### HU-26 — Recuperar merma de perfiles de aluminio según umbral

- **Área:** Precios y cobros · **Épica:** E4 · **Esfuerzo histórico:** 3.
- **Historia:** **Como** encargado del negocio, **necesito** aplicar un umbral configurable a la merma de perfiles de aluminio del pedido, **para** recuperar su costo como cargo separado cuando corresponda.
- **Reglas confirmadas:** se suma el consumo de las ventanas activas por tipo de perfil en cada pedido, incluida la moldura de screen. Se evalúa el consumo residual del último tramo de cada tipo frente a un umbral común editable en inventario, entero de 0 a 100 e inicialmente 80 %; 0 % desactiva la recuperación. Si el consumo residual alcanza el umbral, se cobra el costo de la longitud restante del tramo; si el tramo se consume exactamente, no hay sobrante. Los perfiles usan tramos de 21 pies y la moldura de screen de 12 pies. El cargo de merma se muestra separado, se suma al total del pedido y el encargado puede desmarcarlo. No se aplica ganancia a la merma. El cargo guardado cambia solo con la acción explícita **Recalcular**, no automáticamente al cambiar costos, umbral o ventanas activas. Si el encargado lo desmarca, esa elección se conserva al recalcular y al volver a consultar. Los errores de medición o fabricación del negocio no se cobran como desperdicio.
- **Cambio de decisión:** se sustituye el reparto equitativo oculto en el precio de las ventanas por el cargo separado y desmarcable. Vidrio continúa en HU-27 para el Ciclo 4.
- **Estado:** implementada y aprobada por el usuario; subtarea #77.
- **Criterios de aceptación:**
  1. El encargado puede consultar y editar en inventario un umbral común entero de 0 a 100 a los perfiles de aluminio, inicialmente 80 %; 0 % desactiva la recuperación.
  2. Se agrupa el consumo de ventanas activas por tipo de perfil del pedido, incluida moldura de screen, y se evalúa el consumo residual del último tramo contra el umbral. Al alcanzarlo, se recupera el costo de la longitud restante; un tramo completo no produce sobrante.
  3. Con umbral de 80 % y tramos de 21 pies, consumos de 18, 30, 39 y 42 pies producen respectivamente 3, 0, 3 y 0 pies de merma recuperable. La moldura se evalúa con tramos de 12 pies.
  4. El cargo de merma aparece separado y se suma al total; el encargado puede desmarcarlo. No recibe ganancia de ventanas.
  5. El cargo guardado solo cambia al usar **Recalcular**; cambios de costos, umbral o ventanas activas no lo actualizan automáticamente. Si se desmarca, permanece desmarcado al recalcular y volver a consultar.
  6. Los errores del negocio no aumentan la merma cobrada.
- **Subtarea [#77](https://github.com/ErickRamos37/AVAO/issues/77), implementada y aprobada — Calcular y consultar la merma opcional de aluminio del pedido:** permitir configurar el umbral común en inventario y calcular, por tipo de perfil y para las ventanas activas, el costo de la longitud restante del último tramo cuando su consumo alcance el umbral. Incluir moldura de screen, presentar el cargo separado en el total y permitir al encargado desmarcarlo, sin aplicarle ganancia. Actualizar el cargo guardado solo al usar **Recalcular** y conservar la elección desmarcada al recalcular y volver a consultar. Comprobar los ejemplos de 21 pies, tramos de 12 pies, umbral 0 %, cambios de datos sin recálculo y persistencia de la selección.
- **Dependencias/límites:** depende de HU-18, HU-11 y HU-25. No incluye optimización 1D, reutilización automática de sobrantes ni vidrio.

### Necesidad nueva por refinar: medidas aproximadas antes del pedido de taller

- **Hecho confirmado:** algunos clientes comparten dimensiones aproximadas para recibir una idea de presupuesto. No son medidas verificadas por el vidriero ni se envían al taller. Si el cliente acepta continuar, el vidriero obtiene medidas de fabricación exactas; deben poder compararse con las aproximadas para explicar una diferencia de precio.
- **Preferencia expresada por el usuario:** no asignar etiqueta/código ni posición de cola mientras solo existan medidas aproximadas. La cotización admite varias ventanas y usa los datos de cliente de HU-13: nombre, primer apellido y teléfono obligatorios; los demás opcionales. La cotización y su método para estimar el precio quedan fuera del Ciclo 3 y todavía requieren decisión del usuario.
- **Propuesta del Product Owner:** mantener la cotización preliminar separada del pedido activo de taller. Al aceptarse como trabajo, el encargado podría corregir, agregar o descartar ventanas, capturar medidas exactas y revisar un resumen antes de promoverla. El resumen compararía medidas aproximadas/exactas, precio anterior/nuevo, ventanas agregadas/descartadas y diferencia/total. Solo al promover se asignarían código y posición de cola, manteniendo cotización y medidas originales para explicar el cambio.
- **Dependencia de precios, todavía propuesta:** podría reutilizarse el inventario y el cálculo de costo/precio de HU-18, HU-11 y HU-19 para estimar ventanas a partir de medidas aproximadas, pero esa reutilización no está aprobada y requiere comprobar que sirve para cotizaciones. Evitar crear dos motores de precio sin una necesidad demostrada; tampoco bloquear la cotización bajo una arquitectura general de catálogo.
- **Opciones de alcance aún no decididas:** (A) registrar cotización y monto manual, con menor alcance pero sin cálculo automático; (B) explorar si el cálculo de HU-11 puede usarse con medidas aproximadas, sin asumir que produzca un precio orientativo válido; (C) reutilizar HU-18/HU-11/HU-19 o extenderlas mínimamente para cotizar California por mitad. Ninguna opción está aprobada; la elección depende de validar unidades, datos, reglas de material y ganancia para el caso aproximado.
- **Posible división, aún no aprobada:** una HU para guardar/consultar cotizaciones preliminares con medidas aproximadas, y otra para revisar diferencias y convertir una cotización aceptada en pedido del taller con medidas exactas, etiqueta y posición. El resumen de diferencias parece pertenecer al flujo de conversión, no necesita una HU de interfaz separada. Sin ID, épica, prioridad, esfuerzo, ciclo ni issues todavía.
- **Por preguntar antes de formalizar:** ¿la aprobación final del cliente al total actualizado debe ocurrir antes de promover el pedido al taller? ¿qué componentes concretos de costo/precio y reglas mínimas (unidades, largos de compra, desperdicio, ganancia/servicios) usa California para que el estimador sea repetible? ¿se archivan o eliminan las cotizaciones que no se aceptan, y quién puede encontrarlas? No cambiar la captura actual de HU-01 hasta decidir el nuevo ciclo.

## Ciclo 4 cerrado: completar el pedido

El usuario confirmó continuar el flujo comercial con aceptación, pagos, instalación, cierre y merma de vidrio. HU-14, HU-15, HU-16, HU-17 y HU-27 fueron implementadas y aceptadas por el usuario. HU-17 se integró a develop mediante el [PR #93](https://github.com/ErickRamos37/AVAO/pull/93), commit `6210f5a`. El usuario autorizó el cierre del ciclo. Se conservan historias y esfuerzos históricos y se retiran las prioridades de las terminadas. El 3 propuesto para HU-27 toma como referencia HU-26 y considera el cálculo adicional por área. Las notas de trabajo ya pertenecen a HU-13; no se añaden optimización de corte ni PWA.

| ID | HU | Épica | Esfuerzo histórico | Prioridad actual | Resultado |
| --- | --- | --- | ---: | --- | --- |
| HU-14 | Aceptación, anticipo y saldo | E3 | 5 | — | Implementada y aceptada; subtarea #81 |
| HU-15 | Fechas de instalación | E3 | 2 | — | Implementada y aceptada; subtarea #83 |
| HU-16 | Instalación completa | E3 | 2 | — | Implementada y aceptada; subtarea #85 |
| HU-17 | Pagos, liquidación e histórico | E3 | 5 | — | Implementada y aceptada; subtarea #87; integrada por PR #93 |
| HU-27 | Merma de vidrio | E4 | 3 | — | Implementada y aceptada; subtarea #79 |

### HU-14 — Registrar aceptación, anticipo y consultar saldo

- **Estado:** implementada y aceptada por el usuario; subtarea [#81](https://github.com/ErickRamos37/AVAO/issues/81).

- **Área:** Precios y cobros · **Épica:** E3 · **Esfuerzo histórico:** 5.
- **Historia:** **Como** empleado, **necesito** registrar anticipo y confirmar el pedido aceptado, **para** iniciar el trabajo con total y saldo visibles.
- **Criterios de aceptación propuestos:**
  - [ ] Solo se registra anticipo con el total completo calculado. Un anticipo neto inferior al mínimo no confirma el pedido; uno suficiente sí, y la configuración y movimientos persisten al consultar de nuevo. La falta de fecha programada no impide registrar ni conservar el anticipo; la fecha se exige después.
  - [ ] Un cambio del total actualiza el saldo sin modificar los movimientos ni reducir el total por los pagos; la aceptación se conserva aunque el anticipo quede bajo el mínimo. Si existe excedente, se muestra la diferencia y solo puede devolverse hasta ese excedente (neto menos total).
  - [ ] Antes de alcanzar el anticipo mínimo, el presupuesto queda fuera de la cola y el taller y no admite marcas de fabricación. Si se anula un anticipo y el neto queda bajo el mínimo, vuelve a presupuesto.
  - [ ] Cada pago o devolución conserva importe y fecha automática del día de la acción; la anulación registra también su fecha automáticamente; solo se permite anular cuando todos los precios del pedido están completos. Si el total es parcial o falta, se bloquea la anulación sin modificar el movimiento. Un movimiento anulado sigue visible y se excluye del neto, saldo y liquidación. El pedido se considera liquidado si pagos menos devoluciones no anulados alcanza el total, incluso antes de instalar.
- **Subtarea [#81](https://github.com/ErickRamos37/AVAO/issues/81), implementada y aceptada — Registrar aceptación, anticipo y consultar saldo:** Configurar el porcentaje mínimo de anticipo en inventario (entero 1–100, inicialmente 50 %); exigir el total completo calculado y registrar el anticipo con importe y fecha automática y confirmar el pedido cuando el anticipo neto alcance el mínimo. Solicitar después la fecha programada obligatoria sin impedir ni perder el registro del anticipo por faltar la fecha. Consultar total vigente, movimientos y saldo; permitir varios pagos y devoluciones con fecha automática de la acción, mostrar el excedente y permitir devolver hasta el importe excedente (neto menos total) o conservarlo si el cliente así lo decide. Mantener la aceptación tras cambios de total aunque el anticipo quede bajo el mínimo; si se anula un anticipo y el neto queda bajo el mínimo, volver a presupuesto; mantener el presupuesto fuera de la cola y taller, sin marcas, hasta alcanzar el mínimo. Cambios posteriores al total recalculan el saldo como total vigente menos pagos netos. Permitir anular un movimiento incorrecto solo con todos los precios del pedido completos; si el total es parcial o falta, bloquear la anulación sin modificar el movimiento. Conservar el movimiento anulado visible y registrar el correcto; no definir edición ni cancelación sin decisión previa.
- **Dependencias, límites y preguntas:** Depende del total del pedido y de las decisiones sobre presupuesto previo, etiqueta, cola y marcas. El presupuesto se identifica por ID sin etiqueta; al alcanzar el anticipo mínimo se asignan etiqueta y códigos de ventana. Si una anulación lo devuelve a presupuesto, se libera la etiqueta y, al aceptarlo de nuevo, se asigna una letra disponible conservando ID, ventanas y eventos; la cancelación y la edición de movimientos siguen abiertas; una anulación que deja el neto por debajo del mínimo devuelve el pedido a presupuesto.

### HU-15 — Registrar y consultar fechas de instalación

- **Estado:** implementada y aceptada por el usuario; subtarea [#83](https://github.com/ErickRamos37/AVAO/issues/83). Tras registrar un anticipo que acepta el pedido, se solicita automáticamente la fecha si falta, conservando el pago.

- **Área:** Instalación · **Épica:** E3 · **Esfuerzo histórico:** 2.
- **Historia:** **Como** empleado, **necesito** registrar día y, si se acuerda, hora de instalación, **para** coordinar la visita con el cliente.
- **Criterios de aceptación propuestos:**
  - [ ] La fecha programada se captura por el usuario y persiste; se muestra bloqueada hasta pulsar **Editar**, solo cambia al guardar y cancelar conserva la anterior.
  - [ ] Un pedido aceptado sin fecha programada muestra «Fecha de instalación pendiente» y solicita automáticamente la fecha después del anticipo; la ausencia de fecha no impide registrar ni conservar el pago.
  - [ ] Al marcar instalado se registra automáticamente la fecha real del día y se puede consultar.
- **Subtarea [#83](https://github.com/ErickRamos37/AVAO/issues/83), implementada y aceptada — Registrar y consultar fechas de instalación:** Guardar fecha programada obligatoria capturada por el usuario y fecha real registrada automáticamente al marcar instalado; mostrar «Fecha de instalación pendiente» si el pedido aceptado no tiene fecha programada; la programada se consulta bloqueada, se modifica mediante **Editar** y permite guardar o cancelar. La fecha programada se exige después de registrar el anticipo mínimo y su ausencia no impide registrar ese dinero. La fecha real se registra automáticamente al marcar instalado; no se captura manualmente.
- **Dependencias, límites y preguntas:** La fecha programada es obligatoria después del anticipo mínimo; la fecha real se registra automáticamente al marcar instalado.

### HU-16 — Marcar instalación completa del pedido

- **Estado:** implementada y aceptada por el usuario; subtarea [#85](https://github.com/ErickRamos37/AVAO/issues/85).

- **Área:** Instalación · **Épica:** E3 · **Esfuerzo histórico:** 2.
- **Historia:** **Como** instalador, **necesito** marcar el pedido instalado, **para** distinguir la entrega física de la liquidación del saldo.
- **Criterios de aceptación:**
  - [x] Si falta un corte o ensamble activo, no permite marcar instalado; una vez completos, la marca y señal verde o texto en la esquina de la tarjeta y en el detalle persisten al consultar; la fecha real se registra automáticamente, sin entrada manual.
  - [x] Instalado bloquea ventanas, medidas y fabricación y permite pagos y devoluciones; desmarcar requiere advertencia y devuelve la posibilidad de modificación. Al desmarcar se elimina la fecha real actual; al marcar instalado nuevamente se registra automáticamente la nueva fecha.
- **Subtarea [#85](https://github.com/ErickRamos37/AVAO/issues/85), implementada y aceptada — Marcar instalación completa del pedido:** Permitir marcar instalado cuando todos los cortes y ensambles de las ventanas activas estén completos; mostrar señal verde o texto en la esquina de la tarjeta y en el detalle y registrar automáticamente la fecha real al marcar instalado. Bloquear cambios en ventanas, medidas y fabricación, sin bloquear pagos ni devoluciones; permitir desmarcar con advertencia. El cierre de HU-17 es definitivo y no permite desmarcar desde el histórico.
- **Dependencias, límites y preguntas:** La instalación requiere cortes y ensambles de ventanas activas completos. El cierre e histórico son HU-17 y no forman parte de esta subtarea; el histórico de HU-17 es solo de consulta y no permite desmarcar. No se han acordado requisitos adicionales de precio o fecha para marcar instalado.

### HU-17 — Cerrar y consultar pedidos finalizados

- **Estado:** implementada y aceptada por el usuario; subtarea [#87](https://github.com/ErickRamos37/AVAO/issues/87). Integrada a develop mediante [PR #93](https://github.com/ErickRamos37/AVAO/pull/93), commit `6210f5a`.

- **Área:** Precios y cobros · **Épica:** E3 · **Esfuerzo histórico:** 5.
- **Historia:** **Como** empleado, **necesito** consultar los pedidos instalados y liquidados, **para** conservar un respaldo de su información al concluir el trabajo.
- **Criterios de aceptación:**
  - [x] Un pedido solo instalado o solo liquidado permanece activo. Al estar instalado y alcanzar el total de venta con pagos netos (pagos menos devoluciones, excluyendo movimientos anulados), se cierra automáticamente, sale de la cola activa, libera su etiqueta y aparece en el histórico. El sistema registra automáticamente como fecha de cierre el día en que se cumplen ambas condiciones.
  - [x] El histórico identifica cada pedido por su ID y fecha de cierre, y muestra «Ventanas:» seguido de una lista numerada con únicamente las medidas base ancho × alto (por ejemplo, «1.25 x 25» y «2.35 x 14 1/2»), sin prefijos, tabla, letras ni códigos. No conserva ni muestra la etiqueta de letras ni los códigos de taller del pedido cerrado; la etiqueta liberada puede reutilizarse en otro pedido activo.
  - [x] El histórico conserva cliente, medidas base, importes agregados por ventana (costo, precio y ganancia si aplica), total del pedido, merma, traslado, pagos, devoluciones, movimientos anulados y sus fechas, y fechas del pedido y cierre. No almacena el desglose individual de materiales ni sus costos; tampoco conserva medidas derivadas de corte.
  - [x] En el detalle se muestran, en orden, ventanas, mermas y traslado, total del pedido y pagos. Pagos es desplegable: su encabezado muestra el total pagado y al abrirlo aparecen los movimientos con fecha y detalles.
  - [x] El cierre es definitivo y el pedido histórico es solo de consulta: no se permite reabrir, desmarcar instalado, registrar devoluciones, anular movimientos ni realizar otras correcciones desde el histórico.
  - [x] No se guardan marcas ni resumen de avance de corte y ensamble en el histórico: el pedido instalado implica que esas tareas estaban completas.
- **Subtarea [#87](https://github.com/ErickRamos37/AVAO/issues/87), implementada y aceptada — Cerrar y consultar pedidos finalizados:** Al quedar instalado y liquidado, cerrar automáticamente el pedido, registrar la fecha de cierre, retirarlo de la cola activa, liberar su etiqueta y conservarlo en un histórico de solo consulta con los datos acordados. Identificar el pedido por ID y fecha de cierre y «Ventanas:» y una lista numerada de solo medidas base ancho × alto, sin prefijos ni tabla; no conservar ni mostrar la etiqueta de letras ni códigos de taller. No almacenar el desglose individual de materiales ni sus costos; conservar importes agregados por ventana, total del pedido, merma, traslado y movimientos. Eliminar medidas derivadas de corte y no conservar marcas ni resumen de avance. Presentar ventanas, mermas y traslado, total del pedido y pagos en ese orden; pagos se despliega desde un encabezado con total pagado y muestra los movimientos con fecha y detalles. El cierre es definitivo, sin reapertura, devoluciones ni correcciones desde el histórico.
- **Dependencias y límites:** Usa movimientos y saldo de HU-14 e instalación de HU-16. Las decisiones de reapertura, devoluciones y correcciones desde histórico se resolvieron como no permitidas; tampoco se conservarán marcas ni resumen del avance.

### HU-27 — Recuperar merma de hojas de vidrio

- **Área:** Precios y cobros · **Épica:** E4 · **Esfuerzo histórico:** 3. **Estado:** implementada y aceptada por el usuario, incluida la presentación de importes enteros.
- **Historia:** **Como** encargado del negocio, **necesito** aplicar un umbral configurable a la merma de vidrio del pedido, **para** recuperar su costo como cargo separado cuando corresponda.
- **Reglas confirmadas:** estimar consumo sumando el área en pulgadas cuadradas del vidrio del pedido y evaluar el residual de la última hoja de 71″ × 102″ con las mismas reglas de umbral de aluminio. El umbral de vidrio es editable en inventario de forma independiente al de aluminio; ambos comienzan en 80 %. Es entero de 0 a 100 y 0 % desactiva la recuperación. El cargo es separado y no recibe ganancia; cambia mediante **Recalcular**, y la selección desmarcada persiste. El cálculo por área no comprueba que las piezas quepan en la hoja; no incorpora acomodo ni optimización 2D. Los errores del negocio no se cobran como desperdicio.
- **Cambio de decisión:** la propuesta anterior de distribuir la recuperación dentro del precio de cada ventana se sustituye por el cargo separado confirmado.
- **Criterios de aceptación propuestos:**
  - [ ] Permite editar el umbral de vidrio independientemente del de aluminio en inventario; ambos comienzan en 80 %. Admite enteros de 0 a 100 y 0 % desactiva la recuperación.
  - [ ] Suma el área de vidrio del pedido y evalúa el consumo residual de la última hoja de 71″ × 102″ según la regla acordada; una hoja completa no produce sobrante recuperable.
  - [ ] Presenta el cargo separado, sin ganancia; cambia solo al recalcular y, si se desmarca, mantiene esa elección al recalcular y volver a consultar.
  - [ ] No cobra errores del negocio ni afirma haber comprobado el acomodo físico de las piezas.
- **Subtarea [#79](https://github.com/ErickRamos37/AVAO/issues/79), implementada y aceptada — Calcular y consultar la merma opcional de vidrio:** configurar el umbral acordado, estimar el residual por área del vidrio del pedido, calcular y mostrar el cargo separado y conservar la selección desmarcada; comprobar umbral cero, hoja completa, recálculo explícito y persistencia. Sin optimización 2D.
- **Dependencias/límites:** depende de HU-18, HU-11 y HU-25; incluida en el Ciclo 4. No incluye acomodo u optimización 2D ni reutilización automática de sobrantes.

### Reglas y decisiones transversales del ciclo

**Reglas confirmadas:** el anticipo para aceptar el pedido debe alcanzar un mínimo configurable, entero de 1 a 100 %, inicialmente 50 %, similar al porcentaje de ganancia. Pueden registrarse varios pagos: reducen el saldo, no el total de venta; el total puede pagarse desde el inicio. El saldo es el total vigente menos (pagos menos devoluciones), por lo que cambia cuando cambia el total. Cada pago y cada devolución se registra con importe y fecha automática del día de la acción; la anulación también conserva automáticamente su fecha. Un movimiento incorrecto puede anularse solo cuando todos los precios del pedido están completos; si el total es parcial o falta, se bloquea la anulación sin modificar el movimiento. Permanece visible como anulado y se registra el movimiento correcto; los anulados no cuentan para neto, saldo ni liquidación. Si se anula un anticipo y el neto queda bajo el mínimo, vuelve a presupuesto; un cambio de total por sí solo no revierte la aceptación. El pedido está liquidado cuando la suma de pagos menos la suma de devoluciones es mayor o igual al total de venta. Si se paga de más, se muestra la diferencia; solo se puede devolver el excedente sobre el total, como máximo neto menos total. Se registra la devolución y su importe o el cliente puede decidir dejar voluntariamente el excedente sin devolución, sin asignarle otra clasificación. La fecha de instalación tiene campo propio. El pedido se marca instalado completo solo si todos sus cortes y ensambles están completos; se señalará en la esquina de su tarjeta con palomita verde o texto y en su detalle. Al estar instalado se bloquean ventanas, medidas y fabricación, pero se permiten pagos y devoluciones. Se puede desmarcar instalado con una advertencia por error o trabajos adicionales. Solo instalado **y** liquidado sale de la cola activa al histórico de pedidos finalizados y liquidados y libera su etiqueta. Después del anticipo el pedido sigue modificable: las medidas aproximadas pueden sustituirse por medidas exactas, con cambios en precios y merma; se conserva el porcentaje de ganancia y entonces puede agregarse el traslado. El histórico conserva cliente, medidas base, importes agregados por ventana, total del pedido, merma, traslado y movimientos como respaldo; no almacena el desglose individual de materiales ni sus costos, y elimina las medidas derivadas de corte. Antes del anticipo mínimo el trabajo es un presupuesto fuera de la cola y el taller, sin marcas de fabricación; al alcanzar el mínimo configurable el pedido cuenta para empezar el trabajo. Para registrar el anticipo se exige el total completo calculado. La aceptación permanece tras cambios posteriores del total aun si el anticipo queda por debajo del mínimo. La fecha programada de instalación es obligatoria después de registrar ese anticipo, no una precondición para registrar el dinero; se reajusta de acuerdo con el cliente. La fecha real de instalación se registra automáticamente el día que se marca instalado. La fecha programada se muestra bloqueada por defecto y solo se modifica al pulsar **Editar**, con opciones de guardar o cancelar, siguiendo el patrón de traslado. La fecha real no se captura manualmente.

**Decisiones confirmadas de HU-17:** el cierre es definitivo y el histórico es solo de consulta, sin reapertura, devoluciones, anulaciones ni otras correcciones. Se registra automáticamente la fecha de cierre al cumplirse instalación y liquidación. Se conservan importes agregados por ventana (costo, precio y ganancia si aplica), total del pedido, merma, traslado y movimientos; no se almacena el desglose individual de materiales ni sus costos. No se conservan marcas ni resumen del avance de corte y ensamble. El detalle presenta ventanas, mermas y traslado, total del pedido y pagos, en ese orden; pagos se despliega desde un encabezado con el total pagado y muestra movimientos con fecha y detalles. El histórico identifica el pedido por ID y fecha de cierre y «Ventanas:» y una lista numerada de solo medidas base ancho × alto, sin prefijos, tabla ni códigos, sin conservar ni mostrar etiqueta de letras ni códigos de taller.

**Por decidir antes de implementar:** otros detalles de cancelación. La cancelación, ajustes y comprobantes siguen abiertos cuando correspondan. El usuario autorizó reiniciar los datos de prueba; se preparará respaldo y se conservará el catálogo de costos.

**Tensión con el flujo actual:** al guardar medidas hoy se asignan etiqueta, cola y cortes. El presupuesto anterior al anticipo mínimo queda fuera de cola y taller, sin marcas ni etiqueta, identificado por ID; al aceptarse por anticipo mínimo se asignan etiqueta y códigos de ventana. Una anulación que reduce el neto bajo el mínimo devuelve el pedido a presupuesto y libera su etiqueta; al aceptarlo de nuevo se asigna una letra disponible y se conservan ID, ventanas y eventos; un cambio de total por sí solo no revierte la aceptación.

**Límite por confirmar:** modificar medidas aproximadas de un pedido existente no aprueba por sí solo la cotización preliminar sin etiqueta ni posición descrita más abajo. Esa necesidad conserva sus decisiones abiertas; no incorporarla al ciclo 4 sin acordar su alcance.

HU-14 y HU-17 comparten movimientos: HU-14 los registra y calcula el saldo; HU-17 usa ese resultado para cerrar, evitando construir dos registros de pagos.

## Ciclo 5 cerrado: medición del taller

**Regla implementada y aceptada para el flujo actual:** el presupuesto sin anticipo mínimo no ocupa letra y se identifica por ID; al aceptarse por anticipo mínimo se asignan la etiqueta y los códigos de ventana. Si una anulación lo devuelve a presupuesto se libera la etiqueta; al aceptarlo de nuevo se asigna una letra disponible y se conservan ID, ventanas y eventos.

El usuario acordó registrar eventos y consultar el flujo del taller durante meses y años, sin medir tiempo efectivo ni productividad individual. Las seis historias HU-28 a HU-33 fueron implementadas y aceptadas por el usuario. HU-33 se integró a develop mediante [PR #115](https://github.com/ErickRamos37/AVAO/pull/115), commit `98323c5`; pasaron 41 pruebas del tablero. El usuario autorizó cerrar el ciclo: se conservan historias y esfuerzos históricos y se retiran las prioridades de las terminadas. El usuario aceptó los esfuerzos relativos y las prioridades del ciclo 5. E5 agrupa las consultas y eventos que apoyan decisiones; la captura de eventos precede a las consultas que dependen de ella, sin fijar otro orden entre historias de igual prioridad. Las dependencias orientan el orden, sin sustituir la decisión del usuario. HU-28 se estima en 8 por la variedad de eventos, correcciones e histórico; si al refinar supera 8, se propondrá dividirla en historias con valor propio antes de implementarla.

| ID | HU | Épica | Esfuerzo histórico | Prioridad actual | Resultado |
| --- | --- | --- | --- | --- | --- |
| HU-28 | Consultar hitos y avance de fabricación | E5 | 8 | — | Implementada y aceptada; subtareas #96 y #97 |
| HU-29 | Consultar cambios de medida y piezas afectadas | E5 | 5 | — | Implementada y aceptada; subtarea #99 |
| HU-30 | Consultar programación y reprogramaciones | E5 | 5 | — | Implementada y aceptada; subtarea #101 |
| HU-31 | Consultar producción por periodos | E5 | 5 | — | Implementada y aceptada; subtarea #103 |
| HU-32 | Consultar pedidos e instalaciones | E5 | 5 | — | Implementada y aceptada; subtarea #112 |
| HU-33 | Consultar ingresos y ganancia estimada | E5 | 8 | — | Implementada y aceptada; subtarea #113; integrada por PR #115 |

### HU-28 — Consultar hitos y avance de fabricación

- **Estado:** implementada y aceptada por el usuario; subtareas [#96](https://github.com/ErickRamos37/AVAO/issues/96) y [#97](https://github.com/ErickRamos37/AVAO/issues/97). La clasificación detallada de cambios de medida pertenece a HU-29.

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 8. Integra varios eventos, correcciones y conservación al cierre; requiere revisar tamaño antes de implementar.

- **Historia:** **Como** encargado, **necesito** consultar cuándo se registraron los hitos comerciales y el avance de fabricación de cada pedido, **para** conocer su recorrido y contar el trabajo registrado por periodo.
- **Criterios de aceptación:**
  - [x] Al crear un presupuesto, alcanzar el anticipo mínimo, registrar el primer corte de aluminio o vidrio, registrar cortes y ensambles completos, instalar, liquidar y cerrar, se registran automáticamente los eventos correspondientes con fecha y hora. El anticipo mínimo señala el inicio comercial; el primer corte señala el inicio de fabricación.
  - [x] Se pueden consultar los eventos vinculados al pedido y, cuando corresponda, la ventana y el área. Se cuentan piezas físicas individuales de aluminio o vidrio cortadas y ventanas completas ensambladas por día, semana y mes.
  - [x] Una corrección manual que deshace una marca ajusta el conteo del día original y conserva el evento de corrección.
  - [ ] La identificación detallada de piezas afectadas por una corrección de dimensiones corresponde a HU-29; la producción original se conserva como ocurrida.
  - [x] Los eventos ligeros permanecen consultables tras el cierre, sin conservar por ello planes de corte ni desglose individual de materiales y costos.
- **Dependencias y límites:** depende de la aceptación y movimientos de HU-14, instalación de HU-16 y cierre de HU-17. La hora es del registro, que puede hacerse por tandas después del trabajo: no demuestra la hora real del trabajo, tiempo efectivo ni productividad individual. Los datos antiguos no permiten reconstruir con fiabilidad los eventos que no se registraron.
- **Subtareas verticales propuestas:**
  1. **[Consultar hitos del pedido (#96)](https://github.com/ErickRamos37/AVAO/issues/96), implementada y aceptada:** registrar creación, aceptación, instalación, liquidación y cierre con fecha y hora; consultar y conservarlos al cerrar. Conservar todos los eventos de pérdida y recuperación de liquidación y mostrar el último.
  2. **[Consultar cortes y ensambles registrados (#97)](https://github.com/ErickRamos37/AVAO/issues/97), implementada y aceptada:** registrar primer corte y avance por pieza o ventana, distinguir correcciones manuales y consultar conteos por periodo; conservar eventos al cerrar. Asignar las tandas al día en que se registran.
- **Reglas confirmadas:** conservar todos los eventos de pérdida y recuperación de liquidación y mostrar el último; fechas y horas en la zona de Tijuana, con semanas de lunes a domingo, incluyendo domingos; las tandas se asignan al día del registro aunque el trabajo fuera anterior.

### HU-29 — Consultar cambios de medida y piezas afectadas

- **Estado:** implementada y aceptada por el usuario; subtarea [#99](https://github.com/ErickRamos37/AVAO/issues/99).

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 5. Reutiliza HU-07 y los eventos, pero debe distinguir causas y piezas afectadas.

- **Historia:** **Como** encargado, **necesito** consultar cambios de medida posteriores a la aceptación y piezas cortadas afectadas, **para** conocer su incidencia en el trabajo del taller.
- **Criterios de aceptación:**
  - [x] Se registran y consultan los cambios de medidas base posteriores a la aceptación, con las medidas anteriores y nuevas y el momento del cambio; se excluyen las correcciones realizadas mientras se trata de un presupuesto.
  - [x] Cuando cambiar las dimensiones modifica una medida derivada y HU-07 deshace automáticamente marcas, se registran la cantidad previamente cortada afectada, el tipo de perfil o vidrio, la edición relacionada y la fecha y hora. Las piezas sin cambio de medida derivada conservan su marca y no cuentan como afectadas; desmarcar manualmente no cuenta como este caso.
  - [x] Para perfiles de aluminio, si la nueva longitud requerida supera la ya cortada, las piezas afectadas se clasifican como «sobrante recuperable por cambio de medida». Si la nueva longitud es menor, se registran como afectadas y queda abierta la posibilidad de recorte; si es igual, no se consideran afectadas por longitud.
  - [x] Los eventos de corte originales permanecen en la producción histórica; los eventos de cambio y piezas afectadas se consultan por separado y se conservan tras el cierre.
- **Dependencias y límites:** depende de HU-07 y del registro de HU-28. La clasificación no implica desperdicio definitivo, cargo monetario de HU-26 ni inventario automático de sobrantes; un cambio no demuestra por sí solo error de medición. La regla de longitud mayor o menor se refiere a perfiles y no se extiende al vidrio sin confirmación.
- **Subtarea [#99](https://github.com/ErickRamos37/AVAO/issues/99), implementada y aceptada — Consultar cambios de medidas y piezas cortadas afectadas:** registrar y consultar cambios posteriores a la aceptación, sus medidas anteriores y nuevas y las piezas previamente cortadas afectadas; clasificar perfiles según longitud, conservar producción original y eventos al cierre, y comprobar que correcciones de presupuesto quedan fuera.
- **Reglas confirmadas:** el vidrio afectado se registra sin clasificación de recuperación; descartar una ventana conserva la producción ya registrada.

### HU-30 — Consultar programación y reprogramaciones

- **Estado:** implementada y aceptada por el usuario; subtarea [#101](https://github.com/ErickRamos37/AVAO/issues/101).

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 5. Amplía fechas existentes con historial y motivos por definir.

- **Historia:** **Como** encargado, **necesito** consultar la fecha de instalación acordada y sus cambios, **para** dar seguimiento a los compromisos con el cliente.
- **Criterios de aceptación:**
  - [x] Se conservan y consultan la fecha programada original y cada reprogramación, con fecha anterior y nueva y momento de registro.
  - [x] Al reprogramar se exige un motivo: falta de material, fabricación pendiente, disponibilidad del cliente, disponibilidad del taller/transporte u «Otros» con texto; la fecha real de instalación conserva fecha y hora. Un pedido no instalado queda visiblemente atrasado al pasar la fecha actualmente acordada.
- **Dependencias y límites:** amplía las fechas de HU-15 y el registro de HU-28. La reprogramación y el atraso no tienen necesariamente el mismo motivo.
- **Subtarea [#101](https://github.com/ErickRamos37/AVAO/issues/101), implementada y aceptada — Consultar fechas y motivos de instalación:** conservar y mostrar fecha original, reprogramaciones con valores anterior y nuevo y momento, y motivo obligatorio de catálogo o «Otros» con texto; señalar atraso al pasar la fecha acordada sin instalar y comprobar consulta tras cerrar.
- **Regla confirmada:** catálogo de motivos: falta de material, fabricación pendiente, disponibilidad del cliente, disponibilidad del taller/transporte y «Otros» con texto.

**Criterio común confirmado para HU-31, HU-32 y HU-33:** las consultas de producción, pedidos e instalaciones y finanzas se reúnen en una única página exclusiva de tablero, accesible desde la navegación principal. Las funciones posteriores se incorporan a esa misma página, sin duplicarlas ni dispersarlas por la aplicación. La ruta `/dashboard` es una opción técnica, no un requisito de producto. No se define diseño ni organización visual adicional.

### HU-31 — Consultar producción por periodos

- **Estado:** implementada y aceptada por el usuario; subtarea [#103](https://github.com/ErickRamos37/AVAO/issues/103).

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 5. 
**Historia:** **Como** encargado, **necesito** consultar gráficas y promedios de producción registrada por periodo, **para** observar el comportamiento del taller.
- **Criterios de aceptación:**
  - [x] Consultar cantidades y gráficas de piezas de aluminio y vidrio cortadas y ventanas ensambladas por día, semana, mes y año; semanas de lunes a domingo en horario de Tijuana, incluyendo domingos.
  - [x] Mostrar por separado el total y promedio diario del periodo para aluminio, vidrio y ensambles. En la semana, mes y año actuales, dividir entre los días calendario transcurridos hasta hoy inclusive, incluidos los días sin actividad y domingos, sin contar días futuros. Distinguir registro por tandas de hora real de trabajo y aplicar correcciones de HU-28; advertir la cobertura limitada anterior al registro de eventos.
- **Subtarea [#103](https://github.com/ErickRamos37/AVAO/issues/103), implementada y aceptada — Consultar producción registrada:** presentar gráficas, total y promedio diario por periodo separados para aluminio, vidrio y ensambles, basados en eventos conservados. En periodos actuales incluir solo días transcurridos hasta hoy, con ceros y domingos; advertir cobertura limitada de datos anteriores. **Dependencia:** HU-28. No inferir productividad individual o causas de cuellos de botella.
- **Ajuste de navegación implementado y aceptado:** producción se consulta en la página única del tablero accesible desde la navegación principal, conservando los cálculos y criterios aceptados.
- **Mejora futura por definir:** hacer más clara la lectura de picos y caídas de la gráfica, sin inventar datos ni decidir todavía una técnica de representación.

### HU-32 — Consultar pedidos e instalaciones

- **Estado:** implementada y aceptada por el usuario; subtarea [#112](https://github.com/ErickRamos37/AVAO/issues/112).

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 5. 
**Historia:** **Como** encargado, **necesito** consultar pedidos listos, pendientes e instalaciones y promedios de salidas, **para** organizar compromisos.
- **Criterios de aceptación:**
  - [x] Mostrar estas consultas en la misma página exclusiva de tablero que producción, accesible desde la navegación principal.
  - [x] Consultar pedidos listos para instalar (al menos una ventana activa, todas las activas ensambladas y aún no instalado), pendientes por área y por instalar; pendiente es un pedido aceptado activo que no está listo ni instalado. Indicar los pedidos sin ventanas activas y señalar instalaciones atrasadas conforme a HU-30. Una instalación próxima es la programada en cinco días o menos.
  - [x] Consultar por separado pedidos instalados y pedidos finalizados (instalados y liquidados), y sus promedios diarios por semana, mes y año con la regla de HU-31, incluidos días sin actividad. Se cuenta una instalación vigente por pedido: al desmarcar se retira del conteo y al marcar de nuevo cuenta la nueva instalación; los eventos históricos permanecen.
- **Subtarea [#112](https://github.com/ErickRamos37/AVAO/issues/112), implementada y aceptada — Consultar pedidos y salidas:** mostrar listas y promedios diarios con fechas de instalación e histórico, próximas a cinco días o menos e instalación vigente por pedido. **Dependencias:** HU-28 y HU-30. **Reglas confirmadas:** las próximas son a cinco días o menos; el conteo usa la instalación vigente y conserva el historial de eventos. Los promedios diarios siguen HU-31.

### HU-33 — Consultar ingresos y ganancia estimada

- **Estado:** implementada y aceptada por el usuario; subtarea [#113](https://github.com/ErickRamos37/AVAO/issues/113). Integrada a develop mediante [PR #115](https://github.com/ErickRamos37/AVAO/pull/115), commit `98323c5`.

- **Área:** Visibilidad · **Épica:** E5.

- **Esfuerzo histórico:** 8. **Historia:** **Como** encargado, **necesito** consultar gráficas y promedios de ingresos y ganancia estimada, **para** observar el comportamiento económico del negocio.
- **Criterios de aceptación:**
  - [x] Mostrar estas consultas en la misma página exclusiva de tablero que producción y pedidos, accesible desde la navegación principal.
  - [x] Consultar gráficas y promedios de pagos recibidos, devoluciones e ingresos netos, además de saldos. El promedio monetario diario sigue HU-31: días calendario transcurridos hasta hoy inclusive, incluidos días sin actividad. Para comparar días de la semana, mostrar el ingreso neto promedio por ocurrencia de cada día en el periodo, incluyendo las ocurrencias sin movimiento. Excluir anulaciones conforme a HU-14.
  - [x] Mostrar dos indicadores de ganancia estimada usando la ganancia guardada de ventanas activas no descartadas: pedidos activos aceptados como situación actual, incluidos los ya pagados que aún no están instalados; y pedidos finalizados, instalados y con pagos netos iguales o superiores al total, agrupados por fecha de cierre. No incluir presupuestos, merma ni traslado como ganancia; no presentarla como utilidad neta porque faltan mano de obra y gastos.
- **Subtarea [#113](https://github.com/ErickRamos37/AVAO/issues/113), implementada y aceptada — Consultar movimientos y ganancia estimada:** integrar gráficas y promedios con pagos, devoluciones y saldos; calcular promedio diario con días transcurridos y comparar ingreso neto por ocurrencia de cada día de la semana, incluyendo ceros; mostrar por separado la ganancia guardada de ventanas de pedidos activos aceptados y finalizados agrupados por cierre. **Dependencias:** HU-14 y HU-17. La ganancia de activos es una instantánea actual, no se atribuye al cobro y no permite comparaciones históricas sin capturas adicionales. **Regla confirmada:** los promedios diarios incluyen días calendario sin actividad hasta hoy; la comparación por día de semana divide el ingreso neto entre las ocurrencias de ese día, incluidos ceros.

### HU-34 — Seguimiento de presupuestos, fuera del ciclo 5

El usuario decidió posponer la consulta de presupuestos inactivos o perdidos. Se conserva la intención y el identificador como idea futura, sin prioridad, esfuerzo ni implementación acordados. La propuesta de señalar presupuestos sin pagos y con más de una semana sin actualizar como candidatos por revisar no determina una pérdida definitiva; quedan por decidir qué cuenta como actualización y cómo confirmar una pérdida.

**Temas futuros sin reglas ni historias aprobadas:** definir cómo registrar material surtido o faltante, bloqueos y sus causas, estimaciones de fabricación y satisfacción del cliente. La investigación no fija todavía su alcance ni los incorpora automáticamente a estas entregas.

## Ciclo 6: propuesta de usabilidad por acordar

**Objetivo propuesto:** facilitar el recorrido de trabajo y la comprensión de información y acciones, sin rediseño visual. El usuario aprobó E6, los esfuerzos y las prioridades de HU-35 a HU-38; cada entrega conserva sus reglas pendientes y se refinará antes de construirla.

**Posibles resultados:** mejorar la navegación según el flujo real; ordenar la información y mostrar controles en el momento adecuado; permitir editar por bloques con guardar, cancelar y aviso de cambios sin guardar; y estudiar una previsualización de precios que reduzca la fricción de calcular cada ventana. Cualquier modificación al tratamiento de precios guardados necesita una regla acordada antes de implementarse.

**Hipótesis derivadas de revisión del código, por validar con el usuario:** los datos del cliente pueden quedar editables sin cancelar y una reapertura podría perder cambios; una etiqueta «Precio ventana» podría referirse al costo base; algunos controles de instalación aparecen antes de necesitarlos y se acumulan bajo Medidas; calcular cada ventana por separado podría dificultar el flujo. Estas observaciones no sustituyen una prueba del uso real.

**Flujo de edición aprobado para refinar:** al editar se prepara una vista previa sin perder los valores originales. Una primera confirmación valida que se desean aplicar los cambios. Antes de guardar se muestran solo las ventanas afectadas, con su etiqueta, medidas anteriores y nuevas, precio anterior y precio sugerido tras los cambios, más un resumen de la diferencia del total del pedido; no se muestran perfiles ni filas de ventanas no afectadas. Se ofrece **Conservar precio acordado**, **Actualizar precio** o **Cancelar toda la acción**. Solo tras la segunda confirmación se guardan los cambios conjuntamente; cancelar no modifica los datos originales. Conservar el precio aceptado no impide actualizar internamente los costos. En un presupuesto, mostrar el impacto antes de guardar sin modificar los datos anticipadamente.

**Distinción de importes:** el costo base actualizado de materiales se distingue del precio sugerido con ganancia y del precio acordado elegido. El usuario quiere conocer la ganancia o pérdida al absorber un cambio. La fórmula confirmada de ganancia estimada es precio cobrado elegido menos costo actualizado de materiales; no se resta el precio sugerido que ya incluye ganancia. Esta cifra no es utilidad neta porque no incluye mano de obra ni gastos. Un cambio no se atribuye automáticamente a culpa del taller.

**Reglas confirmadas para la vista previa:** al editar una ventana se usan los costos vigentes del inventario solo para las ventanas editadas; las demás conservan sus importes guardados. Se recalcula la merma del pedido conservando su selección incluida o desmarcada y la vista previa resume la diferencia del cargo. Un cambio de inventario por sí solo no modifica pedidos en segundo plano; el cálculo ocurre al editar o realizar una nueva captura. Se conserva el porcentaje de ganancia guardado.

**Reglas pendientes antes de implementar:** decidir si conservar o actualizar precio se elige por ventana o para todas las afectadas y qué ocurre con el cargo de merma recalculado al conservar precio; precisar la presentación de la pérdida y la comparación en presupuesto y pedido aceptado. Si se conserva el precio acordado con un costo diferente, mostrar la ganancia estimada confirmada, o pérdida cuando sea negativa; precisar su presentación. Precisar el comportamiento para presupuestos y pedidos aceptados antes de definir la entrega.

**Épica aprobada:** E6 — Facilitar el trabajo cotidiano del taller. Los esfuerzos y prioridades indicados están aceptados; las subtareas son propuestas para revisión y no implican incidencias creadas.

| ID | Historia | Épica | Esfuerzo aceptado | Prioridad aceptada | Estado |
| --- | --- | --- | --- | --- | --- |
| HU-35 | Navegar según el flujo del pedido | E6 | 5 | Alta | Propuesta por refinar |
| HU-36 | Editar y cancelar por bloque | E6 | 5 | Alta | Propuesta por refinar |
| HU-37 | Consultar presupuesto durante la captura | E6 | 5 | Alta | Propuesta por refinar |
| HU-38 | Revisar impacto de cambios antes de guardar | E6 | 8 | Alta | Propuesta por refinar |

### HU-35 — Navegar según el flujo del pedido

- **Historia:** **Como** empleado, **necesito** encontrar la información y acciones relevantes en cada momento del pedido, **para** avanzar sin buscar controles que aún no necesito.
- **Criterios propuestos:**
  - [ ] La navegación permite seguir el flujo del presupuesto, fabricación e instalación y encontrar las acciones correspondientes a cada etapa.
  - [ ] La información y controles se presentan cuando corresponden al estado del pedido; las acciones siguen siendo accesibles cuando se necesitan.
- **Subtarea vertical propuesta — Navegar por el flujo del pedido:** organizar acceso a información y acciones según el estado, comprobar presupuesto, fabricación e instalación y conservar controles necesarios.
- **Límites y preguntas:** conservar funcionalidades existentes y estilo actual; acordar con el usuario el recorrido concreto antes de implementarlo. Sin rediseño visual.

### HU-36 — Editar y cancelar por bloque

- **Historia:** **Como** empleado, **necesito** editar cada bloque de información de manera explícita, **para** guardar o cancelar mis cambios sin perderlos accidentalmente.
- **Criterios propuestos:**
  - [ ] Un bloque se consulta y entra en edición explícitamente; guardar persiste sus cambios y cancelar conserva los valores anteriores.
  - [ ] Si hay cambios sin guardar, se advierte antes de abandonar o cambiar de contexto. Editar datos del cliente o fechas no cambia precios acordados.
- **Subtarea vertical propuesta — Editar información por bloque:** activar edición explícita con guardar y cancelar, advertir cambios pendientes al salir y comprobar persistencia, cancelación y navegación.
- **Límites y preguntas:** acordar bloques y comportamiento al navegar; cambios de medidas con impacto de precio dependen de HU-38. Sin rediseño visual.

### HU-37 — Consultar presupuesto durante la captura

- **Historia:** **Como** empleado, **necesito** consultar un cálculo provisional mientras capturo un presupuesto, **para** conocer el impacto de las medidas sin calcular cada ventana por separado.
- **Criterios propuestos:**
  - [ ] Al capturar o cambiar medidas válidas se actualiza la vista provisional de las ventanas y total; si faltan datos se informa sin presentar importes inexistentes como cero.
  - [ ] La vista provisional se distingue del precio guardado y no modifica un precio aceptado por cambios de inventario en segundo plano.
- **Subtarea vertical propuesta — Consultar cálculo provisional al capturar:** actualizar la vista al introducir medidas válidas, mostrar pendientes y comprobar que no guarda borradores ni altera precios aceptados sin decisión.
- **Límites y preguntas:** el cálculo de captura nueva usa costos vigentes y conserva la selección de merma; la captura incompleta no implica un precio definitivo. Precisar cómo mostrar el efecto de la merma. Sin rediseño visual.

### HU-38 — Revisar impacto de cambios antes de guardar

- **Historia:** **Como** empleado, **necesito** revisar el impacto de una edición y elegir el precio antes de guardarla, **para** conservar el acuerdo con el cliente o actualizarlo conscientemente.
- **Criterios propuestos:**
  - [ ] La primera confirmación revisa la intención de aplicar la edición; antes de guardar, la segunda muestra solo ventanas afectadas, su etiqueta, medidas anteriores y nuevas, precio anterior y sugerido, y diferencia total del pedido, sin filas de materiales ni ventanas no afectadas.
  - [ ] La vista previa usa costos vigentes de inventario solo en ventanas editadas, conserva los importes guardados de las demás y el porcentaje de ganancia guardado, y recalcula la merma del pedido manteniendo su selección incluida o desmarcada. El resumen muestra la diferencia del cargo de merma. Cambiar inventario por sí solo no modifica pedidos en segundo plano.
  - [ ] Se puede conservar el precio acordado, actualizarlo o cancelar toda la acción. Guardar ocurre conjuntamente después de la decisión final; cancelar conserva todos los datos originales. El precio conservado no impide actualizar el costo de materiales.
  - [ ] Se distingue costo base de materiales, precio sugerido y precio cobrado elegido. La ganancia estimada es precio cobrado elegido menos costo actualizado de materiales; un resultado negativo es pérdida. No se presenta como utilidad neta ni se presume culpa del taller.
  - [ ] Cambiar solo cliente o fecha y cambios de costos de inventario en segundo plano no alteran los precios aceptados.
- **Subtarea vertical propuesta — Revisar y confirmar cambios de medidas:** preparar comparación, solicitar ambas confirmaciones y aplicar conjuntamente la elección de precio, costos, merma y medidas; comprobar conservar, actualizar y cancelar, ventanas intactas y validaciones existentes de precios, anticipo, saldo y anulaciones.
- **Dependencias y límites:** depende de reglas de cálculo y edición acordadas para HU-36/HU-37; no guarda parcialmente ni modifica datos al cancelar. La etiqueta de un presupuesto sin código debe seguir su identificación por ID.
- **Preguntas abiertas:** ¿la elección de precio se hace por ventana o para todas las afectadas? Al conservar el precio, ¿cómo se trata el cargo de merma recalculado? ¿Cómo presentar la pérdida y la comparación en presupuesto y pedido aceptado?

**Apoyos posibles, sin instalar ni adoptar por anticipado:** Impeccable (audit, clarify y distill) para revisar usabilidad; ProMax si más adelante se solicita trabajo visual; y los flujos de simplicidad y entrega vertical existentes para mantener el alcance pequeño.

## Secuencia comercial prevista: datos, precios, aceptación y liquidación

Secuencia funcional prevista: **empleado captura medidas → completa datos de cliente → calcula precio de ventanas e incorpora servicios opcionales → comunica total → si cliente acepta, registra anticipo y confirma pedido → taller fabrica → se instala; los pagos pueden liquidar el saldo antes o después de instalar → se cierra al cumplir ambas condiciones**. El Ciclo 3 cubrió el precio de las ventanas, el total del pedido, traslado y merma de aluminio; el Ciclo 4 completó aceptación, anticipo y cierre comercial. No hay interfaz del cliente prevista.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-13 | Pedidos y medidas · E3 | **Como** empleado, **necesito** completar, consultar y corregir los datos del cliente y las notas del pedido cuyas ventanas ya guardé, **para** conservar la información de contacto y las especificaciones de trabajo antes de calcular el precio. | Nombre, primer apellido y celular obligatorios; segundo apellido, dirección y notas opcionales. Las notas pertenecen al pedido y las consultan los trabajadores. |
| HU-11 | Precios y cobros · E3 | **Como** empleado, **necesito** calcular el costo de los materiales requeridos por cada ventana según sus medidas y el inventario, **para** conocer la base del precio de venta. | HU-18, unidades y exactitud del valor de insumo. |
| HU-12 | Precios y cobros · E3 | **Como** empleado, **necesito** agregar un importe opcional de traslado al pedido, **para** presentarlo separado del precio de las ventanas y conocer el total. | Importe único estimado manualmente según ubicación y gasolina. Sin instalación como servicio ni tarifa automática. |
| HU-14 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar anticipo y confirmar el pedido aceptado, **para** iniciar el trabajo con total y saldo visibles. | Confirmados anticipo mínimo configurable, varios pagos y saldo; confirmada la modificación posterior de medidas y precios; confirmados excedente visible, devoluciones e importe y fecha automática de cada movimiento y anulación; confirmada anulación con historial visible y exclusión del neto; pendiente cancelación. |
| HU-15 | Instalación · E3 | **Como** empleado, **necesito** registrar día y, si se acuerda, hora de instalación, **para** coordinar la visita con el cliente. | Fechas programada obligatoria y real confirmadas; la programada se muestra bloqueada y se reajusta con el cliente mediante Editar, guardar o cancelar, como traslado. La programada se exige después de registrar el anticipo mínimo, sin bloquear su registro; fecha real registrada automáticamente al marcar instalado. |
| HU-16 | Instalación · E3 | **Como** instalador, **necesito** marcar el pedido instalado, **para** distinguir la entrega física de la liquidación del saldo. | Confirmados cortes y ensambles completos, señal visible, bloqueo de ventanas, medidas y fabricación, pagos permitidos y desmarcado con advertencia; cierre definitivo sin desmarcar desde histórico. |
| HU-17 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar pagos posteriores y la liquidación final, **para** conocer el saldo y cerrar el pedido cuando esté instalado y pagado por completo. | Confirmados varios pagos, cierre instalado y liquidado, histórico y liberación de etiqueta; confirmada conservación de importes agregados por ventana, total, merma, traslado, pagos y medidas base, sin desglose individual de materiales ni sus costos; liquidado cuando pagos menos devoluciones alcanza el total; cierre definitivo de solo consulta; ajustes y comprobantes siguen pendientes fuera del histórico. |

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

La recuperación de desperdicio de vidrio se registra en HU-27 para el Ciclo 4, separada de la futura optimización de cortes. No duplicar las capacidades del Ciclo 3 en esta sección.

| ID | Área · Épica | Historia | Regla pendiente |
| --- | --- | --- | --- |
| HU-18 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** mantener y actualizar el costo real de compra de los perfiles, vidrio y accesorios usados por California por mitad, **para** calcular el costo de sus materiales con valores vigentes. | Catálogo y unidades mínimas del primer caso; otros productos y existencias quedan fuera. |
| HU-19 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** aplicar un porcentaje de ganancia al costo total de materiales de cada ventana, **para** obtener su precio antes de agregar servicios. | Ejemplo del porcentaje; no aplicar ganancia independiente por perfil. |
| HU-20 | Visibilidad · Sin épica | **Como** encargado del negocio, **necesito** ver pedidos pendientes, en fabricación, listos, instalados y liquidados, **para** consultar su situación desde un lugar. | Estados confiables e indicador de avance verificable. |
| HU-21 | Materiales · Sin épica | **Como** encargado de materiales, **necesito** estimar perfiles y hojas de vidrio requeridos por los pedidos actuales, **para** anticipar compras cuando hagan falta. | Demanda frente a faltantes, existencias, unidades de compra, sobrantes y desperdicio. |
| HU-25 | Precios y cobros · E3 | **Como** empleado, **necesito** consultar el total de las ventanas activas de un pedido, **para** comunicar el importe de sus productos antes de agregar servicios o registrar pagos. | Excluir ventanas descartadas; no implica aceptación del presupuesto ni saldo. |
| HU-26 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** aplicar un umbral configurable a la merma de perfiles de aluminio del pedido, **para** recuperar su costo como cargo separado cuando corresponda. | Umbral común inicial de 80 %, editable; cargo desmarcable sin ganancia. Último tramo por perfil, incluida moldura; cargo actualizado solo al recalcular. Sin optimización 1D. |
| HU-27 | Precios y cobros · E4 | **Como** encargado del negocio, **necesito** aplicar un umbral configurable a la merma de vidrio como cargo separado, **para** reflejar el desperdicio según el uso de hojas. | Área por pedido y residual de hoja de 71″ × 102″; cargo separado. Umbral independiente del aluminio, inicialmente 80 %; esfuerzo 3 propuesto. Sin optimización 2D. |

## Reglas transversales confirmadas

- Para California por mitad se usan las fórmulas, cantidades y tres ejemplos de [Medidas.md](../domain/Medidas.md): **17 piezas de aluminio y dos vidrios iguales**. Si el centro matemático cae en treintaidosavos, se **sube al siguiente dieciseisavo** antes de obtener sus cortes dependientes.
- El negocio asume sus errores de medición sin cambiar el precio acordado con el cliente. Puede recortar una ventana demasiado grande, rehacer una demasiado pequeña o reutilizar piezas cuya dimensión era correcta.
- Un pedido tiene una o más ventanas y un cliente puede tener varios pedidos. Otros tipos de ventana, puertas y productos quedan fuera del primer cálculo.
- La etiqueta corta de letras pertenece a un solo pedido activo. La secuencia sigue `A`…`Z`, `AA`, `AB`…; se libera únicamente cuando el pedido está **instalado y pagado por completo**. La identidad interna permanece única aunque una etiqueta visible vuelva a usarse. Falta decidir sobre piezas o papeles remanentes.
- La aceptación de una HU requiere comprobar su resultado. El progreso de subtareas informa trabajo terminado, pero no sustituye los criterios de aceptación. Las subtareas de HU lejanas se crean cuando se acerque su implementación.
- La implementación se hará por cortes verticales pequeños: datos, API e interfaz cuando la capacidad los necesite. La primera HU debe poder usarse para capturar y consultar medidas; no se construyen capas completas por adelantado. El usuario decide alcance y prioridad como Navigator y la IA ejecuta la entrega acordada como Driver.
- La optimización de cortes 1D de perfiles y 2D tipo guillotina de vidrio son propuestas **opcionales** para evaluar después. No forman parte de las HU del primer MVP ni se convierten en requisitos por aparecer aquí.
