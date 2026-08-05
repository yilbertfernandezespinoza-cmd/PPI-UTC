from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventario.models import TipoMovimientoInventario
from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService

from .repositories import MermaRepository


class MermaService:
    """
    Reglas de negocio del módulo Mermas (RF-017).

    Registrar una merma SIEMPRE descuenta stock a través de
    MovimientoInventarioService (tipo "MERMA") — nunca se guarda la merma
    sin afectar el inventario real, para no volver a caer en el patrón que
    la auditoría señaló en ventas/compras (movimientos "de papel" que no
    coinciden con el stock real).
    """

    @staticmethod
    def listar():
        return MermaRepository.listar()

    @staticmethod
    def obtener(id_merma):
        return MermaRepository.obtener(id_merma)

    @staticmethod
    def filtrar(id_producto=None, desde=None, hasta=None):
        return MermaRepository.filtrar(id_producto, desde, hasta)

    @staticmethod
    @transaction.atomic
    def registrar(producto, usuario, cantidad, motivo, fecha, observaciones=None):
        """
        Registra una merma y descuenta el stock correspondiente.

        La sucursal se toma del usuario que registra la merma (mismo
        criterio ya usado en compras: usuario.id_sucursal), porque la
        tabla `merma` no tiene columna de sucursal propia.
        """

        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad de la merma debe ser mayor a cero.")

        if not usuario.id_sucursal:
            raise ValidationError(
                "El usuario no tiene una sucursal asignada; no se puede "
                "determinar de qué inventario descontar la merma."
            )

        inventario = InventarioRepository.obtener_para_actualizar(
            producto, usuario.id_sucursal
        )

        if not inventario:
            raise ValidationError(
                f"El producto {producto.nombre} no está habilitado en el "
                f"inventario de esta sucursal."
            )

        try:
            tipo_merma = TipoMovimientoInventario.objects.get(nombre="MERMA")
        except TipoMovimientoInventario.DoesNotExist:
            raise ValidationError(
                "Falta configurar el tipo de movimiento 'MERMA' en Inventario. "
                "Ejecute: python manage.py seed_tipos_movimiento"
            )

        # Descuenta el stock y deja rastro en movimiento_inventario.
        MovimientoInventarioService.registrar_movimiento(
            inventario=inventario,
            tipo_movimiento=tipo_merma,
            usuario=usuario,
            cantidad=cantidad,
            observaciones=f"Merma: {motivo}",
        )

        return MermaRepository.crear(
            producto=producto,
            usuario=usuario,
            cantidad=cantidad,
            motivo=motivo,
            fecha=fecha,
            observaciones=observaciones,
        )
