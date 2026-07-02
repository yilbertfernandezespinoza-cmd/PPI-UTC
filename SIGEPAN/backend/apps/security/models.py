from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuario personalizado para SIGEPAN.
    """

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )

    fotografia = models.ImageField(
        upload_to="usuarios/",
        blank=True,
        null=True,
        verbose_name="Fotografía"
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Usuario"

        verbose_name_plural = "Usuarios"

    def __str__(self):

        return self.get_full_name() or self.username