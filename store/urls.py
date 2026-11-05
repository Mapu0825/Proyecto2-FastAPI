from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalogo, name="catalogo"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("logout/", views.logout_view, name="logout"),
    path("panel/", views.panel_admin, name="panel_admin"),
    path("panel/productos/nuevo/", views.producto_nuevo, name="producto_nuevo"),
]