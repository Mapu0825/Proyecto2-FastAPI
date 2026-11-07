import requests
from django.conf import settings

TIMEOUT = 60


class ApiError(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _request(method, path, token=None, api_key=None, **kwargs):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["X-API-Key"] = api_key
    try:
        r = requests.request(
            method, f"{settings.API_URL}{path}",
            headers=headers, timeout=TIMEOUT, **kwargs,
        )
    except requests.RequestException:
        raise ApiError(503, "No se pudo conectar con la API de TechGear")

    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", "Error en la API")
        except ValueError:      # la API respondió texto plano (ej. un 500)
            raise ApiError(
                r.status_code,
                f"La API respondió {r.status_code}. Revisa la terminal de uvicorn.",
            )
        if isinstance(detail, list):      # error 422 de validación
            partes = []
            for err in detail:
                campo = ".".join(
                    str(x) for x in err.get("loc", []) if x not in ("body", "query")
                )
                msg = err.get("msg", "Datos inválidos")
                partes.append(f"{campo}: {msg}" if campo else msg)
            detail = " | ".join(partes)
        raise ApiError(r.status_code, detail)
    return r.json() if r.content else None


def login(email, password):
    return _request("POST", "/usuarios/login", json={"email": email, "password": password})


def registro(nombre, email, password):
    return _request("POST", "/usuarios/registro",
                    json={"nombre": nombre, "email": email, "password": password})


def _con_id(registro):
    """Garantiza una clave 'id' (las plantillas no pueden leer '_id')."""
    if isinstance(registro, dict) and not registro.get("id"):
        registro["id"] = (
            registro.get("_id")
            or registro.get("producto_id")
            or registro.get("pedido_id")
        )
    return registro


def listar_productos(categoria=None):
    params = {"categoria": categoria} if categoria else {}
    productos = _request("GET", "/productos/", params=params) or []
    return [_con_id(p) for p in productos]


def crear_producto(datos):
    return _request("POST", "/productos/", api_key=settings.API_KEY, json=datos)


def crear_pedido(token, usuario, producto_id, cantidad, direccion):
    return _request("POST", "/pedidos/", token=token, json={
        "usuario_id": usuario["id"],
        "usuario_email": usuario["email"],
        "usuario_nombre": usuario["nombre"],
        "items": [{"producto_id": producto_id, "cantidad": cantidad}],
        "direccion_envio": direccion,
    })


def listar_pedidos(token, usuario_id):
    pedidos = _request("GET", "/pedidos/", token=token,
                       params={"usuario_id": usuario_id}) or []
    return [_con_id(p) for p in pedidos]

def actualizar_producto(producto_id, datos):
    return _request("PUT", f"/productos/{producto_id}", api_key=settings.API_KEY, json=datos)

def eliminar_producto(producto_id):
    return _request("DELETE", f"/productos/{producto_id}", api_key=settings.API_KEY)