# =====================================================
# SIGEPAN - Módulo: Ventas
# Archivo: forms.py
# =====================================================
#
# Este módulo NO tiene formularios Django activos.
#
# Hasta el 04-08-2026 aquí vivían VentaForm, DetalleVentaForm,
# DetallePagoForm y los inlineformset_factory (DetalleVentaFormSet /
# DetallePagoFormSet), usados por el POS (crear_venta.html) para armar el
# carrito con inputs ocultos tipo "detalle-0-producto", "detalle-0-cantidad",
# etc. Ese enfoque resultó extremadamente frágil: bug de método de pago con
# código de texto en vez de PK real, bug de "agregarAlCarritoDirecto" no
# existente al reanudar una venta pausada y, finalmente, un bug persistente
# de "id_detalle_venta: Este campo es obligatorio" en el formset al guardar
# una venta pendiente — que sobrevivió incluso forzando required=False
# explícitamente sobre el campo de la PK vía un mixin
# (_FormSetPkOpcionalMixin, ya eliminado).
#
# Se decidió abandonar los formsets para el carrito del POS y migrar a un
# flujo JSON/AJAX: el carrito vive como un array de JavaScript (fuente de
# verdad única en el navegador) y se envía completo en un solo fetch() con
# Content-Type: application/json a apps.ventas.views.procesar_venta, que lo
# valida y recalcula todo (precios, impuesto, total) en el servidor sin
# depender de formsets ni de nombres de campo indexados.
#
# Ver apps/ventas/views.py::procesar_venta para el contrato JSON completo.
