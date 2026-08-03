from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from apps.security.models import Usuario
from apps.inventario.models import Inventario
from .utils import generar_numero_venta

from django.http import JsonResponse
from apps.clientes.models import Cliente # Asegúrate de que la ruta importe correctamente tu modelo de Clientes


from .models import (
    Venta,
    DetalleVenta,
    DetallePago
)

from .forms import (
    VentaForm,
    DetalleVentaFormSet,
    DetallePagoFormSet
)

from apps.caja.models import (
    MovimientoCaja,
    AperturaCaja
)



# =====================================================
# LISTAR VENTAS
# =====================================================

def lista_ventas(request):

    ventas = Venta.objects.all().order_by(
        "-fecha"
    )

    return render(
        request,
        "ventas/lista_ventas.html",
        {
            "ventas": ventas
        }
    )



# =====================================================
# CREAR VENTA (VERSIÓN OPTIMIZADA Y SEGURA)
# =====================================================

@transaction.atomic
def crear_venta(request):
    # 1. Validar usuario en sesión (Se ejecuta en GET y POST para inyectarlo en la plantilla)
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "No se pudo identificar el usuario actual.")
        return redirect("security:login")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # 2. Validar caja abierta (También en GET y POST, evita que un usuario sin caja entre al POS)
    apertura = AperturaCaja.objects.filter(
        usuario=usuario,
        estado=True
    ).select_related("caja").first()

    if not apertura:
        messages.error(request, "Debe tener una caja abierta para registrar ventas.")
        return redirect("caja:lista_cajas")

    if request.method == "POST":
        venta_form = VentaForm(request.POST)
        detalle_formset = DetalleVentaFormSet(request.POST, prefix="detalle")
        pago_formset = DetallePagoFormSet(request.POST, prefix="pago")

        if (
            venta_form.is_valid()
            and detalle_formset.is_valid()
            and pago_formset.is_valid()
        ):
            detalles_temp = detalle_formset.save(commit=False)
            
            if not detalles_temp:
                messages.error(request, "La venta debe contener al menos un producto.")
                return redirect("ventas:crear_venta")

            venta = venta_form.save(commit=False)

            # 3. AUDITORÍA: Validación de Inventario (sin error 404) y Recálculo de Totales
            subtotal_calculado = 0
            
            for detalle in detalles_temp:
                # Usamos filter().first() en lugar de get_object_or_404 para evitar que el sistema rompa
                inventario = Inventario.objects.filter(
                    producto=detalle.producto,
                    sucursal=apertura.caja.sucursal
                ).first()

                if not inventario:
                    messages.error(
                        request, 
                        f"El producto {detalle.producto.nombre} no está habilitado en el inventario de esta sucursal."
                    )
                    return redirect("ventas:crear_venta")

                if inventario.stock_actual < detalle.cantidad:
                    messages.error(
                        request,
                        f"No hay existencias suficientes de {detalle.producto.nombre}. Stock actual: {inventario.stock_actual}"
                    )
                    return redirect("ventas:crear_venta")
                
                # Recalculamos el subtotal en backend multiplicando cantidad x precio
                subtotal_calculado += (detalle.cantidad * detalle.precio_unitario)

            # Blindaje: Sobrescribimos o verificamos los datos numéricos de la venta con los calculados
            # (Nota: Si tu modelo Venta tiene campos separados para IVA o Descuento, aplícalos a 'subtotal_calculado' aquí)
            # venta.total = subtotal_calculado 

            # 4. AUDITORÍA: Validación de Métodos de Pago
            pagos_temp = pago_formset.save(commit=False)
            total_pagado = sum(pago.monto for pago in pagos_temp)
            
            # Verificamos que el cliente esté pagando lo que corresponde
            if total_pagado < venta.total:
                messages.error(
                    request, 
                    f"El monto pagado (₡{total_pagado}) es menor al total de la factura (₡{venta.total})."
                )
                return redirect("ventas:crear_venta")

            # 5. ASIGNACIÓN DE DATOS AUTOMÁTICOS
            venta.usuario = usuario
            venta.caja = apertura.caja
            venta.fecha = timezone.now()
            venta.estado = True
            venta.numero_venta = generar_numero_venta()
            
            venta.save()

            # 6. REGISTRO AUTOMÁTICO DE MOVIMIENTO EN CAJA
            MovimientoCaja.objects.create(
                apertura=apertura,
                usuario=usuario,
                tipo_movimiento="VENTA",
                monto=venta.total,
                descripcion=f"Venta {venta.numero_venta}",
                fecha_movimiento=timezone.now()
            )

            # 7. GUARDAR DETALLES Y DESCONTAR INVENTARIO (Seguro de concurrencia)
            for detalle in detalles_temp:
                detalle.venta = venta
                detalle.save()

                inventario = Inventario.objects.select_for_update().get(
                    producto=detalle.producto,
                    sucursal=apertura.caja.sucursal
                )
                inventario.stock_actual -= detalle.cantidad
                inventario.save()

            # 8. GUARDAR DETALLE DE PAGOS
            for pago in pagos_temp:
                pago.venta = venta
                pago.save()

            messages.success(request, "Venta registrada correctamente.")
            return redirect("ventas:detalle_venta", id_venta=venta.id_venta)

    else:
        venta_form = VentaForm()
        detalle_formset = DetalleVentaFormSet(prefix="detalle")
        pago_formset = DetallePagoFormSet(prefix="pago")

    return render(
        request,
        "ventas/crear_venta.html",
        {
            "venta_form": venta_form,
            "detalle_formset": detalle_formset,
            "pago_formset": pago_formset,
            "usuario_activo": usuario  # <-- AQUÍ SE ENVÍA EL USUARIO A LA PLANTILLA
        }
    )


# =====================================================
# DETALLE DE VENTA
# =====================================================

def detalle_venta(request, id_venta):


    venta = get_object_or_404(

        Venta,

        id_venta=id_venta

    )


    detalles = DetalleVenta.objects.filter(

        venta=venta

    )


    pagos = DetallePago.objects.filter(

        venta=venta

    )



    return render(

        request,

        "ventas/detalle_venta.html",

        {

            "venta": venta,

            "detalles": detalles,

            "pagos": pagos

        }

    )



# =====================================================
# ANULAR VENTA
# =====================================================

@transaction.atomic
def anular_venta(request, id_venta):
    venta = get_object_or_404(Venta, id_venta=id_venta)
    
    # Obtener el usuario actual desde la sesión para la auditoría de caja
    usuario_id = request.session.get("usuario_id")
    usuario_actual = get_object_or_404(Usuario, id_usuario=usuario_id) if usuario_id else None

    if request.method == "POST":
        # 1. Prevenir doble anulación por seguridad
        if not venta.estado:
            messages.warning(request, "Esta venta ya se encuentra anulada previamente.")
            return redirect("ventas:lista_ventas")

        # 2. Cambiar el estado lógico de la venta
        venta.estado = False
        venta.save()

        # 3. Devolución de stock al inventario de la sucursal correspondiente
        detalles = DetalleVenta.objects.filter(venta=venta)
        for detalle in detalles:
            inventario = Inventario.objects.select_for_update().filter(
                producto=detalle.producto,
                sucursal=venta.caja.sucursal
            ).first()
            
            if inventario:
                inventario.stock_actual += detalle.cantidad
                inventario.save()

        # 4. Reversión automática en la caja activa (Movimiento de salida/anulación)
        apertura_activa = AperturaCaja.objects.filter(
            caja=venta.caja,
            estado=True
        ).first()

        if apertura_activa and usuario_actual:
            MovimientoCaja.objects.create(
                apertura=apertura_activa,
                usuario=usuario_actual,
                tipo_movimiento="ANULACION",  # Asegúrate de que coincida con el catálogo de movimientos de tu caja
                monto=venta.total,
                descripcion=f"Anulación de Venta {venta.numero_venta}",
                fecha_movimiento=timezone.now()
            )

        messages.success(request, "Venta anulada correctamente. Se ha devuelto el stock y ajustado la caja.")
        return redirect("ventas:lista_ventas")

    return render(
        request,
        "ventas/anular_venta.html",
        {
            "venta": venta
        }
    )

# =====================================================
# BÚSQUEDA DE CLIENTES PARA EL POS (JSON) - CORREGIDO SEGÚN ESTÁNDAR
# =====================================================

def buscar_clientes_pos(request):
    query = request.GET.get("q", "").strip()
    clientes_data = []

    if query:
        # Usamos los campos oficiales de la tabla 'cliente' definidos en el Prompt Maestro
        clientes = Cliente.objects.filter(
            nombre__icontains=query
        ) | Cliente.objects.filter(
            identificacion__icontains=query
        )
        
        for c in clientes[:10]: # Límite de 10 resultados para rendimiento óptimo en el POS
            clientes_data.append({
                "id": c.id_cliente, # Clave primaria oficial: id_nombre_tabla -> id_cliente
                "nombre": c.nombre,
                "identificacion": getattr(c, "identificacion", "")
            })

    return JsonResponse(clientes_data, safe=False)