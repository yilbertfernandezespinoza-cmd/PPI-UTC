# Repositorios del módulo

from apps.inventario.models import TipoMovimientoInventario

from .models import (
    Compra,
    DetalleCompra,
)


class CompraRepository:
    """
    Repositorio para el acceso a datos del módulo Compras.

    Además de las tablas propias (compra, detalle_compra), expone una
    consulta de solo lectura sobre TipoMovimientoInventario (catálogo de
    Inventario) porque CompraService la necesita para registrar los
    movimientos de entrada/devolución de cada compra — mismo criterio que
    VentaRepository.tipo_movimiento_inventario.
    """

    # ---------------------------------------------------
    # Compra
    # ---------------------------------------------------

    @staticmethod
    def listar():
        """Todas las compras, de la más reciente a la más antigua (listado
        principal del módulo)."""
        return Compra.objects.all().order_by("-fecha")

    @staticmethod
    def guardar(compra, update_fields=None):
        """
        Persiste (crea o actualiza) una compra. Acepta update_fields para
        el guardado parcial del total, una vez calculado a partir de los
        detalles (ver CompraService.crear_compra: la compra se guarda
        primero con total en 0 y se actualiza solo esa columna al final,
        igual que hacía la vista antes de esta extracción).
        """
        if update_fields:
            compra.save(update_fields=update_fields)
        else:
            compra.save()
        return compra

    # ---------------------------------------------------
    # DetalleCompra
    # ---------------------------------------------------

    @staticmethod
    def detalles(compra):
        return DetalleCompra.objects.filter(compra=compra)

    @staticmethod
    def guardar_detalle(detalle):
        """Persiste (crea o actualiza) un detalle de compra."""
        detalle.save()
        return detalle

    # ---------------------------------------------------
    # Catálogos y consultas auxiliares (otras apps)
    # ---------------------------------------------------

    @staticmethod
    def tipo_movimiento_inventario(nombre):
        """
        Tipo de movimiento de inventario por nombre (p. ej.
        'ENTRADA_COMPRA', 'DEVOLUCION_COMPRA'). Devuelve None si el
        catálogo todavía no fue sembrado (seed_tipos_movimiento) en vez de
        lanzar DoesNotExist -- es CompraService quien decide cómo reportar
        el catálogo faltante, igual que VentaRepository.tipo_movimiento_inventario.
        """
        return TipoMovimientoInventario.objects.filter(nombre=nombre).first()
