import logging
from .repositories import (
    RolRepository, PermisoRepository, 
    RolPermisoRepository, LogAccionesRepository)
from .models import LogAcciones, RolPermiso, Permiso
from apps.configuracion.models import Modulo
from .menu import MENU
from django.urls import reverse
from django.db import transaction

logger = logging.getLogger(__name__)
class RolService:

    @staticmethod
    def listar_roles():
        return RolRepository.listar()

    @staticmethod
    def obtener_rol(id_rol):
        return RolRepository.obtener(id_rol)
    
    @staticmethod
    def actualizar_rol(id_rol, datos):
        """
        Actualiza la información de un rol.
        """

        rol = RolRepository.obtener(id_rol)

        rol.nombre = datos["nombre"]
        rol.descripcion = datos["descripcion"]
        rol.estado = datos["estado"]

        return RolRepository.actualizar(rol)
    
    @staticmethod
    def deshabilitar_rol(id_rol):
        """
        Deshabilita un rol si no tiene usuarios activos asignados.
        """

        rol = RolRepository.obtener(id_rol)

        if rol.usuario_set.filter(estado=True).exists():
            raise ValueError(
                "No se puede deshabilitar el rol porque tiene usuarios activos asignados."
            )

        rol.estado = False

        return RolRepository.actualizar(rol)

class PermisoService:

    @staticmethod
    def listar():
        return PermisoRepository.listar()

    @staticmethod
    def obtener(id_permiso):
        return PermisoRepository.obtener(id_permiso)    
    

def registrar_log(
    request,
    usuario,
    modulo,
    tipo_accion,
    descripcion,
):
    """
    Registra una acción en la bitácora del sistema.
    """
    try:
        modulo_obj =  Modulo.objects.get(nombre=modulo)
    except Modulo.DoesNotExist:
        logger.warning(
            "No se registró la auditoría"
            "El módulo '%s' no existe en la base de datos.",
            modulo
        )

        return
        
    LogAcciones.objects.create(
        id_usuario=usuario,
        id_modulo=modulo_obj,
        tipo_accion=tipo_accion,
        descripcion=descripcion,
        ip_origen=request.META.get("REMOTE_ADDR"),
        navegador=request.META.get("HTTP_USER_AGENT", "")[:150],
    )    

class BitacoraService:

    @staticmethod
    def listar_ingresos():
        """
        Obtiene la bitácora de ingresos al sistema.
        """

        return LogAccionesRepository.listar_ingresos()

    @staticmethod
    def listar_movimientos():
        """
        Obtiene la bitácora de movimientos del sistema.
        """

        return LogAccionesRepository.listar_movimientos()
class RolPermisoService:

    @staticmethod
    @transaction.atomic
    def actualizar_permisos(rol_id, seleccionados,):

        # Elimina los permisos actuales del rol
        RolPermiso.objects.filter(
            id_rol_id=rol_id
        ).delete()

        for valor in seleccionados:
            
            # -------------------------
            # El permiso ya existe
            # -------------------------
            if valor.startswith("P-"):

                permiso_id = int(
                    valor.replace("P-", "")
                )

                RolPermiso.objects.get_or_create(
                    id_rol_id=rol_id,
                    id_permiso_id=permiso_id,
                )

            # -------------------------
            # El permiso no existe
            # -------------------------
            elif valor.startswith("N-"):

                _, modulo_id, accion = valor.split("-")

                modulo = Modulo.objects.get(
                    id_modulo=modulo_id
                )

                permiso, _ = Permiso.objects.get_or_create(
                    id_modulo=modulo,
                    accion=accion,
                    defaults={
                        "descripcion":(
                            f"{accion.title()} en módulo"
                            f"{modulo.nombre}"
                        )
                    }
                )

                RolPermiso.objects.get_or_create(
                    id_rol_id=rol_id,
                    id_permiso=permiso,
                )

class MenuService:
    """
    Construye el menu lateral del sistema

    proceso:
    1. obtiene el usuario autenticado
    2. consulta los modulos permitidos
    3. filtra unicamente permisos CONSULTAR
    4. contruye la estructura usando menu.py
    5. devuelve el menu listo para renderizar

    el template sidebar.html unicamente muestra la informacion.

    """
    @staticmethod
    def obtener_menu_usuario(request):
        """
        Construye el menú dinámico según el rol del usuario.
        """

        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            return []

        # Obtener nombres de módulos permitidos
        modulos_permitidos = set(
            Modulo.objects.filter(
                permiso__accion="CONSULTAR",
                permiso__rolpermiso__id_rol__usuario__id_usuario=usuario_id,
                estado=True,
            )
            .distinct()
            .values_list("nombre", flat=True)
        )

        menu = []

        for grupo in MENU:

            if grupo["modulo"] in modulos_permitidos:

                nuevo_grupo = {

                    "modulo": grupo["modulo"],

                    "icono": grupo["icono"],

                    "opciones": [],

                    "activo": False,

                }

                for opcion in grupo["opciones"]:

                    nueva_opcion = opcion.copy()

                    url = reverse(opcion["url"])

                    nueva_opcion["url"] = url

                    # ¿La página actual corresponde a esta opción?
                    nueva_opcion["activa"] = (
                        request.path == url
                    )

                    # Si una opción está activa,
                    # el grupo también debe estar activo.
                    if nueva_opcion["activa"]:

                        nuevo_grupo["activo"] = True

                    nuevo_grupo["opciones"].append(
                        nueva_opcion
                    )

                menu.append(nuevo_grupo)
        return menu          