# Flujo de trabajo de la vidriería y oportunidades para AVAO

> Documento de contexto, no backlog paralelo. **Trabajo actual** recoge lo descrito por el usuario; **idea para AVAO** recoge propuestas expresadas durante el refinamiento; **por decidir** señala reglas y alcance que siguen abiertos. El usuario, como experto del negocio y único desarrollador humano, decide qué entra en cada entrega. Las historias de producto están en [Backlog.md](../product/Backlog.md).

## Quiénes participan y qué se busca mejorar

El negocio familiar descrito tiene tres personas. El jefe atiende a clientes y también puede medir, cortar vidrio, apoyar el ensamble y manejar cobros. El trabajador principal se concentra en cortar vidrio y apoyar el ensamble, pero puede cubrir tareas del jefe. El usuario dedica alrededor del 90 % de su trabajo al ensamble y la instalación, y también puede trabajar en casi todas las áreas. La asignación cambia según disponibilidad y carga de trabajo; una persona puede cumplir varios papeles. Las áreas **Negocio** y **Taller** se han propuesto como una organización inicial de la aplicación. Los roles múltiples, permisos detallados o personalizados son una posibilidad posterior, no una condición inicial.

El primer intento del proyecto dedicó esfuerzo temprano a validaciones, supuestos tomados de investigación y diseño excesivo, mientras quedó incompleta la conexión entre captura de medidas y cálculo de cortes. La prioridad técnica y funcional expresada ahora es comprobar un flujo sencillo que funcione: comenzar por **dimensiones de fabricación indicadas por el vidriero → medidas de corte de perfiles y vidrios** para una ventana California por mitad, y después completar el recorrido del pedido hasta el registro del último pago. Las reglas se afinarán con pruebas y ejemplos reales. Esto no elimina la necesidad de evitar resultados de corte inválidos; indica que la robustez debe crecer sobre una función comprobada.

La aplicación está pensada para que **empleados del negocio introduzcan los datos y operen el pedido**. No se ha planteado una interfaz para que el cliente capture medidas, solicite el trabajo o pague por sí mismo.

### Varios pedidos en paralelo

Un **pedido** (nombre de trabajo propuesto para la aplicación) es una solicitud concreta del cliente. Un mismo cliente puede tener más de un pedido, por ejemplo para dos casas o por encargos hechos en momentos distintos. Cada pedido tiene **una o más ventanas**. A futuro podría incluir otros tipos de ventana, puertas u otros productos; el primer MVP solo desarrolla el caso California por mitad. Pueden existir varios pedidos pendientes a la vez. Para AVAO, un pedido llega a la cola cuando el empleado lo guarda.

Los empleados necesitan **consultar y cambiar entre pedidos**. La secuencia de atención no siempre coincide con terminar un pedido antes de iniciar el siguiente: si faltan materiales para uno, puede avanzarse otro que sí pueda fabricarse, por ejemplo porque usa aluminio de un color disponible. Esta capacidad evita detener el trabajo del taller por un solo pedido bloqueado. La lista conserva el orden de llegada a AVAO: abrir y atender B antes que A no cambia ese orden. La posición visible se calcula dentro de la cola y es distinta del ID interno y de la etiqueta de taller. Un pedido sale de la cola solo cuando está instalado **y** pagado por completo; entonces las posiciones restantes se recalculan. La decisión de atender otro pedido y la gestión de existencias no se automatizan por ahora.

**Identificador interno y código de taller.** Cada pedido y ventana tendrán un identificador lógico interno estable. Para el trabajo físico se asigna una etiqueta de letras inglesas a cada pedido activo, en la secuencia `A`…`Z`, `AA`, `AB`…, y se numeran sus ventanas dentro de él: `A1`, `A2`, … para el pedido A; `B1`, `B2`, … para el siguiente. **El trabajador escribe a mano ese código corto en el aluminio y el vidrio**, de modo que pueda reconocer las piezas sin copiar identificadores largos. La etiqueta identifica el pedido activo y el número la ventana; el código se usa para localizar sus piezas, **no como identidad histórica permanente**. **La etiqueta se libera únicamente cuando el pedido está instalado y pagado por completo**; entonces puede asignarse a otro pedido. Así no deben coexistir en el taller piezas de dos pedidos con la misma etiqueta. El identificador interno permite distinguir registros históricos aunque la etiqueta se reutilice. Falta definir el manejo de piezas o papeles remanentes al reutilizar una etiqueta y si se reutilizan números de ventanas eliminadas.

## Línea del tiempo de un pedido

### 0. Contacto inicial y visita acordada

**Trabajo actual.** Se hace el trato inicial con el cliente y se establece la ubicación donde solicita el trabajo. Allí se medirán los huecos de las ventanas.

**Idea para AVAO y mejora esperada.** Relacionar desde el inicio el trabajo, la ubicación y, cuando corresponda, los datos del cliente. Esto ayudaría a mantener juntos los datos que hoy se anotan en papel. La ubicación completa sigue por decidir. Un pedido entra en la cola de AVAO cuando el empleado lo guarda.

### 1. Medición de los huecos y definición de ventanas

**Trabajo actual.** En la ubicación se usa cuaderno y cinta para anotar **el ancho y alto a los que debe fabricarse cada ventana, en pulgadas**, tras medir el hueco irregular y aplicar su criterio con la cinta. AVAO recibe esas dimensiones finales, no las dimensiones brutas del hueco. Se dibuja cada ventana como un rectángulo dividido verticalmente por la mitad; se escribe el ancho bajo el dibujo y también arriba después de determinarlo, y el alto a un lado. Cada ventana recibe un número o una letra que luego identifica sus perfiles y vidrios. Las ventanas de un pedido suelen tener medidas distintas. Se ofrecen opciones de diseño, color de aluminio, tipo de vidrio y tipo de ventana; el caso inicial para AVAO es la **California por mitad**, con una hoja fija y una corrediza, por ser el tipo común descrito por el usuario.

**Idea para AVAO y mejora esperada.** Capturar varias ventanas dentro de un mismo pedido, cada una con sus medidas y un código visible como `A1`, para evitar transcribirlas después y relacionarlas con sus piezas. El dibujo sencillo podría servir como apoyo visual en una interfaz futura; no hace falta para comprobar el primer cálculo. La captura y el cálculo deben quedar conectados de forma que las medidas ingresadas produzcan los cortes de esa misma ventana.

**Por decidir.** Cómo editar o descartar ventanas y pedidos y qué variantes se registran desde el primer caso. Las fórmulas y tres ejemplos revisados están en [Medidas.md](Medidas.md). El taller no usa treintaidosavos para cortar: cuando el centro calculado cae en 1/32″, se sube al siguiente 1/16″ antes de calcular las piezas dependientes. El usuario confirmó que esto corrige el segundo ejemplo original.

### 2. Datos del cliente y presupuesto

**Trabajo actual.** Al terminar las medidas y acordar el tipo de ventana, se anotan nombre, teléfono, una dirección simplificada y las especificaciones del cliente. Se obtiene el precio de cada ventana y el total, y se presenta el presupuesto al cliente.

**Idea para AVAO y mejora esperada.** En el **flujo final previsto**, el empleado captura las medidas de todas las ventanas y después pulsa **Calcular precio**. La aplicación muestra el precio calculado de las ventanas más los servicios aplicables, como visita a domicilio o instalación, y el total que se comunica al cliente. Si acepta, el empleado introduce los datos del cliente y su anticipo; al pulsar **Confirmar** se guarda el pedido para empezar el trabajo. Esta secuencia describe la intención final, no el orden obligado de las primeras integraciones. Asociar cliente, ventanas, servicios, presupuesto y anticipo permitiría consultar qué se ofreció y cuál es el saldo.

El usuario plantea una función de precios más completa: catálogo de perfiles, vidrios y accesorios extra, con precios según **medida, tramo o unidad**. Cuando se use un precio por tramo, habría que registrar también su longitud estándar. La intención es calcular el precio de una ventana de cualquier medida y aplicar un **porcentaje de ganancia deseado por ventana**. Actualizar el precio de un solo perfil o de una hoja de vidrio debería permitir cotizar con los valores nuevos sin rehacer manualmente todos los cálculos.

**Por decidir antes de automatizar precios.** Qué conceptos son costo y cuáles precio de venta; si el porcentaje significa recargo sobre costo o margen sobre precio final; cómo se consideran tramos enteros, sobrantes, desperdicio, accesorios, mano de obra, instalación, descuentos comerciales e impuestos si aplican. También falta decidir si un presupuesto aceptado conserva los precios usados originalmente cuando cambie el catálogo. Aún no se ha descrito la fórmula sencilla de precio ni se han aprobado las reglas del catálogo avanzado. El flujo final deseado usa el botón de cálculo automático.

**Secuencia de precios indicada después.** El usuario quiere terminar parcialmente las medidas, el flujo de taller y las marcas de corte y ensamble como **primer MVP**. Después compartirá una fórmula de precio más sencilla que se usa actualmente para completar presupuesto, anticipo, instalación y liquidación. La función de catálogo y cálculo más flexible vendría más tarde. También existía una forma de cobrar por rangos de medidas estándar; el usuario la considera ineficiente porque las ventanas suelen variar mucho de medida. No se toma esa tabla como fórmula elegida para AVAO.

### 3. Aceptación y anticipo

**Trabajo actual.** Si el cliente acepta, se le solicita un anticipo. Las cifras principales son **total, anticipo(s) y saldo pendiente**.

**Idea para AVAO y mejora esperada.** Tras comunicar el total y recibir la aceptación, el empleado registra los datos del cliente y el anticipo y **confirma el pedido**. Registrar cada anticipo junto al total haría visible cuánto falta por cobrar y reduciría la búsqueda entre notas. La idea del borrador incluye mostrar productos, cantidades, precios individuales, total, anticipos y saldo al cobrar.

**Por decidir.** Si puede haber varios anticipos y pagos parciales, en qué momento se considera aceptado o cancelado un pedido, qué cambios se permiten después de recibir dinero y qué comprobantes se necesitan. No se asume una regla automática de descuentos o impuestos.

### 4. Regreso al taller y preparación de cortes

**Trabajo actual.** Con las dimensiones de fabricación indicadas por el vidriero se calculan a mano, ventana por ventana, las longitudes de cada perfil y de los vidrios. Se entrega una hoja para aluminio y otra para vidrio. En aluminio se sigue el orden `J.`, `M.`, `VF.`, `Alet.`, `HF.`, `HC.`, `GYR.` y `Esc.`. Para cada ventana se cortan dos jambas, un mulio, dos verticales fijos, dos aletas, dos horizontales fijos y dos horizontales corredizos. `GYR.` agrupa en la escritura **una guía y un riel**, dos perfiles físicos diferentes de igual longitud que suelen cortarse juntos. `Esc.` representa perfiles del mismo tipo físico: se cortan dos de ancho y dos de alto, y se escriben **ancho × alto**. Son **17 piezas de aluminio** en total. La hoja de vidrio usa el identificador de ventana seguido de **ancho × alto**; se cortan **dos vidrios iguales por ventana**.

**Idea para AVAO y mejora esperada.** Calcular automáticamente las longitudes para la California por mitad a partir de las medidas capturadas y generar listas legibles para quienes cortan aluminio y vidrio. Esta es la primera función que se quiere probar. La relación entre entrada, cálculo y salida debe comprobarse con ejemplos reales antes de ampliar el catálogo de diseños.

**Regla confirmada.** AVAO no aplica una holgura previa: el vidriero ya entrega la dimensión de fabricación. Los ajustes que puedan requerirse en la instalación por defectos de obra quedan fuera de HU-02. Las cantidades y la regla de subir los resultados de 1/32″ al siguiente 1/16″ ya están definidas para esta ventana base. El cálculo de `screen` para esta etapa usa únicamente las fórmulas base documentadas en `Medidas.md`.

**Por decidir.** Cómo se presentan las fracciones al cortador.

### 5. Corte de aluminio y vidrio

**Trabajo actual.** Quien corta consulta su hoja y va tachando a mano cada corte realizado. Aluminio y vidrio tienen hojas separadas; las medidas se vinculan al identificador visible de la ventana. El trabajador escribe ese código a mano sobre las piezas cortadas para mantenerlas identificadas durante el proceso.

**Idea para AVAO y mejora esperada.** Mostrar piezas y cantidades por cortar y permitir registrar avances parciales de cada medida o pieza, por separado para aluminio y vidrio. Esto daría una cuenta visible de lo pendiente y lo terminado. La lista digital debe conservar la distinción entre guía y riel aunque compartan longitud.

**Trabajo entre pedidos.** Cada lista y cada pieza debe mostrar a qué pedido y ventana pertenece. Si un pedido no puede avanzar por falta de material, el empleado puede abrir otro pedido pendiente y continuar con sus cortes. No se presupone que todos los cortes de un pedido deban terminar antes de empezar otro.

**Por decidir.** Cómo corregir una marca errónea, registrar una pieza repetida o descartada y tratar cortes iguales de ventanas distintas. Las cantidades de la ventana base están definidas; falta validar el formato final de la lista y su uso durante el corte.

### 6. Ensamble y ventana terminada

**Trabajo actual.** Las piezas cortadas pasan al ensamblador, que arma cada ventana hasta tenerla fabricada. Cuando todas las ventanas del pedido están listas, el pedido puede avanzar a instalación.

**Idea para AVAO y mejora esperada.** Marcar cada ventana ensamblada y, después, el pedido completo listo para instalar. Esta distinción permitiría saber si falta una ventana sin confundir su avance con el del pedido entero.

**Por decidir.** Condiciones exactas para marcar una ventana o pedido terminado, y qué hacer si una pieza debe rehacerse después de marcarla.

### 6a. Corrección de un error de medición o fabricación

**Trabajo actual.** Las medidas no deberían cambiar una vez que se empezó el trabajo, pero una persona puede equivocarse al medir. Cuando el error es del propio negocio, este asume la corrección y **el precio acordado con el cliente no cambia**. Una ventana demasiado grande puede recortarse. Una ventana demasiado pequeña puede requerir fabricar otra. Si solo una dimensión fue incorrecta, es habitual sustituir o volver a cortar el material de esa dimensión y reutilizar las piezas cuya medida sí era correcta en el nuevo ensamble.

**Idea para AVAO y mejora esperada.** Permitir registrar la medida correcta y qué piezas se rehacen o se reutilizan evitaría que la lista de cortes anterior se confunda con la nueva. Es una necesidad de corrección del trabajo, distinta de cambiar el diseño solicitado por el cliente. Como recomendación para el refinamiento, convendría conservar la medida original y la corrección para poder explicar el retrabajo; el nivel de detalle de ese registro no está decidido.

**Por decidir.** En qué etapa se permite corregir un pedido, cómo se anulan marcas de corte o ensamble ya registradas, y si una petición de cambio del cliente —distinta de un error del negocio— requiere un nuevo presupuesto. No se debe recalcular automáticamente el precio cobrado por un error de medición asumido por el negocio.

### 7. Aviso al cliente e instalación

**Trabajo actual.** Al terminar la fabricación se avisa al cliente y se acuerda el día y, cuando es posible, la hora de instalación. Se instalan las ventanas en los huecos medidos.

**Idea para AVAO y mejora esperada.** Registrar que el pedido está listo, el acuerdo de instalación y su conclusión ayudaría a consultar qué trabajos faltan fuera del taller. El tablero de trabajos propuesto podría mostrar estas etapas.

**Por decidir.** Si se permiten instalaciones parciales, cambios de cita, incidencias o una aceptación explícita del cliente al terminar. No se ha establecido que todas esas funciones sean necesarias para el MVP.

### 8. Liquidación y cierre

**Trabajo actual.** Tras instalar, normalmente el cliente paga el saldo restante; al registrar el último pago concluye el trabajo descrito.

**Idea para AVAO y mejora esperada.** Mostrar total, anticipos, pagos posteriores y saldo, y registrar la liquidación final. Así sería más fácil saber si un trabajo instalado todavía tiene dinero pendiente.

**Por decidir.** Pago parcial al instalar, saldo vencido, ajustes al total, devoluciones y cómo registrar de forma fiable el cierre. El pedido sale de la cola solo cuando está **instalado y pagado por completo**; instalación y liquidación son condiciones distintas.

## Ideas que atraviesan varias etapas

- **Tablero de trabajos.** El borrador propone ver pendientes, en fabricación, ensamblados, instalados y liquidados, quizá con barras de avance. Puede aportar visibilidad al jefe, pero el valor real depende de definir eventos y estados fiables en las etapas anteriores. No conviene imponer barras de progreso sin una regla clara para calcularlas.
- **Materiales requeridos.** El borrador propone anticipar perfiles y hojas de vidrio para los pedidos actuales. Sumar demanda estimada sería distinto de calcular una compra faltante: para esta última harían falta existencias, unidades de compra, longitudes estándar, sobrantes y desperdicio. El usuario aún no ha definido esa operación ni su prioridad.
- **Más diseños y reglas configurables.** Después de validar California por mitad, el borrador imagina otros productos y una interfaz para elegir perfiles, cantidades y operaciones de cálculo. Es una dirección futura; construir un editor general antes de comprobar la regla base repetiría el riesgo de sobreingeniería del primer intento.
- **Uso sin conexión y sincronización.** No es necesario para el MVP. Si se considera en otra etapa, habrá que aclarar qué tareas funcionarían sin red, cuántos dispositivos compartirían un pedido y cómo se resolverían cambios simultáneos. No convertirlo en trabajo actual.
- **Trabajo individual con Kanban.** El usuario desarrolla, planifica y valida con apoyo de IA. Un tablero sencillo puede ayudar a ver lo pendiente, en curso, bloqueado y terminado, y a limitar el trabajo simultáneo. Las ideas de este documento no son historias definitivas ni fijan por sí mismas la prioridad del MVP.

## Secuencia de aprendizaje propuesta, sujeta a decisión del usuario

1. **Primer MVP de taller:** comprobar que la dimensión de fabricación indicada tras medir cada hueco llega al cálculo y produce longitudes y cantidades correctas y legibles para aluminio y vidrio de la California por mitad; permitir marcar cortes y ventanas ensambladas.
2. **Cierre comercial básico:** conocer y aplicar la fórmula sencilla actual de precio, añadir los servicios, registrar datos del cliente, anticipo, instalación y último pago. Así se completa el recorrido del pedido sin esperar al catálogo más amplio.
3. **Control de precios posterior:** estudiar el catálogo de perfiles, vidrios y accesorios y las reglas de cobro por medida, tramo o unidad y porcentaje de ganancia, para facilitar actualizaciones de insumos.
4. Evaluar tablero completo, previsión de materiales, permisos, sincronización y otros diseños según problemas observados al usar el flujo anterior.

Esta secuencia recoge el orden de intención expresado por el usuario, sin fijar calendario ni arquitectura. [Backlog.md](../product/Backlog.md) reúne 23 historias y las seis prioridades altas que se prepararán a continuación.
