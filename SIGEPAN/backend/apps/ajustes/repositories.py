from .models import Ajuste


class AjusteRepository:
    """
    Repositorio para el acceso a datos del módulo Ajustes.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los ajustes registrados, más recientes primero.
        """

        return (
            Ajuste.objects
            .select_related(
                "producto",
                "usuario",
            )
            .order_by(
                "-fecha",
            )
        )

    @staticmethod
    def obtener(id_ajuste):
        """
        Obtiene un ajuste por su identificador.
        """

        return (
            Ajuste.objects
            .select_related(
                "producto",
                "usuario",
            )
            .get(
                id_ajuste=id_ajuste,
            )
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo registro de ajuste.
        """

        return Ajuste.objects.create(
            **datos
        )

    @staticmethod
    def filtrar(id_producto=None, tipo=None, desde=None, hasta=None):
        """
        Filtra ajustes por producto, tipo y/o rango de fechas.
        """

        consulta = AjusteRepository.listar()

        if id_producto:
            consulta = consulta.filter(producto_id=id_producto)

        if tipo:
            consulta = consulta.filter(tipo=tipo)

        if desde:
            consulta = consulta.filter(fecha__date__gte=desde)

        if hasta:
            consulta = consulta.filter(fecha__date__lte=hasta)

        return consulta
