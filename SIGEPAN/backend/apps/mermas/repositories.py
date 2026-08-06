from datetime import datetime, timedelta

from django.utils import timezone

from .models import Merma


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha` — evita depender de que MySQL
    tenga cargadas las tablas de zona horaria (CONVERT_TZ), que es lo que
    necesitaría internamente `fecha__date__gte=`/`__lte=` con USE_TZ=True.
    Mismo fix aplicado en dashboard/reportes/ventas/ajustes (05-08).
    """
    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


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
            consulta = consulta.filter(fecha__gte=_limite_inferior(desde))

        if hasta:
            consulta = consulta.filter(fecha__lt=_limite_superior(hasta))

        return consulta
