from django.urls import path

from .views import (
    ModuloListView,
    ModuloCreateView,
    ModuloUpdateView,
    SucursalListView,
    SucursalCreateView,
    SucursalUpdateView,
    MetodoPagoListView,
    MetodoPagoCreateView,
    MetodoPagoUpdateView,
    ConfiguracionTributariaListView,
    ConfiguracionTributariaCreateView,
    ConfiguracionTributariaUpdateView,
    DatosEmpresaView,

)

app_name = "configuracion"

urlpatterns = [

    path(
        "modulos/",
        ModuloListView.as_view(),
        name="modulo_list"
    ),

    path(
        "modulos/nuevo/",
        ModuloCreateView.as_view(),
        name="modulo_create"
    ),

    path(
        "modulos/<int:id_modulo>/editar/",
        ModuloUpdateView.as_view(),
        name="modulo_update"
    ),

    path(
        "sucursales/",
        SucursalListView.as_view(),
        name="sucursal_list"
    ),

    path(
        "sucursales/nuevo/",
        SucursalCreateView.as_view(),
        name="sucursal_create"
    ),

    path(
        "sucursales/<int:id_sucursal>/editar/",
        SucursalUpdateView.as_view(),
        name="sucursal_update"
    ),
    path(
        "metodos-pago/",
        MetodoPagoListView.as_view(),
        name="metodo_pago_list"
    ),

    path(
        "metodos-pago/nuevo/",
        MetodoPagoCreateView.as_view(),
        name="metodo_pago_create"
    ),

    path(
        "metodos-pago/<int:id_metodo_pago>/editar/",
        MetodoPagoUpdateView.as_view(),
        name="metodo_pago_update"
    ),

    path(
        "tributaria/",
        ConfiguracionTributariaListView.as_view(),
        name="tributaria_list"
    ),

    path(
        "tributaria/nueva/",
        ConfiguracionTributariaCreateView.as_view(),
        name="tributaria_create"
    ),

    path(
        "tributaria/<int:id_configuracion_tributaria>/editar/",
        ConfiguracionTributariaUpdateView.as_view(),
        name="tributaria_update"
    ),

    path(
        "datos-empresa/",
        DatosEmpresaView.as_view(),
        name="datos_empresa"
    ),
       
]