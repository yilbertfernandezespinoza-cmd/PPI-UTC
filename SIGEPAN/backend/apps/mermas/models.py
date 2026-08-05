from django.db import models


class Merma(models.Model):
    """
    Modelo que representa la tabla merma (RF-017).

    A diferencia de la mayoría de modelos del proyecto, NO hereda de
    BaseModel: la tabla real (database/ddl) no tiene columnas `estado` ni
    `fecha_actualizacion` — una merma es un registro histórico de una
    pérdida ya ocurrida, no una entidad que se active/desactive ni se
    edite después de creada. Coherente con managed=False (Database First,
    mismo patrón que Venta/Compra): la tabla ya existe, Django no la
    gestiona.
    """

    id_merma = models.AutoField(
        primary_key=True,
        db_column="id_merma",
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
        db_table = "merma"
        verbose_name = "Merma"
        verbose_name_plural = "Mermas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Merma #{self.id_merma} — {self.producto} ({self.cantidad})"
