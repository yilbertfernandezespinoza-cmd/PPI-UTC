from django import forms
from .models import Rol, Permiso, Usuario
from django.contrib.auth.hashers import make_password


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



class UsuarioForm(forms.ModelForm):

    class Meta:
        model = Usuario

        fields = [
            "id_empleado",
            "id_rol",
            "id_sucursal",
            "username",
            "password",
            "email",
            "google_email",
            "google_id",
            "google_token",
            "estado",
        ]

        widgets = {
            "id_empleado": forms.Select(attrs={"class": "form-select"}),
            "id_rol": forms.Select(attrs={"class": "form-select"}),
            "id_sucursal": forms.Select(attrs={"class": "form-select"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "google_email": forms.EmailInput(attrs={"class": "form-control"}),
            "google_id": forms.TextInput(attrs={"class": "form-control"}),
            "google_token": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def save(self, commit=True):

        usuario = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if self.instance and self.instance.pk:

            if password:
                usuario.password = make_password(password)

            else:
                usuario.password = (
                    Usuario.objects
                    .get(pk=self.instance.pk)
                    .password
                )

        else:

            usuario.password = make_password(password)

        if commit:
            usuario.save()

        return usuario
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:

            self.fields["password"].required = False
            self.fields["password"].initial = ""

            self.fields["password"].widget.attrs[
                "placeholder"
            ] = "Dejar vacío para conservar la contraseña actual"
    

class LoginForm(forms.Form):

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su usuario",
                "autocomplete": "off",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su contraseña",
            }
        ),
    )   

