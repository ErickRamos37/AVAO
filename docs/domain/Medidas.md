# Medidas de ventanas California por mitad

> Estado: recopilación de la práctica descrita por el usuario y de tres ejemplos. Las fórmulas de `screen` corresponden al cálculo base. Ya se confirmaron las cantidades de piezas y que un resultado de 1/32″ se sube al siguiente 1/16″. El usuario confirmó la corrección del segundo ejemplo conforme a esa regla. El vidriero ya incorpora su criterio de ajuste al indicar las dimensiones de fabricación; AVAO no resta una holgura adicional.

## Alcance y origen

La ventana base es una California por mitad: una hoja fija y una hoja corrediza. `anchoVentana` y `altoVentana` son las medidas **de fabricación de la ventana**, en pulgadas. No son las dimensiones brutas del hueco; representan el ancho y alto a los que debe fabricarse la ventana. El vidriero los define tras medir el hueco irregular con su cinta y su criterio; AVAO recibe esas dimensiones finales, no la dimensión bruta del hueco, y no descuenta otra holgura.

El primer resultado a comprobar es el paso de esas dos medidas a las medidas de corte de perfiles y vidrios. El flujo más amplio del pedido va desde la visita y la toma de medidas hasta el registro del último pago. En el negocio una misma persona puede desempeñar varias tareas; **Negocio** y **Taller** son las dos áreas iniciales propuestas para la aplicación. Los permisos por rol quedan para una etapa posterior.

### Registro manual de cada ventana

1. Se identifica cada ventana con un número o una letra para relacionar sus perfiles y vidrios con ella. Las medidas de ventanas de un pedido normalmente varían entre sí.
2. Se hace un dibujo de baja fidelidad: un rectángulo dividido por una línea vertical central que va del borde superior al inferior y forma dos rectángulos menores.
3. Se anota el **ancho indicado para fabricar la ventana** debajo del dibujo y, después de determinarlo, también sobre su borde superior. El **alto indicado para fabricarla** se anota a uno de los lados; izquierda o derecha es indiferente.
4. El dibujo y la identificación pueden orientar una interfaz posterior. Primero se busca comprobar el cálculo y el flujo.

**Identificación para varios pedidos:** cada pedido y ventana tendrán un **identificador lógico interno** en el sistema. Aparte, una etiqueta de letras inglesas distingue cada pedido activo (secuencia `A`…`Z`, `AA`, `AB`…) y un número correlativo distingue sus ventanas: `A1`, `A2`, …; `B1`, `B2`, …. El código corto se **escribe a mano sobre las piezas de aluminio y vidrio** para reconocer a qué ventana pertenecen sin copiar identificadores largos. La etiqueta se libera **cuando el pedido ya está instalado y pagado por completo**; entonces puede volver a usarse. Hasta ese momento no debe asignarse a otro pedido, para evitar piezas con la misma etiqueta dentro del taller. El identificador interno conserva la identidad de los registros históricos aunque el código visible se reutilice. Véase [FlujoDeTrabajoVidrieria.md](FlujoDeTrabajoVidrieria.md).

## Unidad y escritura de fracciones

La unidad de trabajo es la **pulgada**. Las medidas tomadas y comunicadas en el taller se escriben como números mixtos fraccionarios, por ejemplo `10 1/2`, con resolución práctica de **1/16″** en la cinta. **No se usan treintaidosavos en el trabajo de corte**: si un cálculo produce un valor a mitad de camino entre dos marcas de 1/16″, se **sube al siguiente 1/16″**. El centro ajustado se usa después para los perfiles y vidrios que dependen de él.

Para facilitar la lectura se puede escribir una fracción como suma de una referencia visible y `1/16`: `9/16 = 1/2 + 1/16`, `13/16 = 3/4 + 1/16`, `15/16 = 7/8 + 1/16`. En las anotaciones recibidas aparecen formas como `35 7/8 1/16`, cuyo valor es `35 15/16`, o `23 3/4 1/16`, cuyo valor es `23 13/16`. Aunque la descripción inicial decía que se suele partir de medios o cuartos y evitar octavos, **los ejemplos recibidos también usan octavos**. Para HU-01, el backend convierte la entrada a un número entero de dieciseisavos y solo guarda ese valor. Al consultar, muestra la fracción equivalente simplificada: `24 1/4 1/16` puede mostrarse como `24 5/16`. Más adelante se podrán estudiar preferencias de escritura del taller, sin exigirlas a la primera entrega. En los ejemplos se combinan como máximo dos fracciones.

Dividir entre dos un ancho medido en dieciseisavos puede producir matemáticamente **treintaidosavos**. Para el centro, dividir el entero `ancho_16` entre dos y subir al entero siguiente si aparece una mitad aplica la regla de subir al próximo 1/16″: `753 / 2 = 376.5`, que se ajusta a `377` dieciseisavos (`23 9/16`). Ese ajuste se aplica en el punto indicado por la fórmula, antes de los cortes dependientes; no se redondea la medida capturada. Se aplaza un algoritmo general de presentación según preferencias de escritura, aunque la lista de corte deberá mostrar las fracciones simplificadas de forma legible.

## Fórmulas registradas hasta ahora

Estas son las fórmulas del cálculo base para la ventana California por mitad. Las referencias de abajo presentan `anchoScreen` y `altoScreen` con las etiquetas ya corregidas.

| Resultado | Fórmula a partir de las dimensiones de fabricación |
| --- | --- |
| `centro` | `anchoVentana / 2`; si resulta en 1/32″, subir al siguiente 1/16″ antes de calcular los cortes dependientes |
| `anchoVidrio` | `centro - 2` |
| `altoVidrio` | `altoVentana - 2` |
| `guiaRiel` | `anchoVentana - 1 7/8` |
| `jamba` | `altoVentana` |
| `mulio` | `altoVentana - 1` |
| `aleta` | `altoVentana - 2 1/2` |
| `verticalFijo` | `altoVentana - 1 1/4` |
| `horizontalFijo` | `centro - 2 1/2` |
| `horizontalCorredizo` | `centro - 7/8` |
| `altoScreen` | `verticalFijo` |
| `anchoScreen` | `centro - 1 5/8` |

Los resultados de la tabla son **longitudes**. Para cada ventana se cortan **dos vidrios del mismo ancho y alto**, ambos calculados con `anchoVidrio × altoVidrio`. Las cantidades de aluminio se indican a continuación; guía y riel tienen igual longitud, pero son perfiles físicos distintos.

### Abreviaturas y orden en la hoja de aluminio

| Orden | Nombre | Abreviatura | Cantidad por ventana y nota |
| --- | --- | --- | --- |
| 1 | Jamba | `J.` | 2. |
| 2 | Mulio | `M.` | 1. |
| 3 | Vertical fijo | `VF.` | 2. |
| 4 | Aleta | `Alet.` | 2. |
| 5 | Horizontal fijo | `HF.` | 2. |
| 6 | Horizontal corredizo | `HC.` | 2. |
| 7 | Guía y riel | `GYR.` | **Una guía y un riel**. Son dos perfiles físicamente distintos con la misma longitud calculada; suelen cortarse juntos. No fusionarlos como una sola pieza. |
| 8 | Screen | `Esc.` | **Dos piezas de `anchoScreen` y dos de `altoScreen`**, del mismo tipo físico de perfil. En la hoja se anotan como `ancho × alto`, con el ancho primero. |

En total son **17 piezas de aluminio y dos vidrios por ventana** según estas cantidades. Este total cuenta por separado la guía y el riel, y las cuatro piezas de `screen`.

Los vidrios se anotan **en otra hoja** y se relacionan con el identificador de la ventana. El formato comunicado es `N. Ancho × Alto`. Aplicando la corrección confirmada para la ventana 2, las tres líneas de referencia quedan así:

```text
1. 22 × 34
2. 21 9/16 × 33 7/8 1/16
3. 23 3/8 × 36 1/2
```

Esas líneas identifican medidas por ventana. **De cada línea se cortan dos vidrios iguales.**

## Tres referencias para comprobar el cálculo

Las entradas son **ancho × alto indicados para fabricar la ventana**. La ventana 2 se recalculó con la regla de subir `centro` al siguiente 1/16″; el usuario confirmó esta corrección de la primera hoja manual. Las filas de `screen` muestran los nombres correctos y el cálculo base.

| Resultado anotado | Ventana 1: `48 × 36` | Ventana 2: `47 1/16 × 35 7/8 1/16` | Ventana 3: `50 3/4 × 38 1/2` |
| --- | --- | --- | --- |
| `centro` | `24` | `23 9/16` | `25 3/8` |
| `anchoVidrio` | `22` | `21 9/16` | `23 3/8` |
| `altoVidrio` | `34` | `33 7/8 1/16` | `36 1/2` |
| `guiaRiel` | `46 1/8` | `45 3/16` | `48 7/8` |
| `jamba` | `36` | `35 7/8 1/16` | `38 1/2` |
| `mulio` | `35` | `34 7/8 1/16` | `37 1/2` |
| `aleta` | `33 1/2` | `33 3/8 1/16` | `36` |
| `verticalFijo` | `34 3/4` | `34 5/8 1/16` | `37 1/4` |
| `horizontalFijo` | `21 1/2` | `21 1/16` | `22 7/8` |
| `horizontalCorredizo` | `23 1/8` | `22 11/16` | `24 1/2` |
| `anchoScreen` | `22 3/8` | `21 15/16` | `23 3/4` |
| `altoScreen` | `34 3/4` | `34 5/8 1/16` | `37 1/4` |

### Verificación aritmética y reglas aún abiertas

1. **Ajuste práctico de la ventana 2:** `47 1/16 ÷ 2 = 23 17/32` como resultado matemático. Al subir al siguiente 1/16″, `centro = 23 9/16`. De ese centro se obtienen `anchoVidrio = 21 9/16`, `horizontalFijo = 21 1/16`, `horizontalCorredizo = 22 11/16` y `anchoScreen = 21 15/16`. La primera hoja manual había usado `23 1/2` como centro; esos resultados quedaron sustituidos tras la aclaración y confirmación del usuario.
2. **Screen base:** `anchoScreen = centro - 1 5/8` y `altoScreen = altoVentana - 1 1/4 = verticalFijo`. El ancho se escribe antes del alto en `Esc.`. Los tres ejemplos de la tabla usan estas fórmulas.
3. **Ajuste al hueco:** el vidriero entrega las dimensiones de fabricación ya decididas tras medir el hueco; AVAO no aplica una holgura previa a estas fórmulas. Los ajustes que pueda requerir la instalación por defectos de obra quedan fuera de este cálculo.

Las cifras de las tres referencias concuerdan con las fórmulas base al aplicar el centro ajustado indicado para la ventana 2. Son referencias para validar la implementación; los posibles ajustes durante la instalación por defectos de obra no forman parte de estas fórmulas.

## Notas previas de desarrollo

El borrador anterior proponía pasar de milímetros a pulgadas en el sistema, tomar la ventana California como base antes de otros diseños y documentar las reglas en el repositorio. También planteaba dejar la presentación fraccionaria para una etapa posterior del frontend. Esas son **propuestas previas**, no verificaciones del estado del código. Antes de usar la salida para cortar, se necesita comprobar que las medidas ajustadas se muestran de forma legible.
