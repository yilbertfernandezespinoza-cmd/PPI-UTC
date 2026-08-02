from django.contrib import admin

from .models import Inventario


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):

    list_display = (
        "id_inventario",
        "id_producto",
        "id_sucursal",
        "stock_actual",
        "stock_minimo",
        "stock_maximo",
        "estado",
    )

    list_filter = (
        "id_sucursal",
        "estado",
    )

    search_fields = (
        "id_producto__nombre",
        "id_sucursal__nombre",
    )

    readonly_fields = (
        "stock_actual",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    ordering = (
        "id_producto",
    )