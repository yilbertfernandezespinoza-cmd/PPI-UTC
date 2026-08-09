from django.contrib import admin

from .models import (
    Compra,
    DetalleCompra
)



# =====================================================
# DETALLE COMPRA INLINE
# =====================================================

class DetalleCompraInline(admin.TabularInline):


    model = DetalleCompra


    extra = 1


    readonly_fields = (

        "subtotal",

    )



# =====================================================
# ADMIN COMPRA
# =====================================================

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):


    list_display = (

        "id_compra",

        "proveedor",

        "usuario",

        "fecha",

        "total",

        "estado"

    )


    list_filter = (

        "estado",

        "fecha",

    )


    search_fields = (

        "id_compra",

        "proveedor__nombre",

    )


    readonly_fields = (

        "fecha_creacion",

        "fecha_actualizacion",

    )


    inlines = [

        DetalleCompraInline

    ]



# =====================================================
# ADMIN DETALLE COMPRA
# =====================================================

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):


    list_display = (

        "id_detalle_compra",

        "compra",

        "producto",

        "cantidad",

        "precio_unitario",

        "subtotal"

    )


    search_fields = (

        "compra__id_compra",

        "producto__nombre",

    )