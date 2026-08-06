from datetime import datetime, timedelta

from django.utils import timezone

from .models import Ajuste


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha` — evita depender de que MySQL
    tenga cargadas las tablas de zona horaria (CONVERT_TZ), que es lo que
    necesitaría internamente `fecha__date__gte=`/`fecha__date__lte=` con
    USE_TZ=True. Mismo fix aplicado en dashboard/reportes/ventas (05-08).
    """
    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


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
            consulta = consulta.filter(fecha__gte=_limite_inferior(desde))

        if hasta:
            consulta = consulta.filter(fecha__lt=_limite_superior(hasta))

        return consulta
