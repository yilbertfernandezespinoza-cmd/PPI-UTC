from .repositories import (RolRepository, PermisoRepository)
from .models import LogAcciones, RolPermiso, Permiso
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