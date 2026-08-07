from django.db import transaction

from .models import Ajuste


def generar_folio_ajuste():
    """
    Genera el próximo folio consecutivo de ajuste (AJ000001, AJ000002, ...).

    Mismo patrón que `apps.ventas.utils.generar_numero_venta`: debe
    llamarse dentro de una transacción (AjusteService.registrar ya está
    envuelto en @transaction.atomic). select_for_update() bloquea la fila
    del último ajuste hasta que esa transacción termine, evitando que dos
    registros simultáneos calculen el mismo folio.
    """

    with transaction.atomic():

        ultimo_ajuste = (
            Ajuste.objects
            .select_for_update()
            .order_by("-id_ajuste")
            .first()
        )

        if ultimo_ajuste:
            numero = ultimo_ajuste.id_ajuste + 1
        else:
            numero = 1

        return f"AJ{numero:06d}"
