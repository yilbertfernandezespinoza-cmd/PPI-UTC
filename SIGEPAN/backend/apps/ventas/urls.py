from django.urls import path

from . import views


app_name = "ventas"



urlpatterns = [

    # ==========================================
    # LISTADO DE VENTAS
    # ==========================================

    path(
        "",
        views.lista_ventas,
        name="lista_ventas"
    ),



    # ==========================================
    # CREAR VENTA
    # ==========================================

    path(
        "crear/",
        views.crear_venta,
        name="crear_venta"
    ),



    # ==========================================
    # DETALLE DE VENTA
    # ==========================================

    path(
        "<int:id_venta>/",
        views.detalle_venta,
        name="detalle_venta"
    ),



    # ==========================================
    # ANULAR VENTA
    # ==========================================

    path(
        "<int:id_venta>/anular/",
        views.anular_venta,
        name="anular_venta"
    ),

]