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
# HISTORIAL CAJA
# =====================================================

class HistorialCaja(models.Model):


    id_historial = models.AutoField(
        primary_key=True,
        db_column="id_historial"
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


    tipo_cambio = models.CharField(
        max_length=50,
        db_column="tipo_cambio"
    )


    valor_anterior = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="valor_anterior"
    )


    valor_nuevo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="valor_nuevo"
    )


    observacion = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column="observacion"
    )


    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion"
    )


    class Meta:

        managed = False

        db_table = "historial_caja"

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


    # Agregado 06-08 (RF-014/015): el RF pide un campo "turno" que no
    # existía ni en el modelo ni en la tabla real. Se agrega como columna
    # nueva (ver ALTER TABLE en la nota técnica) — no rompe nada existente,
    # solo suma un dato descriptivo a la apertura de caja.
    TURNOS = [
        ("MANANA", "Mañana"),
        ("TARDE", "Tarde"),
        ("NOCHE", "Noche"),
    ]

    turno = models.CharField(
        max_length=20,
        choices=TURNOS,
        null=True,
        blank=True,
        db_column="turno",
        verbose_name="Turno",
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


    TIPOS_MOVIMIENTO = [

        ("VENTA", "Venta"),
        ("INGRESO", "Ingreso"),
        ("RETIRO", "Retiro"),
        ("GASTO", "Gasto"),
        ("AJUSTE", "Ajuste"),

    ]


    tipo_movimiento = models.CharField(

        max_length=20,

        choices=TIPOS_MOVIMIENTO

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
# ARQUEO CAJA
# =====================================================


class ArqueoCaja(models.Model):


    id_arqueo = models.AutoField(
        primary_key=True,
        db_column="id_arqueo"
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


    fecha_arqueo = models.DateTimeField(
        db_column="fecha_arqueo"
    )


    saldo_sistema = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="saldo_sistema"
    )


    saldo_contado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="saldo_contado"
    )


    diferencia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
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

        db_table = "arqueo_caja"



    def __str__(self):

        return f"Arqueo {self.id_arqueo}"

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