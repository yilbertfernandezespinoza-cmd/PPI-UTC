# Formularios del módulo
from django import forms
from .models import Modulo


class ModuloForm(forms.ModelForm):

    class Meta:
        model = Modulo

        fields = [
            "nombre",
            "descripcion",
            "icono",
            "ruta",
            "orden_menu",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "icono": forms.TextInput(attrs={"class": "form-control"}),
            "ruta": forms.TextInput(attrs={"class": "form-control"}),
            "orden_menu": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }