from datetime import date, timedelta
from django.db.models import Sum, Avg
from apps.ventas.models import Venta, DetalleVenta


class DashboardRepository:

    @staticmethod
    def ventas_del_dia():
        hoy = date.today()
        total = Venta.objects.filter(
            estado=True, fecha__date=hoy
        ).aggregate(total=Sum("total"))["total"]
        return total or 0

    @staticmethod
    def ventas_del_mes():
        hoy = date.today()
        total = Venta.objects.filter(
            estado=True, fecha__year=hoy.year, fecha__month=hoy.month
        ).aggregate(total=Sum("total"))["total"]
        return total or 0

    @staticmethod
    def cantidad_ventas_del_dia():
        hoy = date.today()
        return Venta.objects.filter(estado=True, fecha__date=hoy).count()

    @staticmethod
    def ticket_promedio_del_dia():
        hoy = date.today()
        promedio = Venta.objects.filter(
            estado=True, fecha__date=hoy
        ).aggregate(promedio=Avg("total"))["promedio"]
        return promedio or 0

    @staticmethod
    def top_productos(limite=10, dias=30):
        desde = date.today() - timedelta(days=dias)
        return list(
            DetalleVenta.objects.filter(
                venta__estado=True, venta__fecha__date__gte=desde
            )
            .values("producto__nombre")
            .annotate(cantidad_total=Sum("cantidad"))
            .order_by("-cantidad_total")[:limite]
        )

    @staticmethod
    def ventas_por_sucursal(dias=30):
        desde = date.today() - timedelta(days=dias)
        return list(
            Venta.objects.filter(estado=True, fecha__date__gte=desde)
            .values("caja__sucursal__nombre")
            .annotate(total=Sum("total"))
            .order_by("-total")
        )