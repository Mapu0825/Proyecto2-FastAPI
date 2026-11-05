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
        detail = r.json().get("detail", "Error en la API") if r.content else "Error"
        if isinstance(detail, list):          # error 422 de validación
            detail = detail[0].get("msg", "Datos inválidos")
        raise ApiError(r.status_code, detail)
    return r.json() if r.content else None

def login(email, password):
    return _request("POST", "/usuarios/login", json={"email": email, "password": password})


def registro(nombre, email, password):
    return _request("POST", "/usuarios/registro",
                    json={"nombre": nombre, "email": email, "password": password})


def listar_productos(categoria=None):
    params = {"categoria": categoria} if categoria else {}
    return _request("GET", "/productos/", params=params)

def crear_producto(datos):
    return _request("POST", "/productos/", api_key=settings.API_KEY, json=datos)