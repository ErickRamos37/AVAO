-- Esquema ejecutable de pedidos, ventanas y etiqueta de taller en SQLite.
-- apps.api.init_db agrega la columna a bases anteriores sin modificar sus pedidos.
-- Unidad de ancho_16 y alto_16: dieciseisavos de pulgada.
-- Ejemplos: 24 -> 384; 26 1/2 -> 424; 24 1/4 1/16 -> 389.
-- El backend valida la entrada fraccionaria y la convierte a esta unidad.
-- Al consultar, la aplicación reconstruye una fracción simplificada:
-- 389 -> 24 5/16. No se conserva la escritura original de la entrada.

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY,
    etiqueta TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS pedidos_etiqueta_unica ON pedidos (etiqueta);

CREATE TABLE IF NOT EXISTS ventanas (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos (id),
    numero_en_pedido INTEGER NOT NULL CHECK (numero_en_pedido > 0),
    ancho_16 INTEGER NOT NULL CHECK (ancho_16 > 0),
    alto_16 INTEGER NOT NULL CHECK (alto_16 > 0),
    CONSTRAINT ventanas_numero_por_pedido UNIQUE (pedido_id, numero_en_pedido)
);

-- Se crea al guardar el pedido. Cada fila es un tipo/orientación de perfil;
-- cantidad indica cuántas piezas iguales necesita esa ventana.
CREATE TABLE IF NOT EXISTS plan_aluminio (
    ventana_id INTEGER NOT NULL REFERENCES ventanas (id),
    orden INTEGER NOT NULL CHECK (orden BETWEEN 1 AND 10),
    perfil TEXT NOT NULL,
    longitud_16 INTEGER NOT NULL CHECK (longitud_16 > 0),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    PRIMARY KEY (ventana_id, orden)
);

-- Dos vidrios iguales por ventana, calculados y guardados con el pedido.
CREATE TABLE IF NOT EXISTS plan_vidrio (
    ventana_id INTEGER PRIMARY KEY REFERENCES ventanas (id),
    ancho_16 INTEGER NOT NULL CHECK (ancho_16 > 0),
    alto_16 INTEGER NOT NULL CHECK (alto_16 > 0),
    cantidad INTEGER NOT NULL CHECK (cantidad = 2)
);

-- Guardar pedido y ventanas juntos en una transacción de la aplicación.
-- La aplicación exige al menos una ventana con ambas medidas completas.
-- Una fila vacía se omite; una fila parcial se rechaza antes de guardar.
-- La aplicación rechaza entradas inválidas o más finas que 1/16; no las
-- redondea silenciosamente al guardar. El redondeo de cortes pertenece a HU-02.
-- Para el centro de HU-02, el backend toma el techo de ancho_16 / 2;
-- da el siguiente 1/16 si la mitad exacta cae en 1/32.
-- Ejemplo: 753 / 2 -> 376.5 -> 377 (= 23 9/16).
-- El índice de UNIQUE (pedido_id, numero_en_pedido) cubre búsquedas por pedido.
-- La conexión activa PRAGMA foreign_keys para hacer cumplir la referencia.
-- Los pedidos anteriores a HU-22 conservan etiqueta NULL hasta que el usuario
-- decida reiniciar sus datos de prueba; los pedidos nuevos reciben A, B, ...
-- HU-13 añadirá datos del cliente.
-- No hay tabla de catálogo: solo se registra California por mitad en HU-01.
