# Formularios del módulo
from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['identificacion', 'nombre', 'contacto', 'telefono', 'correo', 'direccion', 'estado']
        labels = {
            'identificacion': 'Identificación',
            'nombre': 'Nombre',
            'contacto': 'Contacto',
            'telefono': 'Teléfono',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
        }
