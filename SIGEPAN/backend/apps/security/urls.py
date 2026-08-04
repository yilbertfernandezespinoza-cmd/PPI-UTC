from django.urls import path

from .views import (
    login_view,
    logout_view,

    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioDisableView,
    UsuarioEmpleadoDatosView,
    cambiar_usuario_view,

    RolPermisoListView,
    
    BitacoraIngresosListView,
    BitacoraMovimientosListView,
    BitacoraIngresosExportPdfView,
    BitacoraIngresosExportExcelView,
    BitacoraMovimientosExportPdfView,
    BitacoraMovimientosExportExcelView,

    recuperar_password_view,
    restablecer_password_view,

    PerfilView,
    google_vincular,
    google_callback,
    google_desvincular,
    
)

app_name = "security"

urlpatterns = [
    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "recuperar-contrasena/",
        recuperar_password_view,
        name="recuperar_password",
    ),

    path(
        "restablecer-contrasena/<str:token>/",
        restablecer_password_view,
        name="restablecer_password",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

    path(
        "cambiar-usuario/",
        cambiar_usuario_view,
        name="cambiar_usuario",
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
        "usuarios/empleado/<int:id_empleado>/datos/",
        UsuarioEmpleadoDatosView.as_view(),
        name="usuario_empleado_datos",
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

    path(
        "bitacoras/ingresos/exportar/pdf/",
        BitacoraIngresosExportPdfView.as_view(),
        name="bitacora_ingresos_pdf",
    ),

    path(
        "bitacoras/ingresos/exportar/excel/",
        BitacoraIngresosExportExcelView.as_view(),
        name="bitacora_ingresos_excel",
    ),

    path(
        "bitacoras/movimientos/exportar/pdf/",
        BitacoraMovimientosExportPdfView.as_view(),
        name="bitacora_movimientos_pdf",
    ),

    path(
        "bitacoras/movimientos/exportar/excel/",
        BitacoraMovimientosExportExcelView.as_view(),
        name="bitacora_movimientos_excel",
    ),

    path(
        "perfil/",
        PerfilView.as_view(),
        name="perfil",
    ),

    path(
        "perfil/google/vincular/",
        google_vincular,
        name="google_vincular",
    ),

    path(
        "perfil/google/callback/",
        google_callback,
        name="google_callback",
    ),

    path(
        "perfil/google/desvincular/",
        google_desvincular,
        name="google_desvincular",
    ),

]

