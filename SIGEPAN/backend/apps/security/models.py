from django.db import models
from apps.core.base_models import BaseModel

class Usuario(BaseModel):
    """
    Modelo que representa la tabla usuario.
    """

    id_usuario = models.AutoField(
        primary_key=True,
        db_column="id_usuario"
    )

    id_empleado = models.ForeignKey(
        "empleados.Empleado",
        on_delete=models.DO_NOTHING,
        db_column="id_empleado",
        verbose_name="Empleado"
    )

    id_rol = models.ForeignKey(
        "security.Rol",
        on_delete=models.DO_NOTHING,
        db_column="id_rol",
        verbose_name="Rol"
    )

    id_sucursal = models.ForeignKey(
        "configuracion.Sucursal",
        on_delete=models.DO_NOTHING,
        db_column="id_sucursal",
        blank=True,
        null=True,
        verbose_name="Sucursal"
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        db_column="username"
    )

    password = models.CharField(
        max_length=255,
        db_column="password"
    )

    email = models.EmailField(
        max_length=150,
        blank=True,
        null=True,
        unique=True,
        db_column="email"
    )

    google_email = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=True,
        db_column="google_email"
    )

    google_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_column="google_id"
    )

    google_token = models.TextField(
        blank=True,
        null=True,
        db_column="google_token"
    )

    ultimo_acceso = models.DateTimeField(
        blank=True,
        null=True,
        db_column="ultimo_acceso"
    )

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

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
        db_table = "permiso"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["accion"]

    def __str__(self):
        return f"{self.id_modulo.nombre} - {self.accion}" 
    