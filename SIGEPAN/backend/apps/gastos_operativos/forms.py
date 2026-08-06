from django import forms
from django.utils import timezone


CATEGORIAS_SUGERIDAS = [
    "Alquiler",
    "Servicios públicos (agua, luz, internet)",
    "Salarios y planilla",
    "Mantenimiento de equipo",
    "Insumos de limpieza",
    "Publicidad y marketing",
    "Transporte y combustible",
    "Otro",
]


class GastoOperativoForm(forms.Form):
    """
    Formulario para registrar un gasto operativo (RF-026).

    Se usa forms.Form (no ModelForm) porque los campos que en verdad se
    piden al usuario (sucursal, usuario, caja) se resuelven en el
    Service a partir del usuario autenticado y de si tiene una caja
    abierta — no se le piden a la persona que registra el gasto.
    """

    categoria = forms.ChoiceField(
        choices=[(valor, valor) for valor in CATEGORIAS_SUGERIDAS],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Categoría",
    )

    descripcion = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: pago de recibo de electricidad de julio",
        }),
        label="Descripción",
    )

    monto = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        label="Monto (₡)",
    )

    fecha_gasto = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Fecha del gasto",
    )

    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Observaciones",
    )

    # Agregado 06-08 (RF-026): comprobante como archivo real (foto/PDF),
    # opcional. Mismo patrón que `AyudaForm.imagen`: ImageField/FileField
    # en el form aunque la columna real (`comprobante`) sea un varchar con
    # la ruta — la conversión la hace `_resolver_ruta_comprobante` en
    # views.py, no el form.
    comprobante = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        label="Comprobante (foto o PDF)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.initial.get("fecha_gasto"):
            self.initial["fecha_gasto"] = timezone.localtime(
                timezone.now()
            ).strftime("%Y-%m-%dT%H:%M")
