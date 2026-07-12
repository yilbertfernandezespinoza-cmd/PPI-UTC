from django.urls import path

from .views import (
    login_view,
    logout_view,

    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioDisableView,

    RolPermisoListView,
    
    BitacoraIngresosListView,
    BitacoraMovimientosListView,
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
    path(
        "usuarios/<int:id_usuario>/deshabilitar/",
        UsuarioDisableView.as_view(),
        name="usuario_disable",
    ),

    path(
        "bitacoras/ingresos/",
        BitacoraIngresosListView.as_view(),
        name="bitacora_ingresos",
    ),

    path(
        "bitacoras/movimientos/",
        BitacoraMovimientosListView.as_view(),
        name="bitacora_movimientos",
    ),
]

