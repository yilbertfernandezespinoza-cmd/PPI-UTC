from django.core.management.base import BaseCommand

from apps.configuracion.models import MetodoPago


class Command(BaseCommand):
    """
    Siembra (idempotente) el catálogo base de métodos de pago que el POS
    de Ventas necesita para funcionar (RF-012/RF-013).

    Contexto del bug que motivó este comando: el POS (crear_venta.html +
    venta_pos.js) tenía 4 checkboxes de pago fijos que enviaban códigos de
    texto ("EFECTIVO", "TARJETA", "SINPE", "TRANSFERENCIA") como si fueran
    el id de MetodoPago — pero DetallePago.metodo_pago es una FK real y
    obligatoria a la tabla metodo_pago, así que esos valores nunca
    validaban y la venta jamás se guardaba (sin ningún mensaje de error
    visible). Se corrigió el formulario para que los checkboxes salgan del
    catálogo real de MetodoPago; este comando asegura que ese catálogo
    tenga, como mínimo, las opciones que un POS de panadería necesita.

    No borra ni modifica métodos de pago existentes — solo agrega los que
    falten, con get_or_create. Si ya tienes tus propios métodos de pago
    cargados (por ejemplo desde Configuración > Métodos de Pago), este
    comando no los toca.

    Uso:
        python manage.py seed_metodos_pago
    """

    help = (
        "Crea el catálogo base de métodos de pago (Efectivo, Tarjeta, "
        "SINPE Móvil, Transferencia) si todavía no existen."
    )

    METODOS = [
        ("Efectivo", "Pago en efectivo"),
        ("Tarjeta", "Pago con tarjeta de crédito o débito"),
        ("SINPE Móvil", "Pago mediante SINPE Móvil"),
        ("Transferencia", "Transferencia bancaria"),
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for nombre, descripcion in self.METODOS:
            metodo, creado = MetodoPago.objects.get_or_create(
                nombre__iexact=nombre,
                defaults={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "estado": True,
                },
            )

            if creado:
                creados += 1
                self.stdout.write(f"  + creado: {nombre}")
            else:
                existentes += 1
                self.stdout.write(f"  = ya existía: {metodo.nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo. {creados} método(s) nuevos, {existentes} ya existían."
            )
        )
