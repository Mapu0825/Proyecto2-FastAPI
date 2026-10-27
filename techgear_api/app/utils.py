from bson import ObjectId
from fastapi import HTTPException

def to_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=422, details=f"ID invalido: {id}")
    return ObjectId(id)

def serializar(doc: dict) -> dict:
    """Convierte _id (ObjectId) en id (str)."""
    doc["id"] = str(doc.pop("_id"))
    return doc