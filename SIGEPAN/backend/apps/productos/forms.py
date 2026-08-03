from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'precio_compra', 
            'porcentaje_utilidad', 'porcentaje_impuesto', 'unidad_medida', 
            'precio_venta', 'imagen', 'estado', 'id_categoria'
        ]
        
        # CORRECCIÓN: labels ahora está dentro de la clase Meta
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
            # No definimos label para estado porque lo mostraremos manualmente según tu indicación
        }

        # CORRECCIÓN: Implementación obligatoria de widgets (Regla 4 y 5)
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
                'step': '0.01'
            }),
            'porcentaje_utilidad': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'step': '0.01'
            }),
            'porcentaje_impuesto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'step': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'step': '0.01',
                'readonly': True  # Usualmente en sistemas POS esto se calcula automático por JS (Compra + Utilidad + Impuesto)
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            'id_categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }