# Formularios del módulo
from django import forms
from .models import Categoria


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

        if not nombre:
            raise forms.ValidationError(
                "El nombre de la categoría es obligatorio."
            )

        existe = Categoria.objects.filter(
            nombre__iexact=nombre
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe una categoría con ese nombre."
            )

        return nombre