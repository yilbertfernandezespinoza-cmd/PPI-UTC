from django.db import models
from apps.core.base_models import BaseModel


class Cargo(BaseModel):
    """
    Modelo que representa la tabla cargo.
    """

    id_cargo = models.AutoField(
        primary_key=True,
        db_column="id_cargo"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_column="nombre"
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion"
    )

    class Meta:
        managed = False
        db_table = "cargo"
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

    def __str__(self):
        return self.nombre
    

class Empleado(BaseModel):
    """
    Modelo que representa la tabla empleado.
    """

    id_empleado = models.AutoField(
        primary_key=True,
        db_column="id_empleado"
    )

    id_cargo = models.ForeignKey(
        Cargo,
        on_delete=models.DO_NOTHING,
        db_column="id_cargo",
        verbose_name="Cargo"
    )

    identificacion = models.CharField(
        max_length=20,
        unique=True,
        db_column="identificacion"
    )

    nombre = models.CharField(
        max_length=100,
        db_column="nombre"
    )

    apellido1 = models.CharField(
        max_length=100,
        db_column="apellido1"
    )

    apellido2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="apellido2"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column="telefono"
    )

    correo = models.EmailField(
        max_length=150,
        blank=True,
        null=True,
        db_column="correo"
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="direccion"
    )

    fecha_ingreso = models.DateField(
        blank=True,
        null=True,
        db_column="fecha_ingreso"
    )

    class Meta:
        managed = False
        db_table = "empleado"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def __str__(self):
        return f"{self.nombre} {self.apellido1}"    