from django.urls import path

from .views import MermaCreateView, MermaDetailView, MermaListView

app_name = "mermas"

urlpatterns = [
    path("", MermaListView.as_view(), name="listar"),
    path("registrar/", MermaCreateView.as_view(), name="registrar"),
    path("<int:id_merma>/", MermaDetailView.as_view(), name="detalle"),
]
