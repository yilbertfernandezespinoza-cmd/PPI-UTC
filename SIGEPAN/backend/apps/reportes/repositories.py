from datetime import datetime, timedelta

from django.db.models import F, Sum
from django.utils import timezone

from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Inventario


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha`.

    Se usa en vez de filtrar con `fecha__date=`/`fecha__date__gte=` sobre un
    DateTimeField: con USE_TZ=True, ese lookup le pide a MySQL convertir el
    valor guardado (UTC) a la zona horaria activa vía CONVERT_TZ(), función
    que devuelve NULL en silencio (sin error) si las tablas de zonas
    horarias de MySQL no están cargadas (`mysql_tzinfo_to_sql`) — el filtro
    entonces no encuentra nada, sin avisar por qué. Calculando el límite del
    día en Python y comparando con >=/< se evita depender de CONVERT_TZ.

    Corregido (07-08): mismo bug encontrado y corregido en mermas/ajustes/
    gastos_operativos — `fecha` llega como string crudo desde
    `request.GET.get("fecha_inicio"/"fecha_fin")` (views.py de este mismo
    módulo), nunca se convertía a `date` antes de llegar aquí, y
    `datetime.combine()` exige un `date`, no un `str`. Afecta Reporte de
    Ventas, Reporte Tributario y Reporte de Utilidad en cuanto se aplica
    cualquier filtro de fecha — se corrige aquí también para no dejar la
    misma trampa activa en un módulo de Yilbert.
    """
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


class ReporteRepository:

    @staticmethod
    def ventas(fecha_inicio=None, fecha_fin=None, sucursal_id=None, usuario_id=None):
        queryset = Venta.objects.filter(estado=True).select_related(
            "cliente", "usuario", "caja", "caja__sucursal", "metodo_pago"
        )

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=_limite_inferior(fecha_inicio))

        if fecha_fin:
            queryset = queryset.filter(fecha__lt=_limite_superior(fecha_fin))

        if sucursal_id:
            queryset = queryset.filter(caja__sucursal_id=sucursal_id)

        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        return queryset.order_by("-fecha")

    @staticmethod
    def inventario(sucursal_id=None, solo_bajo_minimo=False):
        queryset = Inventario.objects.filter(estado=True).select_related(
            "id_producto", "id_sucursal"
        )

        if sucursal_id:
            queryset = queryset.filter(id_sucursal_id=sucursal_id)

        if solo_bajo_minimo:
            queryset = queryset.filter(stock_actual__lte=F("stock_minimo"))

        return queryset.order_by("id_sucursal__nombre", "id_producto__nombre")

    @staticmethod
    def ventas_por_metodo_pago(fecha_inicio=None, fecha_fin=None):
        queryset = Venta.objects.filter(estado=True)

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=_limite_inferior(fecha_inicio))

        if fecha_fin:
            queryset = queryset.filter(fecha__lt=_limite_superior(fecha_fin))

        return list(
            queryset.values("metodo_pago__nombre")
            .annotate(total=Sum("total"))
            .order_by("-total")
        )

    @staticmethod
    def costos_estimados(fecha_inicio=None, fecha_fin=None):
        queryset = DetalleVenta.objects.filter(venta__estado=True)

        if fecha_inicio:
            queryset = queryset.filter(venta__fecha__gte=_limite_inferior(fecha_inicio))

        if fecha_fin:
            queryset = queryset.filter(venta__fecha__lt=_limite_superior(fecha_fin))

        total = queryset.aggregate(
            costo=Sum(F("cantidad") * F("producto__precio_compra"))
        )["costo"]

        return total or 0