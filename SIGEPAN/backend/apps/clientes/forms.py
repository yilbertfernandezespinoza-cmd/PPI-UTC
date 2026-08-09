# Formularios del módulo
from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'identificacion', 'nombre', 'apellido1', 'apellido2',
            'telefono', 'correo', 'direccion', 'estado'
        ]
        labels = {
            'identificacion': 'Identificación',
            'nombre': 'Nombre',
            'apellido1': 'Primer Apellido',
            'apellido2': 'Segundo Apellido',
            'telefono': 'Teléfono',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
        }
