from django import forms

from .models import (
    Caja,
    AperturaCaja,
    MovimientoCaja,
    CierreCaja
)



# =====================================================
# FORMULARIO CAJA
# =====================================================

class CajaForm(forms.ModelForm):

    class Meta:

        model = Caja

        fields = [

            "sucursal",
            "nombre",
            "descripcion",
            "saldo_inicial",
            "saldo_actual",
            "estado"

        ]


        widgets = {


            "sucursal": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),


            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),


            "saldo_inicial": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "saldo_actual": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            )

        }




# =====================================================
# APERTURA CAJA
# =====================================================

class AperturaCajaForm(forms.ModelForm):


    class Meta:


        model = AperturaCaja


        fields = [

            "caja",
            "monto_inicial",
            "observaciones"

        ]


        widgets = {


            "caja": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),


            "monto_inicial": forms.NumberInput(
                attrs={
                    "class": "form-control"
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
# MOVIMIENTO CAJA
# =====================================================

class MovimientoCajaForm(forms.ModelForm):


    class Meta:


        model = MovimientoCaja


        fields = [

            "tipo_movimiento",
            "monto",
            "descripcion"

        ]


        widgets = {


            "tipo_movimiento": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),


            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            )

        }




# =====================================================
# CIERRE CAJA
# =====================================================

class CierreCajaForm(forms.ModelForm):


    class Meta:


        model = CierreCaja


        fields = [

            "monto_final",
            "observaciones"

        ]


        widgets = {


            "monto_final": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            )

        }