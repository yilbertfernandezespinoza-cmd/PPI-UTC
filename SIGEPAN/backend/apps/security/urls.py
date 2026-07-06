from django.urls import path

from .views import (
    RolListView,
    RolCreateView,
    RolUpdateView,
    PermisoListView,
    PermisoCreateView,
    PermisoUpdateView,
)

app_name = "security"

urlpatterns = [
    path(
        "roles/",
        RolListView.as_view(),
        name="rol_list",
    ),

    path(
        "roles/nuevo/",
        RolCreateView.as_view(),
        name="rol_create",
    ),

    path(
        "roles/<int:id_rol>/editar/",
        RolUpdateView.as_view(),
        name="rol_update",
    ),

    path(
    "permisos/",
    PermisoListView.as_view(),
    name="permiso_list",
    ),

    path(
    "permisos/nuevo/",
    PermisoCreateView.as_view(),
    name="permiso_create",
    ),

    path(
    "permisos/<int:id_permiso>/editar/",
    PermisoUpdateView.as_view(),
    name="permiso_update",
    ),
]

