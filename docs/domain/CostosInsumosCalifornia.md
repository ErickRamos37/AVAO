# Insumos y costos de California por mitad

Este documento reúne los materiales conocidos para una ventana California por mitad, sus costos de compra actuales, la presentación en que se compran y la base usada para valorar lo consumido. Completa las fórmulas de corte documentadas en [Medidas.md](Medidas.md). Los datos pendientes y las propuestas de cálculo están separados para no tratarlos como reglas confirmadas.

## Cómo leer la tabla

- Los importes son **costos de compra del negocio**.
- **Base para valorar el consumo** indica si el material se calcula por medida o por unidad.
- **Presentación de compra** describe cómo se adquiere el material.
- La tabla corresponde a **una ventana California por mitad**. Las cantidades numéricas son por ventana.
- El guion `—` significa que el material se valora por medida, no que su consumo sea cero ni desconocido.
- Los importes que faltan están pendientes; no equivalen a cero.

## Costos de compra actuales

| Insumo | Base para valorar el consumo | Costo informado | Presentación de compra | Consumo por ventana |
| --- | --- | ---: | --- | --- |
| Jamba de aluminio | Medida | $428 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Aleta de aluminio | Medida | $364 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Guía de aluminio | Medida | $426 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Riel de aluminio | Medida | $512 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Horizontal fijo | Medida | $168 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Horizontal corredizo | Medida | $160 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Mulio | Medida | $332 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Vertical fijo | Medida | $149 por tramo | Tramo de 21 pies | Longitud según el plan de corte |
| Moldura de screen | Medida | $115 por tramo | Tramo de 12 pies | Longitudes de los perfiles horizontales y verticales del screen en el plan de corte |
| Vidrio doble fuerza de 1/8″ | Medida | $780 por hoja | Hoja de 71″ de alto × 102″ de ancho | Dos vidrios iguales según el plan de corte |
| Vinil doble fuerza | Medida | $1.20 por pie lineal | Rollo de largo variable | Perímetro de cada vidrio por la cantidad de vidrios |
| Finger | Medida | $0.44 por pie | Rollo; longitud variable | `2 × horizontal fijo + 2 × vertical fijo` |
| Felpa | Medida | $0.44 por pie | Rollo; longitud variable | `2 × aleta + 2 × horizontal corredizo` |
| Rodajas | Unidad | $5.50 por unidad | Empaque; cantidad por confirmar | 2 unidades |
| Guías plásticas | Unidad | $1.15 por unidad | Empaque; cantidad por confirmar | 4 unidades |
| Jaladeras | Unidad | $14 por unidad | Empaque; cantidad por confirmar | 1 unidad |
| Cola de rata | Medida | $1.88 por pie | Rollo; longitud variable | Perímetro del screen |
| Tela mosquitera | Área | $3.00 por pie cuadrado; $850 por rollo queda como referencia | Rollo de ancho y largo variables; registrar rollos queda para una etapa futura | `anchoScreen × altoScreen` según las medidas del aluminio |
| Escuadras | Unidad | $3 por unidad | Empaque; cantidad por confirmar | 4 unidades |
| Chilillos | Unidad | $0.20 por unidad | Empaque; cantidad por confirmar | 24 unidades por ventana; $4.80 al costo común actual |
| Taquetes | Unidad | $0.45 por unidad | Empaque; cantidad por confirmar | 4 unidades |
| Pasta | Medida | $47 por tubo | Tubo con rendimiento de 26 pies lineales (312 pulgadas) | Perímetro de fabricación por ambas caras |
| Silicón | Unidad | $82 por unidad | Presentación de compra por confirmar | Fuera del costeo actual |
| Vistas | Medida | $65 por tramo | Tramo de 12 pies | Fuera del costeo actual |

> [!NOTE]
> El silicón y las vistas quedan fuera; se conservan sus datos aquí para una etapa futura.

## Guías plásticas

Las cuatro guías plásticas por ventana se colocan en los horizontales corredizos. Guían la pieza y evitan el roce directo de aluminio con aluminio; el contacto queda entre aluminio y plástico. Son distintas del perfil de aluminio llamado «Guía».

## Presentaciones de compra en paquete (fuera del costeo actual)

Los distribuidores pueden ofrecer algunas piezas en conjunto. Se conserva esta información como referencia; el costo por set y la compra conjunta de guía/riel no se usan ni se distribuyen entre insumos en el alcance actual:

- **Guía y riel:** se ofrecen juntos con un precio menor que la compra individual. La tabla conserva los costos individuales informados; falta revisar facturas para saber si el costo de cada perfil dentro de esa presentación viene desglosado.
- **Set de ventana:** incluye jamba, aleta, guía, riel, horizontal corredizo, horizontal fijo, mulio y vertical fijo. No incluye molduras de screen ni vistas. Falta revisar facturas para confirmar el precio del set y si se desglosa el costo de cada perfil.


## Uso de vistas

Las vistas son perfiles de aluminio que se pegan al vidrio, normalmente para formar rectángulos decorativos. Se cortan y se adhieren con silicón. Esta es la aplicación más común del silicón en la ventana California por mitad; el silicón tiene otros usos que no están descritos aquí.

## Fórmulas de consumo para el costo de materiales

El usuario confirmó estas fórmulas para calcular el costo de materiales de una ventana California por mitad:

- **Vinil doble fuerza:** perímetro de cada vidrio multiplicado por la cantidad de vidrios de la ventana.
- **Finger:** `2 × horizontal fijo + 2 × vertical fijo`; se instala en los perfiles del fijo.
- **Felpa:** `2 × aleta + 2 × horizontal corredizo`; se instala en los perfiles del corredizo.
- **Cola de rata:** perímetro del screen para sujetar la tela a la moldura.

El vinil doble fuerza, el Finger, la felpa y la cola de rata se valoran por pie lineal según la tabla, aunque se compren en rollos de largo variable.

## Tela mosquitera del screen

En el alcance actual, la tela se valorará por pie cuadrado usando las medidas que entrega el cálculo de los perfiles horizontales y verticales del screen: `anchoScreen × altoScreen`. Esas mismas piezas del plan proporcionan la longitud para costear la moldura. Estas dimensiones están en pulgadas; para obtener pies cuadrados, se multiplica el área en pulgadas cuadradas y se divide entre 144. El costo de la tela será esa superficie en pies cuadrados por la tarifa de compra por pie cuadrado.

> [!NOTE]
> Los $850 por rollo se conservan como referencia, pero no se usan para derivar la tarifa por pie cuadrado porque aún no se conocen las dimensiones de cada rollo. La entrega actual no registra tipos, anchos ni largos de rollos, ni optimiza su acomodo o desperdicio. Esas funciones quedan para una etapa futura.

## Catálogo de chilillos

Las tres secciones agrupan los chilillos por tipo de uso. Las cantidades por ventana ya están especificadas; se usa temporalmente el mismo costo de compra por unidad para todas las variantes.

### Ventaneros

| Cabeza | Largo | Grosor informado | Uso | Cantidad requerida por ventana California | Precio por unidad |
| --- | --- | --- | --- | ---: | ---: |
| Gota | 1 pulgada | 3/8 de pulgada | Corredizos | 4 | $0.20 |
| Cónica | 1 pulgada | 3/8 de pulgada | Fijos | 4 | $0.20 |
| Gota | Más corto que 1 pulgada; medida exacta por investigar | 3/8 de pulgada | Marcos de ventana | 8 | $0.20 |

### Pijas

| Variante | Largo | Grosor/ancho informado | Uso | Cantidad requerida por ventana California | Precio por unidad |
| --- | --- | --- | --- | ---: | ---: |
| Rosca normal, cabeza de gota | 3/8 de pulgada | 8 mm | Asegurar las rodajas del corredizo | 2 | $0.20 |
| Punta de broca | 3/8 de pulgada | 8 mm | Asegurar el mulio al marco | 2 | $0.20 |

### Instalación

| Variante | Largo | Grosor/ancho informado | Uso | Cantidad requerida por ventana California | Precio por unidad |
| --- | --- | --- | --- | ---: | ---: |
| Cónico | 2 1/2 pulgadas | 10 mm | Instalación; detalle por precisar | 4 | $0.20 |

> [!NOTE]
> La tarifa de $0.20 por unidad es común y temporal para todas las variantes; no representa precios individuales confirmados. Las seis cantidades suman 24 chilillos por ventana, con un costo total actual de $4.80. Si después se conocen precios por variante, se actualizarán sus filas.

## Pasta

La pasta se aplica por dentro y por fuera de la ventana. Usa el ancho y el alto de fabricación ingresados por el vidriero, en pulgadas. El perímetro de una cara es `2 × (ancho + alto)`. La longitud total de aplicación es el doble de ese perímetro.

Cada tubo cuesta $47.00 y rinde 26 pies lineales (312 pulgadas) de aplicación. La tarifa es `47 ÷ 312`, aproximadamente **$0.1506 por pulgada lineal**. Para costear la ventana, multiplica la longitud total de aplicación por la tarifa sin redondearla previamente. En el desglose, el consumo se muestra como tubos aproximados, redondeados hacia arriba a cuartos de tubo (por ejemplo, 1.30 tubos → 1 1/2 tubos). Esta aproximación sirve para preparar material y no modifica el costo exacto calculado.

## Reglas confirmadas para el costeo

- El costo de compra de cada tramo de aluminio se puede mostrar como costo por pie lineal; los perfiles considerados miden 21 pies, salvo molduras y vistas, que se compran en tramos de 12 pies.
- El costo de compra de una hoja de vidrio se puede mostrar como costo por pie cuadrado, usando la hoja doble fuerza de 1/8″ de 71″ × 102″.
- Los materiales de consumo lineal se valoran por pie lineal; la tela mosquitera se valora por pie cuadrado según `anchoScreen × altoScreen`, convirtiendo de pulgadas cuadradas a pies cuadrados (`÷ 144`).
- Para el costo de una ventana se valora la medida exacta consumida, sin redondear a un tramo de aluminio o una hoja de vidrio completa.
- Los cálculos conservan su precisión. El precio final de venta se muestra en pesos enteros: con 50 centavos o más sube al siguiente peso; con menos de 50 centavos baja al peso anterior. El total del pedido suma los precios redondeados por ventana. El costo base de materiales puede conservar centavos.
- Actualizar el costo de compra afecta cálculos nuevos, no los ya consultados.
- La lista de accesorios necesarios para armar la ventana todavía será proporcionada por el usuario. La tabla conserva los accesorios que ya están identificados; no se considera completa.

## Información por completar

- El registro de tipos y dimensiones de rollos y la optimización de su acomodo quedan para una etapa futura; la tela se valorará en el alcance actual mediante una tarifa por pie cuadrado.
- Completar la lista de accesorios que lleva la ventana.
- Investigar el largo exacto del ventanero para marco, completar las cantidades y precios unitarios del catálogo de chilillos, y conciliar las 24 unidades con el desglose por variante.
