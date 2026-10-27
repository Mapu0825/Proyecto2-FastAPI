from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from app.database import pedidos_col, productos_col, usuarios_col
from app.models.pedido import EstadoPedido, PedidoCreate, PedidoEstadoUpdate, PedidoOut
from app.security import require_admin
from app.utils import serializar, to_object_id
from app.models.usuarios import Rol

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoOut, status_code=201)
def crear_pedido(pedido:PedidoCreate):
    usuarios_col.update_one(
        {"email": pedido.usuario_email},
        {
            "$set": {"django_id": pedido.usuario_id},
            "$setOnInsert": {
                "nombre": pedido.usuario_nombre,
                "rol": Rol.cliente.value,
                "fecha_registro": datetime.now(timezone.outc)
            },
        },
        upsert=True
    )

    items_out, descontados, total = [], [], 0.0
    try:
        for item in pedido.items:
            oid = to_object_id(item.producto_id)
            prod = productos_col.find_one_and_update(
                {"_id": oid, "stock": {"$gte": item.cantidad}},
                {"$inc": {"stock": -item.cantidad}}
            )
            if prod is None:
                if not productos_col.find_one({"_id": oid}):
                    raise HTTPException(404, f"Producto {item.producto_id} no existe")
                raise HTTPException(409, f"Stock insuficiente para {item.producto_id}")
            descontados.append((oid, item.cantidad))
            total += prod["precio"] * item.cantidad
            items_out.append({
                "producto_id": item.producto_id,
                "cantidad": item.cantidad,
                "nombre": prod["nombre"],
                "precio_unitario": prod["precio"],
            })
    except HTTPException:
        # Revertir el stock ya descontado si algo falló
        for oid, cant in descontados:
            productos_col.update_one({"_id": oid}, {"$inc": {"stock": cant}})
        raise

    doc = {
        "usuario_id": pedido.usuario_id,
        "items": items_out,
        "direccion_envio": pedido.direccion_envio,
        "total": round(total, 2),
        "estado": EstadoPedido.pendiente.value,
        "fecha": datetime.now(timezone.utc),
    }
    res = pedidos_col.insert_one(doc)
    doc["_id"] = res.inserted_id
    return serializar(doc)


@router.get("/", response_model=List[PedidoOut])
def listar_pedidos(usuario_id: Optional[int] = None):
    """Con usuario_id: historial del cliente. Sin usuario_id: solo admin."""
    if usuario_id is None:
        raise HTTPException(status_code=400, detail="Indica usuario_id, o usa /pedidos/admin/todos")
    docs = pedidos_col.find({"usuario_id": usuario_id}).sort("fecha", -1)
    return [serializar(d) for d in docs]


@router.get("/admin/todos", response_model=List[PedidoOut],
            dependencies=[Depends(require_admin)])
def listar_todos():
    return [serializar(d) for d in pedidos_col.find().sort("fecha", -1)]


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(pedido_id: str):
    doc = pedidos_col.find_one({"_id": to_object_id(pedido_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return serializar(doc)


@router.patch("/{pedido_id}/estado", response_model=PedidoOut,
              dependencies=[Depends(require_admin)])
def cambiar_estado(pedido_id: str, cambio: PedidoEstadoUpdate):
    doc = pedidos_col.find_one_and_update(
        {"_id": to_object_id(pedido_id)},
        {"$set": {"estado": cambio.estado.value}},
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return serializar(doc)

