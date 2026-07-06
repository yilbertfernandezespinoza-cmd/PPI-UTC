# Repositorios del módulo
from .models import Modulo


class ModuloRepository:

    @staticmethod
    def listar():
        return Modulo.objects.all()

    @staticmethod
    def obtener(id_modulo):
        return Modulo.objects.get(id_modulo=id_modulo)