from django.db import models



class Inventario(models.Model):


    id_inventario = models.AutoField(

        primary_key=True,

        db_column="id_inventario"

    )


    producto = models.ForeignKey(

        "productos.Producto",

        on_delete=models.PROTECT,

        db_column="id_producto"

    )


    sucursal = models.ForeignKey(

        "configuracion.Sucursal",

        on_delete=models.PROTECT,

        db_column="id_sucursal"

    )


    stock_actual = models.IntegerField(

        default=0,

        db_column="stock_actual"

    )


    stock_minimo = models.IntegerField(

        default=0,

        db_column="stock_minimo"

    )


    stock_maximo = models.IntegerField(

        default=0,

        db_column="stock_maximo"

    )


    ubicacion = models.CharField(

        max_length=100,

        null=True,

        blank=True,

        db_column="ubicacion"

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

        db_table = "inventario"



    def __str__(self):

        return f"{self.producto} - {self.stock_actual}"