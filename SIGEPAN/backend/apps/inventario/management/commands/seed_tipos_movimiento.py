from django.core.management.base import BaseCommand

from apps.inventario.models import TipoMovimientoInventario


class Command(BaseCommand):
    """
    Siembra (idempotente) el catálogo de tipos de movimiento de inventario
    que ya usa MovimientoInventarioService (TIPOS_ENTRADA / TIPOS_SALIDA).

    Es seguro ejecutarlo varias veces: usa get_or_create, no borra ni
    modifica registros existentes, y no toca ninguna otra tabla. No
    reemplaza al flujo Database First del proyecto (no crea la tabla,
    solo agrega filas de catálogo a una tabla que ya existe).

    Uso:
        python manage.py seed_tipos_movimiento
    """

    help = (
        "Crea los tipos de movimiento de inventario estándar "
        "(ENTRADA_COMPRA, SALIDA_VENTA, DEVOLUCION_VENTA, DEVOLUCION_COMPRA, "
        "AJUSTE_POSITIVO, AJUSTE_NEGATIVO, TRASLADO_ENTRADA, TRASLADO_SALIDA, "
        "MERMA) si todavía no existen en la base de datos."
    )

    TIPOS = [
        ("ENTRADA_COMPRA", "Entrada de inventario por compra a proveedor"),
        ("SALIDA_VENTA", "Salida de inventario por venta a cliente"),
        ("DEVOLUCION_VENTA", "Reingreso de inventario por anulación de venta"),
        ("DEVOLUCION_COMPRA", "Salida de inventario por anulación de compra"),
        ("AJUSTE_POSITIVO", "Ajuste manual que incrementa el stock"),
        ("AJUSTE_NEGATIVO", "Ajuste manual que reduce el stock"),
        ("TRASLADO_ENTRADA", "Entrada de inventario por traslado entre sucursales"),
        ("TRASLADO_SALIDA", "Salida de inventario por traslado entre sucursales"),
        # Agregado 04-08-2026 junto con el módulo de Mermas (RF-017): se
        # separa de AJUSTE_NEGATIVO a propósito para no mezclar una merma
        # (pérdida documentada: producto vencido/dañado) con un ajuste
        # manual de conteo — son eventos de negocio distintos aunque
        # ambos reduzcan stock.
        ("MERMA", "Salida de inventario por merma (producto vencido, dañado o perdido)"),
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for nombre, descripcion in self.TIPOS:
            tipo, fue_creado = TipoMovimientoInventario.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion, "estado": True},
            )

            if fue_creado:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"  + creado: {nombre}"))
            else:
                existentes += 1
                self.stdout.write(f"  = ya existía: {nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo. {creados} tipo(s) nuevos, {existentes} ya existían."
            )
        )
