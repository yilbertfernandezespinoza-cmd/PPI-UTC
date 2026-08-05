import json
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse

from apps.security.models import Usuario
from apps.inventario.models import TipoMovimientoInventario
from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService
from apps.clientes.models import Cliente
from apps.productos.models import Producto
from apps.categorias.models import Categoria
from apps.configuracion.models import MetodoPago
from apps.caja.models import MovimientoCaja, AperturaCaja

from .models import Venta, DetalleVenta, DetallePago
from .utils import (
    generar_numero_venta,
    calcular_impuesto_ventas,
    determinar_metodo_pago_venta,
)


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
# CREAR VENTA (PANTALLA DEL POS)
# =====================================================
#
# Esta vista solo RENDERIZA la pantalla del POS (GET). El registro real de
# la venta (cobrar) y el guardado de un borrador (pausar) ya no ocurren
# aquí ni dependen de un inlineformset_factory: ambos flujos se manejan en
# procesar_venta() más abajo, que recibe el carrito completo como JSON vía
# fetch() desde crear_venta.html.

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

    # Serializar los detalles de la venta activa (si existe) para enviarlos como JSON al frontend POS.
    # El carrito en JS arranca directamente desde este arreglo (carrito = detallesActivosJson)
    # en vez de depender de una función puente tipo "agregarAlCarritoDirecto".
    detalles_activos_list = []
    if venta_activa:
        for det in venta_activa.detalleventa_set.select_related("producto").all():
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
    metodos_pago_disponibles = MetodoPago.objects.filter(
        estado=True
    ).exclude(
        nombre__iexact="Pendiente"
    ).order_by("nombre")

    # Catálogo de categorías activas para la cuadrícula táctil de productos
    # del POS (pestañas de categoría + tiles de producto). Los productos de
    # cada pestaña se cargan por AJAX vía productos:buscar_producto_pos
    # (parámetro categoria_id) cuando el cajero la toca, no se precargan
    # todos aquí para no inflar el HTML inicial de la página.
    categorias = Categoria.objects.filter(estado=True).order_by("nombre")

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
            # JSON una sola vez. Antes de esta corrección se enviaba aquí un
            # json.dumps(...) y el template volvía a aplicarle json_script
            # encima — eso produce doble codificación (un string JSON
            # dentro de otro string JSON) y hace que
            # JSON.parse(...) en el navegador devuelva un string en vez de
            # un arreglo, rompiendo con un TypeError el repoblado del
            # carrito al reanudar una venta pausada.
            "detalles_activos": detalles_activos_list,
            "metodos_pago_disponibles": metodos_pago_disponibles,
            "categorias": categorias,
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
    recalculan siempre en el servidor a partir de Producto.precio_venta,
    exactamente igual que ya hacía crear_venta() antes de esta migración.
    El navegador nunca es la fuente de verdad del dinero.

    Contrato de salida:
      Éxito: {"ok": true, "id_venta": ..., "numero_venta": "...", "redirect_url": "..."}
      Error: {"ok": false, "error": "mensaje claro"}  (HTTP 400, o 405 si
             el método HTTP no es POST)
    """

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)

    # 1. Usuario y caja abierta (mismos requisitos que el flujo anterior)
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse(
            {"ok": False, "error": "No se pudo identificar el usuario actual. Inicie sesión nuevamente."},
            status=400,
        )

    usuario = Usuario.objects.filter(id_usuario=usuario_id).first()
    if not usuario:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado."}, status=400)

    apertura = AperturaCaja.objects.filter(
        usuario=usuario, estado=True
    ).select_related("caja", "caja__sucursal").first()

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

    productos_json = data.get("productos") or []
    if not isinstance(productos_json, list) or len(productos_json) == 0:
        return JsonResponse({"ok": False, "error": "La venta debe contener al menos un producto."}, status=400)

    # 3. Cliente (opcional — venta "Público General" si no se envía)
    cliente = None
    cliente_id = data.get("cliente_id")
    if cliente_id not in (None, "", 0):
        cliente = Cliente.objects.filter(pk=cliente_id).first()
        if not cliente:
            return JsonResponse({"ok": False, "error": "El cliente seleccionado no existe."}, status=400)

    tipo_comprobante = (data.get("tipo_comprobante") or "TICKET").strip() or "TICKET"

    # 4. VALIDAR Y RECALCULAR CADA LÍNEA DEL CARRITO EN EL SERVIDOR.
    #    El navegador solo informa producto_id + cantidad; precio_unitario
    #    y subtotal se derivan siempre de Producto.precio_venta.
    lineas = []
    for item in productos_json:
        if not isinstance(item, dict):
            return JsonResponse({"ok": False, "error": "Formato de producto inválido en el carrito."}, status=400)

        try:
            producto_id = int(item.get("producto_id"))
            cantidad = int(float(item.get("cantidad")))
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "Producto o cantidad inválidos en el carrito."}, status=400)

        if cantidad <= 0:
            return JsonResponse({"ok": False, "error": "La cantidad de cada producto debe ser mayor a cero."}, status=400)

        producto = Producto.objects.filter(pk=producto_id, estado=True).first()
        if not producto:
            return JsonResponse(
                {"ok": False, "error": f"El producto con id {producto_id} no existe o está inactivo."},
                status=400,
            )

        precio_unitario = producto.precio_venta or Decimal("0.00")
        subtotal_linea = (precio_unitario * cantidad).quantize(Decimal("0.01"))

        lineas.append({
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal_linea,
        })

    subtotal_calculado = sum((linea["subtotal"] for linea in lineas), Decimal("0.00"))
    impuesto_calculado = calcular_impuesto_ventas(subtotal_calculado)
    descuento_calculado = Decimal("0.00")
    total_calculado = subtotal_calculado + impuesto_calculado - descuento_calculado

    # 5. Recuperar la venta activa de la sesión (si el cajero está
    #    reanudando una venta previamente pausada) para actualizarla en vez
    #    de crear una fila duplicada en la tabla venta.
    id_venta_activa = request.session.get("venta_activa_id")
    venta = Venta.objects.filter(id_venta=id_venta_activa).first() if id_venta_activa else None
    if venta is None:
        venta = Venta()

    es_venta_nueva = venta.pk is None

    # =====================================================
    # ACCIÓN: PAUSAR (guardar como borrador pendiente)
    # =====================================================
    if accion == "pausar":
        # Método de pago interno "Pendiente" — igual que el flujo anterior
        # de guardar_venta_pendiente(), reutilizando el mismo patrón
        # get_or_create ya usado en utils.determinar_metodo_pago_venta().
        metodo_pendiente, _creado = MetodoPago.objects.get_or_create(
            nombre__iexact="Pendiente",
            defaults={"nombre": "Pendiente"},
        )

        venta.usuario = usuario
        venta.caja = apertura.caja
        venta.cliente = cliente
        venta.tipo_comprobante = tipo_comprobante
        venta.fecha = timezone.now()
        if es_venta_nueva:
            venta.fecha_creacion = timezone.now()
        venta.fecha_actualizacion = timezone.now()
        venta.estado = True
        venta.metodo_pago = metodo_pendiente
        venta.subtotal = subtotal_calculado
        venta.impuesto = impuesto_calculado
        venta.descuento = descuento_calculado
        venta.total = total_calculado

        if not venta.numero_venta:
            venta.numero_venta = generar_numero_venta()

        venta.save()

        # Pausar es solo un borrador: el inventario NO se toca aquí (igual
        # que hacía guardar_venta_pendiente() antes de esta migración). El
        # stock real se valida y se descuenta únicamente al cobrar de
        # verdad, porque entre el momento de pausar y el de retomar/cobrar
        # puede pasar cualquier cosa con las existencias (otra venta, un
        # ajuste, una merma) — reservarlo en la pausa daría una falsa
        # sensación de reserva de stock que el sistema no implementa.
        DetalleVenta.objects.filter(venta=venta).delete()
        DetallePago.objects.filter(venta=venta).delete()

        for linea in lineas:
            DetalleVenta.objects.create(
                venta=venta,
                producto=linea["producto"],
                cantidad=linea["cantidad"],
                precio_unitario=linea["precio_unitario"],
                subtotal=linea["subtotal"],
            )

        ventas_pendientes = request.session.get("ventas_pendientes", [])
        if venta.id_venta not in ventas_pendientes:
            ventas_pendientes.append(venta.id_venta)
            request.session["ventas_pendientes"] = ventas_pendientes

        # Liberar el POS para el siguiente cliente.
        if "venta_activa_id" in request.session:
            del request.session["venta_activa_id"]

        return JsonResponse({
            "ok": True,
            "id_venta": venta.id_venta,
            "numero_venta": venta.numero_venta,
            "redirect_url": reverse("ventas:crear_venta"),
        })

    # =====================================================
    # ACCIÓN: COBRAR (venta real, descuenta inventario)
    # =====================================================

    # 6. VALIDACIÓN DE MÉTODOS DE PAGO. Se construyen instancias no
    #    guardadas de DetallePago (igual que antes hacía
    #    pago_formset.save(commit=False)) para poder reutilizar
    #    determinar_metodo_pago_venta() sin reescribirla.
    pagos_json = data.get("pagos") or []
    if not isinstance(pagos_json, list) or len(pagos_json) == 0:
        return JsonResponse({"ok": False, "error": "Debe seleccionar al menos un método de pago."}, status=400)

    pagos_temp = []
    for pago in pagos_json:
        if not isinstance(pago, dict):
            return JsonResponse({"ok": False, "error": "Formato de pago inválido."}, status=400)

        metodo_pago = MetodoPago.objects.filter(pk=pago.get("metodo_pago_id"), estado=True).first()
        if not metodo_pago:
            return JsonResponse({"ok": False, "error": "Uno de los métodos de pago seleccionados no es válido."}, status=400)

        try:
            monto = Decimal(str(pago.get("monto")))
        except (InvalidOperation, TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "Monto de pago inválido."}, status=400)

        if monto <= 0:
            return JsonResponse({"ok": False, "error": "El monto de cada pago debe ser mayor a cero."}, status=400)

        referencia = (pago.get("referencia") or "").strip()[:100]

        pagos_temp.append(DetallePago(
            metodo_pago=metodo_pago,
            monto=monto,
            referencia=referencia,
            fecha_creacion=timezone.now(),
        ))

    total_pagado = sum((pago.monto for pago in pagos_temp), Decimal("0.00"))
    if total_pagado < total_calculado:
        return JsonResponse(
            {
                "ok": False,
                "error": f"El monto pagado (₡{total_pagado}) es menor al total de la factura (₡{total_calculado}).",
            },
            status=400,
        )

    # 7. TIPO DE MOVIMIENTO REQUERIDO PARA DESCONTAR STOCK. Se valida antes
    #    de guardar nada para no dejar una venta a medias si todavía no se
    #    sembró el catálogo (seed_tipos_movimiento).
    tipo_salida_venta = TipoMovimientoInventario.objects.filter(nombre="SALIDA_VENTA").first()
    if not tipo_salida_venta:
        return JsonResponse(
            {
                "ok": False,
                "error": "Falta configurar el tipo de movimiento 'SALIDA_VENTA' en Inventario. "
                         "Ejecute: python manage.py seed_tipos_movimiento",
            },
            status=400,
        )

    # 8. VALIDACIÓN DE INVENTARIO (bloqueando cada fila para evitar
    #    condiciones de carrera con otra venta/compra simultánea). Los
    #    registros ya bloqueados se reutilizan más abajo: así se consulta
    #    Inventario una sola vez por producto, no dos.
    inventarios_bloqueados = {}
    for linea in lineas:
        inventario = InventarioRepository.obtener_para_actualizar(
            linea["producto"], apertura.caja.sucursal
        )

        if not inventario:
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"El producto {linea['producto'].nombre} no está habilitado en el "
                             f"inventario de esta sucursal.",
                },
                status=400,
            )

        if inventario.stock_actual < linea["cantidad"]:
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"No hay existencias suficientes de {linea['producto'].nombre}. "
                             f"Stock actual: {inventario.stock_actual}",
                },
                status=400,
            )

        inventarios_bloqueados[linea["producto"].pk] = inventario

    # 9. ASIGNACIÓN DE DATOS Y GUARDADO DE LA VENTA
    venta.usuario = usuario
    venta.caja = apertura.caja
    venta.cliente = cliente
    venta.tipo_comprobante = tipo_comprobante
    venta.fecha = timezone.now()
    if es_venta_nueva:
        venta.fecha_creacion = timezone.now()
    venta.fecha_actualizacion = timezone.now()
    venta.estado = True
    venta.subtotal = subtotal_calculado
    venta.impuesto = impuesto_calculado
    venta.descuento = descuento_calculado
    venta.total = total_calculado
    venta.metodo_pago = determinar_metodo_pago_venta(pagos_temp)

    if not venta.numero_venta:
        venta.numero_venta = generar_numero_venta()

    venta.save()

    # 10. REGISTRO AUTOMÁTICO DE MOVIMIENTO EN CAJA
    MovimientoCaja.objects.create(
        apertura=apertura,
        usuario=usuario,
        tipo_movimiento="VENTA",
        monto=venta.total,
        descripcion=f"Venta {venta.numero_venta}",
        fecha_movimiento=timezone.now(),
    )

    # Si se está reanudando una venta pausada, sus líneas previas (guardadas
    # sin tocar inventario) se reemplazan por el detalle definitivo que
    # llegó en este JSON, para no duplicar filas ni descontar dos veces.
    DetalleVenta.objects.filter(venta=venta).delete()
    DetallePago.objects.filter(venta=venta).delete()

    # 11. GUARDAR DETALLES Y DESCONTAR INVENTARIO (vía
    #     MovimientoInventarioService: deja registro en movimiento_inventario
    #     en vez de mutar stock_actual a mano).
    for linea in lineas:
        detalle = DetalleVenta(
            venta=venta,
            producto=linea["producto"],
            cantidad=linea["cantidad"],
            precio_unitario=linea["precio_unitario"],
            subtotal=linea["subtotal"],
        )
        detalle.save()

        try:
            MovimientoInventarioService.registrar_movimiento(
                inventario=inventarios_bloqueados[linea["producto"].pk],
                tipo_movimiento=tipo_salida_venta,
                usuario=usuario,
                cantidad=linea["cantidad"],
                observaciones=f"Venta {venta.numero_venta}",
            )
        except ValidationError as error_inventario:
            # Fuerza el rollback del bloque @transaction.atomic aunque se
            # responda con un JsonResponse normal (no una excepción).
            transaction.set_rollback(True)
            mensaje = "; ".join(error_inventario.messages) if hasattr(error_inventario, "messages") else str(error_inventario)
            return JsonResponse(
                {"ok": False, "error": f"{linea['producto'].nombre}: {mensaje}"},
                status=400,
            )

    # 12. GUARDAR DETALLE DE PAGOS
    for pago in pagos_temp:
        pago.venta = venta
        pago.save()

    # 13. Limpiar la venta de las listas de sesión (activa y pendientes)
    if request.session.get("venta_activa_id") == venta.id_venta:
        del request.session["venta_activa_id"]

    ventas_pendientes = request.session.get("ventas_pendientes", [])
    if venta.id_venta in ventas_pendientes:
        ventas_pendientes.remove(venta.id_venta)
        request.session["ventas_pendientes"] = ventas_pendientes

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
        # 0. Identificar al usuario que anula (requerido por
        #    MovimientoInventarioService para dejar rastro en la auditoría
        #    de inventario; antes esta vista no identificaba a nadie).
        usuario_id = request.session.get("usuario_id")
        if not usuario_id:
            messages.error(request, "No se pudo identificar el usuario actual.")
            return redirect("security:login")

        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

        try:
            tipo_devolucion_venta = TipoMovimientoInventario.objects.get(
                nombre="DEVOLUCION_VENTA"
            )
        except TipoMovimientoInventario.DoesNotExist:
            messages.error(
                request,
                "Falta configurar el tipo de movimiento 'DEVOLUCION_VENTA' en "
                "Inventario. Ejecute: python manage.py seed_tipos_movimiento"
            )
            return redirect('ventas:lista_ventas')

        # 1. Actualizar el estado de la venta a anulada (False)
        venta.estado = False
        venta.fecha_actualizacion = timezone.now()
        venta.save()

        # 2. Reintegrar los productos al inventario (vía
        #    MovimientoInventarioService: deja registro en
        #    movimiento_inventario en vez de mutar stock_actual a mano).
        detalles = DetalleVenta.objects.filter(venta=venta)
        for detalle in detalles:
            inventario = InventarioRepository.obtener_para_actualizar(
                detalle.producto, venta.caja.sucursal
            )

            if inventario:
                MovimientoInventarioService.registrar_movimiento(
                    inventario=inventario,
                    tipo_movimiento=tipo_devolucion_venta,
                    usuario=usuario,
                    cantidad=detalle.cantidad,
                    observaciones=f"Anulación de venta {venta.numero_venta}",
                )

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
