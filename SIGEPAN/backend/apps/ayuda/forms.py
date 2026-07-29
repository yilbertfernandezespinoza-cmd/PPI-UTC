from django import forms

from apps.ayuda.models import Ayuda
from apps.configuracion.models import Modulo


class AyudaForm(forms.ModelForm):
    """
    Formulario para el mantenimiento de ayudas.
    """

    class Meta:
        model = Ayuda

        fields = [
            "modulo",
            "pantalla",
            "titulo",
            "contenido",
            "icono",
            "orden",
        ]

        widgets = {
            "modulo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "pantalla": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 100,
                }
            ),
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 200,
                }
            ),
            "contenido": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                }
            ),
            "icono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 50,
                }
            ),
            "orden": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["modulo"].queryset = (
            Modulo.objects.filter(
                estado=True
            ).order_by("nombre")
        )

        self.fields["modulo"].empty_label = (
            "Seleccione un módulo"
        )