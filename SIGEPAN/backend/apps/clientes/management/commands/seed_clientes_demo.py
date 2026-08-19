from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from apps.clientes.models import Cliente
from apps.clientes.services import ClienteService


class Command(BaseCommand):
    """
    Siembra (idempotente) un catálogo de clientes de demostración para
    SIGEPAN, con la misma temática de panadería que ya usa
    seed_productos_demo (productos.management.commands).

    Igual que seed_productos_demo, no es un catálogo obligatorio del
    sistema: es contenido de ejemplo para que el POS, los reportes y el
    módulo de Ventas tengan clientes reales con quienes probar el flujo
    completo (búsqueda por cédula, envío de comprobante por correo, etc.)
    sin tener que digitarlos a mano.

    Incluye 4 personas físicas y 2 personas jurídicas (empresas clientes
    frecuentes de la panadería, p. ej. un restaurante y un hotel que
    compran al por mayor), para dejar ambos tipos de cliente cubiertos
    en las pruebas.

    Usa ClienteService.crear (la misma capa de negocio que usa el
    formulario real) en vez de Cliente.objects.create directo, para que
    la siembra pase por la misma validación de identificación duplicada
    que ya aplica el sistema. Es seguro ejecutarlo varias veces: si un
    cliente con esa identificación ya existe, se omite sin duplicar ni
    modificar nada.

    Uso:
        python manage.py seed_clientes_demo
    """

    help = (
        "Crea 6 clientes de ejemplo (panadería: personas físicas y "
        "jurídicas) si todavía no existen."
    )

    CLIENTES = [
        {
            "tipo_cliente": Cliente.TipoCliente.FISICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_FISICA,
            "identificacion": "205680123",
            "nombre": "María",
            "apellido1": "Fernández",
            "apellido2": "Solano",
            "telefono": "8811-2345",
            "correo": "maria.fernandez@example.com",
            "direccion": "Barrio Escalante, San José",
        },
        {
            "tipo_cliente": Cliente.TipoCliente.FISICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_FISICA,
            "identificacion": "109870456",
            "nombre": "Carlos",
            "apellido1": "Rodríguez",
            "apellido2": "Jiménez",
            "telefono": "8822-3456",
            "correo": "carlos.rodriguez@example.com",
            "direccion": "Curridabat, San José",
        },
        {
            "tipo_cliente": Cliente.TipoCliente.FISICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_FISICA,
            "identificacion": "302450789",
            "nombre": "Ana Gabriela",
            "apellido1": "Vargas",
            "apellido2": "Mora",
            "telefono": "8833-4567",
            "correo": "ana.vargas@example.com",
            "direccion": "Heredia Centro",
        },
        {
            "tipo_cliente": Cliente.TipoCliente.FISICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_FISICA,
            "identificacion": "401230567",
            "nombre": "José",
            "apellido1": "Ramírez",
            "apellido2": "Castro",
            "telefono": "8844-5678",
            "correo": "jose.ramirez@example.com",
            "direccion": "San Pedro, Montes de Oca",
        },
        {
            "tipo_cliente": Cliente.TipoCliente.JURIDICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_JURIDICA,
            "identificacion": "3101456789",
            "nombre": "Restaurante El Fogón S.A.",
            "apellido1": None,
            "apellido2": None,
            "telefono": "2255-6677",
            "correo": "compras@elfogon.example.com",
            "direccion": "Sabana Sur, San José",
        },
        {
            "tipo_cliente": Cliente.TipoCliente.JURIDICA,
            "tipo_identificacion": Cliente.TipoIdentificacion.CEDULA_JURIDICA,
            "identificacion": "3101987654",
            "nombre": "Hotel Vista Verde S.A.",
            "apellido1": None,
            "apellido2": None,
            "telefono": "2266-7788",
            "correo": "eventos@vistaverde.example.com",
            "direccion": "Santa Ana, San José",
        },
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for datos in self.CLIENTES:
            if Cliente.objects.filter(
                identificacion=datos["identificacion"]
            ).exists():
                existentes += 1
                self.stdout.write(
                    f"  = ya existía: {datos['identificacion']} — {datos['nombre']}"
                )
                continue

            try:
                cliente = ClienteService.crear(datos)
            except ValidationError as error:
                # No debería pasar (ya se revisó arriba), pero se deja la
                # misma traducción de error que usaría la vista real por
                # si hay una condición de carrera entre el filter() y el
                # crear().
                self.stdout.write(
                    self.style.WARNING(
                        f"  ! omitido {datos['identificacion']}: "
                        f"{'; '.join(error.messages)}"
                    )
                )
                continue

            creados += 1
            self.stdout.write(
                f"  + creado: {cliente.identificacion} — {cliente.nombre_completo}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo. {creados} cliente(s) nuevos, {existentes} ya existían."
            )
        )
