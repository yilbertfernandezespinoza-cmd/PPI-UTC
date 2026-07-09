from .repositories import (RolRepository, PermisoRepository)
from .models import LogAcciones, RolPermiso
from apps.configuracion.models import Modulo
class RolService:

    @staticmethod
    def listar_roles():
        return RolRepository.listar()

    @staticmethod
    def obtener_rol(id_rol):
        return RolRepository.obtener(id_rol)
    

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
        return
        
    LogAcciones.objects.create(
        id_usuario=usuario,
        id_modulo=modulo_obj,
        tipo_accion=tipo_accion,
        descripcion=descripcion,
        ip_origen=request.META.get("REMOTE_ADDR"),
        navegador=request.META.get("HTTP_USER_AGENT", "")[:150],
    )    


class RolPermisoService:

    @staticmethod
    def actualizar_permisos(
        rol_id,
        permisos,
    ):

        RolPermiso.objects.filter(
            id_rol_id=rol_id
        ).delete()

        for permiso_id in permisos:

            RolPermiso.objects.create(
                id_rol_id=rol_id,
                id_permiso_id=permiso_id,
            )    