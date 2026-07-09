from .services import registrar_log


class AuditMixin:
    """
    Mixin para registrar acciones en la bitácora.
    """

    audit_module = None

    def registrar_auditoria(
        self,
        tipo_accion,
        descripcion,
    ):
        """
        Registra una acción en la bitácora del sistema.
        """

        registrar_log(
            request=self.request,
            usuario=self.request.usuario,
            modulo=self.audit_module,
            tipo_accion=tipo_accion,
            descripcion=descripcion,
        )