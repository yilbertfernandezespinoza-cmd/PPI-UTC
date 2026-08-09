from django.db import models
from apps.categorias.models import Categoria

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        db_column="id_categoria",
        related_name="productos"
    )
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_utilidad = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=13.00)
    unidad_medida = models.CharField(max_length=30, default="Unidad")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
