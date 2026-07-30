from django import forms

from .models import Cliente
from .validators import (
    validar_identificacion,
    validar_telefono,
    normalizar_correo,
)


class ClienteForm(forms.ModelForm):
    """
    Formulario para la gestión de Clientes.
    """

    class Meta:
        model = Cliente

        fields = [
            "tipo_cliente",
            "tipo_identificacion",
            "identificacion",
            "nombre",
            "apellido1",
            "apellido2",
            "telefono",
            "correo",
            "direccion",
            "estado",
        ]

        widgets = {

            "tipo_cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "tipo_identificacion": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "identificacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),

            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "apellido1": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "apellido2": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "8",
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "direccion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_identificacion(self):
        """
        Valida la identificación según el tipo seleccionado.
        """

        identificacion = self.cleaned_data.get(
            "identificacion"
        )

        tipo = self.cleaned_data.get(
            "tipo_identificacion"
        )

        return validar_identificacion(
            tipo,
            identificacion,
        )

    def clean_telefono(self):
        """
        Valida el teléfono.
        """

        telefono = self.cleaned_data.get(
            "telefono"
        )

        return validar_telefono(
            telefono
        )

    def clean_correo(self):
        """
        Normaliza el correo electrónico.
        """

        correo = self.cleaned_data.get(
            "correo"
        )

        return normalizar_correo(
            correo
        )

    def clean(self):
        """
        Reglas de negocio del formulario.
        """

        cleaned_data = super().clean()

        tipo_cliente = cleaned_data.get(
            "tipo_cliente"
        )

        tipo_identificacion = cleaned_data.get(
            "tipo_identificacion"
        )

        apellido1 = cleaned_data.get(
            "apellido1"
        )

        if (
            tipo_cliente
            == Cliente.TipoCliente.FISICA
        ):

            if not apellido1:

                self.add_error(
                    "apellido1",
                    "El primer apellido es obligatorio."
                )

            if tipo_identificacion == Cliente.TipoIdentificacion.CEDULA_JURIDICA:

                self.add_error(
                    "tipo_identificacion",
                    "Una persona física no puede utilizar una cédula jurídica."
                )

        if (
            tipo_cliente
            == Cliente.TipoCliente.JURIDICA
        ):

            if tipo_identificacion != Cliente.TipoIdentificacion.CEDULA_JURIDICA:

                self.add_error(
                    "tipo_identificacion",
                    "Una persona jurídica únicamente puede utilizar una cédula jurídica."
                )

            cleaned_data["apellido1"] = ""
            cleaned_data["apellido2"] = ""

        return cleaned_data