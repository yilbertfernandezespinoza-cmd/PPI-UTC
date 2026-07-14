from django.db import models

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    identificacion = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido1 = models.CharField(max_length=100, null=True, blank=True)
    apellido2 = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.CharField(max_length=150, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} {self.apellido1} {self.apellido2}"
