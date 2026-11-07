from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import admin_required
from django.utils.http import url_has_allowed_host_and_scheme
from functools import wraps
from urllib.parse import quote
from django.urls import reverse
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

                if rol_real == "administrador":
                    return redirect("panel_admin")

                # Cliente: si venía del botón "Comprar", vuelve a esa compra
                destino = request.GET.get("next")
                if destino and url_has_allowed_host_and_scheme(
                    destino, allowed_hosts={request.get_host()}
                ):
                    return redirect(destino)
                return redirect("catalogo")
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

def cliente_required(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not request.session.get("token") or not usuario:
            messages.info(request, "Inicia sesión como cliente para comprar")
            return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")
        if usuario.get("rol") != "cliente":
            messages.error(request, "Solo los clientes pueden comprar")
            return redirect("catalogo")
        return vista(request, *args, **kwargs)
    return envoltura


@cliente_required
def comprar(request, producto_id):
    try:
        productos = api_client.listar_productos()
    except ApiError as e:
        messages.error(request, e.detail)
        return redirect("catalogo")

    producto = next((p for p in productos if str(p.get("id")) == str(producto_id)), None)
    if not producto:
        messages.error(request, "Producto no encontrado")
        return redirect("catalogo")
    if producto["stock"] <= 0:
        messages.error(request, "Este producto está agotado")
        return redirect("catalogo")

    direccion = ""
    if request.method == "POST":
        direccion = request.POST.get("direccion", "").strip()
        try:
            cantidad = int(request.POST.get("cantidad", "1"))
            if cantidad < 1 or cantidad > producto["stock"]:
                raise ValueError
        except ValueError:
            messages.error(request, "Cantidad inválida")
        else:
            if len(direccion) < 5:
                messages.error(request, "Escribe una dirección de envío válida")
            else:
                try:
                    api_client.crear_pedido(
                        request.session["token"], request.session["usuario"],
                        producto_id, cantidad, direccion,
                    )
                except ApiError as e:
                    messages.error(request, e.detail)
                else:
                    messages.success(request, "¡Pedido realizado con éxito!")
                    return redirect("mis_pedidos")
    return render(request, "comprar.html", {"producto": producto, "direccion": direccion})

@cliente_required
def mis_pedidos(request):
    try:
        pedidos = api_client.listar_pedidos(request.session["token"], _usuario_id(request))
    except ApiError as e:
        messages.error(request, e.detail)
        pedidos = []
    return render(request, "mis_pedidos.html", {"pedidos": pedidos})

def _usuario_id(request):
    u = request.session.get("usuario", {})
    return u.get("id") or u.get("_id")

@admin_required
def producto_editar(request, producto_id):
    try:
        productos = api_client.listar_productos()
    except ApiError as e:
        messages.error(request, e.detail)
        return redirect("catalogo")

    producto = next((p for p in productos if str(p.get("id")) == str(producto_id)), None)
    if not producto:
        messages.error(request, "Producto no encontrado")
        return redirect("catalogo")

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
            api_client.actualizar_producto(producto_id, datos)
        except ValueError:
            messages.error(request, "Precio y stock deben ser números")
        except ApiError as e:
            messages.error(request, e.detail)
        else:
            messages.success(request, "Producto actualizado correctamente")
            return redirect("catalogo")
        # Si hubo error, conserva lo que el admin había escrito
        for campo in ("nombre", "descripcion", "precio", "stock", "categoria", "imagen_url"):
            if campo in request.POST:
                producto[campo] = request.POST[campo]

    return render(request, "producto_editar.html", {"producto": producto})


@admin_required
def producto_eliminar(request, producto_id):
    if request.method == "POST":
        try:
            api_client.eliminar_producto(producto_id)
        except ApiError as e:
            messages.error(request, e.detail)
        else:
            messages.success(request, "Producto eliminado")
    return redirect("catalogo")