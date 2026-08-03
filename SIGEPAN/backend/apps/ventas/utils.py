from .models import Venta


def generar_numero_venta():

    ultima_venta = (
        Venta.objects
        .order_by("-id_venta")
        .first()
    )


    if ultima_venta:

        numero = ultima_venta.id_venta + 1

    else:

        numero = 1


    return f"V{numero:06d}"