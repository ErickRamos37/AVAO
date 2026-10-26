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
| E1. Preparar ventanas California para corte | Registrar medidas de huecos y obtener cortes identificados por ventana. | HU-01, HU-02, HU-06, HU-22 |
| E2. Seguir la fabricación de pedidos | Saber qué aluminio, vidrio y ventanas están terminados con varios pedidos pendientes. | HU-03, HU-04, HU-05, HU-07, HU-08, HU-09, HU-10 |
| E3. Completar un pedido desde presupuesto hasta liquidación | Comunicar total, registrar aceptación y pagos, instalar y cerrar. | HU-11 a HU-17 |
| E4. Actualizar el cálculo comercial desde insumos | Cambiar precios individuales y aplicar ganancia definida. | HU-18, HU-19 |

HU-20 y HU-21 quedan independientes hasta que su alcance justifique agruparlas. El progreso de una épica no reemplaza la aceptación de cada HU.

## Primer MVP: medidas y taller

El empleado captura ancho y alto del hueco en pulgadas. Se calculan cortes para la ventana California por mitad, con una hoja fija y una corrediza, y se sigue corte y ensamble. Cada pedido y ventana conserva identidad interna estable. Primero se guardan y consultan las medidas (HU-01); después se asigna el código corto de taller `A1`, `A2`, `B1` (HU-22), que el trabajador escribirá a mano en aluminio y vidrio. La letra se liberará solo cuando el pedido esté **instalado y pagado por completo**; automatizar esa liberación depende del registro posterior de instalación y pagos.

### Seis HU altas para preparar ahora

#### HU-01 — Registrar ventanas medidas en un pedido

- **Área:** Pedidos y medidas · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**. Alcance acotado a guardar y consultar medidas sin datos del cliente ni generación de códigos; revisar al preparar la implementación.
- **Historia:** **Como** empleado que mide, **necesito** registrar y volver a consultar el ancho y alto del hueco de una o más ventanas California dentro de un pedido, **para** conservar las medidas de cada trabajo.
- **Criterios de aceptación:**
  1. Desde un formulario sencillo se puede crear un pedido con una o más ventanas California, cada una con ancho y alto del hueco en pulgadas. La entrada admite entero solo o una suma de fracciones como `26 1/2` y `24 1/4 1/16`.
  2. Durante la captura se pueden añadir filas de ventana y descartar una fila **antes de guardar**. Una fila adicional completamente vacía no se guarda; una fila parcialmente llena se señala para que el empleado la complete o descarte. Se requiere al menos una ventana con ambas medidas.
  3. Tras guardar, se pueden listar los pedidos y abrir uno para consultar sus ventanas y medidas. Una medida ingresada como `24 1/4 1/16` puede mostrarse como su fracción simplificada equivalente `24 5/16`; no es necesario conservar la escritura original. Las ventanas se distinguen dentro del pedido y conservan su identidad.
- **Subtareas técnicas propuestas, aún sin crear en el tablero:** cada paso debe producir un resultado comprobable, no una capa aislada.
  1. **Guardar y reabrir un pedido con una ventana:** capturar, guardar y volver a abrir desde la web un pedido con **una** ventana California y sus medidas, incorporando la persistencia, el backend y la interfaz necesarios.
  2. **Capturar varias ventanas y descartar filas antes de guardar:** ampliar ese recorrido para varias ventanas y permitir añadir o descartar filas antes de guardar, sin enviar filas vacías.
  3. **Listar pedidos y consultar sus ventanas:** listar los pedidos y abrir cualquiera para comprobar desde la web sus ventanas y medidas, si esa consulta no quedó cubierta en el primer paso.
- **Fuera de alcance y por decidir:** los datos de cliente y las especificaciones o notas del pedido permanecen en HU-13; el código corto es HU-22; el cálculo es HU-02; corregir o descartar una ventana **ya guardada** es HU-06. Se posponen preferencias avanzadas de presentación de fracciones. Falta decidir el comportamiento de la numeración si más adelante se corrige o descarta una ventana persistida. PostgreSQL se eligió como dialecto para expresar el diseño SQL, sin fijar todavía el stack de ejecución; no se define aquí un catálogo de productos ni reglas adicionales para las especificaciones.

#### HU-22 — Identificar pedidos y ventanas con códigos cortos de taller

- **Área:** Pedidos y medidas · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**. Incluye asignación y consulta estable de letras y números sin repetir letras entre pedidos activos; la liberación automática requiere HU-16 y HU-17.
- **Historia:** **Como** trabajador del taller, **necesito** ver un código corto para cada ventana de los pedidos activos, **para** escribirlo a mano en sus piezas y distinguirlas durante la fabricación.
- **Criterios de aceptación:**
  1. Los pedidos activos reciben letras inglesas distintas y sus ventanas muestran el número que les corresponde dentro del pedido, como `A1`, `A2` y `B1`.
  2. El código de una ventana permanece igual al reabrir su pedido; pedido y ventana conservan identidades internas independientes del código visible.
  3. Mientras no exista el registro de instalación y liquidación, una letra asignada no se reutiliza. Al integrar HU-16 y HU-17, la liberación seguirá la regla confirmada: pedido instalado **y** pagado por completo.
- **Por decidir al implementarla:** más de 26 pedidos activos y piezas o papeles remanentes. La asignación exacta de letras y el comportamiento de números tras correcciones no se inventan aquí.

#### HU-02 — Obtener el plan de corte de una ventana California

- **Área:** Cortes y taller · **Épica:** E1 · **Prioridad:** Alta · **Esfuerzo inicial:** **8**.
- **Historia:** **Como** trabajador del taller, **necesito** obtener la lista de cortes de aluminio y vidrio a partir de las medidas registradas, **para** preparar las piezas sin repetir los cálculos a mano.
- **Criterios de aceptación:**
  1. Para cada ventana, se muestran perfil, longitud y cantidad de **17 piezas de aluminio** y **dos vidrios iguales** según [Medidas.md](../domain/Medidas.md).
  2. Guía y riel son perfiles físicos distintos aunque compartan longitud. El screen muestra dos piezas de ancho y dos de alto.
  3. Los tres ejemplos de [Medidas.md](../domain/Medidas.md) coinciden; el centro calculado en treintaidosavos se sube al siguiente dieciseisavo antes de obtener cortes dependientes.
- **Por refinar al trabajarla:** presentación de fracciones para quien corta. Las marcas de cortes realizados son HU-03 y HU-04.

#### HU-03 — Registrar cortes de aluminio

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **5**.
- **Historia:** **Como** quien corta aluminio, **necesito** marcar las piezas realizadas de cada perfil y medida, **para** ver cuántas faltan sin tachar una hoja.
- **Criterios de aceptación:**
  1. Cada corte muestra cantidad requerida, realizada y pendiente, asociado al pedido y al código corto de su ventana generado en HU-22.
  2. Puede registrarse avance parcial para piezas repetidas; guía y riel se marcan por separado.
  3. El avance permanece al cambiar de ventana o reabrir el pedido y no se mezcla con otra ventana.
- **Por decidir al implementarla:** reversión de marca errónea, descartes y retrabajo; HU-07 trata correcciones de medida.

#### HU-04 — Registrar cortes de vidrio

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **3**.
- **Historia:** **Como** quien corta vidrio, **necesito** marcar los dos vidrios iguales de cada ventana conforme se cortan, **para** ver cuántos faltan sin contarlos en papel.
- **Criterios de aceptación:**
  1. Se muestran el pedido y el código corto de su ventana generado en HU-22, medidas `ancho × alto`, cantidad requerida `2` y realizada.
  2. Puede registrarse uno de los dos vidrios sin declarar completa la pareja.
  3. El avance permanece al cambiar de pedido o reabrirlo y no se confunde con otra ventana de igual medida.
- **Por decidir al implementarla:** reversión de marca errónea o vidrio descartado.

#### HU-05 — Marcar ventanas ensambladas

- **Área:** Cortes y taller · **Épica:** E2 · **Prioridad:** Alta · **Esfuerzo inicial:** **3**.
- **Historia:** **Como** ensamblador, **necesito** indicar qué ventanas están ensambladas y cuáles faltan, **para** conocer el avance real del pedido.
- **Criterios de aceptación:**
  1. Cada ventana puede señalarse como ensamblada y distinguirse de las pendientes.
  2. El estado permanece al reabrir el pedido y no cambia el de otra ventana o pedido.
  3. Se ven las ventanas pendientes; marcar una no declara instalado ni pagado el pedido.
- **Por decidir al implementarla:** condiciones previas y reversión por retrabajo. Declarar listo todo el pedido es HU-08.

### Otras HU del primer MVP, por refinar cuando se acerquen

| ID | Área · Épica | Prioridad | Esfuerzo | Historia y límite conocido |
| --- | --- | --- | --- | --- |
| HU-06 | Pedidos y medidas · E1 | Media | Pendiente | **Como** empleado, **necesito** corregir o descartar una ventana ya guardada, **para** evitar que una medida errónea llegue al cálculo. Quitar filas antes del primer guardado forma parte de HU-01; falta decidir qué ocurre tras confirmar un pedido y cómo afecta la numeración. |
| HU-07 | Cortes y taller · E2 | Media | Pendiente | **Como** trabajador del taller, **necesito** registrar una corrección de medida y qué piezas se recortan, rehacen o reutilizan, **para** fabricar la ventana correcta sin confundirla con cortes anteriores. Un error del negocio no cambia el precio pactado. |
| HU-08 | Cortes y taller · E2 | Media | Pendiente | **Como** trabajador del taller, **necesito** señalar que todas las ventanas del pedido están ensambladas, **para** distinguir un pedido listo para coordinar instalación de una sola ventana terminada. Al refinarla, comprobar si basta derivar este dato del estado de cada ventana en HU-05, sin crear un segundo estado manual divergente. |
| HU-09 | Cortes y taller · E2 | Media | Pendiente | **Como** empleado, **necesito** consultar los pedidos del taller y sus pendientes de corte y ensamble, **para** retomar el trabajo que corresponde. La forma de la pantalla sigue abierta. |
| HU-10 | Pedidos y medidas · E2 | Media | Pendiente | **Como** empleado, **necesito** cambiar entre pedidos pendientes sin perder su avance, **para** continuar con otro cuando falta material para el actual. Un cliente puede tener varios pedidos y cada pedido varias ventanas. |

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
| HU-17 | Precios y cobros · E3 | **Como** empleado, **necesito** registrar pagos posteriores y la liquidación final, **para** conocer el saldo y cerrar el pedido cuando esté instalado y pagado por completo. | Pagos parciales, ajustes y comprobantes. Su estado de cierre habilita la liberación de la letra definida en HU-22. |

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
- La letra corta pertenece a un solo pedido activo. Se libera únicamente cuando está **instalado y pagado por completo**. La identidad interna permanece única aunque una letra visible vuelva a usarse. Falta decidir sobre piezas o papeles remanentes y más de 26 pedidos activos.
- La aceptación de una HU requiere comprobar su resultado. El progreso de subtareas informa trabajo terminado, pero no sustituye los criterios de aceptación. Las subtareas de HU lejanas se crean cuando se acerque su implementación.
- La implementación se hará por cortes verticales pequeños: datos, API e interfaz cuando la capacidad los necesite. La primera HU debe poder usarse para capturar y consultar medidas; no se construyen capas completas por adelantado. El usuario decide alcance y prioridad como Navigator y la IA ejecuta la entrega acordada como Driver.
- La optimización de cortes 1D de perfiles y 2D tipo guillotina de vidrio son propuestas **opcionales** para evaluar después. No forman parte de las HU del primer MVP ni se convierten en requisitos por aparecer aquí.
