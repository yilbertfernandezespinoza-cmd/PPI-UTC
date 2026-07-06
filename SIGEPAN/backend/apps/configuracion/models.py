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
        db_table = "sucursal"
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre    