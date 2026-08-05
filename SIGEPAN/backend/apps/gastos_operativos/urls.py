from django.urls import path

from .views import (
    GastoOperativoCreateView,
    GastoOperativoDisableView,
    GastoOperativoListView,
)

app_name = "gastos_operativos"

urlpatterns = [
    path("", GastoOperativoListView.as_view(), name="listar"),
    path("registrar/", GastoOperativoCreateView.as_view(), name="registrar"),
    path("estado/<int:id_gasto>/", GastoOperativoDisableView.as_view(), name="estado"),
]
