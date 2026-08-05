from .models import GastoOperativo


class GastoOperativoRepository:
    """
    Repositorio para el acceso a datos del módulo Gastos Operativos.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los gastos operativos, más recientes primero.
        """

        return (
            GastoOperativo.objects
            .select_related(
                "sucursal",
                "usuario",
                "caja",
            )
            .order_by(
                "-fecha_gasto",
            )
        )

    @staticmethod
    def obtener(id_gasto):
        """
        Obtiene un gasto operativo por su identificador.
        """

        return (
            GastoOperativo.objects
            .select_related(
                "sucursal",
                "usuario",
                "caja",
            )
            .get(
                id_gasto=id_gasto,
            )
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo gasto operativo.
        """

        return GastoOperativo.objects.create(
            **datos
        )

    @staticmethod
    def actualizar(gasto):
        """
        Guarda los cambios de un gasto operativo.
        """

        gasto.save()

        return gasto

    @staticmethod
    def filtrar(id_sucursal=None, categoria=None, desde=None, hasta=None):
        """
        Filtra gastos operativos por sucursal, categoría y/o rango de
        fechas.
        """

        consulta = GastoOperativoRepository.listar()

        if id_sucursal:
            consulta = consulta.filter(sucursal_id=id_sucursal)

        if categoria:
            consulta = consulta.filter(categoria__iexact=categoria)

        if desde:
            consulta = consulta.filter(fecha_gasto__date__gte=desde)

        if hasta:
            consulta = consulta.filter(fecha_gasto__date__lte=hasta)

        return consulta
