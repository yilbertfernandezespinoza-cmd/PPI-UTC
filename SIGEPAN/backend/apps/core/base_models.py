from django.db import models


class BaseModel(models.Model):
    """
    Modelo base para todas las entidades de SIGEPAN.
    Contiene los campos comunes de auditoría.
    """

    estado = models.BooleanField(
        default=True,
        verbose_name="Estado",
        help_text="Indica si el registro está activo."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    class Meta:
        abstract = True