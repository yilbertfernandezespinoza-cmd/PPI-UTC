from datetime import datetime, timedelta

from django.utils import timezone

from .models import (
    Inventario,
    TipoMovimientoInventario,
    MovimientoInventario,
)


def _limite_inferior(fecha):
    """
    Medianoche local (aware) del día `fecha` — evita depender de que MySQL
    tenga cargadas las tablas de zona horaria (CONVERT_TZ). Mismo patrón
    usado en mermas/ajustes/gastos_operativos/reportes (05-08/07-08),
    incluyendo la conversión de string a date (el input type="date" del
    filtro llega como texto crudo desde request.GET, nunca ya parseado).
    """
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))


def _limite_superior(fecha):
    """Medianoche local (aware) del día siguiente a `fecha` (límite exclusivo)."""
    return _limite_inferior(fecha) + timedelta(days=1)


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

    @staticmethod
    def obtener_por_producto_sucursal(id_producto, id_sucursal):
        """
        Obtiene el registro de inventario de un producto en una sucursal.
        Devuelve None si no existe (a diferencia de obtener_o_crear, que sí
        lo crea). Punto único de acceso: evita repetir
        Inventario.objects.filter(...) con nombres de campo distintos en
        cada app que necesita consultar existencias (ventas, compras).
        """

        return (
            Inventario.objects
            .filter(
                id_producto=id_producto,
                id_sucursal=id_sucursal,
            )
            .first()
        )

    @staticmethod
    def obtener_para_actualizar(id_producto, id_sucursal):
        """
        Igual que obtener_por_producto_sucursal, pero bloquea la fila
        (select_for_update) para uso dentro de una transacción atómica
        que va a modificar el stock — evita condiciones de carrera cuando
        dos ventas/compras simultáneas afectan el mismo producto+sucursal.
        Debe llamarse siempre dentro de una vista/bloque @transaction.atomic.
        """

        return (
            Inventario.objects
            .select_for_update()
            .filter(
                id_producto=id_producto,
                id_sucursal=id_sucursal,
            )
            .first()
        )


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
    def filtrar(id_producto=None, desde=None, hasta=None):
        """
        Filtra movimientos de inventario por producto y/o rango de fechas
        (mismo criterio de filtro ya usado en Mermas/Ajustes/Gastos
        Operativos para sus respectivos listados).
        """

        consulta = MovimientoInventarioRepository.listar()

        if id_producto:
            consulta = consulta.filter(id_inventario__id_producto_id=id_producto)

        if desde:
            consulta = consulta.filter(fecha_creacion__gte=_limite_inferior(desde))

        if hasta:
            consulta = consulta.filter(fecha_creacion__lt=_limite_superior(hasta))

        return consulta

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