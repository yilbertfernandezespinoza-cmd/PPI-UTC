from django import forms

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import Rol, Permiso, Usuario
from .services import UsuarioService

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

    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirme la contraseña",
            }
        ),
    )

    class Meta:
        model = Usuario

        fields = [
            "id_empleado",
            "id_rol",
            "id_sucursal",
            "password",
            "estado",
        ]

        widgets = {
            "id_empleado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "id_rol": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "id_sucursal": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:

            self.fields["id_empleado"].disabled = True

            self.fields["password"].required = False
            self.fields["confirmar_password"].required = False

            self.fields["password"].initial = ""

            self.fields["password"].widget.attrs[
                "placeholder"
            ] = (
                "Dejar vacío para conservar "
                "la contraseña actual"
            )

    def clean_id_empleado(self):

        empleado = self.cleaned_data["id_empleado"]

        if not empleado.correo:

            raise forms.ValidationError(
                "El empleado debe tener un correo "
                "registrado antes de crear un usuario."
            )

        usuarios = Usuario.objects.filter(
            id_empleado=empleado
        )

        if self.instance and self.instance.pk:

            usuarios = usuarios.exclude(
                pk=self.instance.pk
            )

        if usuarios.exists():

            raise forms.ValidationError(
                "El empleado ya tiene una cuenta "
                "de usuario asignada."
            )

        return empleado

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")

        confirmar_password = cleaned_data.get(
            "confirmar_password"
        )

        if not self.instance.pk and not password:

            self.add_error(
                "password",
                "Debe ingresar una contraseña inicial."
            )

        if password:

            if password != confirmar_password:

                self.add_error(
                    "confirmar_password",
                    "Las contraseñas no coinciden."
                )

            else:

                validate_password(password)

        return cleaned_data

    def save(self, commit=True):

        usuario = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if not usuario.pk:

            usuario.username = (
                UsuarioService.generar_username(
                    usuario.id_empleado
                )
            )

        if password:

            usuario.password = make_password(
                password
            )

        else:

            usuario.password = (
                Usuario.objects
                .get(pk=usuario.pk)
                .password
            )

        if commit:

            usuario.save()

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

class RecuperarPasswordForm(forms.Form):
    """
    Formulario para solicitar la recuperación de contraseña.
    """

    identificador = forms.CharField(
        label="Usuario o correo electrónico",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su usuario o correo",
                "autocomplete": "off",
            }
        ),
    )


class RestablecerPasswordForm(forms.Form):
    """
    Formulario para establecer una nueva contraseña.
    """

    password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese la nueva contraseña",
            }
        ),
    )

    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirme la nueva contraseña",
            }
        ),
    )

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get(
            "confirmar_password"
        )

        if password and confirmar_password:

            if password != confirmar_password:

                raise forms.ValidationError(
                    "Las contraseñas no coinciden."
                )

            validate_password(password)

        return cleaned_data
    

