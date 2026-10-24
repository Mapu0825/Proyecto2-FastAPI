import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URL = (
    os.getenv("MONGO_URI")
    or os.getenv("MONGODB_URI")
    or os.getenv("MONGO_URL")
)
DB_NAME = os.getenv("MONGODB_DB", "techgear")

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

db = client[DB_NAME]
productos_col = db["productos"]
pedidos_col = db["pedidos"]


def verificar_conexion() -> bool:
    try:
        client.admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False