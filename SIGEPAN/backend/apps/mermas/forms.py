from django import forms
from django.utils import timezone

from .models import Merma


class MermaForm(forms.ModelForm):
    """
    Formulario para registrar una merma (RF-017).

    No incluye `producto` como ModelChoiceField con todos los productos:
    se filtra a los productos con inventario en la sucursal del usuario
    para evitar registrar mermas de productos que la sucursal ni siquiera
    maneja. El filtrado real ocurre en la vista (ahí se conoce al usuario
    autenticado); aquí solo se define el widget.
    """

    class Meta:
        model = Merma
        fields = [
            "producto",
            "cantidad",
            "motivo",
            "fecha",
            "observaciones",
        ]
        widgets = {
            "producto": forms.Select(
                attrs={"class": "form-select"}
            ),
            "cantidad": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "1"}
            ),
            "motivo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: producto vencido, dañado en manipulación...",
                }
            ),
            "fecha": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "observaciones": forms.Textarea(
                attrs={"class": "form-control", "rows": 3},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fecha"].input_formats = ["%Y-%m-%dT%H:%M"]

        if not self.initial.get("fecha"):
            self.initial["fecha"] = timezone.localtime(
                timezone.now()
            ).strftime("%Y-%m-%dT%H:%M")

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")

        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        return cantidad
