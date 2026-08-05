from django.db import models

from apps.core.base_models import BaseModel
from apps.configuracion.models import Modulo


class Ayuda(BaseModel):
    """
    Modelo que representa las ayudas contextuales del sistema.
    """

    id_ayuda = models.AutoField(
        primary_key=True,
        db_column="id_ayuda"
    )

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.PROTECT,
        db_column="id_modulo",
        related_name="ayudas",
        verbose_name="Módulo",
    )

    pantalla = models.CharField(
        max_length=100,
        verbose_name="Pantalla"
    )

    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )

    contenido = models.TextField(
        verbose_name="Contenido"
    )

    icono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ícono"
    )

    imagen = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="imagen",
        verbose_name="Imagen"
    )

    orden = models.PositiveIntegerField(
        default=1,
        verbose_name="Orden"
    )

    class Meta:
        # La tabla `ayuda` ya existe en la BD real (Database First, igual
        # que el resto del sistema) con la FK a `modulo` correctamente
        # aplicada. La migración 0001_initial.py de esta app quedó
        # desincronizada (se generó cuando el campo todavía era un
        # IntegerField `id_modulo`, antes de convertirse en el ForeignKey
        # `modulo` que hay ahora) — con managed=False, Django deja de
        # intentar reconciliar el modelo actual contra ese historial de
        # migración desactualizado.
        managed = False
        db_table = "ayuda"
        verbose_name = "Ayuda"
        verbose_name_plural = "Ayudas"
        ordering = ["modulo", "orden", "titulo"]
        constraints = [
            models.UniqueConstraint(
                fields=["modulo", "pantalla"],
                name="uk_ayuda_modulo_pantalla"
            )
        ]

    def __str__(self):
        return f"{self.modulo} - {self.titulo}"