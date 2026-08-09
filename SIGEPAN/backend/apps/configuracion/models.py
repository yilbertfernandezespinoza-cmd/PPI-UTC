from django.db import models
from apps.core.base_models import BaseModel


class Modulo(BaseModel):
    """
    Modelo que representa la tabla modulo.
    """

    id_modulo = models.AutoField(
        primary_key=True,
        db_column="id_modulo"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_column="nombre",
        verbose_name="Nombre"
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion",
        verbose_name="Descripción"
    )

    icono = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="icono",
        verbose_name="Icono"
    )

    ruta = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_column="ruta",
        verbose_name="Ruta"
    )

    orden_menu = models.IntegerField(
        db_column="orden_menu",
        verbose_name="Orden"
    )

    class Meta:
        managed = False
        db_table = "modulo"
        ordering = ["orden_menu"]
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"

    def __str__(self):
        return self.nombre
    

class Sucursal(BaseModel):
    """
    Modelo que representa la tabla sucursal.
    """

    id_sucursal = models.AutoField(
        primary_key=True,
        db_column="id_sucursal"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_column="nombre"
    )

    direccion = models.CharField(
        max_length=255,
        db_column="direccion"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column="telefono"
    )

    encargado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="encargado"
    )

    class Meta:
        managed = False
        db_table = "sucursal"
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):

        return self.nombre    
    

class MetodoPago(BaseModel):
    """
    Modelo que representa la tabla metodo_pago (RF-013).

    Hasta el 04-08-2026 este modelo NO heredaba de BaseModel: redefinía a
    mano estado/fecha_creacion/fecha_actualizacion con los mismos nombres
    de columna que ya usa BaseModel, sin auto_now_add/auto_now — el mismo
    tipo de bug de "fecha_creacion se guarda en NULL" que se corrigió hoy
    en Venta. Se corrigió heredando BaseModel: mismas columnas reales
    (db_table sin cambios), ahora con timestamps automáticos.
    """

    id_metodo_pago = models.AutoField(
        primary_key=True,
        db_column="id_metodo_pago"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_column="nombre",
        verbose_name="Nombre",
    )

    descripcion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="descripcion",
        verbose_name="Descripción",
    )

    class Meta:
        managed = False
        db_table = "metodo_pago"
        verbose_name = "Método de pago"
        verbose_name_plural = "Métodos de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ConfiguracionTributaria(BaseModel):
    """
    Modelo que representa la tabla configuracion_tributaria.
    """

    id_configuracion_tributaria = models.AutoField(
        primary_key=True,
        db_column="id_configuracion_tributaria"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_column="nombre",
        verbose_name="Nombre"
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion",
        verbose_name="Descripción"
    )

    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        db_column="porcentaje",
        verbose_name="Porcentaje"
    )

    aplica_compras = models.BooleanField(
        default=True,
        db_column="aplica_compras",
        verbose_name="Aplica a compras"
    )

    aplica_ventas = models.BooleanField(
        default=True,
        db_column="aplica_ventas",
        verbose_name="Aplica a ventas"
    )

    class Meta:
        managed = False
        db_table = "configuracion_tributaria"
        verbose_name = "Configuración tributaria"
        verbose_name_plural = "Configuraciones tributarias"

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"     

class DatosEmpresa(models.Model):
    """
    Datos fiscales de la empresa (RF-024). Registro único (singleton).
    Tabla creada directamente en la base de datos (Database First).

    Nota: existía una segunda definición de esta misma clase, heredando de
    BaseModel, más arriba en este archivo. En Python la definición que se
    ejecuta después sobreescribe a la anterior en el mismo módulo, así que
    Django nunca llegó a registrar esa primera versión — quedó como código
    muerto. Se eliminó el 04-08-2026 para dejar una única fuente de verdad.
    """

    REGIMEN_TRADICIONAL = "TRADICIONAL"
    REGIMEN_SIMPLIFICADO = "SIMPLIFICADO"
    REGIMEN_OTRO = "OTRO"

    REGIMENES_TRIBUTARIOS = [
        (REGIMEN_TRADICIONAL, "Régimen Tradicional (General)"),
        (REGIMEN_SIMPLIFICADO, "Régimen de Tributación Simplificada (RTS)"),
        (REGIMEN_OTRO, "Otro"),
    ]

    id_datos_empresa = models.AutoField(
        primary_key=True,
        db_column="id_datos_empresa"
    )

    nombre_comercial = models.CharField(
        max_length=150,
        db_column="nombre_comercial",
        verbose_name="Nombre comercial"
    )

    cedula_juridica = models.CharField(
        max_length=30,
        db_column="cedula_juridica",
        verbose_name="Cédula jurídica"
    )

    regimen_tributario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGIMENES_TRIBUTARIOS,
        db_column="regimen_tributario",
        verbose_name="Régimen tributario"
    )

    direccion_fiscal = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="direccion_fiscal",
        verbose_name="Dirección fiscal"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column="telefono",
        verbose_name="Teléfono"
    )

    correo = models.EmailField(
        max_length=150,
        blank=True,
        null=True,
        db_column="correo",
        verbose_name="Correo electrónico"
    )

    estado = models.BooleanField(
        default=True,
        db_column="estado"
    )

    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion",
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        db_column="fecha_actualizacion",
        auto_now=True,
    )

    class Meta:
        managed = False
        db_table = "datos_empresa"
        verbose_name = "Datos de la empresa"
        verbose_name_plural = "Datos de la empresa"

    def __str__(self):
        return self.nombre_comercial