"""AVAO API - punto de entrada.

HU: infraestructura base (pendiente asignar HU de setup).
#27 / HU-01: include router de recepción de pedidos.
#29 / HU-02: include router de listado de tareas pendientes.
"""

from fastapi import FastAPI

from routers import pedidos, tareas

app = FastAPI(title="AVAO API")
app.include_router(pedidos.router)
app.include_router(tareas.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
