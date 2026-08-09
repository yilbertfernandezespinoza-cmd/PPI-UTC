from django.urls import path

from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDisableView,
    buscar_cliente_pos,
)

app_name = "clientes"

urlpatterns = [

    path(
        "",
        ClienteListView.as_view(),
        name="listar",
    ),

    path(
        "crear/",
        ClienteCreateView.as_view(),
        name="crear",
    ),

    path(
        "editar/<int:id_cliente>/",
        ClienteUpdateView.as_view(),
        name="editar",
    ),

    path(
        "estado/<int:id_cliente>/",
        ClienteDisableView.as_view(),
        name="estado",
    ),

    path(
        "pos/buscar/",
        buscar_cliente_pos,
        name="buscar_cliente_pos",
    ),

]