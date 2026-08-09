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