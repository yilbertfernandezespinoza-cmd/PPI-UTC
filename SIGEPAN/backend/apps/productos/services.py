# Servicios del módulo
from decimal import Decimal, ROUND_HALF_UP


class ProductoService:

    @staticmethod
    def calcular_precio_venta(precio_compra, porcentaje_utilidad, porcentaje_impuesto):
        """
        Calcula el precio de venta a partir del precio de compra,
        el porcentaje de utilidad y el porcentaje de impuesto.

        precio_con_utilidad = precio_compra * (1 + utilidad / 100)
        precio_venta = precio_con_utilidad * (1 + impuesto / 100)
        """

        precio_compra = Decimal(precio_compra or 0)
        porcentaje_utilidad = Decimal(porcentaje_utilidad or 0)
        porcentaje_impuesto = Decimal(porcentaje_impuesto or 0)

        precio_con_utilidad = precio_compra * (
            Decimal("1") + (porcentaje_utilidad / Decimal("100"))
        )

        precio_venta = precio_con_utilidad * (
            Decimal("1") + (porcentaje_impuesto / Decimal("100"))
        )

        return precio_venta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)