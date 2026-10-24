from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: str = Field(..., max_length=500)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    categoria: str
    imagen_url: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None

class ProductoOut(ProductoBase):
    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)