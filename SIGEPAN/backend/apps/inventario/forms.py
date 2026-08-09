# Formularios del módulo
from django import forms

from apps.productos.models import Producto
from apps.configuracion.models import Sucursal

from .models import Inventario, TipoMovimientoInventario


# =====================================================
# FORMULARIO INVENTARIO
# =====================================================

class InventarioForm(forms.ModelForm):

    class Meta:

        model = Inventario

        fields = [
            "stock_minimo",
            "stock_maximo",
            "ubicacion",
            "estado"
        ]

        widgets = {

            "stock_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0
                }
            ),

            "stock_maximo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0
                }
            ),

            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: Bodega principal"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            )
        }


# =====================================================
# FORMULARIO ENTRADA DE INVENTARIO (RF-028)
# =====================================================

class MovimientoInventarioForm(forms.Form):

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        label="Producto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.filter(estado=True).order_by("nombre"),
        label="Sucursal",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    tipo_movimiento = forms.ModelChoiceField(
        queryset=TipoMovimientoInventario.objects.filter(
            estado=True,
            nombre__in=[
                "ENTRADA_COMPRA",
                "AJUSTE_POSITIVO",
                "DEVOLUCION_VENTA",
                "TRASLADO_ENTRADA",
            ],
        ).order_by("nombre"),
        label="Tipo de movimiento",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )

    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )