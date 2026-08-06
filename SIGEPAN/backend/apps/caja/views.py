
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .utils import (calcular_saldo_sistema, calcular_saldo_movimientos)
from decimal import Decimal

from .models import (
    Caja,
    HistorialCaja,
    AperturaCaja,
    MovimientoCaja,
    ArqueoCaja,
    CierreCaja
)

from apps.security.models import Usuario
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log

from .forms import (
    CajaForm,
    AperturaCajaForm,
    MovimientoCajaForm,
    ArqueoCajaForm,
    CierreCajaForm
)

# =====================================================
# UTILIDADES DE USUARIO
# =====================================================

def obtener_usuario(request):

    usuario_id = request.session.get(
        "usuario_id"
    )

    if not usuario_id:

        return None


    return get_object_or_404(
        Usuario,
        id_usuario=usuario_id
    )



def es_administrador(usuario):

    if not usuario:

        return False


    return (
        usuario.id_rol.nombre.upper()
        ==
        "ADMINISTRADOR"
    )

# =====================================================
# LISTAR CAJAS
# =====================================================

@login_required
@permiso_requerido("Caja", "CONSULTAR")
def lista_cajas(request):

    cajas = Caja.objects.all()

    for caja in cajas:
        caja.apertura_activa = AperturaCaja.objects.filter(
            caja=caja,
            estado=True
        ).first()

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

@login_required
@permiso_requerido("Caja", "CREAR")
@transaction.atomic
def crear_caja(request):


    usuario = obtener_usuario(request)


    # =========================================
    # VALIDAR USUARIO
    # =========================================

    if not usuario:


        messages.error(
            request,
            "Usuario no válido."
        )


        return redirect(
            "security:login"
        )



    # =========================================
    # VALIDAR PERMISOS
    # =========================================

    if not es_administrador(usuario):


        messages.error(
            request,
            "No tiene permisos para crear cajas."
        )


        return redirect(
            "caja:lista_cajas"
        )



    # =========================================
    # PROCESAR FORMULARIO
    # =========================================

    if request.method == "POST":


        form = CajaForm(
            request.POST
        )



        if form.is_valid():


            # =========================================
            # GUARDAR CAMBIOS
            # =========================================


            caja = form.save(
                commit=False
            )


            # =========================================
            # INICIALIZAR CAMPOS LEGACY
            # =========================================

            caja.saldo_inicial = Decimal("0.00")
            caja.saldo_actual = Decimal("0.00")

            caja.save()


            messages.success(
                request,
                "Caja creada correctamente."
            )

            registrar_log(
                request=request,
                usuario=usuario,
                modulo="Caja",
                tipo_accion="CREAR",
                descripcion=f"Se creó la caja {caja.nombre}",
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
# EDITAR CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "MODIFICAR")
@transaction.atomic
def editar_caja(request, id_caja):

    # =========================================
    # OBTENER CAJA
    # =========================================

    caja = get_object_or_404(
        Caja,
        id_caja=id_caja
    )


    if not caja.estado:

        messages.error(
            request,
            "No se puede modificar una caja inactiva."
        )

        return redirect(
             "caja:administrar_caja",
                id_caja=caja.id_caja
        )


    # =========================================
    # FORMULARIO
    # =========================================

    if request.method == "POST":

        form = CajaForm(
            request.POST,
            instance=caja
        )


        if form.is_valid():



            # =========================================
            # ACTUALIZAR CAJA
            # =========================================

            caja = form.save()



            caja.save()


            messages.success(
                request,
                "Caja actualizada correctamente."
            )

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Caja",
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó la caja {caja.nombre}",
            )

            return redirect(
                "caja:administrar_caja",
                id_caja=caja.id_caja
            )


        else:


            messages.error(
                request,
                "Verifique la información ingresada."
            )


    else:


        form = CajaForm(
            instance=caja
        )



    # =========================================
    # RETORNAR VISTA
    # =========================================

    return render(
        request,
        "caja/editar_caja.html",
        {
            "form": form,
            "caja": caja
        }
    )

# =====================================================
# ACTIVAR CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "MODIFICAR")
@transaction.atomic
def activar_caja(request, id_caja):

    # Hallazgo de auditoría de seguridad (04-08-2026): esta vista mutaba
    # estado en una petición GET (se disparaba desde un <a href> en
    # lista_cajas.html), sin exigir POST ni CSRF — activar/desactivar una
    # caja bastaba con precargar el link. Se exige POST explícitamente;
    # el template ahora envía un <form method="post"> con {% csrf_token %}.
    if request.method != "POST":
        return redirect(
            "caja:lista_cajas"
        )

    caja = get_object_or_404(

        Caja,

        id_caja=id_caja

    )


    caja.estado = True


    caja.save()



    messages.success(

        request,

        "Caja activada correctamente."

    )

    registrar_log(
        request=request,
        usuario=request.usuario,
        modulo="Caja",
        tipo_accion="MODIFICAR",
        descripcion=f"Se activó la caja {caja.nombre}",
    )

    return redirect(

        "caja:lista_cajas"

    )



# =====================================================
# DESACTIVAR CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "ELIMINAR")
@transaction.atomic
def desactivar_caja(request, id_caja):

    # Mismo hallazgo/fix que activar_caja: exigir POST + CSRF real en
    # vez de mutar en GET.
    if request.method != "POST":
        return redirect(
            "caja:lista_cajas"
        )

    caja = get_object_or_404(

        Caja,

        id_caja=id_caja

    )


    # =========================================
    # VALIDAR APERTURA ACTIVA
    # =========================================

    # Bug real encontrado en auditoría (06-08): `hasattr(caja, "apertura_activa")`
    # nunca es verdadero aquí. Ese atributo solo se asigna dinámicamente en
    # lista_cajas() (fuera de este objeto), pero `caja` se acaba de obtener
    # con un get_object_or_404 nuevo que jamás lo tiene — el hasattr() daba
    # siempre False y esta validación nunca se ejecutaba: se podía
    # desactivar una caja con una apertura activa pese al mensaje de error
    # que la función muestra. Se reemplaza por una consulta real.
    tiene_apertura_activa = AperturaCaja.objects.filter(
        caja=caja, estado=True
    ).exists()

    if tiene_apertura_activa:

        messages.error(

            request,

            "No se puede desactivar una caja con una apertura activa. Debe cerrar caja primero."

        )

        return redirect(

            "caja:lista_cajas"

        )


    # =========================================
    # DESACTIVAR CAJA
    # =========================================

    caja.estado = False

    caja.save()


    messages.success(

        request,

        "Caja desactivada correctamente."

    )

    registrar_log(
        request=request,
        usuario=request.usuario,
        modulo="Caja",
        tipo_accion="ELIMINAR",
        descripcion=f"Se desactivó la caja {caja.nombre}",
    )

    return redirect(

        "caja:lista_cajas"

    )

# =====================================================
# APERTURA DE CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "CREAR")
@transaction.atomic
def abrir_caja(request, id_caja):
    caja = get_object_or_404(
        Caja,
        id_caja=id_caja
    )

    if request.method == "POST":


        form = AperturaCajaForm(
            request.POST
        )


        if form.is_valid():


            apertura = form.save(commit=False)

            apertura.caja = caja


            # =========================================
            # VALIDAR QUE NO EXISTA APERTURA ACTIVA
            # =========================================

            existe = AperturaCaja.objects.filter(
                caja=caja,
                estado=True
            ).exists()



            if existe:


                messages.error(
                    request,
                    "La caja ya tiene una apertura activa."
                )


                return redirect(
                    "caja:abrir_caja",
                    id_caja=id_caja
                )



            # =========================================
            # DATOS DEL SISTEMA
            # =========================================

            apertura.fecha_apertura = timezone.now()


            apertura.estado = True


            apertura.usuario = request.usuario


            apertura.save()



            messages.success(
                request,
                "Caja abierta correctamente."
            )

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Caja",
                tipo_accion="CREAR",
                descripcion=f"Se abrió la caja {caja.nombre}",
            )

            return redirect(
                "caja:administrar_caja",
                id_caja=caja.id_caja
            )



    else:

        form = AperturaCajaForm()



    return render(
        request,
        "caja/abrir_caja.html",
        {
            "form": form,
            "caja": caja
        }
    )

# =====================================================
# EDITAR APERTURA DE CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "MODIFICAR")
@transaction.atomic
def editar_apertura(request, id_apertura):

    # =========================================
    # OBTENER APERTURA
    # =========================================

    apertura = get_object_or_404(
        AperturaCaja,
        id_apertura=id_apertura
    )

    # =========================================
    # VALIDAR APERTURA ACTIVA
    # =========================================

    if not apertura.estado:

        messages.error(
            request,
            "Solo se puede editar una apertura activa."
        )

        return redirect(
            "caja:administrar_caja",
            id_caja=apertura.caja.id_caja
        )

    # =========================================
    # FORMULARIO
    # =========================================

    if request.method == "POST":

        form = AperturaCajaForm(
            request.POST,
            instance=apertura
        )

        if form.is_valid():

            monto_anterior = apertura.monto_inicial

            apertura = form.save(
                commit=False
            )

            apertura.save()

            # =========================================
            # REGISTRAR HISTORIAL
            # =========================================

            if monto_anterior != apertura.monto_inicial:

                HistorialCaja.objects.create(

                    caja=apertura.caja,

                    usuario=request.usuario,

                    tipo_cambio="AJUSTE_APERTURA",

                    valor_anterior=str(monto_anterior),

                    valor_nuevo=str(apertura.monto_inicial),

                    observacion="Modificación del monto inicial de la apertura."

                )

            messages.success(
                request,
                "Apertura actualizada correctamente."
            )

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Caja",
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó la apertura de la caja {apertura.caja.nombre}",
            )

            return redirect(
                "caja:administrar_caja",
                id_caja=apertura.caja.id_caja
            )

    else:

        form = AperturaCajaForm(
            instance=apertura
        )

    return render(

        request,

        "caja/editar_apertura.html",

        {

            "form": form,

            "apertura": apertura

        }

    )
    

# =====================================================
# MOVIMIENTO DE CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "CREAR")
@transaction.atomic
def movimiento_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )

    usuario_actual = request.usuario


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

            movimiento = form.save(commit=False)

            movimiento.apertura = apertura

            movimiento.usuario = usuario_actual

            movimiento.fecha_movimiento = timezone.now()

            movimiento.save()


            messages.success(
                request,
                "Movimiento registrado correctamente."
            )

            registrar_log(
                request=request,
                usuario=usuario_actual,
                modulo="Caja",
                tipo_accion="CREAR",
                descripcion=f"Se registró un movimiento de caja en {apertura.caja.nombre}",
            )

            return redirect(
                "caja:administrar_caja",
                id_caja=apertura.caja.id_caja
            )


        else:

            messages.error(
                request,
                "Revise los datos ingresados."
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
# ADMINISTRAR CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "CONSULTAR")
def administrar_caja(request, id_caja):

    # =========================================
    # OBTENER LA CAJA
    # =========================================

    # 1. Obtener la caja seleccionada
    caja = get_object_or_404(
        Caja,
        id_caja=id_caja
    )

    # =========================================
    # BUSCAR APERTURA ACTIVA
    # =========================================

    # 2. Buscar si tiene una apertura activa
    apertura = AperturaCaja.objects.filter(
        caja=caja,
        estado=True
    ).first()

    # =========================================
    # ESTADO DE LA CAJA
    # =========================================

    caja_abierta = apertura is not None

    # =========================================
    # MOVIMIENTOS
    # =========================================

    if caja_abierta:

        consulta_movimientos = MovimientoCaja.objects.filter(
            apertura=apertura
        )

        total_movimientos = consulta_movimientos.count()

        movimientos = consulta_movimientos.order_by(
            "-fecha_movimiento"
        )[:10]


        # =========================================
        # SALDO ACUMULADO DE LA CAJA
        # =========================================

        saldo_caja = calcular_saldo_sistema(
            apertura
        )


        # =========================================
        # SALDO SOLO DE MOVIMIENTOS
        # =========================================

        saldo_movimientos = calcular_saldo_movimientos(
            apertura
        )


    else:

        movimientos = []

        total_movimientos = 0

        saldo_caja = caja.saldo_actual

        saldo_movimientos = 0



    # =========================================
    # HISTORIAL DE ARQUEOS
    # =========================================

    if apertura:

        arqueos = ArqueoCaja.objects.filter(
            apertura=apertura
        ).order_by(
            "-fecha_arqueo"
        )

        ultimo_arqueo = arqueos.first()

        total_arqueos = arqueos.count()

    else:

        arqueos = []

        ultimo_arqueo = None

        total_arqueos = 0


    # =========================================
    # HISTORIAL ADMINISTRATIVO
    # =========================================

    historial = HistorialCaja.objects.filter(
        caja=caja
    ).order_by("-fecha_creacion")


    # =========================================
    # CONTEXTO
    # =========================================

    contexto = {

        "caja": caja,

        "apertura": apertura,

        "caja_abierta": caja_abierta,

        "movimientos": movimientos,

        "total_movimientos": total_movimientos,

        "saldo_caja": saldo_caja,

        "saldo_movimientos": saldo_movimientos,

        "arqueos": arqueos,

        "total_arqueos": total_arqueos,

        "ultimo_arqueo": ultimo_arqueo,

        "historial": historial,

    }

    # =========================================
    # RETORNAR VISTA
    # =========================================

    return render(
        request,
        "caja/administrar_caja.html",
        contexto
    )

# =====================================================
# DETALLE CAJA ABIERTA
# =====================================================

@login_required
@permiso_requerido("Caja", "CONSULTAR")
def detalle_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )


    movimientos = MovimientoCaja.objects.filter(

        apertura=apertura

    ).order_by(

        "-fecha_movimiento"

    )


    saldo_sistema = calcular_saldo_sistema(

        apertura

    )


    return render(

        request,

        "caja/detalle_caja.html",

        {

            "apertura": apertura,

            "movimientos": movimientos,

            "saldo_sistema": saldo_sistema

        }

    )

# =====================================================
# ARQUEO DE CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "CREAR")
@transaction.atomic
def crear_arqueo(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )



    if not apertura.estado:


        messages.error(

            request,

            "No se puede realizar un arqueo de una caja cerrada."

        )


        return redirect(

            "caja:lista_cajas"

        )



    # =====================================================
    # CALCULAR SALDO DEL SISTEMA
    # =====================================================


    saldo_sistema = calcular_saldo_sistema(

        apertura

    )



    # =========================================
    # FORMULARIO
    # =========================================

    if request.method == "POST":


        form = ArqueoCajaForm(

            request.POST

        )



        if form.is_valid():


            arqueo = form.save(

                commit=False

            )


            arqueo.apertura = apertura



            arqueo.saldo_sistema = saldo_sistema



            arqueo.diferencia = (

                arqueo.saldo_contado

                -

                saldo_sistema

            )



            arqueo.fecha_arqueo = timezone.now()



            # =========================================
            # USUARIO RESPONSABLE
            # =========================================

            arqueo.usuario = request.usuario



            arqueo.save()



            messages.success(

                request,

                "Arqueo registrado correctamente."

            )

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Caja",
                tipo_accion="CREAR",
                descripcion=f"Se registró un arqueo en {apertura.caja.nombre}",
            )

            return redirect(

                "caja:administrar_caja",

                id_caja=apertura.caja.id_caja

            )



    else:


        form = ArqueoCajaForm()



    return render(

        request,

        "caja/crear_arqueo.html",

        {

            "form": form,

            "apertura": apertura,

            "saldo_sistema": saldo_sistema

        }

    )

# =====================================================
# CIERRE DE CAJA
# =====================================================

@login_required
@permiso_requerido("Caja", "ELIMINAR")
@transaction.atomic
def cerrar_caja(request, id_apertura):


    apertura = get_object_or_404(

        AperturaCaja,

        id_apertura=id_apertura

    )


    # =========================================
    # VALIDAR APERTURA ACTIVA
    # =========================================

    if not apertura.estado:

        messages.error(

            request,

            "La caja ya se encuentra cerrada."

        )

        return redirect(

            "caja:administrar_caja",

            id_caja=apertura.caja.id_caja

        )

    # =========================================
    # VALIDAR CIERRE EXISTENTE
    # =========================================

    if CierreCaja.objects.filter(apertura=apertura).exists():

        messages.error(

            request,

            "La apertura ya posee un cierre registrado."

        )

        return redirect(

            "caja:administrar_caja",

            id_caja=apertura.caja.id_caja

        )

    # =========================================
    # VALIDAR ARQUEO PREVIO
    # =========================================

    existe_arqueo = ArqueoCaja.objects.filter(
        apertura=apertura
    ).exists()


    if not existe_arqueo:

        messages.error(
            request,
            "Debe realizar al menos un arqueo antes de cerrar la caja."
        )


        return redirect(
            "caja:administrar_caja",
            id_caja=apertura.caja.id_caja
        )

    # =====================================
    # CALCULAR SALDO DEL SISTEMA
    # =====================================

    saldo_sistema = calcular_saldo_sistema(
        apertura
    )


    # =====================================
    # OBTENER ÚLTIMO ARQUEO
    # =====================================

    ultimo_arqueo = ArqueoCaja.objects.filter(
        apertura=apertura
    ).order_by(
        "-fecha_arqueo"
    ).first()

    # =========================================
    # FORMULARIO
    # =========================================

    if request.method == "POST":

        form = CierreCajaForm(
            request.POST
        )

        if form.is_valid():

            cierre = form.save(
                commit=False
            )

            # =====================================
            # DATOS DEL CIERRE
            # =====================================

            cierre.apertura = apertura

            cierre.fecha_cierre = timezone.now()

            cierre.monto_inicial = apertura.monto_inicial

            # =====================================
            # CALCULAR DIFERENCIA
            # =====================================

            cierre.diferencia = (

                cierre.monto_final

                -

                saldo_sistema

            )

            # =========================================
            # USUARIO RESPONSABLE
            # =========================================

            cierre.usuario = request.usuario


            cierre.save()

            # =========================================
            # ACTUALIZAR SALDO DE LA CAJA
            # =========================================

            apertura.caja.saldo_actual = cierre.monto_final

            apertura.caja.save()

            # =========================================
            # CERRAR APERTURA
            # =========================================

            apertura.estado = False

            apertura.save()



            messages.success(
                request,
                "Caja cerrada correctamente."
            )

            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Caja",
                tipo_accion="ELIMINAR",
                descripcion=f"Se cerró la caja {apertura.caja.nombre}",
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

            "apertura": apertura,

            "saldo_sistema": saldo_sistema,

            "ultimo_arqueo": ultimo_arqueo

        }

    )