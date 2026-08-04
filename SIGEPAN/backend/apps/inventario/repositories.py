from .models import (
    Inventario,
    TipoMovimientoInventario,
    MovimientoInventario,
)


class InventarioRepository:
    """
    Repositorio para el acceso a datos del inventario.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los registros de inventario.
        """

        return (
            Inventario.objects
            .select_related(
                "id_producto",
                "id_sucursal",
            )
            .order_by(
                "id_producto__nombre",
            )
        )

    @staticmethod
    def obtener(id_inventario):
        """
        Obtiene un registro de inventario por su identificador.
        """

        return Inventario.objects.get(
            id_inventario=id_inventario
        )

    @staticmethod
    def actualizar(inventario):
        """
        Guarda los cambios de un registro de inventario.
        """

        inventario.save()

        return inventario

    @staticmethod
    def obtener_o_crear(id_producto, id_sucursal):
        """
        Obtiene el registro de inventario de un producto en una sucursal,
        o lo crea en cero si todavía no existe.
        """

        inventario, _creado = Inventario.objects.get_or_create(
            id_producto=id_producto,
            id_sucursal=id_sucursal,
            defaults={"stock_actual": 0},
        )

        return inventario


class TipoMovimientoInventarioRepository:
    """
    Repositorio para el acceso a datos de los tipos de movimiento de inventario.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los tipos de movimiento activos.
        """

        return (
            TipoMovimientoInventario.objects
            .filter(
                estado=True
            )
            .order_by(
                "nombre"
            )
        )

    @staticmethod
    def obtener(id_tipo_movimiento_inventario):
        """
        Obtiene un tipo de movimiento por su identificador.
        """

        return TipoMovimientoInventario.objects.get(
            id_tipo_movimiento_inventario=id_tipo_movimiento_inventario
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo tipo de movimiento.
        """

        return TipoMovimientoInventario.objects.create(
            **datos
        )

    @staticmethod
    def actualizar(tipo_movimiento):
        """
        Guarda los cambios de un tipo de movimiento.
        """

        tipo_movimiento.save()

        return tipo_movimiento


class MovimientoInventarioRepository:
    """
    Repositorio para el acceso a datos de los movimientos de inventario.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los movimientos de inventario.
        """

        return (
            MovimientoInventario.objects
            .select_related(
                "id_inventario",
                "id_tipo_movimiento_inventario",
                "id_usuario",
            )
            .order_by(
                "-fecha_creacion",
            )
        )

    @staticmethod
    def listar_por_inventario(id_inventario):
        """
        Obtiene los movimientos de un inventario.
        """

        return (
            MovimientoInventario.objects
            .filter(
                id_inventario=id_inventario
            )
            .select_related(
                "id_tipo_movimiento_inventario",
                "id_usuario",
            )
            .order_by(
                "-fecha_creacion",
            )
        )

    @staticmethod
    def obtener(id_movimiento_inventario):
        """
        Obtiene un movimiento por su identificador.
        """

        return MovimientoInventario.objects.get(
            id_movimiento_inventario=id_movimiento_inventario
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo movimiento de inventario.
        """

        return MovimientoInventario.objects.create(
            **datos
        )

    @staticmethod
    def actualizar(movimiento):
        """
        Guarda los cambios de un movimiento de inventario.
        """

        movimiento.save()

        return movimiento