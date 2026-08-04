from django.urls import path

from . import views


app_name = "inventario"


urlpatterns = [

    # =====================================================
    # LISTADO INVENTARIO
    # =====================================================

    path(
        "",
        views.lista_inventario,
        name="lista_inventario"
    ),

    # =====================================================
    # ENTRADA DE INVENTARIO (RF-028)
    # =====================================================

    path(
        "entrada/",
        views.EntradaInventarioView.as_view(),
        name="entrada_inventario"
    ),

    # =====================================================
    # HISTORIAL DE MOVIMIENTOS (RF-028)
    # =====================================================

    path(
        "movimientos/",
        views.MovimientosInventarioListView.as_view(),
        name="lista_movimientos"
    ),

    # =====================================================
    # DETALLE INVENTARIO
    # =====================================================

    path(
        "<int:id_inventario>/",
        views.detalle_inventario,
        name="detalle_inventario"
    ),

    # =====================================================
    # EDITAR INVENTARIO
    # =====================================================

    path(
        "<int:id_inventario>/editar/",
        views.editar_inventario,
        name="editar_inventario"
    ),

]