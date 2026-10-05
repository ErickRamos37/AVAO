# Plan de Trabajo: Diseño Lógico y Físico de Base de Datos (Fase 1 - Prioridad Inicial)

**Estándar de Referencia:** IEEE Std 1016-2009 (Software Design Descriptions).
**Trazabilidad:** Tareas #26, #27, #28, #29, #30, #31 | Historias de Usuario: HU-01, HU-02, HU-03.

---

## 1. Alcance Estricto (Principio YAGNI / Cero Sobreingeniería)
Este diseño cubre **únicamente** las entidades necesarias para soportar el flujo inicial de captura de pedidos en Ventas y visualización/actualización de cortes en Taller:
1. `clientes`: Información de contacto básica del cliente (HU-01).
2. `pedidos`: Cabecera del pedido, estados del flujo y timestamps (HU-01, #27).
3. `productos`: Catálogo base de materiales (vidrio/aluminio) y sus características técnicas (HU-01).
4. `piezas`: Detalle de cortes individuales con dimensiones milimétricas, cantidades, estado de corte y asignación de operario (HU-01, HU-02, #29, #30, #31).

*Nota:* Tablas de optimización 2D (guillotina/rectpack), inventario complejo (HU-14) o usuarios avanzados (HU-10) se integrarán en fases posteriores para no inflar el modelo.

---

## 2. Entregables Esperados del Agente de Base de Datos
1. **Modelo Lógico de Datos (LMD):** Entidades, atributos de negocio, relaciones, cardinalidades y claves candidatas (notación Mermaid ERD).
2. **Modelo Físico de Datos (PMD):** Tipos de datos específicos de PostgreSQL (UUID v4, `NUMERIC(10, 2)` para medidas en mm, `TIMESTAMP WITH TIME ZONE`, Enums o Checks para estados), restricciones (`NOT NULL`, `CHECK (ancho > 0)`, `ON DELETE RESTRICT/CASCADE`), índices necesarios (`btree` en FKs y estados).
3. **Diccionario de Datos:** Descripción exhaustiva de cada campo y justificación técnica.
4. **Archivo de Salida:** `/home/erick/Proyectos/AVAO/docs/design/ERD-FASE1.md`.

---

## 3. Flujo de Trabajo del Agente (Gestión de Tareas en GitHub Projects)
1. **Inicio:** Tomar la primera tarea de la columna **"Por hacer"** (la más prioritaria) y moverla a **"En proceso"** en el tablero de GitHub Projects.
2. **Ejecución:** Desarrollar e implementar exactamente lo definido en el checklist de esa tarea, siguiendo estándares IEEE aplicables y pruebas TDD (o estrategia de QA equivalente para diseño/modelos).
3. **Validación:** Ejecutar todas las pruebas especificadas en la tarea y asegurar cero errores de integridad/compilación.
4. **Finalización:** Solo tras validar éxito, notificar al orquestador para que **mueva la tarea a "Finalizada"** en GitHub Projects.
5. **Avance:** Inmediatamente tomar la siguiente tarea de "Por hacer", moverla a "En proceso" y repetir el ciclo.
6. **Restricción:** No avanzar a una nueva tarea sin que la anterior esté en "Finalizada".
