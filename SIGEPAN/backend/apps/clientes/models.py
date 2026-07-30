from django.db import models

from apps.core.base_models import BaseModel


class Cliente(BaseModel):
    """
    Modelo que representa la tabla cliente.
    """

    class TipoCliente(models.TextChoices):
        FISICA = "FISICA", "Persona Física"
        JURIDICA = "JURIDICA", "Persona Jurídica"

    class TipoIdentificacion(models.TextChoices):
        CEDULA_FISICA = "CF", "Cédula Física"
        CEDULA_JURIDICA = "CJ", "Cédula Jurídica"
        DIMEX = "DIMEX", "DIMEX"
        PASAPORTE = "PASS", "Pasaporte"

    id_cliente = models.AutoField(
        primary_key=True,
        db_column="id_cliente",
    )

    tipo_cliente = models.CharField(
        max_length=10,
        choices=TipoCliente.choices,
        default=TipoCliente.FISICA,
        db_column="tipo_cliente",
        verbose_name="Tipo de cliente",
    )

    tipo_identificacion = models.CharField(
        max_length=10,
        choices=TipoIdentificacion.choices,
        default=TipoIdentificacion.CEDULA_FISICA,
        db_column="tipo_identificacion",
        verbose_name="Tipo de identificación",
    )

    identificacion = models.CharField(
        max_length=20,
        unique=True,
        db_column="identificacion",
        verbose_name="Identificación",
    )

    nombre = models.CharField(
        max_length=100,
        db_column="nombre",
        verbose_name="Nombre / Razón Social",
    )

    apellido1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="apellido1",
        verbose_name="Primer apellido",
    )

    apellido2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="apellido2",
        verbose_name="Segundo apellido",
    )

    telefono = models.CharField(
        max_length=20,
        db_column="telefono",
        verbose_name="Teléfono",
    )

    correo = models.EmailField(
        max_length=150,
        db_column="correo",
        verbose_name="Correo electrónico",
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column="direccion",
        verbose_name="Dirección",
    )

    class Meta:
        db_table = "cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = [
            "nombre",
            "apellido1",
        ]

    @property
    def nombre_completo(self):
        """
        Devuelve el nombre completo del cliente.
        Si es persona jurídica devuelve únicamente la razón social.
        """

        if self.tipo_cliente == self.TipoCliente.JURIDICA:
            return self.nombre

        return " ".join(
            filtro
            for filtro in [
                self.nombre,
                self.apellido1,
                self.apellido2,
            ]
            if filtro
        )

    @property
    def es_persona_fisica(self):
        """
        Indica si el cliente es una persona física.
        """
        return self.tipo_cliente == self.TipoCliente.FISICA

    @property
    def es_persona_juridica(self):
        """
        Indica si el cliente es una persona jurídica.
        """
        return self.tipo_cliente == self.TipoCliente.JURIDICA

    def __str__(self):
        return self.nombre_completo