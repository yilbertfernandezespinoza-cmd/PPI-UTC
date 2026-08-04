from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
import json

from apps.security.models import Usuario
from apps.inventario.models import Inventario
from apps.clientes.models import Cliente
from apps.configuracion.models import MetodoPago
from apps.caja.models import MovimientoCaja, AperturaCaja

from .models import Venta, DetalleVenta, DetallePago
from .forms import VentaForm, DetalleVentaFormSet, DetallePagoFormSet
from .utils import generar_numero_venta


# =====================================================
# LISTAR VENTAS
# =====================================================

def lista_ventas(request):
    ventas = Venta.objects.all().order_by("-fecha")
    return render(
        request,
        "ventas/lista_ventas.html",
        {
            "ventas": ventas
        }
    )


# =====================================================
# CREAR VENTA (VERSIÓN OPTIMIZADA Y SEGURA CON POS)
# =====================================================

@transaction.atomic
def crear_venta(request):
    # 1. Validar usuario en sesión
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "No se pudo identificar el usuario actual.")
        return redirect("security:login")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # 2. Validar caja abierta
    apertura = AperturaCaja.objects.filter(
        usuario=usuario,
        estado=True
    ).select_related("caja").first()

    if not apertura:
        messages.error(request, "Debe tener una caja abierta para registrar ventas.")
        return redirect("caja:lista_cajas")

    # Recuperar venta activa en curso (si el usuario está retomando una pendiente)
    id_venta_activa = request.session.get("venta_activa_id")
    venta_activa = Venta.objects.filter(id_venta=id_venta_activa).first() if id_venta_activa else None

    if request.method == "POST":
        venta_form = VentaForm(request.POST, instance=venta_activa)
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

            # 3. AUDITORÍA: Validación de Inventario
            for detalle in detalles_temp:
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

            # 4. AUDITORÍA: Validación de Métodos de Pago
            pagos_temp = pago_formset.save(commit=False)
            total_pagado = sum(pago.monto for pago in pagos_temp)
            
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
            
            if not venta.numero_venta:
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

            # 7. GUARDAR DETALLES Y DESCONTAR INVENTARIO
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

            # Limpiar la venta activa de la sesión si se completó exitosamente
            if request.session.get("venta_activa_id") == venta.id_venta:
                del request.session["venta_activa_id"]

            messages.success(request, "Venta registrada correctamente.")
            return redirect("ventas:detalle_venta", id_venta=venta.id_venta)

    else:
        venta_form = VentaForm(instance=venta_activa) if venta_activa else VentaForm()
        detalle_formset = DetalleVentaFormSet(prefix="detalle", instance=venta_activa) if venta_activa else DetalleVentaFormSet(prefix="detalle")
        pago_formset = DetallePagoFormSet(prefix="pago", instance=venta_activa) if venta_activa else DetallePagoFormSet(prefix="pago")

    # Serializar los detalles de la venta activa (si existe) para enviarlos como JSON al frontend POS
    detalles_activos_list = []
    if venta_activa:
        for det in venta_activa.detalleventa_set.all():
            detalles_activos_list.append({
                "producto_id": getattr(det.producto, 'id_producto', det.producto.pk),
                "nombre": det.producto.nombre,
                "cantidad": float(det.cantidad),
                "precio": float(det.precio_unitario),
                "subtotal": float(det.subtotal)
            })

    return render(
        request,
        "ventas/crear_venta.html",
        {
            "venta_form": venta_form,
            "detalle_formset": detalle_formset,
            "pago_formset": pago_formset,
            "usuario_activo": usuario,
            "apertura": apertura,
            "caja": apertura.caja if apertura else None,
            "venta_activa": venta_activa,
            "detalles_activos_json": json.dumps(detalles_activos_list),
        }
    )


# =====================================================
# FLUJO POS: PAUSAR, GUARDAR Y RETOMAR VENTAS PENDIENTES
# =====================================================

def pausar_venta(request, id_venta):
    """Pausa la venta actual guardando su ID en la sesión para liberar la caja."""
    venta = get_object_or_404(Venta, id_venta=id_venta)
    
    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if id_venta not in ventas_pendientes:
        ventas_pendientes.append(id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes
        
    if 'venta_activa_id' in request.session:
        del request.session['venta_activa_id']
        
    messages.info(request, f"Venta {venta.numero_venta} guardada como pendiente. Puede atender al siguiente cliente.")
    return redirect('ventas:crear_venta')


@transaction.atomic
def guardar_venta_pendiente(request):
    """Guarda la venta actual del POS como borrador pendiente asignando el método de pago 'Pendiente'."""
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("ventas:crear_venta")

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "No se pudo identificar el usuario actual.")
        return redirect("security:login")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    apertura = AperturaCaja.objects.filter(
        usuario=usuario,
        estado=True
    ).select_related("caja").first()

    if not apertura:
        messages.error(request, "Debe tener una caja abierta.")
        return redirect("caja:lista_cajas")

    # Obtener o crear automáticamente el método de pago "Pendiente" en la base de datos
    metodo_pendiente, _ = MetodoPago.objects.get_or_create(
        nombre__iexact="Pendiente",
        defaults={"nombre": "Pendiente"}
    )

    # Recuperar si ya existía una venta activa en la sesión
    id_venta_activa = request.session.get("venta_activa_id")
    venta = Venta.objects.filter(id_venta=id_venta_activa).first() if id_venta_activa else None

    if not venta:
        venta = Venta()

    # Asignar datos generales de la venta
    venta.usuario = usuario
    venta.caja = apertura.caja
    venta.fecha = timezone.now()
    venta.estado = True
    venta.tipo_comprobante = request.POST.get("tipo_comprobante") or "TICKET"

    # ASIGNAR EL MÉTODO DE PAGO EXPLÍCITO "PENDIENTE"
    venta.metodo_pago = metodo_pendiente

    cliente_id = request.POST.get("cliente")
    venta.cliente_id = cliente_id if cliente_id else None

    if not venta.numero_venta:
        venta.numero_venta = generar_numero_venta()

    # Procesar los detalles desde el formset de manera robusta
    detalle_formset = DetalleVentaFormSet(request.POST, prefix="detalle")
    
    if detalle_formset.is_valid():
        detalles_temp = detalle_formset.save(commit=False)
        detalles_validos = [d for d in detalles_temp if d and getattr(d, 'producto', None) and d.cantidad > 0]
    else:
        detalles_validos = []

    if not detalles_validos:
        messages.error(request, "No hay productos válidos en el carrito para guardar como pendiente.")
        return redirect("ventas:crear_venta")

    # Calcular totales basados en el carrito actual
    subtotal_calculado = sum((d.subtotal for d in detalles_validos if d.subtotal), Decimal('0.00'))
    venta.subtotal = subtotal_calculado
    
    try:
        venta.impuesto = Decimal(request.POST.get("impuesto", "0"))
    except (ValueError, TypeError):
        venta.impuesto = Decimal('0.00')
        
    try:
        venta.descuento = Decimal(request.POST.get("descuento", "0"))
    except (ValueError, TypeError):
        venta.descuento = Decimal('0.00')

    venta.total = venta.subtotal + venta.impuesto - venta.descuento
    venta.save()

    # Limpiar pagos previos y sincronizar los nuevos detalles del carrito
    DetallePago.objects.filter(venta=venta).delete()
    DetalleVenta.objects.filter(venta=venta).delete()

    for detalle in detalles_validos:
        detalle.venta = venta
        detalle.save()

    # Registrar el ID de la venta en la lista de pendientes de la sesión
    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if venta.id_venta not in ventas_pendientes:
        ventas_pendientes.append(venta.id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes

    # Limpiar la venta activa de la sesión para liberar el POS
    if 'venta_activa_id' in request.session:
        del request.session['venta_activa_id']

    messages.success(request, f"Venta {venta.numero_venta} guardada temporalmente. Ya puede atender al siguiente cliente.")
    return redirect('ventas:crear_venta')


def listar_ventas_pendientes(request):
    """Muestra la lista de facturas que fueron pausadas temporalmente."""
    ids_pendientes = request.session.get('ventas_pendientes', [])
    ventas_pendientes = Venta.objects.filter(id_venta__in=ids_pendientes).select_related('cliente', 'usuario', 'metodo_pago')
    
    return render(
        request,
        'ventas/ventas_pendientes.html',
        {
            'ventas_pendientes': ventas_pendientes
        }
    )


def retomar_venta(request, id_venta):
    """Carga una venta pendiente de regreso al POS para continuar con el cobro."""
    request.session['venta_activa_id'] = id_venta
    
    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if id_venta in ventas_pendientes:
        ventas_pendientes.remove(id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes
        
    messages.success(request, "Venta retomada con éxito. Puede proceder al cobro.")
    return redirect('ventas:crear_venta')


@transaction.atomic
def eliminar_venta_pendiente(request, id_venta):
    """Elimina una venta pendiente de la sesión y borra su registro borrador."""
    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if id_venta in ventas_pendientes:
        ventas_pendientes.remove(id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes

    venta = Venta.objects.filter(id_venta=id_venta).first()
    if venta:
        DetalleVenta.objects.filter(venta=venta).delete()
        DetallePago.objects.filter(venta=venta).delete()
        venta.delete()

    messages.success(request, "Venta pendiente eliminada correctamente.")
    return redirect('ventas:ventas_pendientes')


# =====================================================
# DETALLE DE VENTA
# =====================================================

def detalle_venta(request, id_venta):
    venta = get_object_or_404(Venta, id_venta=id_venta)
    detalles = DetalleVenta.objects.filter(venta=venta)
    pagos = DetallePago.objects.filter(venta=venta)

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
    """
    Anula una venta existente, revierte su estado e incrementa nuevamente 
    el stock en el inventario de la sucursal correspondiente.
    """
    venta = get_object_or_404(Venta, pk=id_venta)
    
    # Validar si ya está anulada
    if not venta.estado:
        messages.warning(request, f"La venta {venta.numero_venta} ya se encuentra anulada.")
        return redirect('ventas:lista_ventas')

    if request.method == "POST":
        # 1. Actualizar el estado de la venta a anulada (False)
        venta.estado = False
        venta.fecha_actualizacion = timezone.now()
        venta.save()

        # 2. Reintegrar los productos al inventario
        detalles = DetalleVenta.objects.filter(venta=venta)
        for detalle in detalles:
            inventario = Inventario.objects.select_for_update().filter(
                producto=detalle.producto,
                sucursal=venta.caja.sucursal
            ).first()

            if inventario:
                inventario.stock_actual += detalle.cantidad
                inventario.save()

        messages.success(request, f"La venta **{venta.numero_venta}** ha sido anulada exitosamente y el inventario fue devuelto.")
        return redirect('ventas:lista_ventas')

    context = {
        "venta": venta
    }
    return render(request, "ventas/anular_venta.html", context) 


# =====================================================
# BÚSQUEDA DE CLIENTES PARA EL POS (JSON)
# =====================================================

def buscar_clientes_pos(request):
    query = request.GET.get("q", "").strip()
    clientes_data = []

    if query:
        clientes = Cliente.objects.filter(
            nombre__icontains=query
        ) | Cliente.objects.filter(
            identificacion__icontains=query
        )
        
        for c in clientes[:10]:
            clientes_data.append({
                "id": c.id_cliente,
                "nombre": c.nombre,
                "identificacion": getattr(c, "identificacion", "")
            })

    return JsonResponse(clientes_data, safe=False)