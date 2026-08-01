from django.core.exceptions import ValidationError

from .repositories import (
    InventarioRepository,
    MovimientoInventarioRepository,
)

class MovimientoInventarioService:

    TIPOS_ENTRADA = {
        "ENTRADA_COMPRA",
        "AJUSTE_POSITIVO",
        "DEVOLUCION_VENTA",
        "TRASLADO_ENTRADA",
    }

    TIPOS_SALIDA = {
        "SALIDA_VENTA",
        "AJUSTE_NEGATIVO",
        "DEVOLUCION_COMPRA",
        "TRASLADO_SALIDA",
    }

    @staticmethod
    def registrar_movimiento(
        inventario,
        tipo_movimiento,
        usuario,
        cantidad,
        observaciones=None,
    ):
        """
        Registra un movimiento de inventario y actualiza el stock.
        """

        stock_anterior = inventario.stock_actual

        if tipo_movimiento.nombre in MovimientoInventarioService.TIPOS_ENTRADA:
            stock_nuevo = stock_anterior + cantidad

        elif tipo_movimiento.nombre in MovimientoInventarioService.TIPOS_SALIDA:
            stock_nuevo = stock_anterior - cantidad

            if stock_nuevo < 0:
                raise ValidationError(
                    "No hay existencias suficientes para realizar el movimiento."
                )

        else:
            raise ValidationError(
                "El tipo de movimiento no es válido."
            )

        inventario.stock_actual = stock_nuevo

        InventarioRepository.actualizar(
            inventario
        )

        return MovimientoInventarioRepository.crear(
            id_inventario=inventario,
            id_tipo_movimiento_inventario=tipo_movimiento,
            id_usuario=usuario,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            observaciones=observaciones,
        )    

    @staticmethod
    def listar():
        """
        Obtiene todos los movimientos de inventario.
        """

        return MovimientoInventarioRepository.listar()

    @staticmethod
    def listar_por_inventario(id_inventario):
        """
        Obtiene los movimientos de un inventario.
        """

        return MovimientoInventarioRepository.listar_por_inventario(
            id_inventario
        )