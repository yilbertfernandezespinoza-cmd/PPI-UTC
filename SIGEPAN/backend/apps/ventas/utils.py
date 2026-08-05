from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from .models import Venta


def generar_numero_venta():
    """
    Genera el próximo número de venta consecutivo (V000001, V000002, ...).

    Debe llamarse siempre dentro de una transacción (procesar_venta ya está
    envuelta en @transaction.atomic). select_for_update() bloquea la fila
    de la última venta hasta que esa transacción termine (commit/rollback):
    si dos cobros llegan al mismo tiempo, el segundo espera a que el
    primero guarde su venta antes de leer "la última venta", evitando que
    ambos calculen el mismo número y choquen contra el UNIQUE de
    numero_venta.
    """

    with transaction.atomic():

        ultima_venta = (
            Venta.objects
            .select_for_update()
            .order_by("-id_venta")
            .first()
        )

        if ultima_venta:

            numero = ultima_venta.id_venta + 1

        else:

            numero = 1

        return f"V{numero:06d}"


def calcular_impuesto_ventas(subtotal):
    """
    Calcula el impuesto aplicable a una venta a partir de las tasas
    activas configuradas en ConfiguracionTributaria (aplica_ventas=True).

    Es la única fuente de verdad del cálculo de impuesto en el backend:
    el valor que el POS muestra en pantalla (JS) es solo un estimado
    visual para el cajero, nunca se recibe ni se confía en él desde el
    navegador para calcular el total real que se guarda en la venta.

    Si no hay ninguna tasa activa configurada, el impuesto es 0.00 en
    vez de fallar — una venta debe poder completarse aunque todavía no
    se haya configurado la tasa de impuesto del negocio.
    """

    # Import local para evitar dependencia circular a nivel de módulo
    # entre configuracion y ventas.
    from apps.configuracion.models import ConfiguracionTributaria

    if not subtotal:
        return Decimal("0.00")

    tasas_activas = ConfiguracionTributaria.objects.filter(
        estado=True,
        aplica_ventas=True,
    )

    impuesto = Decimal("0.00")

    for tasa in tasas_activas:
        impuesto += subtotal * (tasa.porcentaje / Decimal("100"))

    return impuesto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def determinar_metodo_pago_venta(pagos_temp):
    """
    Determina el método de pago "principal" de la venta (campo venta.metodo_pago)
    a partir de las líneas de DetallePago ya validadas.

    Existe porque la columna id_metodo_pago de la tabla venta es NOT NULL en la
    base de datos real, pero el formulario del POS (crear_venta.html) no la
    expone — solo captura los métodos de pago por línea (DetallePago, que sí
    soporta pago mixto). En vez de dejar ese campo sin asignar (lo que produce
    IntegrityError al guardar), se deriva de forma coherente con esas líneas:

    - Un solo método de pago  -> se usa ese mismo método.
    - Varios métodos (pago mixto) -> catálogo "Mixto" (se crea una sola vez,
      mismo patrón ya usado en este módulo para el método "Pendiente" de
      guardar_venta_pendiente).
    - Sin pagos (caso extremo, venta en 0) -> catálogo "Pendiente".
    """

    from apps.configuracion.models import MetodoPago

    if len(pagos_temp) == 1:
        return pagos_temp[0].metodo_pago

    if len(pagos_temp) > 1:
        metodo_mixto, _ = MetodoPago.objects.get_or_create(
            nombre__iexact="Mixto",
            defaults={"nombre": "Mixto"},
        )
        return metodo_mixto

    metodo_pendiente, _ = MetodoPago.objects.get_or_create(
        nombre__iexact="Pendiente",
        defaults={"nombre": "Pendiente"},
    )
    return metodo_pendiente