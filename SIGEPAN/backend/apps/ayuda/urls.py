from django.urls import path

from apps.ayuda.views import (
    AyudaListView,
    AyudaCreateView,
    AyudaUpdateView,
    AyudaDisableView,
)

app_name = "ayuda"

urlpatterns = [
    path(
        "",
        AyudaListView.as_view(),
        name="list",
    ),

    path(
        "crear/",
        AyudaCreateView.as_view(),
        name="create",
    ),

    path(
        "editar/<int:id_ayuda>/",
        AyudaUpdateView.as_view(),
        name="update",
    ),

    path(
        "deshabilitar/<int:id_ayuda>/",
        AyudaDisableView.as_view(),
        name="disable",
    ),
]