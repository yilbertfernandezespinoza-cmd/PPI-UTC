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

        ]


        widgets = {


            "producto": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),


            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "precio_unitario": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control"
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
                    "class": "form-control"
                }
            ),


            "referencia": forms.TextInput(
                attrs={
                    "class": "form-control"
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