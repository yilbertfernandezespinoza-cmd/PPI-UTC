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
    # BÚSQUEDA DE CLIENTES (AJAX)
    # ==========================================
    path(
        "clientes/buscar/",
        views.buscar_clientes_pos,
        name="buscar_clientes_pos"
    ),

    # ==========================================
    # VENTAS PENDIENTES (PAUSAR / RETOMAR / GUARDAR / ELIMINAR)
    # ==========================================
    path(
        "pendientes/",
        views.listar_ventas_pendientes,
        name="ventas_pendientes"
    ),
    # Alias añadido para solucionar el NoReverseMatch de 'lista_ventas_pausadas'
    path(
        "pendientes/",
        views.listar_ventas_pendientes,
        name="lista_ventas_pausadas"
    ),
    path(
        "guardar-pendiente/",
        views.guardar_venta_pendiente,
        name="guardar_venta_pendiente"
    ),
    path(
        "pausar/<int:id_venta>/",
        views.pausar_venta,
        name="pausar_venta"
    ),
    path(
        "retomar/<int:id_venta>/",
        views.retomar_venta,
        name="retomar_venta"
    ),
    path(
        "retomar/<int:id_venta>/",
        views.retomar_venta,
        name="reanudar_venta"
    ),
    path(
        "pendientes/eliminar/<int:id_venta>/",
        views.eliminar_venta_pendiente,
        name="eliminar_venta_pendiente"
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