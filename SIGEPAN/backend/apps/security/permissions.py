from django.shortcuts import redirect
from django.contrib import messages

from .models import RolPermiso

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

        usuario = self.request.usuario

        return RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre=self.permission_module,
            id_permiso__accion=self.permission_action,
        ).exists()

    def dispatch(self, request, *args, **kwargs):
        """
        Valida que el usuario tenga el permiso requerido.
        """

        if not self.tiene_permiso():

            messages.error(
                request,
                "No tiene permisos para acceder a esta opción."
            )

            return redirect("home")

        return super().dispatch(request, *args, **kwargs)
