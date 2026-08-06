import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse

from apps.security.models import Usuario, RolPermiso
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log

from .models import Venta
from .repositories import VentaRepository
from .services import ComprobanteEmailService, VentaService, VentaValidationError


# =====================================================
# LISTAR VENTAS
# =====================================================

@login_required
@permiso_requerido("Ventas", "CONSULTAR")
def lista_ventas(request):
    # Reporte de ventas del día: filtra por la fecha recibida en ?fecha=
    # (input type="date" del template) o, si no se envía nada, por hoy.
    fecha_str = request.GET.get("fecha", "").strip()

    if fecha_str:
        try:
            fecha_filtro = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_filtro = timezone.localdate()
    else:
        fecha_filtro = timezone.localdate()

    # Bug corregido (05-08): filtrar con `fecha__date=fecha_filtro` depende de que
    # MySQL pueda convertir el DATETIME (guardado en UTC, porque USE_TZ=True) a la
    # zona horaria local ('America/Costa_Rica') vía CONVERT_TZ() — y esa función
    # devuelve NULL en silencio si las tablas de zonas horarias de MySQL no están
    # cargadas (mysql_tzinfo_to_sql), algo que casi nunca viene configurado por
    # defecto. El resultado es que el filtro no fallaba con un error visible: solo
    # dejaba de encontrar filas, como si no existiera ninguna venta ese día.
    # En vez de depender de esa conversión en SQL, se calcula el rango
    # [inicio_dia, fin_dia) del día local directamente en Python (aware,
    # usando la zona horaria activa) y se compara con >=/< — Django convierte esos
    # dos límites a UTC una sola vez, sin necesitar CONVERT_TZ en cada fila.
    inicio_dia = timezone.make_aware(
        datetime.combine(fecha_filtro, datetime.min.time())
    )
    fin_dia = inicio_dia + timedelta(days=1)

    ventas = VentaRepository.listar_por_rango(inicio_dia, fin_dia)

    # Las anuladas (estado=False) se siguen listando (para que se vea el
    # badge "Anulada"), pero no cuentan para el total recaudado del día.
    ventas_activas = ventas.filter(estado=True)

    total_recaudado = VentaRepository.total_recaudado(ventas_activas)
    cantidad_ventas = ventas_activas.count()

    # Caja abierta del usuario actual, para el botón "Volver a Caja".
    apertura = VentaRepository.apertura_activa(request.usuario)

    return render(
        request,
        "ventas/lista_ventas.html",
        {
            "ventas": ventas,
            "fecha_filtro": fecha_filtro,
            "total_recaudado": total_recaudado,
            "cantidad_ventas": cantidad_ventas,
            "apertura": apertura,
        }
    )


# =====================================================
# CREAR VENTA (PANTALLA DEL POS)
# =====================================================
#
# Esta vista solo RENDERIZA la pantalla del POS (GET). El registro real de
# la venta (cobrar) y el guardado de un borrador (pausar) ya no ocurren
# aquí ni dependen de un inlineformset_factory: ambos flujos se manejan en
# procesar_venta() más abajo, que recibe el carrito completo como JSON vía
# fetch() desde crear_venta.html.

@login_required
@permiso_requerido("Ventas", "CREAR")
def crear_venta(request):
    # 1. Usuario en sesión (ya validado por @login_required)
    usuario = request.usuario

    # 2. Validar caja abierta
    apertura = VentaRepository.apertura_activa(usuario)

    if not apertura:
        messages.error(request, "Debe tener una caja abierta para registrar ventas.")
        return redirect("caja:lista_cajas")

    # Recuperar venta activa en curso (si el usuario está retomando una pendiente)
    id_venta_activa = request.session.get("venta_activa_id")
    venta_activa = VentaRepository.obtener_activa_sesion(id_venta_activa)

    # Serializar los detalles de la venta activa (si existe) para enviarlos como JSON al frontend POS.
    # El carrito en JS arranca directamente desde este arreglo (carrito = detallesActivosJson)
    # en vez de depender de una función puente tipo "agregarAlCarritoDirecto".
    detalles_activos_list = []
    if venta_activa:
        for det in VentaRepository.detalles_con_producto(venta_activa):
            detalles_activos_list.append({
                "producto_id": det.producto_id,
                "nombre": det.producto.nombre,
                "cantidad": int(det.cantidad),
                "precio": float(det.precio_unitario),
                "subtotal": float(det.subtotal),
            })

    # Catálogo real de métodos de pago para los checkboxes del POS. Se excluye
    # "Pendiente" porque es un método interno usado solo por el flujo de
    # pausar, no una opción de cobro real.
    metodos_pago_disponibles = VentaRepository.metodos_pago_pos()

    # Tasa de IVA real (suma de las tasas activas con aplica_ventas=True),
    # para que el preview del carrito en el navegador use el mismo
    # porcentaje que calcular_impuesto_ventas() usa en el servidor — antes
    # el JS tenía un 13% fijo, que podía no coincidir con la tasa
    # configurada y rechazar un cobro válido por "monto insuficiente".
    tasa_iva = VentaRepository.tasa_iva_activa()

    # Catálogo de categorías activas para la cuadrícula táctil de productos
    # del POS (pestañas de categoría + tiles de producto). Los productos de
    # cada pestaña se cargan por AJAX vía productos:buscar_producto_pos
    # (parámetro categoria_id) cuando el cajero la toca, no se precargan
    # todos aquí para no inflar el HTML inicial de la página.
    categorias = VentaRepository.categorias_activas()

    return render(
        request,
        "ventas/crear_venta.html",
        {
            "usuario_activo": usuario,
            "apertura": apertura,
            "caja": apertura.caja if apertura else None,
            "venta_activa": venta_activa,
            # Objeto Python crudo (NO pre-serializado): el template lo pasa
            # por el filtro |json_script, que ya se encarga de convertirlo a
            # JSON una sola vez.
            "detalles_activos": detalles_activos_list,
            "metodos_pago_disponibles": metodos_pago_disponibles,
            "categorias": categorias,
            "tasa_iva": tasa_iva,
        }
    )


# =====================================================
# PROCESAR VENTA (JSON/AJAX) — COBRAR O PAUSAR
# =====================================================

@transaction.atomic
def procesar_venta(request):
    """
    Vista JSON/AJAX que reemplaza la lógica POST que antes tenían
    crear_venta() y guardar_venta_pendiente(). El carrito del POS ya no se
    arma como un Django inlineformset_factory (nombres de campo tipo
    "detalle-0-producto", con un input oculto para la PK de cada fila) —
    ese enfoque resultó frágil: bug de método de pago con código de texto
    en vez de PK real, bug de repoblado de carrito al reanudar una venta
    pausada y, finalmente, un bug persistente de
    "id_detalle_venta: Este campo es obligatorio" que sobrevivió incluso
    forzando required=False sobre el campo de la PK.

    Ahora el carrito vive como un array de JavaScript (fuente de verdad
    única en el navegador, ver venta_pos.js) y se envía completo como un
    solo JSON en el body de un POST con Content-Type: application/json.
    Esta vista lo procesa directamente: sin formsets, sin índices de fila,
    sin campos ocultos de PK.

    La validación/cálculo del carrito, el cobro y el pausado viven en
    VentaService (apps.ventas.services) — esta vista se limita a
    autenticar, parsear el JSON de entrada, orquestar las llamadas al
    servicio y traducir el resultado (o una VentaValidationError) a
    JsonResponse.

    Contrato de entrada (JSON):
    {
        "accion": "cobrar" | "pausar",
        "cliente_id": 5 | null,
        "tipo_comprobante": "TICKET",
        "productos": [
            {"producto_id": 12, "cantidad": 2}
        ],
        "pagos": [
            {"metodo_pago_id": 3, "monto": "150.00", "referencia": ""}
        ]
    }

    "pagos" solo es obligatorio (y se valida) cuando accion == "cobrar".

    REGLA DE SEGURIDAD DEL PROYECTO: precio_unitario y subtotal NUNCA se
    leen del JSON recibido, ni para "cobrar" ni para "pausar" — se
    recalculan siempre en el servidor a partir de Producto.precio_venta.
    El navegador nunca es la fuente de verdad del dinero.

    Contrato de salida:
      Éxito: {"ok": true, "id_venta": ..., "numero_venta": "...", "redirect_url": "..."}
      Error: {"ok": false, "error": "mensaje claro"}  (HTTP 400, o 405 si
             el método HTTP no es POST)
    """

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)

    # 1. Usuario, permiso y caja abierta.
    #
    # Endpoint JSON/AJAX: no se usa @login_required/@permiso_requerido
    # (redirigen a HTML, lo que rompe el fetch() del navegador) — se
    # valida sesión y permiso a mano, respondiendo siempre JSON.
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse(
            {"ok": False, "error": "No se pudo identificar el usuario actual. Inicie sesión nuevamente."},
            status=401,
        )

    usuario = Usuario.objects.filter(id_usuario=usuario_id, estado=True).first()
    if not usuario:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado o inactivo."}, status=401)

    tiene_permiso = RolPermiso.objects.filter(
        id_rol=usuario.id_rol,
        id_permiso__id_modulo__nombre="Ventas",
        id_permiso__accion="CREAR",
    ).exists()
    if not tiene_permiso:
        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Ventas",
            tipo_accion="ACCESO_DENEGADO",
            descripcion="Intento de ejecutar CREAR sin autorización.",
        )
        return JsonResponse(
            {"ok": False, "error": "No tiene permisos para registrar ventas."},
            status=403,
        )

    apertura = VentaRepository.apertura_activa(usuario)

    if not apertura:
        return JsonResponse(
            {"ok": False, "error": "Debe tener una caja abierta para registrar ventas."},
            status=400,
        )

    # 2. Parseo del body JSON
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "El cuerpo de la solicitud no es JSON válido."}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"ok": False, "error": "El cuerpo de la solicitud no tiene el formato esperado."}, status=400)

    accion = data.get("accion")
    if accion not in ("cobrar", "pausar"):
        return JsonResponse({"ok": False, "error": "Acción inválida. Debe ser 'cobrar' o 'pausar'."}, status=400)

    tipo_comprobante = (data.get("tipo_comprobante") or "TICKET").strip() or "TICKET"

    # 3. Recuperar la venta activa de la sesión (si el cajero está
    #    reanudando una venta previamente pausada) para actualizarla en vez
    #    de crear una fila duplicada en la tabla venta.
    id_venta_activa = request.session.get("venta_activa_id")
    venta = VentaRepository.obtener_activa_sesion(id_venta_activa)
    if venta is None:
        venta = Venta()

    es_venta_nueva = venta.pk is None

    # 4. Validación/cálculo del carrito, cliente y (si aplica) pagos —
    #    delegado a VentaService. Cualquier problema de negocio se
    #    traduce aquí a la misma respuesta JsonResponse que antes.
    try:
        cliente = VentaService.resolver_cliente(data.get("cliente_id"))
        lineas = VentaService.validar_y_calcular_lineas(data.get("productos") or [])
        totales = VentaService.calcular_totales(lineas)

        if accion == "pausar":
            venta = VentaService.pausar(
                venta, usuario, apertura, cliente, tipo_comprobante,
                lineas, totales, es_venta_nueva,
            )
        else:
            pagos_temp = VentaService.validar_pagos(data.get("pagos") or [], totales["total"])
            venta = VentaService.cobrar(
                venta, usuario, apertura, cliente, tipo_comprobante,
                lineas, totales, pagos_temp, es_venta_nueva,
            )
    except VentaValidationError as error:
        return JsonResponse({"ok": False, "error": str(error)}, status=400)

    # 5. Bookkeeping de sesión y auditoría (según la acción realizada).
    if accion == "pausar":
        ventas_pendientes = request.session.get("ventas_pendientes", [])
        if venta.id_venta not in ventas_pendientes:
            ventas_pendientes.append(venta.id_venta)
            request.session["ventas_pendientes"] = ventas_pendientes

        # Liberar el POS para el siguiente cliente.
        if "venta_activa_id" in request.session:
            del request.session["venta_activa_id"]

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Ventas",
            tipo_accion="CREAR",
            descripcion=f"Se pausó la venta {venta.numero_venta}",
        )

        return JsonResponse({
            "ok": True,
            "id_venta": venta.id_venta,
            "numero_venta": venta.numero_venta,
            "redirect_url": reverse("ventas:crear_venta"),
        })

    # accion == "cobrar"
    if request.session.get("venta_activa_id") == venta.id_venta:
        del request.session["venta_activa_id"]

    ventas_pendientes = request.session.get("ventas_pendientes", [])
    if venta.id_venta in ventas_pendientes:
        ventas_pendientes.remove(venta.id_venta)
        request.session["ventas_pendientes"] = ventas_pendientes

    registrar_log(
        request=request,
        usuario=usuario,
        modulo="Ventas",
        tipo_accion="CREAR",
        descripcion=f"Se registró la venta {venta.numero_venta}",
    )

    return JsonResponse({
        "ok": True,
        "id_venta": venta.id_venta,
        "numero_venta": venta.numero_venta,
        "redirect_url": reverse("ventas:detalle_venta", args=[venta.id_venta]),
    })


# =====================================================
# FLUJO POS: LISTAR / RETOMAR / ELIMINAR VENTAS PENDIENTES
# =====================================================
#
# pausar_venta() y guardar_venta_pendiente() (POST con formset) se
# eliminaron: "pausar" ahora es una de las dos acciones de
# procesar_venta() (JSON). listar_ventas_pendientes, retomar_venta y
# eliminar_venta_pendiente no dependían del formset y siguen igual.

@login_required
@permiso_requerido("Ventas", "CONSULTAR")
def listar_ventas_pendientes(request):
    """Muestra la lista de facturas que fueron pausadas temporalmente."""
    ids_pendientes = request.session.get('ventas_pendientes', [])
    ventas_pendientes = VentaRepository.listar_pendientes(ids_pendientes)

    return render(
        request,
        'ventas/ventas_pendientes.html',
        {
            'ventas_pendientes': ventas_pendientes
        }
    )


@login_required
@permiso_requerido("Ventas", "CREAR")
def retomar_venta(request, id_venta):
    """Carga una venta pendiente de regreso al POS para continuar con el cobro."""
    request.session['venta_activa_id'] = id_venta

    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if id_venta in ventas_pendientes:
        ventas_pendientes.remove(id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes

    venta = VentaRepository.obtener_activa_sesion(id_venta)
    registrar_log(
        request=request,
        usuario=request.usuario,
        modulo="Ventas",
        tipo_accion="MODIFICAR",
        descripcion=f"Retomó la venta pendiente {venta.numero_venta if venta else id_venta} para continuar el cobro.",
    )

    messages.success(request, "Venta retomada con éxito. Puede proceder al cobro.")
    return redirect('ventas:crear_venta')


@login_required
@permiso_requerido("Ventas", "ELIMINAR")
@transaction.atomic
def eliminar_venta_pendiente(request, id_venta):
    """Elimina una venta pendiente de la sesión y borra su registro borrador."""

    # Antes accesible por GET (un simple <a href>, sin CSRF): cualquier
    # enlace/imagen manipulado podía borrar una venta pendiente con solo
    # cargarse en el navegador de un usuario autenticado. Ahora exige POST
    # (el template ya envía la eliminación como formulario con token CSRF).
    if request.method != "POST":
        return redirect('ventas:ventas_pendientes')

    ventas_pendientes = request.session.get('ventas_pendientes', [])
    if id_venta in ventas_pendientes:
        ventas_pendientes.remove(id_venta)
        request.session['ventas_pendientes'] = ventas_pendientes

    venta = VentaRepository.obtener_activa_sesion(id_venta)
    if venta:
        numero_venta = venta.numero_venta
        VentaRepository.eliminar_detalles(venta)
        VentaRepository.eliminar_pagos(venta)
        VentaRepository.eliminar(venta)

        registrar_log(
            request=request,
            usuario=request.usuario,
            modulo="Ventas",
            tipo_accion="ELIMINAR",
            descripcion=f"Se eliminó la venta pendiente {numero_venta}",
        )

    messages.success(request, "Venta pendiente eliminada correctamente.")
    return redirect('ventas:ventas_pendientes')


# =====================================================
# DETALLE DE VENTA
# =====================================================

@login_required
@permiso_requerido("Ventas", "CONSULTAR")
def detalle_venta(request, id_venta):
    venta = get_object_or_404(
        VentaRepository.con_relaciones_completas(), id_venta=id_venta
    )
    detalles = VentaRepository.detalles_con_producto(venta)
    pagos = VentaRepository.pagos_con_metodo(venta)

    # Una venta está pendiente/pausada si y solo si su método de pago
    # directo es el método interno "Pendiente" (ver VentaService.pausar,
    # única fuente de verdad de esta regla).
    es_pendiente = bool(venta.metodo_pago_id) and venta.metodo_pago.nombre.strip().lower() == "pendiente"

    return render(
        request,
        "ventas/detalle_venta.html",
        {
            "venta": venta,
            "detalles": detalles,
            "pagos": pagos,
            "es_pendiente": es_pendiente,
        }
    )


# =====================================================
# COMPROBANTE DE VENTA (IMPRIMIBLE)
# =====================================================

@login_required
@permiso_requerido("Ventas", "CONSULTAR")
def comprobante_venta(request, id_venta):
    """Recibo/factura imprimible de una venta ya registrada (standalone,
    sin sidebar/navbar) — pensado para abrirse en una pestaña nueva desde
    detalle_venta.html y usarse con window.print()."""
    venta = get_object_or_404(
        VentaRepository.con_relaciones_completas(), id_venta=id_venta
    )
    detalles = VentaRepository.detalles_con_producto(venta)
    pagos = VentaRepository.pagos_con_metodo(venta)
    datos_empresa = VentaRepository.datos_empresa()

    return render(
        request,
        "ventas/comprobante_venta.html",
        {
            "venta": venta,
            "detalles": detalles,
            "pagos": pagos,
            "datos_empresa": datos_empresa,
        }
    )


# =====================================================
# ENVIAR COMPROBANTE POR CORREO
# =====================================================

@login_required
@permiso_requerido("Ventas", "CONSULTAR")
def enviar_comprobante_email(request, id_venta):
    """
    Envía el comprobante de una venta ya registrada al correo del cliente
    asociado (botón "Enviar por correo" de detalle_venta.html).

    Solo POST: mismo criterio aplicado el 05-08 a activar_caja/
    desactivar_caja — una acción con efecto real (aquí, disparar un envío
    de correo) nunca debe poder dispararse desde un simple enlace/GET.
    """
    if request.method != "POST":
        return redirect("ventas:detalle_venta", id_venta=id_venta)

    venta = get_object_or_404(
        VentaRepository.con_relaciones_completas(), id_venta=id_venta
    )
    detalles = VentaRepository.detalles_con_producto(venta)
    pagos = VentaRepository.pagos_con_metodo(venta)
    datos_empresa = VentaRepository.datos_empresa()

    try:
        destinatario = ComprobanteEmailService.enviar(
            venta, detalles, pagos, datos_empresa
        )
    except ValueError as error:
        # Validación de negocio (sin cliente / sin correo registrado) — el
        # mensaje ya viene listo para mostrar, no es un error de servidor.
        messages.error(request, str(error))
    except Exception:
        # Cualquier falla real de envío (servidor SMTP caído, credenciales
        # inválidas en EMAIL_HOST_USER/EMAIL_HOST_PASSWORD, sin conexión,
        # etc.) no debe romper la página — se avisa con un mensaje claro.
        messages.error(
            request,
            "No se pudo enviar el comprobante por correo. Verifique la "
            "configuración de correo del sistema (EMAIL_HOST/"
            "EMAIL_HOST_USER/EMAIL_HOST_PASSWORD en el archivo .env) e "
            "intente de nuevo."
        )
    else:
        messages.success(
            request, f"Comprobante enviado correctamente a {destinatario}."
        )
        # No existe un tipo_accion propio para "envío de correo" en el ENUM
        # de log_acciones (LOGIN/LOGOUT/CREAR/MODIFICAR/ELIMINAR/CONSULTAR/
        # EXPORTAR/IMPORTAR/ERROR/ACCESO_DENEGADO/RECUPERAR_PASSWORD/
        # CAMBIAR_PASSWORD) — se reutiliza "EXPORTAR", el mismo que ya usa
        # el módulo de Reportes para "entregar un documento generado hacia
        # afuera del sistema", que es exactamente lo que hace esta acción.
        registrar_log(
            request=request,
            usuario=request.usuario,
            modulo="Ventas",
            tipo_accion="EXPORTAR",
            descripcion=(
                f"Envió el comprobante de la venta {venta.numero_venta} "
                f"por correo a {destinatario}."
            ),
        )

    return redirect("ventas:detalle_venta", id_venta=id_venta)


# =====================================================
# ANULAR VENTA
# =====================================================

@login_required
@permiso_requerido("Ventas", "ELIMINAR")
@transaction.atomic
def anular_venta(request, id_venta):
    """
    Anula una venta existente, revierte su estado e incrementa nuevamente
    el stock en el inventario de la sucursal correspondiente. La lógica de
    negocio (validar el tipo de movimiento, revertir estado, reintegrar
    inventario) vive en VentaService.anular().
    """
    venta = get_object_or_404(Venta, pk=id_venta)

    # Validar si ya está anulada
    if not venta.estado:
        messages.warning(request, f"La venta {venta.numero_venta} ya se encuentra anulada.")
        return redirect('ventas:lista_ventas')

    if request.method == "POST":
        usuario = request.usuario

        # El formulario pide un motivo de anulación (campo obligatorio en
        # anular_venta.html), pero la tabla real `venta` no tiene columna
        # para guardarlo. En vez de descartarlo en silencio, se persiste en
        # la bitácora (LogAcciones vía registrar_log), que es la fuente de
        # auditoría del sistema para este tipo de acción.
        motivo_anulacion = (request.POST.get("motivo_anulacion") or "").strip()

        try:
            venta = VentaService.anular(venta, usuario, motivo_anulacion)
        except VentaValidationError as error:
            messages.error(request, str(error))
            return redirect('ventas:lista_ventas')

        messages.success(request, f"La venta **{venta.numero_venta}** ha sido anulada exitosamente y el inventario fue devuelto.")

        descripcion_log = f"Se anuló la venta {venta.numero_venta}"
        if motivo_anulacion:
            descripcion_log += f" — motivo: {motivo_anulacion}"

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Ventas",
            tipo_accion="MODIFICAR",
            descripcion=descripcion_log,
        )

        return redirect('ventas:lista_ventas')

    context = {
        "venta": venta
    }
    return render(request, "ventas/anular_venta.html", context)


# =====================================================
# BÚSQUEDA DE CLIENTES PARA EL POS (JSON)
# =====================================================

def buscar_clientes_pos(request):
    # Endpoint AJAX (fetch desde el POS): no se usa @login_required (que
    # redirige a /security/login/, rompiendo el fetch con HTML en vez de
    # JSON) — se valida la sesión a mano y se responde 401 en JSON.
    if not request.session.get("usuario_id"):
        return JsonResponse({"error": "No autenticado."}, status=401)

    query = request.GET.get("q", "")
    return JsonResponse(VentaService.buscar_clientes_pos(query))
