from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalogo, name="catalogo"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("logout/", views.logout_view, name="logout"),
    path("panel/", views.panel_admin, name="panel_admin"),
    path("panel/productos/nuevo/", views.producto_nuevo, name="producto_nuevo"),
    path("comprar/<str:producto_id>/", views.comprar, name="comprar"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("productos/<str:producto_id>/editar/", views.producto_editar, name="producto_editar"),
    path("productos/<str:producto_id>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
]