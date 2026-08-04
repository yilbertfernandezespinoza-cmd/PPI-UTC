from django import forms
from django.forms import inlineformset_factory

from .models import (
    Venta,
    DetalleVenta,
    DetallePago
)


# =====================================================
# FORMULARIO VENTA
# =====================================================

class VentaForm(forms.ModelForm):

    class Meta:
        model = Venta
        fields = [
            "cliente",
            "tipo_comprobante",
            "metodo_pago",
        ]
        widgets = {
            "cliente": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "tipo_comprobante": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "metodo_pago": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }


# =====================================================
# DETALLE VENTA
# =====================================================

class DetalleVentaForm(forms.ModelForm):

    class Meta:
        model = DetalleVenta
        fields = [
            "producto",
            "cantidad",
            "precio_unitario",
            "subtotal",
        ]
        widgets = {
            "producto": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1"
                }
            ),
            "precio_unitario": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),
            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),
        }


# =====================================================
# DETALLE PAGO
# =====================================================

class DetallePagoForm(forms.ModelForm):

    class Meta:
        model = DetallePago
        fields = [
            "metodo_pago",
            "monto",
            "referencia"
        ]
        widgets = {
            "metodo_pago": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),
            "referencia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nº de referencia o voucher (opcional)"
                }
            ),
        }


# =====================================================
# FORMSETS
# =====================================================

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True
)


DetallePagoFormSet = inlineformset_factory(
    Venta,
    DetallePago,
    form=DetallePagoForm,
    extra=1,
    can_delete=True
)