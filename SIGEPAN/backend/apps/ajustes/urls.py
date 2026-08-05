from django.urls import path

from .views import AjusteCreateView, AjusteDetailView, AjusteListView

app_name = "ajustes"

urlpatterns = [
    path("", AjusteListView.as_view(), name="listar"),
    path("registrar/", AjusteCreateView.as_view(), name="registrar"),
    path("<int:id_ajuste>/", AjusteDetailView.as_view(), name="detalle"),
]
