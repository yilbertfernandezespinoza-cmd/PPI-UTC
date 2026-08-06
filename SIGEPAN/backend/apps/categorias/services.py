# Servicios del módulo
from django.core.exceptions import ValidationError
from django.db import transaction

from .repositories import CategoriaRepository


class CategoriaService:
    """
    Reglas de negocio del módulo Categorías.
    """

    @staticmethod
    def listar():
        return CategoriaRepository.listar()

    @staticmethod
    def obtener(id_categoria):
        return CategoriaRepository.obtener_por_id(id_categoria)

    @staticmethod
    def validar_nombre_unico(nombre, excluir_id=None):
        """
        Valida que el nombre no esté vacío y que no exista ya otra
        categoría con el mismo nombre (comparación insensible a
        mayúsculas/minúsculas).

        La usan tanto CategoriaForm.clean_nombre como crear()/
        actualizar(), para que la regla quede en un único lugar y no
        se duplique la consulta entre el formulario y el service.
        """

        nombre = (nombre or "").strip()

        if not nombre:
            raise ValidationError(
                "El nombre de la categoría es obligatorio."
            )

        if CategoriaRepository.existe_nombre(nombre, excluir_id=excluir_id):
            raise ValidationError(
                "Ya existe una categoría con ese nombre."
            )

        return nombre

    @staticmethod
    @transaction.atomic
    def crear(nombre, descripcion=None):
        """
        Crea una nueva categoría, validando que el nombre sea único.
        """

        nombre = CategoriaService.validar_nombre_unico(nombre)

        return CategoriaRepository.crear(
            nombre=nombre,
            descripcion=descripcion,
        )

    @staticmethod
    @transaction.atomic
    def actualizar(id_categoria, nombre, descripcion=None):
        """
        Actualiza el nombre/descripción de una categoría existente,
        validando que el nuevo nombre siga siendo único.
        """

        nombre = CategoriaService.validar_nombre_unico(
            nombre,
            excluir_id=id_categoria,
        )

        categoria = CategoriaRepository.obtener_por_id(id_categoria)
        categoria.nombre = nombre
        categoria.descripcion = descripcion

        return CategoriaRepository.actualizar(categoria)

    @staticmethod
    @transaction.atomic
    def cambiar_estado(id_categoria):
        """
        Activa/desactiva una categoría (no la borra), igual que el
        resto de módulos con BaseModel (Cliente, Gasto Operativo).
        """

        categoria = CategoriaRepository.obtener_por_id(id_categoria)
        categoria.estado = not categoria.estado

        return CategoriaRepository.actualizar(categoria)
