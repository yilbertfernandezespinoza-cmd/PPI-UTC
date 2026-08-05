from .models import Merma


class MermaRepository:
    """
    Repositorio para el acceso a datos del módulo Mermas.
    """

    @staticmethod
    def listar():
        """
        Obtiene todas las mermas registradas, más recientes primero.
        """

        return (
            Merma.objects
            .select_related(
                "producto",
                "usuario",
            )
            .order_by(
                "-fecha",
            )
        )

    @staticmethod
    def obtener(id_merma):
        """
        Obtiene una merma por su identificador.
        """

        return (
            Merma.objects
            .select_related(
                "producto",
                "usuario",
            )
            .get(
                id_merma=id_merma,
            )
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo registro de merma.
        """

        return Merma.objects.create(
            **datos
        )

    @staticmethod
    def filtrar(id_producto=None, desde=None, hasta=None):
        """
        Filtra mermas por producto y/o rango de fechas (para reportes
        y para el listado con filtros del RF).
        """

        consulta = MermaRepository.listar()

        if id_producto:
            consulta = consulta.filter(producto_id=id_producto)

        if desde:
            consulta = consulta.filter(fecha__date__gte=desde)

        if hasta:
            consulta = consulta.filter(fecha__date__lte=hasta)

        return consulta
