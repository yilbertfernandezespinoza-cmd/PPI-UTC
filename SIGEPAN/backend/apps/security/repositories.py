from .models import Rol, Permiso


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