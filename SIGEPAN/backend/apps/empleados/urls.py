from django.urls import path

from .views import (
    CargoListView,
    CargoCreateView,
    CargoUpdateView,
    EmpleadoListView,
    EmpleadoCreateView,
    EmpleadoUpdateView,
)

app_name = "empleados"

urlpatterns = [
    path(
        "cargos/",
        CargoListView.as_view(),
        name="cargo_list",
    ),

    path(
        "cargos/nuevo/",
        CargoCreateView.as_view(),
        name="cargo_create",
    ),

    path(
        "cargos/<int:id_cargo>/editar/",
        CargoUpdateView.as_view(),
        name="cargo_update",
    ),

    path(
    "empleados/",
    EmpleadoListView.as_view(),
    name="empleado_list",
        ),

    path(
    "empleados/nuevo/",
    EmpleadoCreateView.as_view(),
    name="empleado_create",
    ),

    path(
    "empleados/<int:id_empleado>/editar/",
    EmpleadoUpdateView.as_view(),
    name="empleado_update",
    ),
]

