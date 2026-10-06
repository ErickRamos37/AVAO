# AVAO — Asistente para Vidrieras Administrativo y Operativo

## 1. Identidad del Proyecto
**Nombre Oficial:** Automatización de procesos operativos y gestión de taller para MiPyMEs vidrieras mediante una Aplicación Web Progresiva con asistente gráfico de corte.
**Nombre del Producto:** AVAO.

## 2. Objetivo General
Desarrollar una Aplicación Web Progresiva (PWA) B2B para automatizar el cálculo de descuentos, digitalizar el seguimiento de pedidos y asistir visualmente la ejecución de cortes en MiPyMEs vidrieras, eliminando la fricción de los procesos manuales.

## 3. Stack Tecnológico Estructural
La plataforma se divide en dos entornos que garantizan escalabilidad y resiliencia offline:

*   **Entorno Cliente (Frontend B2B):**
    *   **Framework:** Vite + React.
    *   **Motor Gráfico:** HTML5 Canvas 2D (Renderizado de guías de corte en Taller).
    *   **Persistencia Local:** Dexie.js para soporte Offline-First mediante IndexedDB.
*   **Entorno Servidor (Backend & DB en Docker / Oracle Cloud):**
    *   **API y Lógica:** Python (FastAPI).
    *   **Motor de Optimización:** `rectpack` (Algoritmo de Guillotina 2D).
    *   **Seguridad:** `fastapi-users` (Autenticación JWT) e implementación de UUIDs.
    *   **Base de Datos:** PostgreSQL gestionado vía SQLAlchemy (ORM) y Alembic (Migraciones).
    *   **Proxy / Web Server:** Nginx (Proxy Pass, Terminación SSL/TLS, WSS).

## 4. Estándares de Codificación
*   Todo componente, API o modelo de base de datos debe ser referenciado a su respectiva Historia de Usuario (HU) y documentado in-line.
*   Los scripts de despliegue local de Docker se ubicarán en la raíz del repositorio (pendiente de definición por DevOps). Actualmente existe `infra/docker-compose.yml` para desarrollo; su ubicación definitiva sigue pendiente. No agregar scripts nuevos hasta resolverla.
