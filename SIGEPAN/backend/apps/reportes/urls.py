from django.urls import path

from .views import (
    ReporteVentasView,
    ReporteInventarioView,
    ReporteTributarioView,
    ReporteUtilidadView,
)

app_name = "reportes"

urlpatterns = [

    path("ventas/", ReporteVentasView.as_view(), name="ventas"),
    path("inventario/", ReporteInventarioView.as_view(), name="inventario"),
    path("tributario/", ReporteTributarioView.as_view(), name="tributario"),
    path("utilidad/", ReporteUtilidadView.as_view(), name="utilidad"),

]