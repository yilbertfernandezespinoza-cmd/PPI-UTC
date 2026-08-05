from django import forms
from .models import Producto


UNIDADES_MEDIDA = [
    ('Unidad', 'Unidad'),
    ('Kilogramo', 'Kilogramo (kg)'),
    ('Gramo', 'Gramo (g)'),
    ('Litro', 'Litro (L)'),
    ('Mililitro', 'Mililitro (ml)'),
    ('Docena', 'Docena'),
    ('Paquete', 'Paquete'),
    ('Caja', 'Caja'),
]


class ProductoForm(forms.ModelForm):

    imagen = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        })
    )

    unidad_medida = forms.ChoiceField(
        choices=UNIDADES_MEDIDA,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'precio_compra',
            'porcentaje_utilidad', 'porcentaje_impuesto', 'unidad_medida',
            'precio_venta', 'imagen', 'estado', 'id_categoria'
        ]

        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio_compra': 'Precio de compra (₡)',
            'precio_venta': 'Precio de venta (₡)',
            'porcentaje_utilidad': 'Porcentaje de utilidad (%)',
            'porcentaje_impuesto': 'Porcentaje de impuesto (%)',
            'unidad_medida': 'Unidad de medida',
            'imagen': 'Imagen',
            'id_categoria': 'Categoría',
        }

        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. PROD-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del producto'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'id': 'id_precio_compra'
            }),
            'porcentaje_utilidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'id': 'id_porcentaje_utilidad'
            }),
            'porcentaje_impuesto': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'id': 'id_porcentaje_impuesto'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'id': 'id_precio_venta',
                'readonly': True
            }),
            'id_categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }