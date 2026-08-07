
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from .utils import (calcular_saldo_sistema, calcular_saldo_movimientos)
from .services import (
    CajaService,
    AperturaCajaService,
    MovimientoCajaService,
    ArqueoCajaService,
    CierreCajaService,
)
from .repositories import (
    CajaRepository,
    AperturaCajaRepository,
    MovimientoCajaRepository,
    ArqueoCajaRepository,
    HistorialCajaRepository,
)
from decimal import Decimal

# (07-08) Los modelos de este módulo ya no se consultan directo aquí —
# toda la lectura/escritura pasa por CajaRepository/AperturaCajaRepository/
# MovimientoCajaRepository/ArqueoCajaRepository/HistorialCajaRepository
# (repositories.py) y los Service correspondientes (services.py).

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



# (06-08) Se eliminó `es_administrador()`: era una verificación de rol
# manual y duplicada frente al sistema de permisos real
# (`@permiso_requerido`), su único uso (en `crear_caja`) ya se retiró.

# =====================================================
# LISTAR CAJAS
# =====================================================

@login_required
@permiso_requerido("Caja", "CONSULTAR")
def lista_cajas(request):

    cajas = CajaRepository.listar_todas()

    for caja in cajas:
        caja.apertura_activa = CajaRepository.apertura_activa(caja)

    # Serialización a JSON (07-08): la tabla migra de jQuery DataTables
    # (ya no funciona, base.html no carga jQuery desde que el proyecto
    # adoptó Tabulator.js) al mismo patrón que ya usa Clientes. Con 9
    # cajas de prueba ya sin paginación real, esto además evita que la
    # lista crezca sin control visual.
    cajas_json = [
        {
            "id_caja": caja.id_caja,
            "nombre": caja.nombre,
            "sucursal": str(caja.sucursal),
            "saldo_actual": str(caja.saldo_actual),
            "estado": caja.estado,
            "apertura_activa": caja.apertura_activa is not None,
            "administrar": reverse("caja:administrar_caja", args=[caja.id_caja]),
            "abrir": reverse("caja:abrir_caja", args=[caja.id_caja]),
            "desactivar": reverse("caja:desactivar_caja", args=[caja.id_caja]),
            "activar": reverse("caja:activar_caja", args=[caja.id_caja]),
        }
        for caja in cajas
    ]

    return render(
        request,
        "caja/lista_cajas.html",
        {
            "cajas": cajas,
            "cajas_json": cajas_json,
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
    # (06-08) Se retiró la verificación manual `es_administrador()` que
    # vivía aquí: era una comprobación de rol duplicada e independiente
    # del sistema de permisos real. El decorador `@permiso_requerido(
    # "Caja", "CREAR")` de arriba ya cubre exactamente este caso —
    # cualquier rol sin el permiso CREAR sobre "Caja" nunca llega a
    # ejecutar el cuerpo de esta vista.



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
            # GUARDAR (CajaService inicializa saldo_inicial/
            # saldo_actual en 0, igual que antes)
            # =========================================

            caja = CajaService.crear(caja)


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

    caja = CajaRepository.obtener(id_caja)


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

    caja = CajaRepository.obtener(id_caja)

    CajaService.activar(caja)



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

    caja = CajaRepository.obtener(id_caja)


    # =========================================
    # VALIDAR APERTURA ACTIVA Y DESACTIVAR
    # =========================================

    # Bug real encontrado en auditoría (06-08): `hasattr(caja, "apertura_activa")`
    # nunca era verdadero aquí. Ese atributo solo se asigna dinámicamente en
    # lista_cajas() (fuera de este objeto), pero `caja` se obtenía con un
    # get_object_or_404 nuevo que jamás lo tenía — el hasattr() daba siempre
    # False y esta validación nunca se ejecutaba: se podía desactivar una
    # caja con una apertura activa pese al mensaje de error que la función
    # muestra. Corregido con una consulta real, ahora centralizada en
    # `CajaService.desactivar` (07-08).
    try:
        CajaService.desactivar(caja)
    except ValidationError as error:

        messages.error(

            request,

            "; ".join(error.messages) if hasattr(error, "messages") else str(error)

        )

        return redirect(

            "caja:lista_cajas"

        )


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
    caja = CajaRepository.obtener(id_caja)

    if request.method == "POST":


        form = AperturaCajaForm(
            request.POST
        )


        if form.is_valid():


            apertura = form.save(commit=False)

            # =========================================
            # VALIDAR QUE NO EXISTA APERTURA ACTIVA Y ABRIR
            # =========================================

            try:
                apertura = AperturaCajaService.abrir(
                    caja=caja,
                    apertura_sin_guardar=apertura,
                    usuario=request.usuario,
                )
            except ValidationError as error:

                messages.error(
                    request,
                    "; ".join(error.messages) if hasattr(error, "messages") else str(error)
                )

                return redirect(
                    "caja:abrir_caja",
                    id_caja=id_caja
                )

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

    apertura = AperturaCajaRepository.obtener(id_apertura)

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

            # =========================================
            # GUARDAR Y REGISTRAR HISTORIAL SI CAMBIÓ EL MONTO
            # =========================================

            apertura = AperturaCajaService.editar(
                apertura_sin_guardar=apertura,
                monto_anterior=monto_anterior,
                usuario=request.usuario,
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


    apertura = AperturaCajaRepository.obtener(id_apertura)

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

            movimiento = MovimientoCajaService.registrar(
                apertura=apertura,
                movimiento_sin_guardar=movimiento,
                usuario=usuario_actual,
            )


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
    caja = CajaRepository.obtener(id_caja)

    # =========================================
    # BUSCAR APERTURA ACTIVA
    # =========================================

    # 2. Buscar si tiene una apertura activa
    apertura = CajaRepository.apertura_activa(caja)

    # =========================================
    # ESTADO DE LA CAJA
    # =========================================

    caja_abierta = apertura is not None

    # =========================================
    # MOVIMIENTOS
    # =========================================

    if caja_abierta:

        total_movimientos = MovimientoCajaRepository.contar(apertura)

        movimientos = MovimientoCajaRepository.recientes(apertura, 10)


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

        arqueos = ArqueoCajaRepository.listar_por_apertura(apertura)

        ultimo_arqueo = arqueos.first()

        total_arqueos = arqueos.count()

    else:

        arqueos = []

        ultimo_arqueo = None

        total_arqueos = 0


    # =========================================
    # HISTORIAL ADMINISTRATIVO
    # =========================================

    historial = HistorialCajaRepository.listar_por_caja(caja)


    # =========================================
    # SERIALIZACIÓN A JSON (07-08)
    # =========================================
    # Mismo motivo que lista_cajas: las tablas de "Últimos Movimientos" y
    # "Historial de Arqueos" usaban jQuery DataTables, que ya no funciona
    # (base.html no carga jQuery desde que el proyecto adoptó Tabulator.js).
    # El listado de arqueos de una apertura larga puede crecer bastante
    # dentro de un mismo turno, así que también le hace falta paginación
    # real, no solo la de movimientos.

    movimientos_json = [
        {
            "tipo_movimiento": m.tipo_movimiento,
            "descripcion": m.descripcion or "",
            "usuario": str(m.usuario),
            "monto": str(m.monto),
            "fecha_movimiento": timezone.localtime(m.fecha_movimiento).strftime("%d/%m/%Y %H:%M"),
        }
        for m in movimientos
    ]

    arqueos_json = [
        {
            "fecha_arqueo": timezone.localtime(a.fecha_arqueo).strftime("%d/%m/%Y %H:%M"),
            "usuario": str(a.usuario),
            "saldo_sistema": str(a.saldo_sistema),
            "saldo_contado": str(a.saldo_contado),
            "diferencia": str(a.diferencia),
            "observaciones": a.observaciones or "",
        }
        for a in arqueos
    ]

    # =========================================
    # CONTEXTO
    # =========================================

    contexto = {

        "caja": caja,

        "apertura": apertura,

        "caja_abierta": caja_abierta,

        "movimientos": movimientos,

        "movimientos_json": movimientos_json,

        "total_movimientos": total_movimientos,

        "saldo_caja": saldo_caja,

        "saldo_movimientos": saldo_movimientos,

        "arqueos": arqueos,

        "arqueos_json": arqueos_json,

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


    apertura = AperturaCajaRepository.obtener(id_apertura)


    movimientos = MovimientoCajaRepository.listar_por_apertura(apertura)


    saldo_sistema = calcular_saldo_sistema(

        apertura

    )

    # Serialización a JSON (07-08): mismo motivo que administrar_caja —
    # jQuery DataTables ya no funciona (base.html no carga jQuery desde
    # que el proyecto adoptó Tabulator.js), y esta es la lista COMPLETA
    # de movimientos de la apertura (sin límite de 10 como en
    # "Administrar caja"), así que le hace más falta aún la paginación.
    movimientos_json = [
        {
            "tipo_movimiento": m.tipo_movimiento,
            "descripcion": m.descripcion or "",
            "monto": str(m.monto),
            "fecha_movimiento": timezone.localtime(m.fecha_movimiento).strftime("%d/%m/%Y %H:%M"),
        }
        for m in movimientos
    ]

    return render(

        request,

        "caja/detalle_caja.html",

        {

            "apertura": apertura,

            "movimientos": movimientos,

            "movimientos_json": movimientos_json,

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


    apertura = AperturaCajaRepository.obtener(id_apertura)



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


            arqueo = ArqueoCajaService.registrar(
                apertura=apertura,
                arqueo_sin_guardar=arqueo,
                usuario=request.usuario,
                saldo_sistema=saldo_sistema,
            )



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

    # (06-08) Las 3 validaciones que antes vivían aquí a mano (if/else +
    # messages.error + redirect) se movieron a
    # `CierreCajaService.validar_puede_cerrar`, que levanta
    # `ValidationError` — mismo patrón que `GastoOperativoService`. El
    # texto de cada mensaje de error es idéntico al que ya se mostraba.

    apertura = AperturaCajaRepository.obtener(id_apertura)

    try:
        CierreCajaService.validar_puede_cerrar(apertura)
    except ValidationError as error:
        messages.error(
            request,
            "; ".join(error.messages) if hasattr(error, "messages") else str(error),
        )
        return redirect(
            "caja:administrar_caja",
            id_caja=apertura.caja.id_caja
        )

    # =====================================
    # CALCULAR SALDO DEL SISTEMA (para mostrarlo en el formulario)
    # =====================================

    saldo_sistema = calcular_saldo_sistema(
        apertura
    )


    # =====================================
    # OBTENER ÚLTIMO ARQUEO
    # =====================================

    ultimo_arqueo = ArqueoCajaRepository.ultimo(apertura)

    # =========================================
    # FORMULARIO
    # =========================================

    if request.method == "POST":

        form = CierreCajaForm(
            request.POST
        )

        if form.is_valid():

            try:
                CierreCajaService.cerrar(
                    apertura=apertura,
                    usuario=request.usuario,
                    monto_final=form.cleaned_data["monto_final"],
                    observaciones=form.cleaned_data.get("observaciones"),
                )
            except ValidationError as error:
                messages.error(
                    request,
                    "; ".join(error.messages) if hasattr(error, "messages") else str(error),
                )
                return redirect(
                    "caja:administrar_caja",
                    id_caja=apertura.caja.id_caja
                )

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