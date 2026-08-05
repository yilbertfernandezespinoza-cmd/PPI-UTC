from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Usuario, RolPermiso
from .services import registrar_log


def login_required(view_func):
    """
    Valida que exista una sesión activa con un usuario válido (mismo
    criterio que SessionRequiredMixin, usado en las vistas basadas en
    clase: usuario debe existir y estar activo). Deja disponibles
    request.usuario / request.empleado / request.rol / request.sucursal
    para que la vista los use si lo necesita.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            return redirect("security:login")

        try:
            usuario = Usuario.objects.select_related(
                "id_empleado",
                "id_rol",
                "id_sucursal",
            ).get(
                id_usuario=usuario_id,
                estado=True,
            )
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect("security:login")

        request.usuario = usuario
        request.empleado = usuario.id_empleado
        request.rol = usuario.id_rol
        request.sucursal = usuario.id_sucursal

        return view_func(request, *args, **kwargs)

    return wrapper


def permiso_requerido(modulo, accion):
    """
    Equivalente a PermissionRequiredMixin (apps/security/permissions.py)
    pero para vistas basadas en función. Debe usarse DESPUÉS de
    @login_required en la cadena de decoradores, porque depende de
    request.usuario.

    No se aplica todavía en caja/proveedores: requiere confirmar primero
    que existan filas de Modulo/RolPermiso para esos módulos, para no
    bloquear a todos los usuarios por accidente. Queda disponible para
    cuando se verifique eso.
    """

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            usuario = getattr(request, "usuario", None)

            tiene_permiso = usuario is not None and RolPermiso.objects.filter(
                id_rol=usuario.id_rol,
                id_permiso__id_modulo__nombre=modulo,
                id_permiso__accion=accion,
            ).exists()

            if not tiene_permiso:

                registrar_log(
                    request=request,
                    usuario=usuario,
                    modulo=modulo,
                    tipo_accion="ACCESO_DENEGADO",
                    descripcion=f"Intento de ejecutar {accion} sin autorización.",
                )

                messages.error(
                    request,
                    "No tiene permisos para acceder a esta opción.",
                )

                return redirect("home")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorador