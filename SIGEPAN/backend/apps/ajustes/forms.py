from django import forms
from django.utils import timezone

from .models import Ajuste


class AjusteForm(forms.ModelForm):
    """
    Formulario para registrar un ajuste de inventario (RF-018).

    El queryset de `producto` se restringe en la vista según el tipo de
    ajuste y la sucursal del usuario (una SALIDA solo puede ofrecer
    productos con inventario existente; una ENTRADA puede ofrecer
    cualquier producto activo).
    """

    class Meta:
        model = Ajuste
        fields = [
            "producto",
            "tipo",
            "cantidad",
            "motivo",
            "fecha",
            "observaciones",
        ]
        widgets = {
            "producto": forms.Select(
                attrs={"class": "form-select"}
            ),
            "tipo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "cantidad": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "1"}
            ),
            "motivo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: conteo físico no coincide con el sistema...",
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
