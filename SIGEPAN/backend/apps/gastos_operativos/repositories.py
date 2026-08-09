from datetime import datetime, timedelta

from django.utils import timezone

from .models import GastoOperativo


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha` — evita depender de que MySQL
    tenga cargadas las tablas de zona horaria (CONVERT_TZ), que es lo que
    necesitaría internamente `fecha_gasto__date__gte=`/`__lte=` con
    USE_TZ=True. Mismo fix aplicado en dashboard/reportes/ventas (05-08).

    Corregido (07-08): `fecha` llega como string crudo desde
    `request.GET.get("desde")` (el input type="date" del filtro), nunca
    se convertía a `date` antes de llegar aquí — `datetime.combine()`
    exige un `date`, no un `str`, y esto rompía el listado con
    `TypeError: combine() argument 1 must be datetime.date, not str` en
    cuanto se aplicaba cualquier filtro de fecha.
    """
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


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
            consulta = consulta.filter(fecha_gasto__gte=_limite_inferior(desde))

        if hasta:
            consulta = consulta.filter(fecha_gasto__lt=_limite_superior(hasta))

        return consulta
