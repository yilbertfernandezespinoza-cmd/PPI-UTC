from django.db import models



class Compra(models.Model):

    id_compra = models.AutoField(
        primary_key=True,
        db_column="id_compra"
    )


    proveedor = models.ForeignKey(
        "proveedores.Proveedor",
        on_delete=models.PROTECT,
        db_column="id_proveedor"
    )


    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario"
    )


    fecha = models.DateTimeField(
        db_column="fecha"
    )


    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="total"
    )


    observaciones = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="observaciones"
    )


    estado = models.BooleanField(
        default=True,
        db_column="estado"
    )


    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        db_column="fecha_creacion"
    )


    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        db_column="fecha_actualizacion"
    )


    class Meta:

        managed = False

        db_table = "compra"


    def __str__(self):

        return f"Compra {self.id_compra}"





class DetalleCompra(models.Model):


    id_detalle_compra = models.AutoField(
        primary_key=True,
        db_column="id_detalle_compra"
    )


    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        db_column="id_compra"
    )


    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        db_column="id_producto"
    )


    cantidad = models.IntegerField(
        db_column="cantidad"
    )


    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="precio_unitario"
    )


    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="subtotal"
    )



    class Meta:

        managed = False

        db_table = "detalle_compra"



    def __str__(self):

        return f"Detalle compra {self.id_detalle_compra}"