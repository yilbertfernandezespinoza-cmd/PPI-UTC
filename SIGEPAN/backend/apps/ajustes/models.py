from django.db import models


class Ajuste(models.Model):
    """
    Modelo que representa la tabla ajuste (RF-018).

    Igual que Merma: NO hereda BaseModel porque la tabla real no tiene
    columnas `estado` ni `fecha_actualizacion` — un ajuste es un registro
    histórico de una corrección de inventario ya aplicada, no una entidad
    editable después de creada. managed=False (Database First).
    """

    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada (incrementa stock)"
        SALIDA = "SALIDA", "Salida (reduce stock)"

    id_ajuste = models.AutoField(
        primary_key=True,
        db_column="id_ajuste",
    )

    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        db_column="id_producto",
        verbose_name="Producto",
    )

    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario",
        verbose_name="Usuario",
    )

    cantidad = models.IntegerField(
        db_column="cantidad",
        verbose_name="Cantidad",
    )

    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        db_column="tipo",
        verbose_name="Tipo de ajuste",
    )

    motivo = models.CharField(
        max_length=255,
        db_column="motivo",
        verbose_name="Motivo",
    )

    fecha = models.DateTimeField(
        db_column="fecha",
        verbose_name="Fecha",
    )

    observaciones = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="observaciones",
        verbose_name="Observaciones",
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        db_column="fecha_creacion",
        verbose_name="Fecha de creación",
    )

    class Meta:
        managed = False
        db_table = "ajuste"
        verbose_name = "Ajuste de inventario"
        verbose_name_plural = "Ajustes de inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Ajuste #{self.id_ajuste} — {self.get_tipo_display()} de {self.producto} ({self.cantidad})"
