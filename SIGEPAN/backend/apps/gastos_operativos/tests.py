from decimal import Decimal

from django.test import TestCase

from .forms import GastoOperativoForm


class GastoOperativoFormTests(TestCase):
    """
    Pruebas de validación del formulario de gastos operativos que no
    requieren base de datos. Correr con:
    python manage.py test apps.gastos_operativos
    """

    def test_monto_cero_no_es_valido(self):
        form = GastoOperativoForm(data={
            "categoria": "Alquiler",
            "descripcion": "Pago de alquiler de agosto",
            "monto": "0",
            "fecha_gasto": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("monto", form.errors)

    def test_monto_negativo_no_es_valido(self):
        form = GastoOperativoForm(data={
            "categoria": "Alquiler",
            "descripcion": "Pago de alquiler de agosto",
            "monto": "-100",
            "fecha_gasto": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("monto", form.errors)

    def test_gasto_valido_pasa_validacion(self):
        form = GastoOperativoForm(data={
            "categoria": "Alquiler",
            "descripcion": "Pago de alquiler de agosto",
            "monto": "150000.00",
            "fecha_gasto": "2026-08-04T10:00",
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["monto"], Decimal("150000.00"))
