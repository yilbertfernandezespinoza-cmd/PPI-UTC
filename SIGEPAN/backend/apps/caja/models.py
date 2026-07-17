from django.db import models



# =====================================================
# CAJA
# =====================================================

class Caja(models.Model):

    id_caja = models.AutoField(
        primary_key=True,
        db_column="id_caja"
    )


    sucursal = models.ForeignKey(
        "configuracion.Sucursal",
        on_delete=models.PROTECT,
        db_column="id_sucursal"
    )


    nombre = models.CharField(
        max_length=100,
        db_column="nombre"
    )


    descripcion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="descripcion"
    )


    saldo_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="saldo_inicial"
    )


    saldo_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="saldo_actual"
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

        db_table = "caja"



    def __str__(self):

        return self.nombre





# =====================================================
# APERTURA CAJA
# =====================================================

class AperturaCaja(models.Model):


    id_apertura = models.AutoField(
        primary_key=True,
        db_column="id_apertura"
    )


    caja = models.ForeignKey(
        Caja,
        on_delete=models.PROTECT,
        db_column="id_caja"
    )


    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario"
    )


    fecha_apertura = models.DateTimeField(
        db_column="fecha_apertura"
    )


    monto_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto_inicial"
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
        db_column="fecha_creacion"
    )


    class Meta:

        managed = False

        db_table = "apertura_caja"





# =====================================================
# MOVIMIENTO CAJA
# =====================================================

class MovimientoCaja(models.Model):


    id_movimiento = models.AutoField(
        primary_key=True,
        db_column="id_movimiento"
    )


    apertura = models.ForeignKey(
        AperturaCaja,
        on_delete=models.PROTECT,
        db_column="id_apertura"
    )


    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario"
    )


    tipo_movimiento = models.CharField(
        max_length=20,
        db_column="tipo_movimiento"
    )


    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto"
    )


    descripcion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="descripcion"
    )


    fecha_movimiento = models.DateTimeField(
        db_column="fecha_movimiento"
    )


    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion"
    )


    class Meta:

        managed = False

        db_table = "movimiento_caja"





# =====================================================
# CIERRE CAJA
# =====================================================

class CierreCaja(models.Model):


    id_cierre = models.AutoField(
        primary_key=True,
        db_column="id_cierre"
    )


    apertura = models.OneToOneField(
        AperturaCaja,
        on_delete=models.PROTECT,
        db_column="id_apertura"
    )


    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario"
    )


    fecha_cierre = models.DateTimeField(
        db_column="fecha_cierre"
    )


    monto_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto_inicial"
    )


    monto_final = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto_final"
    )


    diferencia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column="diferencia"
    )


    observaciones = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="observaciones"
    )


    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion"
    )


    class Meta:

        managed = False

        db_table = "cierre_caja"