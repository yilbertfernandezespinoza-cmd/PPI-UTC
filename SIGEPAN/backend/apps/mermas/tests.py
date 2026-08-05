from django.test import TestCase

from .forms import MermaForm


class MermaFormTests(TestCase):
    """
    Pruebas de validación del formulario de mermas que no requieren base
    de datos (no incluyen `producto`, que se valida contra la BD real).
    Correr con: python manage.py test apps.mermas
    """

    def test_cantidad_cero_no_es_valida(self):
        form = MermaForm(data={
            "cantidad": 0,
            "motivo": "Producto vencido",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("cantidad", form.errors)

    def test_cantidad_negativa_no_es_valida(self):
        form = MermaForm(data={
            "cantidad": -5,
            "motivo": "Producto vencido",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("cantidad", form.errors)

    def test_motivo_es_obligatorio(self):
        form = MermaForm(data={
            "cantidad": 3,
            "motivo": "",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("motivo", form.errors)
