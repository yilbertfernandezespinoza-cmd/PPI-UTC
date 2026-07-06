from .repositories import (RolRepository, PermisoRepository)

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