from django.core.management.base import BaseCommand

from apps.proveedores.models import Proveedor


class Command(BaseCommand):
    """
    Siembra (idempotente) un catálogo de proveedores de demostración,
    con la misma temática de panadería que ya usan seed_productos_demo y
    seed_clientes_demo: insumos típicos de una panadería (harinas y
    granos, lácteos, huevos, azúcar/saborizantes, café en grano y
    empaques), para que Compras (RF-030) tenga con quién registrar
    compras de prueba.

    Proveedores.models.Proveedor no tiene una capa de servicio propia
    todavía (apps/proveedores/services.py está vacío) — a diferencia de
    seed_clientes_demo, este comando usa el ORM directo con
    get_or_create, igual que ya hace seed_productos_demo con Inventario.
    Es seguro ejecutarlo varias veces: no duplica ni modifica proveedores
    ya existentes.

    Uso:
        python manage.py seed_proveedores_demo
    """

    help = (
        "Crea 6 proveedores de ejemplo (insumos de panadería) si "
        "todavía no existen."
    )

    PROVEEDORES = [
        {
            "identificacion": "3101112233",
            "nombre": "Molinos de Costa Rica S.A.",
            "contacto": "Luis Chacón Alvarado",
            "telefono": "2233-4455",
            "correo": "ventas@molinoscr.example.com",
            "direccion": "Zona Industrial de Pavas, San José",
        },
        {
            "identificacion": "3101223344",
            "nombre": "Lácteos La Vaquita S.A.",
            "contacto": "Marcela Hidalgo Rojas",
            "telefono": "2244-5566",
            "correo": "pedidos@lavaquita.example.com",
            "direccion": "Zarcero, Alajuela",
        },
        {
            "identificacion": "3101334455",
            "nombre": "Huevos Frescos del Valle",
            "contacto": "Esteban Solís Vindas",
            "telefono": "2255-6677",
            "correo": "contacto@huevosdelvalle.example.com",
            "direccion": "Ochomogo, Cartago",
        },
        {
            "identificacion": "3101445566",
            "nombre": "Azúcar y Endulzantes Tropical S.A.",
            "contacto": "Diego Araya Méndez",
            "telefono": "2266-7788",
            "correo": "comercial@endulzantestropical.example.com",
            "direccion": "San Rafael de Alajuela",
        },
        {
            "identificacion": "3101556677",
            "nombre": "Café Volcán Barva S.A.",
            "contacto": "Kattia Núñez Brenes",
            "telefono": "2277-8899",
            "correo": "ventas@volcanbarva.example.com",
            "direccion": "Barva, Heredia",
        },
        {
            "identificacion": "3101667788",
            "nombre": "Distribuidora de Empaques CR",
            "contacto": "Randall Ugalde Porras",
            "telefono": "2288-9900",
            "correo": "info@empaquescr.example.com",
            "direccion": "La Uruca, San José",
        },
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for datos in self.PROVEEDORES:
            proveedor, creado = Proveedor.objects.get_or_create(
                identificacion=datos["identificacion"],
                defaults={
                    "nombre": datos["nombre"],
                    "contacto": datos["contacto"],
                    "telefono": datos["telefono"],
                    "correo": datos["correo"],
                    "direccion": datos["direccion"],
                    "estado": True,
                },
            )

            if creado:
                creados += 1
                self.stdout.write(f"  + creado: {proveedor.nombre}")
            else:
                existentes += 1
                self.stdout.write(f"  = ya existía: {proveedor.nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo. {creados} proveedor(es) nuevos, {existentes} ya existían."
            )
        )
