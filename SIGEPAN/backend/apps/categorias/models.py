from django.db import models

class Categoria(models.Model):

    id_categoria = models.AutoField(primary_key=True,db_column="id_categoria")
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255,blank=True,null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categoria"   # <--  nombre exacto de la tabla en sigepan_db
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre