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
        "abrir/<int:id_caja>/",
        views.abrir_caja,
        name="abrir_caja"
    ),

    # ==========================================
    # EDITAR APERTURA DE CAJA
    # ==========================================

    path(
        "apertura/<int:id_apertura>/editar/",
        views.editar_apertura,
        name="editar_apertura"
    ),

    # =====================================================
    # ADMINISTRAR CAJA
    # =====================================================

    path(
        "administrar/<int:id_caja>/",
        views.administrar_caja,
        name="administrar_caja"
    ),

    # ==========================================
    # EDITAR CAJA
    # ==========================================

    path(
        "editar/<int:id_caja>/",
        views.editar_caja,
        name="editar_caja"
    ),

    # ==========================================
    # ACTIVAR / DESACTIVAR CAJA
    # ==========================================

    path(
        "activar/<int:id_caja>/",
        views.activar_caja,
        name="activar_caja"
    ),


    path(
        "desactivar/<int:id_caja>/",
        views.desactivar_caja,
        name="desactivar_caja"
    ),

    # ==========================================
    # DETALLE DE CAJA ABIERTA
    # ==========================================

    path(
        "detalle/<int:id_apertura>/",
        views.detalle_caja,
        name="detalle_caja"
    ),



    # ==========================================
    # REGISTRAR MOVIMIENTO
    # ==========================================

    path(
        "movimiento/<int:id_apertura>/",
        views.movimiento_caja,
        name="movimiento_caja"
    ),



    # ==========================================
    # ARQUEO DE CAJA
    # ==========================================

    path(
        "arqueo/<int:id_apertura>/",
        views.crear_arqueo,
        name="crear_arqueo"
    ),



    # ==========================================
    # CERRAR CAJA
    # ==========================================

    path(
        "cerrar/<int:id_apertura>/",
        views.cerrar_caja,
        name="cerrar_caja"
    ),

]