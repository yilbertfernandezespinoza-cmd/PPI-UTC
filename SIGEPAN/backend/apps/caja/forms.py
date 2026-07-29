from django import forms

from .models import (
    Caja,
    AperturaCaja,
    MovimientoCaja,
    ArqueoCaja,
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

        }

        
# =====================================================
# APERTURA CAJA
# =====================================================

class AperturaCajaForm(forms.ModelForm):


    class Meta:

        model = AperturaCaja


        fields = [

            "monto_inicial",
            "observaciones"

        ]


        widgets = {


            "monto_inicial": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese monto inicial"
                }
            ),


            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones de apertura"
                }
            )


        }


    # =========================================
    # VALIDAR MONTO INICIAL
    # =========================================

    def clean_monto_inicial(self):

        monto = self.cleaned_data.get(
            "monto_inicial"
        )


        if monto is None:

            raise forms.ValidationError(
                "Debe ingresar un monto inicial."
            )


        if monto < 0:

            raise forms.ValidationError(
                "El monto inicial no puede ser negativo."
            )


        return monto



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
                    "class": "form-control",
                    "step": "0.01"
                }
            ),


            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            )

        }


    # =========================================
    # VALIDAR MONTO DEL MOVIMIENTO
    # =========================================

    def clean_monto(self):

        monto = self.cleaned_data.get(
            "monto"
        )


        if monto is None:

            raise forms.ValidationError(
                "Debe ingresar un monto."
            )


        if monto <= 0:

            raise forms.ValidationError(
                "El monto debe ser mayor que cero."
            )


        return monto

    # =========================================
    # VALIDAR TIPO DE MOVIMIENTO
    # =========================================

    def clean_tipo_movimiento(self):

        tipo = self.cleaned_data.get(
            "tipo_movimiento"
        )


        tipos_validos = [

            "VENTA",
            "INGRESO",
            "RETIRO",
            "GASTO",
            "AJUSTE"

        ]


        if tipo not in tipos_validos:

            raise forms.ValidationError(
                "Tipo de movimiento no permitido."
            )


        return tipo

# =====================================================
# ARQUEO CAJA
# =====================================================

class ArqueoCajaForm(forms.ModelForm):


    class Meta:

        model = ArqueoCaja


        fields = [

            "saldo_contado",

            "observaciones"

        ]


        widgets = {


            "saldo_contado": forms.NumberInput(

                attrs={

                    "class": "form-control",

                    "step": "0.01",

                    "placeholder": "Ingrese efectivo contado"

                }

            ),


            "observaciones": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3,

                    "placeholder": "Detalle cualquier diferencia encontrada..."

                }

            )

        }



    def clean_saldo_contado(self):

        saldo = self.cleaned_data.get(
            "saldo_contado"
        )


        if saldo is None:

            raise forms.ValidationError(
                "Debe ingresar el monto contado físicamente."
            )


        if saldo < 0:

            raise forms.ValidationError(
                "El monto contado no puede ser negativo."
            )


        return saldo


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
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Ingrese efectivo contado"
                }
            ),


            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Detalle cualquier diferencia encontrada..."
                }
            )

        }


    # =========================================
    # VALIDAR MONTO FINAL
    # =========================================

    def clean_monto_final(self):

        monto = self.cleaned_data.get(
            "monto_final"
        )


        if monto is None:

            raise forms.ValidationError(
                "Debe ingresar el monto contado físicamente."
            )


        if monto < 0:

            raise forms.ValidationError(
                "El monto final no puede ser negativo."
            )


        return monto