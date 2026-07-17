from django.urls import path

from . import views



app_name = "compras"



urlpatterns = [


    # =====================================================
    # LISTADO DE COMPRAS
    # =====================================================

    path(

        "",

        views.lista_compras,

        name="lista_compras"

    ),



    # =====================================================
    # CREAR COMPRA
    # =====================================================

    path(

        "crear/",

        views.crear_compra,

        name="crear_compra"

    ),



    # =====================================================
    # DETALLE COMPRA
    # =====================================================

    path(

        "<int:id_compra>/",

        views.detalle_compra,

        name="detalle_compra"

    ),



    # =====================================================
    # ANULAR COMPRA
    # =====================================================

    path(

        "<int:id_compra>/anular/",

        views.anular_compra,

        name="anular_compra"

    ),


]