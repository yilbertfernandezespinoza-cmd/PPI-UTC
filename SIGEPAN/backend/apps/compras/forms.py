from django import forms
from django.forms import inlineformset_factory

from .models import (
    Compra,
    DetalleCompra
)



# =====================================================
# FORMULARIO COMPRA
# =====================================================

class CompraForm(forms.ModelForm):


    class Meta:

        model = Compra

        fields = [

            "proveedor",
            "total",
            "observaciones"

        ]


        widgets = {


            "proveedor": forms.Select(

                attrs={

                    "class": "form-select"

                }

            ),



            "total": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01"

                }

            ),



            "observaciones": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3

                }

            )

        }





# =====================================================
# FORMULARIO DETALLE COMPRA
# =====================================================

class DetalleCompraForm(forms.ModelForm):


    class Meta:


        model = DetalleCompra


        fields = [

            "producto",
            "cantidad",
            "precio_unitario"

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

                    "min": 1

                }

            ),



            "precio_unitario": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01"

                }

            )

        }




# =====================================================
# FORMSET DETALLE COMPRA
# =====================================================

DetalleCompraFormSet = inlineformset_factory(

    Compra,

    DetalleCompra,

    form=DetalleCompraForm,

    extra=1,

    can_delete=True

)