from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db.models import Max

from apps.configuracion.models import Modulo, Sucursal
from apps.empleados.models import Cargo, Empleado
from apps.security.models import Permiso, Rol, RolPermiso, Usuario


class Command(BaseCommand):
    """
    Agregado 07-08: preparación para instalación desde cero (Entregable 5,
    "para que el profesor también pueda instalarlo").

    El esquema en database/ddl/ crea las tablas vacías, sin datos — y
    como SIGEPAN usa un modelo de Usuario propio (no el sistema de auth
    de Django), no existe un equivalente a `createsuperuser`. Sin este
    comando, una instalación 100% nueva no tiene ninguna forma de iniciar
    sesión.

    Es idempotente (usa get_or_create en todo): correrlo varias veces no
    duplica nada ni pisa datos ya existentes. Crea, si hacen falta:
    - Una sucursal por defecto.
    - Un cargo y un empleado "administrativos" (Usuario exige id_empleado).
    - El rol "Administrador".
    - El catálogo completo de módulos/permisos que el sistema realmente
      valida en sus vistas (ver permission_module / permiso_requerido en
      apps/*/views.py) — no solo los 4 módulos nuevos que ya cubre
      `seed_permisos_modulos`.
    - Un usuario "admin" con el rol Administrador.

    Uso:
        python manage.py seed_admin
    """

    help = (
        "Crea la sucursal, rol Administrador, catálogo completo de "
        "permisos y el primer usuario admin, si todavía no existen. "
        "Necesario en cualquier instalación nueva (base de datos vacía)."
    )

    # Módulo -> acciones que el sistema realmente valida (confirmado
    # contra `permission_module=` y `permiso_requerido(...)` en las
    # vistas). El Administrador recibe siempre las 4 acciones estándar
    # por módulo — sobre-otorgar un permiso que ninguna vista todavía
    # revisa no rompe nada, y evita tener que mantener esta lista en
    # sincronía exacta con cada vista nueva.
    MODULOS = {
        "Configuración": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Categorías": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Productos": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        # OJO: el permission_module real de Clientes está en minúscula
        # ("clientes") en apps/clientes/views.py — se respeta tal cual
        # está en el código, aunque es inconsistente con el resto
        # (title case). No se corrige aquí para no cambiar comportamiento
        # existente como efecto secundario de este comando.
        "clientes": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Proveedores": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Inventario": ["CONSULTAR", "CREAR", "MODIFICAR"],
        "Compras": ["CONSULTAR", "CREAR", "ELIMINAR"],
        "Ventas": ["CONSULTAR", "CREAR", "ELIMINAR"],
        "Caja": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Reportes": ["CONSULTAR", "EXPORTAR"],
        "Seguridad": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Ayudas": ["CONSULTAR", "CREAR", "MODIFICAR", "ELIMINAR"],
        "Mermas": ["CONSULTAR", "CREAR"],
        "Ajustes": ["CONSULTAR", "CREAR"],
        "Gastos Operativos": ["CONSULTAR", "CREAR", "ELIMINAR"],
    }

    USERNAME_ADMIN = "admin"
    PASSWORD_ADMIN = "Admin123*"

    def handle(self, *args, **options):

        sucursal = self._crear_sucursal()
        empleado = self._crear_empleado()
        rol = self._crear_rol_administrador()

        siguiente_orden = (
            Modulo.objects.aggregate(maximo=Max("orden_menu"))["maximo"] or 0
        ) + 1

        for nombre_modulo, acciones in self.MODULOS.items():
            modulo, creado = self._crear_modulo(nombre_modulo, siguiente_orden)
            if creado:
                siguiente_orden += 1
            permisos = self._crear_permisos(modulo, acciones)
            self._otorgar_a_rol(rol, permisos)

        self._crear_usuario_admin(empleado, rol, sucursal)

        self.stdout.write(self.style.SUCCESS("\nListo."))

    def _crear_sucursal(self):
        sucursal, creado = Sucursal.objects.get_or_create(
            nombre="Sucursal Principal",
            defaults={"direccion": "Por definir"},
        )
        self.stdout.write(
            f"Sucursal 'Sucursal Principal': {'creada' if creado else 'ya existía'}"
        )
        return sucursal

    def _crear_empleado(self):
        cargo, _ = Cargo.objects.get_or_create(
            nombre="Administrador del Sistema",
            defaults={"descripcion": "Cargo administrativo del sistema"},
        )
        empleado, creado = Empleado.objects.get_or_create(
            identificacion="000000000",
            defaults={
                "id_cargo": cargo,
                "nombre": "Administrador",
                "apellido1": "SIGEPAN",
            },
        )
        self.stdout.write(
            f"Empleado administrativo: {'creado' if creado else 'ya existía'}"
        )
        return empleado

    def _crear_rol_administrador(self):
        rol, creado = Rol.objects.get_or_create(
            nombre="Administrador",
            defaults={"descripcion": "Acceso completo al sistema"},
        )
        self.stdout.write(f"Rol 'Administrador': {'creado' if creado else 'ya existía'}")
        return rol

    def _crear_modulo(self, nombre, orden_menu):
        modulo, creado = Modulo.objects.get_or_create(
            nombre=nombre,
            defaults={"orden_menu": orden_menu, "estado": True},
        )
        self.stdout.write(f"  Módulo '{nombre}': {'creado' if creado else 'ya existía'}")
        return modulo, creado

    def _crear_permisos(self, modulo, acciones):
        permisos = []
        for accion in acciones:
            permiso, _ = Permiso.objects.get_or_create(
                id_modulo=modulo,
                accion=accion,
                defaults={
                    "descripcion": f"{accion} sobre el módulo {modulo.nombre}",
                    "estado": True,
                },
            )
            permisos.append(permiso)
        return permisos

    def _otorgar_a_rol(self, rol, permisos):
        # fecha_creacion es auto_now_add=True en RolPermiso: Django la
        # completa solo, no hace falta (ni se puede) pasarla a mano.
        for permiso in permisos:
            RolPermiso.objects.get_or_create(
                id_rol=rol,
                id_permiso=permiso,
            )

    def _crear_usuario_admin(self, empleado, rol, sucursal):
        if Usuario.objects.filter(username=self.USERNAME_ADMIN).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"\nUsuario '{self.USERNAME_ADMIN}' ya existe, no se modifica."
                )
            )
            return

        Usuario.objects.create(
            id_empleado=empleado,
            id_rol=rol,
            id_sucursal=sucursal,
            username=self.USERNAME_ADMIN,
            password=make_password(self.PASSWORD_ADMIN),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nUsuario administrador creado:\n"
                f"  usuario:    {self.USERNAME_ADMIN}\n"
                f"  contraseña: {self.PASSWORD_ADMIN}\n"
                f"  (cámbiala desde 'Mi perfil' apenas inicies sesión)"
            )
        )
