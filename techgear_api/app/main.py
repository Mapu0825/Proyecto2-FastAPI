from fastapi import FastAPI
from app.database import verificar_conexion

app = FastAPI(title="TechGear API", version="1.0.0")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mongodb": "conectado" if verificar_conexion() else "sin conexión",
    }