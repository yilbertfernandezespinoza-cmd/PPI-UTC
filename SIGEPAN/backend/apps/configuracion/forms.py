# Formularios del módulo
from django import forms
from .models import Modulo, Sucursal, ConfiguracionTributaria


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

class SucursalForm(forms.ModelForm):

    class Meta:
        model = Sucursal

        fields = [
            "nombre",
            "direccion",
            "telefono",
            "encargado",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "encargado": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }    

class ConfiguracionTributariaForm(forms.ModelForm):

    class Meta:
        model = ConfiguracionTributaria

        fields = [
            "nombre",
            "descripcion",
            "porcentaje",
            "aplica_compras",
            "aplica_ventas",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: IVA",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción de la configuración tributaria",
                }
            ),
            "porcentaje": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "aplica_compras": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "aplica_ventas": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }            