from django.db import models

from apps.core.base_models import BaseModel


class GastoOperativo(BaseModel):
    """
    Modelo que representa la tabla gasto_operativo (RF-026).

    A diferencia de Merma/Ajuste, esta tabla real SÍ tiene `estado` y
    `fecha_actualizacion` (columnas iguales a las que ya provee
    BaseModel), así que sí puede heredar de BaseModel — permite
    deshabilitar un gasto cargado por error sin borrar el registro,
    igual que Categoria/Cliente. managed=False (Database First): la
    tabla ya existe, Django no la gestiona ni requiere migración.
    """

    id_gasto = models.AutoField(
        primary_key=True,
        db_column="id_gasto",
    )

    sucursal = models.ForeignKey(
        "configuracion.Sucursal",
        on_delete=models.PROTECT,
        db_column="id_sucursal",
        verbose_name="Sucursal",
    )

    usuario = models.ForeignKey(
        "security.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario",
        verbose_name="Usuario",
    )

    caja = models.ForeignKey(
        "caja.Caja",
        on_delete=models.PROTECT,
        db_column="id_caja",
        null=True,
        blank=True,
        verbose_name="Caja",
        help_text=(
            "Solo se asigna si el gasto se registra mientras hay una caja "
            "abierta; en ese caso también genera un movimiento de caja "
            "tipo GASTO que afecta el saldo real."
        ),
    )

    descripcion = models.CharField(
        max_length=255,
        db_column="descripcion",
        verbose_name="Descripción",
    )

    categoria = models.CharField(
        max_length=100,
        db_column="categoria",
        verbose_name="Categoría",
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="monto",
        verbose_name="Monto",
    )

    fecha_gasto = models.DateTimeField(
        db_column="fecha_gasto",
        verbose_name="Fecha del gasto",
    )

    observaciones = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="observaciones",
        verbose_name="Observaciones",
    )

    class Meta:
        managed = False
        db_table = "gasto_operativo"
        verbose_name = "Gasto operativo"
        verbose_name_plural = "Gastos operativos"
        ordering = ["-fecha_gasto"]

    def __str__(self):
        return f"{self.categoria}: {self.descripcion} (₡{self.monto})"
