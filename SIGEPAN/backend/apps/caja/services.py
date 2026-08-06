# Servicios del módulo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ArqueoCaja, CierreCaja
from .utils import calcular_saldo_sistema


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
