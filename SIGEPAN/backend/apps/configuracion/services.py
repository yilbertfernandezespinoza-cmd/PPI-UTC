# Servicios del módulo
from .repositories import ModuloRepository


class ModuloService:

    @staticmethod
    def listar():
        return ModuloRepository.listar()

    @staticmethod
    def obtener(id_modulo):
        return ModuloRepository.obtener(id_modulo)