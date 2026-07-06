from django.urls import path

from .views import (
    ModuloListView,
    ModuloCreateView,
    ModuloUpdateView,
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
]