from django.core.management.base import BaseCommand
from django.db.models import Max
from django.utils import timezone

from apps.configuracion.models import Modulo
from apps.security.models import Permiso, Rol, RolPermiso


class Command(BaseCommand):
    """
    Siembra (idempotente) los módulos, permisos y asignaciones de rol
    para las apps nuevas: Mermas (RF-017), Ajustes (RF-018) y Gastos
    Operativos (RF-026).

    Es el mismo tipo de paso que ya se hizo "a mano" por shell de Django
    para el módulo Reportes (ver CHECKLIST_YILBERT.md, 03-08) — aquí queda
    como comando reutilizable en vez de instrucciones sueltas, para que
    sea reproducible en cualquier entorno (desarrollo, entrega, otra
    máquina) sin tener que recordar los pasos exactos.

    No borra ni modifica módulos/permisos/roles existentes — solo agrega
    lo que falte, con get_or_create.

    También incluye "Inventario", que ya existe como módulo (lo usan
    EntradaInventarioView/MovimientosInventarioListView con las acciones
    CONSULTAR/CREAR desde antes) — se agrega aquí únicamente para
    garantizar que exista el permiso MODIFICAR, requerido por el fix de
    seguridad de editar_inventario (auditoría 04-08-2026: esa vista no
    tenía ningún control de permisos). Como todo se hace con
    get_or_create, correr este comando NO toca ni duplica los permisos
    CONSULTAR/CREAR de Inventario que ya existían.

    Uso:
        python manage.py seed_permisos_modulos
    """

    help = (
        "Crea los módulos, permisos y asignaciones de rol para Mermas, "
        "Ajustes, Gastos Operativos e Inventario (permiso MODIFICAR), "
        "si todavía no existen."
    )

    # Acciones que cada módulo realmente usa en sus vistas — no se crean
    # permisos "por si acaso" para acciones sin una vista que los revise
    # (Mermas y Ajustes son registros históricos, sin edición ni
    # deshabilitado; Gastos Operativos sí permite deshabilitar).
    MODULOS = {
        "Mermas": {
            "descripcion": "Registro de mermas de inventario (RF-017)",
            "icono": "bi-exclamation-triangle",
            "acciones": ["CONSULTAR", "CREAR"],
        },
        "Ajustes": {
            "descripcion": "Ajustes manuales de inventario (RF-018)",
            "icono": "bi-sliders",
            "acciones": ["CONSULTAR", "CREAR"],
        },
        "Gastos Operativos": {
            "descripcion": "Registro de gastos operativos del negocio (RF-026)",
            "icono": "bi-cash-coin",
            "acciones": ["CONSULTAR", "CREAR", "ELIMINAR"],
        },
        "Inventario": {
            "descripcion": "Existencias de productos por sucursal (RF-016)",
            "icono": "bi-box-seam",
            # CONSULTAR y CREAR ya existían (usados por las vistas basadas
            # en clase de este módulo) y get_or_create simplemente las
            # va a encontrar sin tocarlas. MODIFICAR es la que falta y la
            # que necesita editar_inventario tras el fix de seguridad.
            "acciones": ["CONSULTAR", "CREAR", "MODIFICAR"],
        },
    }

    # Rol -> acciones que recibe. Administrador siempre recibe todas las
    # acciones definidas arriba para cada módulo; Supervisor solo
    # consulta y crea (mismo criterio ya usado para el módulo Reportes);
    # Cajero no recibe nada — son operaciones de back-office, no de caja.
    ROLES_CON_ACCESO_TOTAL = ["Administrador"]
    ROLES_CON_ACCESO_LIMITADO = {
        "Supervisor": ["CONSULTAR", "CREAR"],
    }

    def handle(self, *args, **options):
        # `Modulo.orden_menu` es NOT NULL y sin default en la BD real — hay
        # que calcular el siguiente valor disponible nosotros mismos antes
        # de crear cada módulo nuevo (se detectó este bug al correr el
        # comando: "Column 'orden_menu' cannot be null").
        siguiente_orden = (
            Modulo.objects.aggregate(maximo=Max("orden_menu"))["maximo"] or 0
        ) + 1

        for nombre_modulo, config in self.MODULOS.items():
            modulo, creado = self._crear_modulo(nombre_modulo, config, siguiente_orden)

            if creado:
                siguiente_orden += 1

            permisos_por_accion = self._crear_permisos(modulo, config["acciones"])
            self._asignar_roles(nombre_modulo, permisos_por_accion)

        self.stdout.write(self.style.SUCCESS("\nListo."))

    def _crear_modulo(self, nombre, config, orden_menu):
        modulo, creado = Modulo.objects.get_or_create(
            nombre=nombre,
            defaults={
                "descripcion": config["descripcion"],
                "icono": config["icono"],
                "orden_menu": orden_menu,
                "estado": True,
            },
        )
        estado = "creado" if creado else "ya existía"
        self.stdout.write(f"Módulo '{nombre}': {estado}")
        return modulo, creado

    def _crear_permisos(self, modulo, acciones):
        permisos_por_accion = {}

        for accion in acciones:
            permiso, creado = Permiso.objects.get_or_create(
                id_modulo=modulo,
                accion=accion,
                defaults={
                    "descripcion": f"{accion} sobre el módulo {modulo.nombre}",
                    "estado": True,
                },
            )
            permisos_por_accion[accion] = permiso

            estado = "creado" if creado else "ya existía"
            self.stdout.write(f"  Permiso {modulo.nombre}/{accion}: {estado}")

        return permisos_por_accion

    def _asignar_roles(self, nombre_modulo, permisos_por_accion):
        for nombre_rol in self.ROLES_CON_ACCESO_TOTAL:
            self._otorgar(nombre_rol, permisos_por_accion.values())

        for nombre_rol, acciones in self.ROLES_CON_ACCESO_LIMITADO.items():
            permisos = [
                permisos_por_accion[accion]
                for accion in acciones
                if accion in permisos_por_accion
            ]
            self._otorgar(nombre_rol, permisos)

    def _otorgar(self, nombre_rol, permisos):
        rol = Rol.objects.filter(nombre__iexact=nombre_rol).first()

        if not rol:
            self.stdout.write(
                self.style.WARNING(
                    f"  Rol '{nombre_rol}' no existe en esta base de datos; "
                    f"se omite la asignación."
                )
            )
            return

        for permiso in permisos:
            _rol_permiso, creado = RolPermiso.objects.get_or_create(
                id_rol=rol,
                id_permiso=permiso,
                defaults={"fecha_creacion": timezone.now()},
            )

            if creado:
                self.stdout.write(
                    f"    + otorgado a {rol.nombre}: "
                    f"{permiso.id_modulo.nombre}/{permiso.accion}"
                )
