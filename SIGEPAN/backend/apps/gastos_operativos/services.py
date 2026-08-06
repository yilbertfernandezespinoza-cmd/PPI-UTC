from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.caja.models import AperturaCaja, MovimientoCaja

from .repositories import GastoOperativoRepository


class GastoOperativoService:
    """
    Reglas de negocio del módulo Gastos Operativos (RF-026).

    Si el usuario tiene una caja abierta al momento de registrar el
    gasto, se vincula automáticamente a esa caja Y se crea un
    MovimientoCaja tipo "GASTO" — ese tipo ya existe en el catálogo de
    caja (caja/models.py) y calcular_saldo_sistema() en caja/utils.py ya
    lo resta del saldo, así que el gasto queda reflejado en el saldo real
    de la caja en vez de ser un registro aislado.

    Si no hay caja abierta (por ejemplo, un gasto administrativo como el
    alquiler, registrado fuera del turno de un cajero), el gasto se
    guarda igual, sin caja asociada — la columna id_caja es NULL en la
    base de datos precisamente para permitir este caso.
    """

    @staticmethod
    def listar():
        return GastoOperativoRepository.listar()

    @staticmethod
    def obtener(id_gasto):
        return GastoOperativoRepository.obtener(id_gasto)

    @staticmethod
    def filtrar(id_sucursal=None, categoria=None, desde=None, hasta=None):
        return GastoOperativoRepository.filtrar(id_sucursal, categoria, desde, hasta)

    @staticmethod
    @transaction.atomic
    def registrar(
        usuario,
        descripcion,
        categoria,
        monto,
        fecha_gasto,
        observaciones=None,
        comprobante=None,
    ):
        if monto is None or monto <= 0:
            raise ValidationError("El monto del gasto debe ser mayor a cero.")

        if not usuario.id_sucursal:
            raise ValidationError(
                "El usuario no tiene una sucursal asignada; no se puede "
                "registrar el gasto."
            )

        apertura = (
            AperturaCaja.objects
            .filter(usuario=usuario, estado=True)
            .select_related("caja")
            .first()
        )

        gasto = GastoOperativoRepository.crear(
            sucursal=usuario.id_sucursal,
            usuario=usuario,
            caja=apertura.caja if apertura else None,
            descripcion=descripcion,
            categoria=categoria,
            monto=monto,
            fecha_gasto=fecha_gasto,
            observaciones=observaciones,
            # `comprobante` ya viene resuelto como ruta (string) o None
            # desde la vista (ver _resolver_ruta_comprobante) — el Service
            # no maneja archivos directamente, igual que el resto del
            # patrón de Ayuda/Productos.
            comprobante=comprobante,
        )

        if apertura:
            MovimientoCaja.objects.create(
                apertura=apertura,
                usuario=usuario,
                tipo_movimiento="GASTO",
                monto=monto,
                descripcion=f"Gasto operativo: {categoria} — {descripcion}",
                fecha_movimiento=timezone.now(),
                fecha_creacion=timezone.now(),
            )

        return gasto

    @staticmethod
    def cambiar_estado(id_gasto):
        """
        Activa/desactiva un gasto operativo (no lo borra, igual que el
        resto de módulos con BaseModel). No revierte el MovimientoCaja
        que ya se haya generado — deshabilitar un gasto es una corrección
        administrativa del registro, no una anulación contable
        automática; si se requiere revertir el efecto en caja, se hace
        con un movimiento de caja de tipo INGRESO por separado, dejando
        rastro de ambos movimientos.
        """

        gasto = GastoOperativoRepository.obtener(id_gasto)

        gasto.estado = not gasto.estado

        return GastoOperativoRepository.actualizar(gasto)
