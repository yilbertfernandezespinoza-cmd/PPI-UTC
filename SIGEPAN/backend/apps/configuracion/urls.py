from django.urls import path

from .views import (
    ModuloListView,
    ModuloCreateView,
    ModuloUpdateView,
    SucursalListView,
    SucursalCreateView,
    SucursalUpdateView,
    SucursalUpdateView,

)

app_name = "configuracion"

urlpatterns = [

    path(
        "modulos/",
        ModuloListView.as_view(),
        name="modulo_list"
    ),

    path(
        "modulos/nuevo/",
        ModuloCreateView.as_view(),
        name="modulo_create"
    ),

    path(
        "modulos/<int:id_modulo>/editar/",
        ModuloUpdateView.as_view(),
        name="modulo_update"
    ),

    path(
        "sucursales/",
        SucursalListView.as_view(),
        name="sucursal_list"
    ),

    path(
        "sucursales/nuevo/",
        SucursalCreateView.as_view(),
        name="sucursal_create"
    ),

    path(
        "sucursales/<int:id_sucursal>/editar/",
        SucursalUpdateView.as_view(),
        name="sucursal_update"
    ),
]