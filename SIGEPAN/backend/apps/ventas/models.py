from django.db import models



# =====================================================
# VENTA
# =====================================================

class Venta(models.Model):

    id_venta = models.AutoField(
        primary_key=True,
        db_column="id_venta"
    )


    numero_venta = models.CharField(
        max_length=30,
        unique=True,
        db_column="numero_venta"
    )


    tipo_comprobante = models.CharField(
        max_length=20,
        db_column="tipo_comprobante"
    )


    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        db_column="id_cliente",
        null=True,
        blank=True
    )


    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario"
    )


    caja = models.ForeignKey(
        "caja.Caja",
        on_delete=models.PROTECT,
        db_column="id_caja"
    )


    metodo_pago = models.ForeignKey(
        "configuracion.MetodoPago",
        on_delete=models.PROTECT,
        db_column="id_metodo_pago"
    )


    fecha = models.DateTimeField(
        db_column="fecha"
    )


    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="subtotal"
    )


    impuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column="impuesto"
    )


    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column="descuento"
    )


    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="total"
    )


    estado = models.BooleanField(
        default=True,
        db_column="estado"
    )


    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion"
    )


    fecha_actualizacion = models.DateTimeField(
        db_column="fecha_actualizacion"
    )


    class Meta:

        managed = False

        db_table = "venta"



    def __str__(self):

        return self.numero_venta





# =====================================================
# DETALLE VENTA
# =====================================================

class DetalleVenta(models.Model):


    id_detalle_venta = models.AutoField(
        primary_key=True,
        db_column="id_detalle_venta"
    )


    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        db_column="id_venta"
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

        db_table = "detalle_venta"




# =====================================================
# DETALLE PAGO
# =====================================================

class DetallePago(models.Model):


    id_detalle_pago = models.AutoField(
        primary_key=True,
        db_column="id_detalle_pago"
    )


    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        db_column="id_venta"
        
    )


    metodo_pago = models.ForeignKey(
        "configuracion.MetodoPago",
        on_delete=models.PROTECT,
        db_column="id_metodo_pago"
    )


    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto"
    )


    referencia = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="referencia"
    )


    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion"
    )


    class Meta:

        managed = False

        db_table = "detalle_pago"