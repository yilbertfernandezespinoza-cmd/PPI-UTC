# Formularios del módulo
from django import forms

from .models import Inventario



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