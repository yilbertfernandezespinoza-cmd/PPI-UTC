from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from apps.security.models import Usuario
from apps.inventario.models import Inventario


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
# CREAR VENTA
# =====================================================

@transaction.atomic
def crear_venta(request):

    if request.method == "POST":

        venta_form = VentaForm(
            request.POST
        )

        detalle_formset = DetalleVentaFormSet(
            request.POST,
            prefix="detalle"
        )

        pago_formset = DetallePagoFormSet(
            request.POST,
            prefix="pago"
        )

        if (
            venta_form.is_valid()
            and detalle_formset.is_valid()
            and pago_formset.is_valid()
        ):

            venta = venta_form.save(
                commit=False
            )

            # ==========================================
            # DATOS DEL SISTEMA
            # ==========================================

            usuario_id = request.session.get(
                "usuario_id"
            )

            if not usuario_id:

                messages.error(
                    request,
                    "No se pudo identificar el usuario actual."
                )

                return redirect(
                    "security:login"
                )

            usuario = get_object_or_404(
                Usuario,
                id_usuario=usuario_id
            )

            # ==========================================
            # VALIDAR CAJA ABIERTA
            # ==========================================

            apertura = AperturaCaja.objects.filter(
                usuario=usuario,
                estado=True
            ).select_related(
                "caja"
            ).first()

            if not apertura:

                messages.error(
                    request,
                    "Debe tener una caja abierta para registrar ventas."
                )

                return redirect(
                    "caja:lista_cajas"
                )

            # ==========================================
            # ASIGNAR DATOS AUTOMÁTICOS
            # ==========================================

            venta.usuario = usuario

            venta.caja = apertura.caja

            venta.fecha = timezone.now()

            venta.estado = True

            # ==========================================
            # GUARDAR VENTA
            # ==========================================

            venta.save()



            # =====================================================
            # INTEGRACIÓN VENTA - CAJA
            # REGISTRO AUTOMÁTICO MOVIMIENTO
            # =====================================================

            MovimientoCaja.objects.create(

                apertura=apertura,

                usuario=usuario,

                tipo_movimiento="VENTA",

                monto=venta.total,

                descripcion=f"Venta {venta.numero_venta}",

                fecha_movimiento=timezone.now()

            )


            # =====================================================
            # GUARDAR DETALLE DE VENTA
            # =====================================================


            detalles = detalle_formset.save(
                commit=False
            )



            for detalle in detalles:


                detalle.venta = venta

                detalle.save()



                inventario = get_object_or_404(

                    Inventario,

                    producto=detalle.producto,

                    sucursal=venta.caja.sucursal

                )


                if inventario.stock_actual < detalle.cantidad:

                    messages.error(

                        request,

                        f"No hay existencias suficientes de {detalle.producto.nombre}."

                    )

                    return redirect(
                        "ventas:crear_venta"
                    )


                inventario.stock_actual -= detalle.cantidad

                inventario.save()


            # =====================================================
            # GUARDAR DETALLE DE PAGOS
            # =====================================================


            pagos = pago_formset.save(
                commit=False
            )



            for pago in pagos:


                pago.venta = venta

                pago.save()



            messages.success(
                request,
                "Venta registrada correctamente."
            )



            return redirect(
                "ventas:detalle_venta",
                id_venta=venta.id_venta
            )



    else:


        venta_form = VentaForm()


        detalle_formset = DetalleVentaFormSet(
            prefix="detalle"
        )


        pago_formset = DetallePagoFormSet(
            prefix="pago"
        )



    return render(
        request,
        "ventas/crear_venta.html",
        {

            "venta_form": venta_form,

            "detalle_formset": detalle_formset,

            "pago_formset": pago_formset

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


    venta = get_object_or_404(

        Venta,

        id_venta=id_venta

    )



    if request.method == "POST":


        venta.estado = False

        venta.save()



        messages.success(

            request,

            "Venta anulada correctamente."

        )



        return redirect(

            "ventas:lista_ventas"

        )



    return render(

        request,

        "ventas/anular_venta.html",

        {

            "venta": venta

        }

    )