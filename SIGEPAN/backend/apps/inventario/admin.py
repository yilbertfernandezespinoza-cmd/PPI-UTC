from django.contrib import admin

from .models import Inventario



@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):


    list_display = (

        "id_inventario",

        "producto",

        "sucursal",

        "stock_actual",

        "stock_minimo",

        "stock_maximo",

        "estado"

    )


    list_filter = (

        "sucursal",

        "estado",

    )


    search_fields = (

        "producto__nombre",

        "sucursal__nombre",

    )


    readonly_fields = (

        "stock_actual",

        "fecha_creacion",

        "fecha_actualizacion",

    )


    ordering = (

        "producto",

    )