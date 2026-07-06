from django import forms
from .models import Rol, Permiso


class RolForm(forms.ModelForm):
    """
    Formulario para la gestión de Roles.
    """

    class Meta:
        model = Rol
        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del rol",
                }
            ),
            "descripcion": forms.Textarea(
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

class PermisoForm(forms.ModelForm):

    class Meta:
        model = Permiso

        fields = [
            "id_modulo",
            "accion",
            "descripcion",
            "estado",
        ]

        widgets = {
            "id_modulo": forms.Select(attrs={"class": "form-select"}),
            "accion": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }        

