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

    google_refresh_token = models.TextField(
        blank=True,
        null=True,
        db_column="google_refresh_token"
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

class RolPermiso(models.Model):
    """
    Modelo que representa la tabla rol_permiso.
    """

    id_rol_permiso = models.AutoField(
        primary_key=True,
        db_column="id_rol_permiso"
    )

    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.DO_NOTHING,
        db_column="id_rol",
        verbose_name="Rol"
    )

    id_permiso = models.ForeignKey(
        Permiso,
        on_delete=models.DO_NOTHING,
        db_column="id_permiso",
        verbose_name="Permiso"
    )

    fecha_creacion = models.DateTimeField(
        db_column="fecha_creacion",
        auto_now_add=True,
    )

    class Meta:
        db_table = "rol_permiso"
        verbose_name = "Rol - Permiso"
        verbose_name_plural = "Roles - Permisos"

    def __str__(self):
        return f"{self.id_rol} - {self.id_permiso}"

class LogAcciones(models.Model):

    id_log = models.AutoField(
        primary_key=True,
        db_column="id_log"
    )

    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column="id_usuario"
    )

    id_modulo = models.ForeignKey(
        "configuracion.Modulo",
        on_delete=models.DO_NOTHING,
        db_column="id_modulo"
    )

    TIPO_ACCIONES = [
        ("LOGIN", "LOGIN"),
        ("LOGOUT", "LOGOUT"),
        ("CREAR", "CREAR"),
        ("MODIFICAR", "MODIFICAR"),
        ("ELIMINAR", "ELIMINAR"),
        ("CONSULTAR","CONSULTAR"),
        ("EXPORTAR","EXPORTAR"),
        ("IMPORTAR","IMPORTAR"),
        ("ERROR","ERROR"),
        ("ACCESO_DENEGADO","ACCESO DENEGADO"),
        ("RECUPERAR_PASSWORD","RECUPERAR CONTRASEÑA"),
        ("CAMBIAR_PASSWORD","CAMBIAR CONTRASEÑA"),
        # Agregado 06-08 (RF-034): antes se reutilizaba "LOGOUT" para
        # registrar un cambio de usuario, lo cual mezclaba en la bitácora
        # un cierre de sesión real con un cambio de usuario. Requiere
        # correr el ALTER TABLE de log_acciones (ver nota técnica) antes
        # de usar este valor contra la BD real.
        ("CAMBIAR_USUARIO","CAMBIAR USUARIO"),
    ]

    tipo_accion = models.CharField(
        max_length=20,
        choices=TIPO_ACCIONES,
        db_column="tipo_accion"
    )

    descripcion = models.CharField(
        max_length=500,
        db_column="descripcion"
    )

    ip_origen = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        db_column="ip_origen"
    )

    navegador = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_column="navegador"
    )

    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        db_column="fecha_hora"
    )

    class Meta:
        db_table = "log_acciones"
        verbose_name = "Log de acciones"
        verbose_name_plural = "Logs de acciones"    