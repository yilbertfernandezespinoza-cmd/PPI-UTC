from django.test import TestCase

from .forms import AjusteForm
from .models import Ajuste


class AjusteFormTests(TestCase):
    """
    Pruebas de validación del formulario de ajustes que no requieren base
    de datos. Correr con: python manage.py test apps.ajustes
    """

    def test_cantidad_cero_no_es_valida(self):
        form = AjusteForm(data={
            "cantidad": 0,
            "tipo": Ajuste.Tipo.ENTRADA,
            "motivo": "Conteo físico",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("cantidad", form.errors)

    def test_tipo_invalido_no_es_valido(self):
        form = AjusteForm(data={
            "cantidad": 5,
            "tipo": "OTRO",
            "motivo": "Conteo físico",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("tipo", form.errors)

    def test_motivo_es_obligatorio(self):
        form = AjusteForm(data={
            "cantidad": 5,
            "tipo": Ajuste.Tipo.SALIDA,
            "motivo": "",
            "fecha": "2026-08-04T10:00",
        })
        form.is_valid()
        self.assertIn("motivo", form.errors)
