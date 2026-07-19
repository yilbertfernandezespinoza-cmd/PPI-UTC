from django.urls import path

from . import views



app_name = "caja"



urlpatterns = [

    # ==========================================
    # LISTADO DE CAJAS
    # ==========================================

    path(
        "",
        views.lista_cajas,
        name="lista_cajas"
    ),



    # ==========================================
    # CREAR CAJA
    # ==========================================

    path(
        "crear/",
        views.crear_caja,
        name="crear_caja"
    ),



    # ==========================================
    # APERTURA DE CAJA
    # ==========================================

    path(
        "abrir/",
        views.abrir_caja,
        name="abrir_caja"
    ),



    # ==========================================
    # DETALLE DE CAJA ABIERTA
    # ==========================================

    path(
        "<int:id_apertura>/",
        views.detalle_caja,
        name="detalle_caja"
    ),



    # ==========================================
    # REGISTRAR MOVIMIENTO
    # ==========================================

    path(
        "<int:id_apertura>/movimiento/",
        views.movimiento_caja,
        name="movimiento_caja"
    ),



    # ==========================================
    # CERRAR CAJA
    # ==========================================

    path(
        "<int:id_apertura>/cerrar/",
        views.cerrar_caja,
        name="cerrar_caja"
    ),

]