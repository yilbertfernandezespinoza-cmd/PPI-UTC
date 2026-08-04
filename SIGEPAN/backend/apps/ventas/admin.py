from django.contrib import admin

from .models import (
    Venta,
    DetalleVenta,
    DetallePago
)


# =====================================================
# DETALLE VENTA INLINE
# =====================================================

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = (
        "subtotal",
    )


# =====================================================
# DETALLE PAGO INLINE
# =====================================================

class DetallePagoInline(admin.TabularInline):
    model = DetallePago
    extra = 0


# =====================================================
# ADMIN VENTA
# =====================================================

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        "numero_venta",
        "cliente",
        "usuario",
        "caja",
        "total",
        "estado",
        "fecha"
    )

    list_filter = (
        "estado",
        "tipo_comprobante",
        "fecha",
        "caja__sucursal"
    )

    search_fields = (
        "numero_venta",
        "cliente__nombre",
        "cliente__identificacion"
    )

    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
        "subtotal",
        "impuesto",
        "descuento",
        "total"
    )

    inlines = [
        DetalleVentaInline,
        DetallePagoInline
    ]


# =====================================================
# ADMIN DETALLE VENTA
# =====================================================

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = (
        "venta",
        "producto",
        "cantidad",
        "precio_unitario",
        "subtotal"
    )

    search_fields = (
        "venta__numero_venta",
        "producto__nombre"
    )


# =====================================================
# ADMIN DETALLE PAGO
# =====================================================

@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = (
        "venta",
        "metodo_pago",
        "monto",
        "referencia",
        "fecha_creacion"
    )

    search_fields = (
        "venta__numero_venta",
        "referencia"
    )