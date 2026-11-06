from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import admin_required

from . import api_client
from .api_client import ApiError


def catalogo(request):
    categoria = request.GET.get("categoria") or None
    try:
        productos = api_client.listar_productos(categoria)
    except ApiError as e:
        messages.error(request, e.detail)
        productos = []
    return render(request, "catalogo.html",
                  {"productos": productos, "categoria": categoria or ""})


def login_view(request):
    if request.session.get("token"):
        return redirect("catalogo")
    if request.method == "POST":
        rol_elegido = request.POST.get("rol", "cliente")
        try:
            data = api_client.login(
                request.POST.get("email", "").strip(),
                request.POST.get("password", ""),
            )
        except ApiError as e:
            messages.error(request, e.detail)
        else:
            rol_real = data["usuario"]["rol"]
            if rol_elegido != rol_real:
                if rol_elegido == "administrador":
                    messages.error(request, "Esta cuenta no tiene permisos de administrador")
                else:
                    messages.error(request, "Esta cuenta es de administrador: elige 'Administrador' para entrar")
            else:
                request.session["token"] = data["access_token"]
                request.session["usuario"] = data["usuario"]
                messages.success(request, f"Bienvenido, {data['usuario']['nombre']}")
                return redirect("panel_admin" if rol_real == "administrador" else "catalogo")
    return render(request, "login.html")


def registro_view(request):
    if request.method == "POST":
        try:
            api_client.registro(
                request.POST.get("nombre", "").strip(),
                request.POST.get("email", "").strip(),
                request.POST.get("password", ""),
            )
        except ApiError as e:
            messages.error(request, e.detail)
        else:
            messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
            return redirect("login")
    return render(request, "registro.html")


def logout_view(request):
    request.session.flush()       # borra token y datos de la sesión
    messages.info(request, "Sesión cerrada")
    return redirect("catalogo")

@admin_required
def producto_nuevo(request):
    if request.method == "POST":
        try:
            datos = {
                "nombre": request.POST.get("nombre", "").strip(),
                "descripcion": request.POST.get("descripcion", "").strip(),
                "precio": float(request.POST.get("precio", "0")),
                "stock": int(request.POST.get("stock", "0")),
                "categoria": request.POST.get("categoria", "").strip(),
                "imagen_url": request.POST.get("imagen_url", "").strip() or None,
            }
            api_client.crear_producto(datos)
        except ValueError:
            messages.error(request, "Precio y stock deben ser números")
        except ApiError as e:
            messages.error(request, e.detail)
        else:
            messages.success(request, "Producto creado correctamente")
            return redirect("catalogo")
    return render(request, "producto_form.html")
    
@admin_required
def panel_admin(request):
    return render(request, "panel_admin.html")