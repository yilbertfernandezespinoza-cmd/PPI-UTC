from django.db import models

class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True, db_column='id_proveedor')
    identificacion = models.CharField(max_length=20, unique=True, null=True, blank=True, db_column='identificacion')
    nombre = models.CharField(max_length=150, null=True, blank=True, db_column='nombre')
    contacto = models.CharField(max_length=100, null=True, blank=True, db_column='contacto')
    telefono = models.CharField(max_length=20, null=True, blank=True, db_column='telefono')
    correo = models.CharField(max_length=150, null=True, blank=True, db_column='correo')
    direccion = models.CharField(max_length=255, null=True, blank=True, db_column='direccion')
    estado = models.BooleanField(default=True, db_column='estado')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')

    class Meta:
        db_table = "proveedor"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"

