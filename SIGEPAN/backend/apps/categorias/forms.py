# Formularios del módulo
from django import forms
from .models import Categoria
from .services import CategoriaService


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Panadería, Repostería, Bebidas'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción breve de la categoría'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()

        # La regla de unicidad vive en el service (CategoriaService.
        # validar_nombre_unico) para que no se duplique la consulta
        # entre el formulario y cualquier otro llamador que no pase por
        # este form (por ejemplo, un futuro endpoint). django.forms.
        # ValidationError es la misma clase que django.core.exceptions.
        # ValidationError, así que se propaga tal cual y queda asociada
        # al campo "nombre" igual que antes.
        CategoriaService.validar_nombre_unico(
            nombre,
            excluir_id=self.instance.pk,
        )

        return nombre