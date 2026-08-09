# Repositorios del módulo

from django.db.models import Q

from .models import Producto


class ProductoRepository:
    """
    Repositorio para el acceso a datos del módulo Productos.
    """

    @staticmethod
    def listar():
        """
        Todos los productos (activos e inactivos), con la categoría
        precargada. Usado por el listado principal (Tabulator/DataTable)
        y como queryset base para obtener un producto puntual por id
        (get_object_or_404), para no repetir el select_related en cada
        vista.
        """
        return Producto.objects.select_related("id_categoria").all()

    @staticmethod
    def obtener_por_id(pk):
        """
        Obtiene un producto por su id, con la categoría precargada.
        Devuelve None si no existe.
        """
        return (
            Producto.objects
            .select_related("id_categoria")
            .filter(pk=pk)
            .first()
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo producto.
        """
        return Producto.objects.create(**datos)

    @staticmethod
    def guardar(producto):
        """
        Persiste los cambios de un producto ya modificado en memoria.
        """
        producto.save()
        return producto

    @staticmethod
    def cambiar_estado(producto, estado):
        """
        Activa/deshabilita (lógicamente) un producto. Se hace un save()
        completo (no update_fields) a propósito, para que
        fecha_actualizacion (auto_now) se siga actualizando igual que
        antes de este refactor.
        """
        producto.estado = estado
        producto.save()
        return producto

    @staticmethod
    def activos():
        """Queryset de productos activos."""
        return Producto.objects.filter(estado=True)

    @staticmethod
    def buscar_pos(texto="", categoria_id="", limite=10):
        """
        Búsqueda de productos activos para el POS: usada por el buscador
        de texto (?q=...) y por los tiles de producto de cada pestaña de
        categoría (?categoria_id=...). `texto` filtra por nombre o
        código; `categoria_id`, por categoría. Ambos son opcionales y
        pueden combinarse.
        """
        productos = ProductoRepository.activos()

        if categoria_id:
            productos = productos.filter(id_categoria_id=categoria_id)

        if texto:
            productos = productos.filter(
                Q(nombre__icontains=texto)
                |
                Q(codigo__icontains=texto)
            )

        return productos.order_by("nombre")[:limite]
