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
    # PROCESAR VENTA (JSON/AJAX) — COBRAR O PAUSAR
    # ==========================================
    # Reemplaza el POST clásico de crear_venta() (formset) y a
    # guardar_venta_pendiente(). El carrito del POS se envía completo como
    # JSON (ver apps/ventas/views.py::procesar_venta para el contrato).
    path(
        "procesar/",
        views.procesar_venta,
        name="procesar_venta"
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
    # VENTAS PENDIENTES (LISTAR / RETOMAR / ELIMINAR)
    # ==========================================
    # "pausar" ya no es una vista propia con URL/GET (pausar_venta) ni un
    # POST con formset (guardar_venta_pendiente): ahora es la acción
    # "pausar" de procesar_venta(). Se confirmó por grep que ningún
    # template referenciaba pausar_venta antes de eliminarla.
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