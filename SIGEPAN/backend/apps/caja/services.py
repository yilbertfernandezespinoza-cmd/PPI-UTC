# Servicios del módulo

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ArqueoCaja, CierreCaja
from .repositories import CajaRepository, HistorialCajaRepository
from .utils import calcular_saldo_sistema


# =====================================================
# CAJA
# =====================================================

class CajaService:
    """
    Reglas de negocio de Caja (RF-014).

    Agregado 07-08 (hallazgo de auditoría): extrae a esta capa las
    mutaciones que antes vivían directo en views.py (crear_caja,
    activar_caja, desactivar_caja), sin cambiar ningún texto de mensaje
    ni ninguna validación — solo centraliza la lógica, igual que ya
    hacía `CierreCajaService` para RF-015.
    """

    @staticmethod
    def crear(caja_sin_guardar):
        """Recibe la instancia de `CajaForm.save(commit=False)`, inicializa
        los campos legacy `saldo_inicial`/`saldo_actual` en 0 (igual que
        hacía la vista) y guarda."""
        caja = caja_sin_guardar
        caja.saldo_inicial = Decimal("0.00")
        caja.saldo_actual = Decimal("0.00")
        caja.save()
        return caja

    @staticmethod
    def activar(caja):
        caja.estado = True
        caja.save()
        return caja

    @staticmethod
    def desactivar(caja):
        """Levanta ValidationError si la caja tiene una apertura activa —
        mismo texto que ya mostraba la vista."""
        if CajaRepository.tiene_apertura_activa(caja):
            raise ValidationError(
                "No se puede desactivar una caja con una apertura activa. "
                "Debe cerrar caja primero."
            )

        caja.estado = False
        caja.save()
        return caja


# =====================================================
# APERTURA DE CAJA
# =====================================================

class AperturaCajaService:
    """Reglas de negocio de Apertura de Caja (RF-014). Agregado 07-08."""

    @staticmethod
    def abrir(caja, apertura_sin_guardar, usuario):
        """Levanta ValidationError si la caja ya tiene una apertura activa
        — mismo texto que ya mostraba la vista."""
        if CajaRepository.tiene_apertura_activa(caja):
            raise ValidationError("La caja ya tiene una apertura activa.")

        apertura = apertura_sin_guardar
        apertura.caja = caja
        apertura.fecha_apertura = timezone.now()
        apertura.estado = True
        apertura.usuario = usuario
        apertura.save()
        return apertura

    @staticmethod
    def editar(apertura_sin_guardar, monto_anterior, usuario):
        """Guarda la apertura y, si el monto inicial cambió, deja
        constancia en HistorialCaja — misma condición y mismo texto que
        ya usaba la vista."""
        apertura = apertura_sin_guardar
        apertura.save()

        if monto_anterior != apertura.monto_inicial:
            HistorialCajaRepository.registrar(
                caja=apertura.caja,
                usuario=usuario,
                tipo_cambio="AJUSTE_APERTURA",
                valor_anterior=monto_anterior,
                valor_nuevo=apertura.monto_inicial,
                observacion="Modificación del monto inicial de la apertura.",
            )

        return apertura


# =====================================================
# MOVIMIENTOS DE CAJA
# =====================================================

class MovimientoCajaService:
    """Reglas de negocio de Movimientos de Caja (RF-014). Agregado 07-08."""

    @staticmethod
    def registrar(apertura, movimiento_sin_guardar, usuario):
        movimiento = movimiento_sin_guardar
        movimiento.apertura = apertura
        movimiento.usuario = usuario
        movimiento.fecha_movimiento = timezone.now()
        movimiento.save()
        return movimiento


# =====================================================
# ARQUEOS DE CAJA
# =====================================================

class ArqueoCajaService:
    """Reglas de negocio de Arqueo de Caja (RF-014/015). Agregado 07-08."""

    @staticmethod
    def registrar(apertura, arqueo_sin_guardar, usuario, saldo_sistema):
        arqueo = arqueo_sin_guardar
        arqueo.apertura = apertura
        arqueo.saldo_sistema = saldo_sistema
        arqueo.diferencia = arqueo.saldo_contado - saldo_sistema
        arqueo.fecha_arqueo = timezone.now()
        arqueo.usuario = usuario
        arqueo.save()
        return arqueo


# =====================================================
# CIERRE DE CAJA
# =====================================================

class CierreCajaService:
    """
    Reglas de negocio del cierre de caja (RF-015).

    Agregado 06-08: antes toda esta lógica (incluidas las 3 validaciones
    de negocio) vivía directo en `views.py::cerrar_caja`, con cada
    validación cortando el flujo a mano con `messages.error` + `redirect`
    en vez de levantar una excepción — inconsistente con el resto del
    proyecto (ver `GastoOperativoService.registrar`, que sí usa
    `ValidationError`). Se extrae aquí para seguir ese mismo patrón: el
    Service valida y levanta `ValidationError` con el mismo texto que ya
    mostraba `messages.error`, y la vista solo necesita un
    `try/except ValidationError` para convertir eso en el mensaje al
    usuario, igual que ya hace Gastos Operativos.
    """

    @staticmethod
    def validar_puede_cerrar(apertura):
        """
        Valida las 3 condiciones que ya validaba la vista, en el mismo
        orden, con el mismo texto de error. No muta nada, solo valida.
        """

        if not apertura.estado:
            raise ValidationError("La caja ya se encuentra cerrada.")

        if CierreCaja.objects.filter(apertura=apertura).exists():
            raise ValidationError("La apertura ya posee un cierre registrado.")

        if not ArqueoCaja.objects.filter(apertura=apertura).exists():
            raise ValidationError(
                "Debe realizar al menos un arqueo antes de cerrar la caja."
            )

    @staticmethod
    @transaction.atomic
    def cerrar(apertura, usuario, monto_final, observaciones=None):
        """
        Cierra una apertura de caja: valida, calcula la diferencia contra
        el saldo del sistema, crea el CierreCaja, actualiza el saldo de
        la Caja y desactiva la AperturaCaja. Todo dentro de la misma
        transacción — si cualquier paso falla, no queda un cierre a medias.
        """

        CierreCajaService.validar_puede_cerrar(apertura)

        saldo_sistema = calcular_saldo_sistema(apertura)

        cierre = CierreCaja(
            apertura=apertura,
            usuario=usuario,
            fecha_cierre=timezone.now(),
            monto_inicial=apertura.monto_inicial,
            monto_final=monto_final,
            diferencia=monto_final - saldo_sistema,
            observaciones=observaciones,
            fecha_creacion=timezone.now(),
        )
        cierre.save()

        apertura.caja.saldo_actual = monto_final
        apertura.caja.save()

        apertura.estado = False
        apertura.save()

        return cierre, saldo_sistema
