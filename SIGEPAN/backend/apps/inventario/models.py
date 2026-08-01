from django.db import models

from apps.core.base_models import BaseModel


class Inventario(BaseModel):
    """
    Modelo que representa la tabla inventario.
    """

    id_inventario = models.AutoField(
        primary_key=True,
        db_column="id_inventario",
    )

    id_producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.DO_NOTHING,
        db_column="id_producto",
        verbose_name="Producto",
    )

    id_sucursal = models.ForeignKey(
        "configuracion.Sucursal",
        on_delete=models.DO_NOTHING,
        db_column="id_sucursal",
        verbose_name="Sucursal",
    )

    stock_actual = models.IntegerField(
        default=0,
        db_column="stock_actual",
        verbose_name="Stock actual",
    )

    stock_minimo = models.IntegerField(
        default=0,
        db_column="stock_minimo",
        verbose_name="Stock mínimo",
    )

    stock_maximo = models.IntegerField(
        default=0,
        db_column="stock_maximo",
        verbose_name="Stock máximo",
    )

    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="ubicacion",
        verbose_name="Ubicación",
    )

    class Meta:
        db_table = "inventario"
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        ordering = [
            "id_producto",
        ]

    def __str__(self):
        return f"{self.id_producto} - {self.stock_actual}"


class TipoMovimientoInventario(BaseModel):
    """
    Modelo que representa la tabla tipo_movimiento_inventario.
    """

    id_tipo_movimiento_inventario = models.AutoField(
        primary_key=True,
        db_column="id_tipo_movimiento_inventario",
    )

    nombre = models.CharField(
        max_length=50,
        unique=True,
        db_column="nombre",
        verbose_name="Nombre",
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion",
        verbose_name="Descripción",
    )

    class Meta:
        db_table = "tipo_movimiento_inventario"
        verbose_name = "Tipo de Movimiento de Inventario"
        verbose_name_plural = "Tipos de Movimiento de Inventario"
        ordering = [
            "nombre",
        ]

    def __str__(self):
        return self.nombre


class MovimientoInventario(BaseModel):
    """
    Modelo que representa la tabla movimiento_inventario.
    """

    id_movimiento_inventario = models.AutoField(
        primary_key=True,
        db_column="id_movimiento_inventario",
    )

    id_inventario = models.ForeignKey(
        Inventario,
        on_delete=models.DO_NOTHING,
        db_column="id_inventario",
        verbose_name="Inventario",
    )

    id_tipo_movimiento_inventario = models.ForeignKey(
        TipoMovimientoInventario,
        on_delete=models.DO_NOTHING,
        db_column="id_tipo_movimiento_inventario",
        verbose_name="Tipo de movimiento",
    )

    id_usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.DO_NOTHING,
        db_column="id_usuario",
        verbose_name="Usuario",
    )

    cantidad = models.IntegerField(
        db_column="cantidad",
        verbose_name="Cantidad",
    )

    stock_anterior = models.IntegerField(
        db_column="stock_anterior",
        verbose_name="Stock anterior",
    )

    stock_nuevo = models.IntegerField(
        db_column="stock_nuevo",
        verbose_name="Stock nuevo",
    )

    observaciones = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="observaciones",
        verbose_name="Observaciones",
    )

    class Meta:
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = [
            "-fecha_creacion",
        ]

    def __str__(self):
        return (
            f"{self.id_tipo_movimiento_inventario.nombre} - "
            f"{self.id_inventario.id_producto.nombre} "
            f"({self.cantidad})"
        )    