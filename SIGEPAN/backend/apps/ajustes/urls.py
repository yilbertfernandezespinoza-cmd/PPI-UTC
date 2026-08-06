from django.urls import path

from .views import (
    AjusteCreateView,
    AjusteDetailView,
    AjusteListView,
    productos_disponibles_ajuste,
)

app_name = "ajustes"

urlpatterns = [
    path("", AjusteListView.as_view(), name="listar"),
    path("registrar/", AjusteCreateView.as_view(), name="registrar"),
    path("productos-disponibles/", productos_disponibles_ajuste, name="productos_disponibles"),
    path("<int:id_ajuste>/", AjusteDetailView.as_view(), name="detalle"),
]
