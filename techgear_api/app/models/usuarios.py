from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class Rol(str, Enum):
    cliente = "cliente"
    administrador = "administrador"


class UsuarioDB(BaseModel):
    """Esquema del documento en la colección 'usuarios' de Mongo."""
    django_id: int
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: Rol = Rol.cliente
    fecha_registro: datetime