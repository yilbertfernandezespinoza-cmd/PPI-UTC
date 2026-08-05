# Formularios del módulo
from django import forms
from .models import Modulo, Sucursal, MetodoPago, ConfiguracionTributaria, DatosEmpresa


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

class MetodoPagoForm(forms.ModelForm):

    class Meta:
        model = MetodoPago

        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: Efectivo, Tarjeta, SINPE Móvil",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción del método de pago",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()

        existe = MetodoPago.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise forms.ValidationError(
                "Ya existe un método de pago con ese nombre."
            )

        return nombre


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

class DatosEmpresaForm(forms.ModelForm):

    class Meta:
        model = DatosEmpresa

        fields = [
            "nombre_comercial",
            "cedula_juridica",
            "regimen_tributario",
            "direccion_fiscal",
            "telefono",
            "correo",
        ]

        widgets = {
            "nombre_comercial": forms.TextInput(attrs={"class": "form-control"}),
            "cedula_juridica": forms.TextInput(attrs={"class": "form-control"}),
            "regimen_tributario": forms.Select(attrs={"class": "form-control"}),
            "direccion_fiscal": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
        }        