from django.shortcuts import redirect
from django.contrib import messages

from .models import RolPermiso
from .services import registrar_log

class PermissionRequiredMixin:
    """
    Mixin para validar permisos.
    """

    required_permission = None

    permission_module = None 
    permission_action = None

    def tiene_permiso(self):
        """
        Verifica si el usuario tiene el permiso requerido.
        """

        return self.usuario_tiene_permiso(
            self.permission_module,
            self.permission_action,
        )

    def usuario_tiene_permiso(self, modulo, accion):
        """
        Verifica si el usuario autenticado posee un permiso específico.
        """

        usuario = self.request.usuario

        return RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre=modulo,
            id_permiso__accion=accion,
        ).exists()
    
    def dispatch(self, request, *args, **kwargs):
        """
        Valida que el usuario tenga el permiso requerido.
        """

        if not self.tiene_permiso():

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo=self.permission_module,
                tipo_accion="ACCESO_DENEGADO",
                descripcion=(
                    f"Intento de ejecutar "
                    f"{self.permission_action} "
                    f"sin autorización."
                ),
            )

            messages.error(
                request,
                "No tiene permisos para acceder a esta opción."
            )

            return redirect("home")

        return super().dispatch(
            request,
            *args,
            **kwargs
        )
