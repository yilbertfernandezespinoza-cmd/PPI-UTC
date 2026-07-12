from django.shortcuts import redirect

from .models import Usuario

class SessionRequiredMixin:
    """
    Valida la sesión y carga la información del usuario autenticado.
    """

    def dispatch(self, request, *args, **kwargs):

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

        return super().dispatch(request, *args, **kwargs)