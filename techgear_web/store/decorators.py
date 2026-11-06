from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not usuario:
            messages.warning(request, "Inicia sesión para continuar")
            return redirect("login")
        if usuario.get("rol") != "administrador":
            messages.error(request, "No tienes permisos de administrador")
            return redirect("catalogo")
        return view(request, *args, **kwargs)
    return wrapper