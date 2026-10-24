from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from app.models.producto import PyObjectId

class EstadoPedido(str, Enum):
    pendiente = "pendiente"
    enviado = "enviado"
    entregado = "entregado"
    cancelado = "cancelado"

class ItemPedido(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)

class ItemPedidoOut(ItemPedido):
    nombre: str
    precio_unitario: float

class PedidoCreate(BaseModel):
    usuario_id: int            # id del usuario en Django
    items: List[ItemPedido] = Field(..., min_length=1)
    direccion_envio: str = Field(..., min_length=5)

class PedidoOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    usuario_id: int
    items: List[ItemPedidoOut]
    direccion_envio: str
    total: float
    estado: EstadoPedido = EstadoPedido.pendiente
    fecha: datetime
    model_config = ConfigDict(populate_by_name=True)