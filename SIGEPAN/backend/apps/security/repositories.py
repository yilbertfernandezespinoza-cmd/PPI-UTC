from .models import Rol, Permiso, Usuario, RolPermiso, LogAcciones

class RolRepository:

    @staticmethod
    def listar():
        return Rol.objects.all()

    @staticmethod
    def obtener(id_rol):
        return Rol.objects.get(id_rol=id_rol)

    @staticmethod
    def crear(**datos):
        return Rol.objects.create(**datos)

    @staticmethod
    def actualizar(rol):
        rol.save()
        return rol
    
    @staticmethod
    def eliminar(rol):
        rol.delete()

class RolPermisoRepository:

    @staticmethod
    def eliminar_por_rol(rol):
        """
        Elimina las relaciones de permisos asociadas a un rol
        """        

        RolPermiso.objects.filter(
            id_rol=rol
        ).delete()
    

class PermisoRepository:

    @staticmethod
    def listar():
        return (
            Permiso.objects
            .select_related("modulo")
            .all()
        )

    @staticmethod
    def obtener(id_permiso):
        return Permiso.objects.get(
            id_permiso=id_permiso
        )  

class LogAccionesRepository:

    @staticmethod
    def listar_ingresos():
        """
        Obtiene los registros de LOGIN y LOGOUT.
        """

        return LogAcciones.objects.filter(
            tipo_accion__in=[
                "LOGIN",
                "LOGOUT",
            ]
        ).order_by("-fecha_hora")

    @staticmethod
    def listar_movimientos():
        """
        Obtiene los registros de movimientos del sistema.
        """

        return LogAcciones.objects.filter(
            tipo_accion__in=[
                "CREAR",
                "MODIFICAR",
                "ELIMINAR",
            ]
        ).order_by("-fecha_hora")      