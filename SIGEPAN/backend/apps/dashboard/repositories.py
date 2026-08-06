from datetime import datetime, timedelta

from django.db.models import Sum, Avg
from django.utils import timezone

from apps.ventas.models import Venta, DetalleVenta


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha`.

    Bug corregido (05-08): este archivo usaba `date.today()` (hora del
    sistema operativo del servidor, no necesariamente la misma zona horaria
    que TIME_ZONE) junto con `fecha__date=`/`fecha__date__gte=` sobre un
    DateTimeField. Con USE_TZ=True, ese lookup depende de que MySQL pueda
    convertir el valor guardado (UTC) a la zona horaria activa vía
    CONVERT_TZ() — función que devuelve NULL en silencio si las tablas de
    zonas horarias de MySQL no están cargadas (`mysql_tzinfo_to_sql`), muy
    común que no lo estén por defecto. El resultado: "ventas del día" podía
    mostrar 0 aunque sí hubiera ventas, sin ningún error visible. Se
    reemplaza por `timezone.localdate()` (respeta TIME_ZONE de Django) +
    comparación >=/< contra límites de día calculados en Python.
    """
    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


class DashboardRepository:

    @staticmethod
    def ventas_del_dia():
        hoy = timezone.localdate()
        total = Venta.objects.filter(
            estado=True,
            fecha__gte=_limite_inferior(hoy),
            fecha__lt=_limite_superior(hoy),
        ).aggregate(total=Sum("total"))["total"]
        return total or 0

    @staticmethod
    def ventas_del_mes():
        # Mismo problema que _limite_inferior/_limite_superior: `fecha__year=`/
        # `fecha__month=` sobre un DateTimeField también dependen de CONVERT_TZ
        # en MySQL. Se calcula el rango [1° del mes, 1° del mes siguiente) en
        # Python en su lugar.
        hoy = timezone.localdate()
        inicio_mes = hoy.replace(day=1)
        if inicio_mes.month == 12:
            inicio_mes_siguiente = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
        else:
            inicio_mes_siguiente = inicio_mes.replace(month=inicio_mes.month + 1)

        total = Venta.objects.filter(
            estado=True,
            fecha__gte=_limite_inferior(inicio_mes),
            fecha__lt=_limite_inferior(inicio_mes_siguiente),
        ).aggregate(total=Sum("total"))["total"]
        return total or 0

    @staticmethod
    def cantidad_ventas_del_dia():
        hoy = timezone.localdate()
        return Venta.objects.filter(
            estado=True,
            fecha__gte=_limite_inferior(hoy),
            fecha__lt=_limite_superior(hoy),
        ).count()

    @staticmethod
    def ticket_promedio_del_dia():
        hoy = timezone.localdate()
        promedio = Venta.objects.filter(
            estado=True,
            fecha__gte=_limite_inferior(hoy),
            fecha__lt=_limite_superior(hoy),
        ).aggregate(promedio=Avg("total"))["promedio"]
        return promedio or 0

    @staticmethod
    def top_productos(limite=10, dias=30):
        desde = timezone.localdate() - timedelta(days=dias)
        return list(
            DetalleVenta.objects.filter(
                venta__estado=True, venta__fecha__gte=_limite_inferior(desde)
            )
            .values("producto__nombre")
            .annotate(cantidad_total=Sum("cantidad"))
            .order_by("-cantidad_total")[:limite]
        )

    @staticmethod
    def ventas_por_sucursal(dias=30):
        desde = timezone.localdate() - timedelta(days=dias)
        return list(
            Venta.objects.filter(estado=True, fecha__gte=_limite_inferior(desde))
            .values("caja__sucursal__nombre")
            .annotate(total=Sum("total"))
            .order_by("-total")
        )