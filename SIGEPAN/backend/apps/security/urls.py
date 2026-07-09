from django.urls import path

from .views import (
    login_view,
    logout_view,

    RolListView,
    RolCreateView,
    RolUpdateView,

    PermisoListView,
    PermisoCreateView,
    PermisoUpdateView,

    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,

    RolPermisoListView,
    
)

app_name = "security"

urlpatterns = [
    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

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

    path(
        "rol-permisos/",
        RolPermisoListView.as_view(),
        name="rol_permiso_list",
    ),

    path(
        "usuarios/",
        UsuarioListView.as_view(),
        name="usuario_list",
    ),

    path(
        "usuarios/nuevo/",
        UsuarioCreateView.as_view(),
        name="usuario_create",
    ),

    path(
        "usuarios/<int:id_usuario>/editar/",
        UsuarioUpdateView.as_view(),
        name="usuario_update",
    ),
]

