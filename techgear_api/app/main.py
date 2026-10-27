from fastapi import FastAPI
from app.database import verificar_conexion
from app.routers import pedidos, productos

app = FastAPI(title="TechGear API", description = "API de produtos y pedidos", version="1.0.0")

app.include_router(productos.router)
app.include_router(pedidos.router)

@app.get("/", tags=["Sistema"])
def raiz():
    return {"mensaje": "TechGear API", "docs": "/docs"}


@app.get("/health", tags = ["Sistema"])
def health():
    return {
        "status": "ok",
        "mongodb": "conectado" if verificar_conexion() else "sin conexión",
    }