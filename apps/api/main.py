"""AVAO API - punto de entrada.

HU: infraestructura base (pendiente asignar HU de setup).
#27 / HU-01: include router de recepción de pedidos.
"""

from fastapi import FastAPI

from routers import pedidos

app = FastAPI(title="AVAO API")
app.include_router(pedidos.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
