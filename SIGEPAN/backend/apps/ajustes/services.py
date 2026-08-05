from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventario.models import TipoMovimientoInventario
from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService

from .models import Ajuste
from .repositories import AjusteRepository


class AjusteService:
    """
    Reglas de negocio del módulo Ajustes (RF-018).

    Un ajuste de tipo ENTRADA incrementa el stock (tipo de movimiento
    AJUSTE_POSITIVO); uno de tipo SALIDA lo reduce (AJUSTE_NEGATIVO) y
    respeta la misma regla de "no dejar stock negativo" que ya aplica
    MovimientoInventarioService en el resto del sistema.
    """

    _TIPO_A_MOVIMIENTO = {
        Ajuste.Tipo.ENTRADA: "AJUSTE_POSITIVO",
        Ajuste.Tipo.SALIDA: "AJUSTE_NEGATIVO",
    }

    @staticmethod
    def listar():
        return AjusteRepository.listar()

    @staticmethod
    def obtener(id_ajuste):
        return AjusteRepository.obtener(id_ajuste)

    @staticmethod
    def filtrar(id_producto=None, tipo=None, desde=None, hasta=None):
        return AjusteRepository.filtrar(id_producto, tipo, desde, hasta)

    @staticmethod
    @transaction.atomic
    def registrar(producto, usuario, cantidad, tipo, motivo, fecha, observaciones=None):
        """
        Registra un ajuste de inventario (entrada o salida) y actualiza el
        stock correspondiente a través de MovimientoInventarioService.
        """

        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad del ajuste debe ser mayor a cero.")

        if tipo not in Ajuste.Tipo.values:
            raise ValidationError("El tipo de ajuste no es válido.")

        if not usuario.id_sucursal:
            raise ValidationError(
                "El usuario no tiene una sucursal asignada; no se puede "
                "determinar de qué inventario ajustar el stock."
            )

        nombre_tipo_movimiento = AjusteService._TIPO_A_MOVIMIENTO[tipo]

        try:
            tipo_movimiento = TipoMovimientoInventario.objects.get(
                nombre=nombre_tipo_movimiento
            )
        except TipoMovimientoInventario.DoesNotExist:
            raise ValidationError(
                f"Falta configurar el tipo de movimiento "
                f"'{nombre_tipo_movimiento}' en Inventario. "
                f"Ejecute: python manage.py seed_tipos_movimiento"
            )

        if tipo == Ajuste.Tipo.SALIDA:
            # No se puede sacar stock de un inventario que no existe.
            inventario = InventarioRepository.obtener_para_actualizar(
                producto, usuario.id_sucursal
            )
            if not inventario:
                raise ValidationError(
                    f"El producto {producto.nombre} no está habilitado en "
                    f"el inventario de esta sucursal."
                )
        else:
            # Una entrada de ajuste sí puede crear el registro de
            # inventario si todavía no existía (corrige una omisión).
            inventario = InventarioRepository.obtener_o_crear(
                producto, usuario.id_sucursal
            )

        MovimientoInventarioService.registrar_movimiento(
            inventario=inventario,
            tipo_movimiento=tipo_movimiento,
            usuario=usuario,
            cantidad=cantidad,
            observaciones=f"Ajuste ({tipo}): {motivo}",
        )

        return AjusteRepository.crear(
            producto=producto,
            usuario=usuario,
            cantidad=cantidad,
            tipo=tipo,
            motivo=motivo,
            fecha=fecha,
            observaciones=observaciones,
        )
