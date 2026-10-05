"""AVAO API - punto de entrada.

HU: infraestructura base (pendiente asignar HU de setup).
#27 / HU-01: include router de recepción de pedidos.
#29 / HU-02: include router de listado de tareas pendientes.
#31 / HU-02+HU-09: include router de completar pieza.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import pedidos, piezas, tareas

app = FastAPI(title="AVAO API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(pedidos.router)
app.include_router(tareas.router)
app.include_router(piezas.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
