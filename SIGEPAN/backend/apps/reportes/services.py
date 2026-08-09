from datetime import datetime

from apps.mermas.repositories import MermaRepository

from .repositories import ReporteRepository


class ReporteService:

    @staticmethod
    def _parse_fecha(valor):
        if not valor:
            return None
        return datetime.strptime(valor, "%Y-%m-%d").date()

    @staticmethod
    def reporte_ventas(fecha_inicio="", fecha_fin="", sucursal_id="", usuario_id=""):
        queryset = ReporteRepository.ventas(
            fecha_inicio=ReporteService._parse_fecha(fecha_inicio),
            fecha_fin=ReporteService._parse_fecha(fecha_fin),
            sucursal_id=sucursal_id or None,
            usuario_id=usuario_id or None,
        )
        total = sum((v.total for v in queryset), start=0)
        return queryset, total

    @staticmethod
    def reporte_inventario(sucursal_id="", solo_bajo_minimo=False):
        return ReporteRepository.inventario(
            sucursal_id=sucursal_id or None,
            solo_bajo_minimo=solo_bajo_minimo,
        )

    @staticmethod
    def reporte_tributario(fecha_inicio="", fecha_fin=""):
        _, total_ventas = ReporteService.reporte_ventas(fecha_inicio, fecha_fin)
        por_metodo = ReporteRepository.ventas_por_metodo_pago(
            fecha_inicio=ReporteService._parse_fecha(fecha_inicio),
            fecha_fin=ReporteService._parse_fecha(fecha_fin),
        )
        return total_ventas, por_metodo

    @staticmethod
    def reporte_utilidad(fecha_inicio="", fecha_fin=""):
        _, total_ventas = ReporteService.reporte_ventas(fecha_inicio, fecha_fin)
        costos = ReporteRepository.costos_estimados(
            fecha_inicio=ReporteService._parse_fecha(fecha_inicio),
            fecha_fin=ReporteService._parse_fecha(fecha_fin),
        )
        utilidad = total_ventas - costos
        return total_ventas, costos, utilidad

    @staticmethod
    def reporte_mermas(fecha_inicio="", fecha_fin="", id_producto=""):
        """
        RF-017: reporte dedicado de mermas, reutilizando el mismo
        `MermaRepository.filtrar()` que ya usa el listado del módulo
        Mermas (ya corregido para recibir fechas como string "YYYY-MM-DD").
        """
        queryset = MermaRepository.filtrar(
            id_producto=id_producto or None,
            desde=fecha_inicio or None,
            hasta=fecha_fin or None,
        )
        total_unidades = sum((m.cantidad for m in queryset), start=0)
        return queryset, total_unidades