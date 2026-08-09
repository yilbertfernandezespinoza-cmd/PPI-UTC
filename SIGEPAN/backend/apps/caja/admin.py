from django.contrib import admin

from .models import (
    Caja,
    AperturaCaja,
    MovimientoCaja,
    ArqueoCaja,
    CierreCaja
)



# =====================================================
# INLINE MOVIMIENTOS
# =====================================================

class MovimientoCajaInline(admin.TabularInline):

    model = MovimientoCaja

    extra = 0

    readonly_fields = (

        "fecha_movimiento",
        "fecha_creacion",

    )



# =====================================================
# ADMIN CAJA
# =====================================================

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):


    list_display = (

        "id_caja",
        "nombre",
        "sucursal",
        "saldo_inicial",
        "saldo_actual",
        "estado"

    )


    list_filter = (

        "estado",
        "sucursal",

    )


    search_fields = (

        "nombre",

    )


    readonly_fields = (

        "fecha_creacion",
        "fecha_actualizacion",

    )





# =====================================================
# ADMIN APERTURA CAJA
# =====================================================

@admin.register(AperturaCaja)
class AperturaCajaAdmin(admin.ModelAdmin):


    list_display = (

        "id_apertura",
        "caja",
        "usuario",
        "fecha_apertura",
        "monto_inicial",
        "estado"

    )


    list_filter = (

        "estado",
        "fecha_apertura",

    )


    search_fields = (

        "caja__nombre",

    )


    readonly_fields = (

        "fecha_creacion",

    )


    inlines = [

        MovimientoCajaInline

    ]





# =====================================================
# ADMIN MOVIMIENTO CAJA
# =====================================================

@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):


    list_display = (

        "id_movimiento",
        "apertura",
        "usuario",
        "tipo_movimiento",
        "monto",
        "fecha_movimiento"

    )


    list_filter = (

        "tipo_movimiento",
        "fecha_movimiento",

    )


    search_fields = (

        "descripcion",
        "apertura__caja__nombre",

    )


    readonly_fields = (

        "fecha_creacion",

    )


# =====================================================
# ADMIN ARQUEO CAJA
# =====================================================

@admin.register(ArqueoCaja)
class ArqueoCajaAdmin(admin.ModelAdmin):


    list_display = (

        "id_arqueo",
        "apertura",
        "usuario",
        "fecha_arqueo",
        "saldo_sistema",
        "saldo_contado",
        "diferencia"

    )


    list_filter = (

        "fecha_arqueo",

    )


    search_fields = (

        "apertura__caja__nombre",

    )


    readonly_fields = (

        "fecha_creacion",

    )


# =====================================================
# ADMIN CIERRE CAJA
# =====================================================

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):


    list_display = (

        "id_cierre",
        "apertura",
        "usuario",
        "fecha_cierre",
        "monto_inicial",
        "monto_final",
        "diferencia"

    )


    list_filter = (

        "fecha_cierre",

    )


    search_fields = (

        "apertura__caja__nombre",

    )


    readonly_fields = (

        "fecha_creacion",

    )