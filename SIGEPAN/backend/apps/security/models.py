from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.base_models import BaseModel

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para SIGEPAN.
    """

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )

    fotografia = models.ImageField(
        upload_to="usuarios/",
        blank=True,
        null=True,
        verbose_name="Fotografía"
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Usuario"

        verbose_name_plural = "Usuarios"

    def __str__(self):

        return self.get_full_name() or self.username
    
class Rol(BaseModel):
    """
    Modelo que representa la tabla rol de la base de datos.
    """

    id_rol = models.AutoField(
        primary_key=True,
        db_column="id_rol"
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

    class Meta:
        managed = False
        db_table = "rol"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
    

class Permiso(BaseModel):
    """
    Modelo que representa la tabla permiso.
    """

    id_permiso = models.AutoField(
        primary_key=True,
        db_column="id_permiso"
    )

    id_modulo = models.ForeignKey(
        "configuracion.Modulo",
        on_delete=models.DO_NOTHING,
        db_column="id_modulo",
        verbose_name="Módulo"
    )

    accion = models.CharField(
        max_length=50,
        db_column="accion",
        verbose_name="Acción"
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion",
        verbose_name="Descripción"
    )

    class Meta:
        managed = False
        db_table = "permiso"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["accion"]

    def __str__(self):
        return f"{self.id_modulo} - {self.accion}" 
    
class Permiso(BaseModel):
    """
    Modelo para la gestión de permisos del sistema.
    """

    id_permiso = models.AutoField(
        primary_key=True,
        db_column="id_permiso"
    )

    modulo = models.ForeignKey(
        "configuracion.Modulo",
        on_delete=models.DO_NOTHING,
        db_column="id_modulo",
        verbose_name="Módulo"
    )

    accion = models.CharField(
        max_length=50,
        db_column="accion",
        verbose_name="Acción"
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="descripcion",
        verbose_name="Descripción"
    )

    class Meta:
        managed = False
        db_table = "permiso"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["modulo", "accion"]

    def __str__(self):
        return f"{self.modulo} - {self.accion}"    