# Repositorios del módulo
from .models import Categoria


class CategoriaRepository:
    """
    Repositorio para el acceso a datos del módulo Categorías.
    """

    @staticmethod
    def listar():
        """
        Obtiene todas las categorías.
        """

        return Categoria.objects.all()

    @staticmethod
    def obtener_por_id(id_categoria):
        """
        Obtiene una categoría por su identificador.
        """

        return Categoria.objects.get(pk=id_categoria)

    @staticmethod
    def existe_nombre(nombre, excluir_id=None):
        """
        Indica si ya existe una categoría con ese nombre (comparación
        insensible a mayúsculas/minúsculas), excluyendo opcionalmente
        una categoría puntual (caso de edición).
        """

        consulta = Categoria.objects.filter(nombre__iexact=nombre)

        if excluir_id:
            consulta = consulta.exclude(pk=excluir_id)

        return consulta.exists()

    @staticmethod
    def crear(**datos):
        """
        Crea una nueva categoría.
        """

        return Categoria.objects.create(**datos)

    @staticmethod
    def actualizar(categoria):
        """
        Guarda los cambios de una categoría.
        """

        categoria.save()

        return categoria
