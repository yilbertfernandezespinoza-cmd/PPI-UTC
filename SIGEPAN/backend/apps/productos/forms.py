# Formularios del módulo
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'precio_compra', 'porcentaje_utilidad',
          'porcentaje_impuesto', 'unidad_medida', 'precio_venta', 'imagen',
          'estado', 'id_categoria']

    labels = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio_compra': 'Precio de compra',
            'precio_venta': 'Precio de venta',
            'porcentaje_utilidad': 'Porcentaje de utilidad',
            'porcentaje_impuesto': 'Porcentaje de impuesto',
            'unidad_medida': 'Unidad de medida',
            'imagen': 'Imagen',
            'id_categoria': 'Categoría',
            #  no definimos label para estado porque lo mostraremos manualmente
        }