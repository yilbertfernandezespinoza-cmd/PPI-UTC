from django import forms
from .models import Cargo, Empleado


class CargoForm(forms.ModelForm):

    class Meta:
        model = Cargo

        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
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


class EmpleadoForm(forms.ModelForm):

    class Meta:
        model = Empleado

        fields = [
            "id_cargo",
            "identificacion",
            "nombre",
            "apellido1",
            "apellido2",
            "telefono",
            "correo",
            "direccion",
            "fecha_ingreso",
            "estado",
        ]

        widgets = {
            "id_cargo": forms.Select(attrs={"class": "form-select"}),

            "identificacion": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "apellido1": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "apellido2": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "telefono": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "correo": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "direccion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "fecha_ingreso": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }        