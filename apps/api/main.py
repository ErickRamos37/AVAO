"""AVAO API - punto de entrada.
HU: infraestructura base (pendiente asignar HU de setup).
"""
from fastapi import FastAPI

app = FastAPI(title="AVAO API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
