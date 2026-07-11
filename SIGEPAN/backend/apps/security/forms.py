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

        print("===== UsuarioForm.save() =====")
        print("Password recibida:", self.cleaned_data.get("password"))

        usuario = super().save(commit=False)

        if usuario.password:
            print("Antes de encriptar:", usuario.password)
            usuario.password = make_password(usuario.password)
            print("Después de encriptar:", usuario.password)

        if commit:
            usuario.save()
            print("Usuario guardado")
        return usuario
    

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

