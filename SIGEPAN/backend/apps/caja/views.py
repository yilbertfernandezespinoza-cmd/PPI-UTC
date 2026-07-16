from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import (
    Caja,
    AperturaCaja,
    MovimientoCaja,
    CierreCaja
)

from .forms import (
    CajaForm,
    AperturaCajaForm,
    MovimientoCajaForm,
    CierreCajaForm
)



# =====================================================
# LISTAR CAJAS
# =====================================================

def lista_cajas(request):

    cajas = Caja.objects.all()

    return render(
        request,
        "caja/lista_cajas.html",
        {
            "cajas": cajas
        }
    )



# =====================================================
# CREAR CAJA
# =====================================================

def crear_caja(request):


    if request.method == "POST":


        form = CajaForm(
            request.POST
        )


        if form.is_valid():


            form.save()


            messages.success(
                request,
                "Caja creada correctamente."
            )


            return redirect(
                "caja:lista_cajas"
            )


    else:

        form = CajaForm()



    return render(
        request,
        "caja/crear_caja.html",
        {
            "form": form
        }
    )



# =====================================================
# APERTURA DE CAJA
# =====================================================

@transaction.atomic
def abrir_caja(request):


    if request.method == "POST":


        form = AperturaCajaForm(
            request.POST
        )


        if form.is_valid():


            apertura = form.save(
                commit=False
            )


            # =========================================
            # VALIDAR QUE NO EXISTA APERTURA ACTIVA
            # =========================================

            existe = AperturaCaja.objects.filter(

                caja=apertura.caja,

                estado=True

            ).exists()



            if existe:


                messages.error(
                    request,
                    "La caja ya tiene una apertura activa."
                )


                return redirect(
                    "caja:abrir_caja"
                )



            # =========================================
            # DATOS DEL SISTEMA
            # =========================================

            apertura.fecha_apertura = timezone.now()


            apertura.estado = True


            # Pendiente:
            # apertura.usuario = usuario_actual



            apertura.save()



            messages.success(
                request,
                "Caja abierta correctamente."
            )


            return redirect(
                "caja:lista_cajas"
            )



    else:

        form = AperturaCajaForm()



    return render(
        request,
        "caja/abrir_caja.html",
        {
            "form": form
        }
    )



# =====================================================
# MOVIMIENTO DE CAJA
# =====================================================

@transaction.atomic
def movimiento_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )



    if not apertura.estado:


        messages.error(
            request,
            "La caja no está abierta."
        )


        return redirect(
            "caja:lista_cajas"
        )



    if request.method == "POST":


        form = MovimientoCajaForm(
            request.POST
        )


        if form.is_valid():


            movimiento = form.save(
                commit=False
            )


            movimiento.apertura = apertura


            movimiento.fecha_movimiento = timezone.now()



            # Pendiente:
            # movimiento.usuario = usuario_actual



            movimiento.save()



            messages.success(
                request,
                "Movimiento registrado correctamente."
            )


            return redirect(
                "caja:detalle_caja",
                id_apertura
            )


    else:


        form = MovimientoCajaForm()



    return render(
        request,
        "caja/movimiento_caja.html",
        {
            "form": form,
            "apertura": apertura
        }
    )



# =====================================================
# DETALLE CAJA ABIERTA
# =====================================================

def detalle_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )


    movimientos = MovimientoCaja.objects.filter(

        apertura=apertura

    )


    return render(

        request,

        "caja/detalle_caja.html",

        {

            "apertura": apertura,

            "movimientos": movimientos

        }

    )



# =====================================================
# CIERRE DE CAJA
# =====================================================

@transaction.atomic
def cerrar_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )



    if request.method == "POST":


        form = CierreCajaForm(
            request.POST
        )


        if form.is_valid():


            cierre = form.save(
                commit=False
            )


            cierre.apertura = apertura


            cierre.fecha_cierre = timezone.now()



            cierre.monto_inicial = apertura.monto_inicial



            # =====================================
            # CALCULAR DIFERENCIA
            # =====================================

            cierre.diferencia = (

                cierre.monto_final

                -

                cierre.monto_inicial

            )



            # Pendiente:
            # cierre.usuario = usuario_actual



            cierre.save()



            # cerrar apertura

            apertura.estado = False

            apertura.save()



            messages.success(
                request,
                "Caja cerrada correctamente."
            )



            return redirect(
                "caja:lista_cajas"
            )



    else:


        form = CierreCajaForm()



    return render(

        request,

        "caja/cerrar_caja.html",

        {

            "form": form,

            "apertura": apertura

        }

    )