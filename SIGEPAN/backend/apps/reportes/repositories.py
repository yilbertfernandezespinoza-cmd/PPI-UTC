from django.db.models import F, Sum
from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Inventario


class ReporteRepository:

    @staticmethod
    def ventas(fecha_inicio=None, fecha_fin=None, sucursal_id=None, usuario_id=None):
        queryset = Venta.objects.filter(estado=True).select_related(
            "cliente", "usuario", "caja", "caja__sucursal", "metodo_pago"
        )

        if fecha_inicio:
            queryset = queryset.filter(fecha__date__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__date__lte=fecha_fin)

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
            queryset = queryset.filter(fecha__date__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__date__lte=fecha_fin)

        return list(
            queryset.values("metodo_pago__nombre")
            .annotate(total=Sum("total"))
            .order_by("-total")
        )

    @staticmethod
    def costos_estimados(fecha_inicio=None, fecha_fin=None):
        queryset = DetalleVenta.objects.filter(venta__estado=True)

        if fecha_inicio:
            queryset = queryset.filter(venta__fecha__date__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(venta__fecha__date__lte=fecha_fin)

        total = queryset.aggregate(
            costo=Sum(F("cantidad") * F("producto__precio_compra"))
        )["costo"]

        return total or 0