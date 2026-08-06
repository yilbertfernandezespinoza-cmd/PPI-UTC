# Servicios del módulo
#
# VentaValidationError + VentaService (06-08): capa de negocio del flujo
# de venta (POS), extraída de views.py::procesar_venta/anular_venta para
# que ventas quede con la misma arquitectura Model → Repository → Service
# → View que ya usan clientes/ayuda/inventario. VentaService no depende
# de HttpRequest ni de JsonResponse: lanza VentaValidationError ante
# cualquier problema de negocio y la vista decide cómo mostrarlo
# (JsonResponse 400 en procesar_venta, messages.error en anular_venta).

from decimal import Decimal, InvalidOperation
from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService

from .models import DetallePago, DetalleVenta
from .repositories import VentaRepository
from .utils import (
    calcular_impuesto_ventas,
    determinar_metodo_pago_venta,
    generar_numero_venta,
)


class VentaValidationError(Exception):
    """
    Error de validación de negocio del flujo de venta (POS): carrito
    vacío, producto inválido, stock insuficiente, pago insuficiente, tipo
    de movimiento de inventario sin configurar, etc. Las vistas de este
    módulo (procesar_venta, anular_venta) capturan esta excepción y la
    traducen a la respuesta HTTP correspondiente.
    """
    pass


class VentaService:
    """
    Lógica de negocio del flujo de venta: búsqueda de clientes del POS,
    validar/calcular el carrito, cobrar o pausar una venta y anular una
    venta ya registrada. Las consultas a la base de datos viven en
    VentaRepository (y en los repositorios de otras apps, como
    InventarioRepository); este servicio orquesta esas consultas y aplica
    las reglas de negocio.
    """

    # ---------------------------------------------------
    # Búsqueda de clientes para el POS
    # ---------------------------------------------------

    @staticmethod
    def _serializar_cliente_pos(cliente):
        # Nota (06-08): "telefono" se mantiene en la respuesta aunque el
        # JS del POS no lo pinte en pantalla todavía — César confirmó que
        # se usa de forma interna para temas administrativos, así que no
        # se retira.
        return {
            "id": cliente.id_cliente,
            "nombre": cliente.nombre_completo,
            "identificacion": cliente.identificacion or "",
            "telefono": cliente.telefono or "",
        }

    @staticmethod
    def buscar_clientes_pos(query):
        """
        Regla de negocio: la cédula (identificacion) es única en la BD
        (Cliente.identificacion tiene unique=True), el nombre no. Por eso
        se prioriza la búsqueda por cédula: si el texto ingresado coincide
        EXACTO (sin importar mayúsculas/minúsculas) con la identificación
        de un cliente activo, se responde solo ese cliente con
        "exacto": true, para que el POS lo autoseleccione igual que lo
        haría un lector de código de barras/cédula, sin obligar al cajero
        a elegir entre una lista de personas que podrían compartir el
        mismo nombre. Sin match exacto, se hace una búsqueda parcial por
        cédula, nombre y apellidos (ver
        VentaRepository.buscar_clientes_activos).
        """
        query = (query or "").strip()
        if not query:
            return {"exacto": False, "resultados": []}

        cliente_exacto = VentaRepository.cliente_activo_por_identificacion_exacta(query)
        if cliente_exacto:
            return {
                "exacto": True,
                "resultados": [VentaService._serializar_cliente_pos(cliente_exacto)],
            }

        clientes = VentaRepository.buscar_clientes_activos(query)
        return {
            "exacto": False,
            "resultados": [VentaService._serializar_cliente_pos(c) for c in clientes],
        }

    # ---------------------------------------------------
    # Cliente para procesar_venta
    # ---------------------------------------------------

    @staticmethod
    def resolver_cliente(cliente_id):
        """Cliente opcional del carrito (venta 'Público General' si no se
        envía). Lanza VentaValidationError si se envió un id que no
        corresponde a ningún cliente."""
        if cliente_id in (None, "", 0):
            return None
        cliente = VentaRepository.cliente_por_id(cliente_id)
        if not cliente:
            raise VentaValidationError("El cliente seleccionado no existe.")
        return cliente

    # ---------------------------------------------------
    # Validación y cálculo del carrito
    # ---------------------------------------------------

    @staticmethod
    def validar_y_calcular_lineas(productos_json):
        """
        Valida cada línea del carrito recibido del navegador y recalcula
        su precio unitario y subtotal SIEMPRE en el servidor, a partir de
        Producto.precio_venta — el navegador solo informa producto_id +
        cantidad. Regla de seguridad del proyecto: precio_unitario y
        subtotal nunca se leen del JSON recibido. Lanza
        VentaValidationError con el mismo mensaje que antes vivía
        directamente en procesar_venta ante cualquier dato inválido.
        """
        if not isinstance(productos_json, list) or len(productos_json) == 0:
            raise VentaValidationError("La venta debe contener al menos un producto.")

        lineas = []
        for item in productos_json:
            if not isinstance(item, dict):
                raise VentaValidationError("Formato de producto inválido en el carrito.")

            try:
                producto_id = int(item.get("producto_id"))
                cantidad = int(float(item.get("cantidad")))
            except (TypeError, ValueError):
                raise VentaValidationError("Producto o cantidad inválidos en el carrito.")

            if cantidad <= 0:
                raise VentaValidationError("La cantidad de cada producto debe ser mayor a cero.")

            producto = VentaRepository.producto_activo(producto_id)
            if not producto:
                raise VentaValidationError(
                    f"El producto con id {producto_id} no existe o está inactivo."
                )

            precio_unitario = producto.precio_venta or Decimal("0.00")
            subtotal_linea = (precio_unitario * cantidad).quantize(Decimal("0.01"))

            lineas.append({
                "producto": producto,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal_linea,
            })

        return lineas

    @staticmethod
    def calcular_totales(lineas):
        """Subtotal, impuesto, descuento y total de la venta a partir de
        las líneas ya validadas. El descuento queda fijo en 0.00: el POS
        todavía no tiene una función de descuentos."""
        subtotal = sum((linea["subtotal"] for linea in lineas), Decimal("0.00"))
        impuesto = calcular_impuesto_ventas(subtotal)
        descuento = Decimal("0.00")
        total = subtotal + impuesto - descuento
        return {
            "subtotal": subtotal,
            "impuesto": impuesto,
            "descuento": descuento,
            "total": total,
        }

    # ---------------------------------------------------
    # Pagos (solo para "cobrar")
    # ---------------------------------------------------

    @staticmethod
    def validar_pagos(pagos_json, total_calculado):
        """Valida cada método de pago recibido y arma las instancias (sin
        guardar) de DetallePago. Lanza VentaValidationError si algún pago
        es inválido, o si la suma pagada no cubre el total de la
        venta."""
        if not isinstance(pagos_json, list) or len(pagos_json) == 0:
            raise VentaValidationError("Debe seleccionar al menos un método de pago.")

        pagos_temp = []
        for pago in pagos_json:
            if not isinstance(pago, dict):
                raise VentaValidationError("Formato de pago inválido.")

            metodo_pago = VentaRepository.metodo_pago_valido(pago.get("metodo_pago_id"))
            if not metodo_pago:
                raise VentaValidationError("Uno de los métodos de pago seleccionados no es válido.")

            try:
                monto = Decimal(str(pago.get("monto")))
            except (InvalidOperation, TypeError, ValueError):
                raise VentaValidationError("Monto de pago inválido.")

            if monto <= 0:
                raise VentaValidationError("El monto de cada pago debe ser mayor a cero.")

            referencia = (pago.get("referencia") or "").strip()[:100]

            pagos_temp.append(DetallePago(
                metodo_pago=metodo_pago,
                monto=monto,
                referencia=referencia,
                fecha_creacion=timezone.now(),
            ))

        total_pagado = sum((pago.monto for pago in pagos_temp), Decimal("0.00"))
        if total_pagado < total_calculado:
            raise VentaValidationError(
                f"El monto pagado (₡{total_pagado}) es menor al total de la factura (₡{total_calculado})."
            )

        return pagos_temp

    # ---------------------------------------------------
    # Pausar / Cobrar
    # ---------------------------------------------------

    @staticmethod
    def pausar(venta, usuario, apertura, cliente, tipo_comprobante, lineas, totales, es_venta_nueva):
        """
        Guarda la venta como borrador pendiente. El inventario NO se toca
        aquí (igual que hacía guardar_venta_pendiente() antes de la
        migración a JSON/AJAX): el stock real se valida y se descuenta
        únicamente al cobrar de verdad, porque entre el momento de pausar
        y el de retomar/cobrar puede pasar cualquier cosa con las
        existencias (otra venta, un ajuste, una merma) — reservarlo en la
        pausa daría una falsa sensación de reserva de stock que el
        sistema no implementa.
        """
        metodo_pendiente = VentaRepository.metodo_pago_pendiente()

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
        venta.subtotal = totales["subtotal"]
        venta.impuesto = totales["impuesto"]
        venta.descuento = totales["descuento"]
        venta.total = totales["total"]

        if not venta.numero_venta:
            venta.numero_venta = generar_numero_venta()

        VentaRepository.guardar(venta)

        VentaRepository.eliminar_detalles(venta)
        VentaRepository.eliminar_pagos(venta)

        for linea in lineas:
            VentaRepository.crear_detalle(
                venta=venta,
                producto=linea["producto"],
                cantidad=linea["cantidad"],
                precio_unitario=linea["precio_unitario"],
                subtotal=linea["subtotal"],
            )

        return venta

    @staticmethod
    def cobrar(venta, usuario, apertura, cliente, tipo_comprobante, lineas, totales, pagos_temp, es_venta_nueva):
        """
        Registra la venta real: valida inventario (bloqueando cada fila
        para evitar condiciones de carrera con otra venta/compra
        simultánea), guarda la venta, registra el movimiento en caja,
        reemplaza detalle/pagos y descuenta stock vía
        MovimientoInventarioService (deja registro en
        movimiento_inventario en vez de mutar stock_actual a mano).

        Lanza VentaValidationError ante cualquier problema. Debe llamarse
        siempre dentro de un @transaction.atomic (lo aplica la vista) —
        si el descuento de inventario de una línea falla a mitad de
        camino, se marca la transacción para rollback antes de lanzar la
        excepción, exactamente igual que antes de esta extracción.
        """
        tipo_salida_venta = VentaRepository.tipo_movimiento_inventario("SALIDA_VENTA")
        if not tipo_salida_venta:
            raise VentaValidationError(
                "Falta configurar el tipo de movimiento 'SALIDA_VENTA' en Inventario. "
                "Ejecute: python manage.py seed_tipos_movimiento"
            )

        # Validación de inventario (bloqueando cada fila). Los registros
        # ya bloqueados se reutilizan más abajo: así se consulta
        # Inventario una sola vez por producto, no dos.
        inventarios_bloqueados = {}
        for linea in lineas:
            inventario = InventarioRepository.obtener_para_actualizar(
                linea["producto"], apertura.caja.sucursal
            )

            if not inventario:
                raise VentaValidationError(
                    f"El producto {linea['producto'].nombre} no está habilitado en el "
                    f"inventario de esta sucursal."
                )

            if inventario.stock_actual < linea["cantidad"]:
                raise VentaValidationError(
                    f"No hay existencias suficientes de {linea['producto'].nombre}. "
                    f"Stock actual: {inventario.stock_actual}"
                )

            inventarios_bloqueados[linea["producto"].pk] = inventario

        # Asignación de datos y guardado de la venta
        venta.usuario = usuario
        venta.caja = apertura.caja
        venta.cliente = cliente
        venta.tipo_comprobante = tipo_comprobante
        venta.fecha = timezone.now()
        if es_venta_nueva:
            venta.fecha_creacion = timezone.now()
        venta.fecha_actualizacion = timezone.now()
        venta.estado = True
        venta.subtotal = totales["subtotal"]
        venta.impuesto = totales["impuesto"]
        venta.descuento = totales["descuento"]
        venta.total = totales["total"]
        venta.metodo_pago = determinar_metodo_pago_venta(pagos_temp)

        if not venta.numero_venta:
            venta.numero_venta = generar_numero_venta()

        VentaRepository.guardar(venta)

        # Registro automático de movimiento en caja
        VentaRepository.crear_movimiento_caja(
            apertura=apertura,
            usuario=usuario,
            tipo_movimiento="VENTA",
            monto=venta.total,
            descripcion=f"Venta {venta.numero_venta}",
            fecha_movimiento=timezone.now(),
            fecha_creacion=timezone.now(),
        )

        # Si se está reanudando una venta pausada, sus líneas previas
        # (guardadas sin tocar inventario) se reemplazan por el detalle
        # definitivo que llegó en este JSON, para no duplicar filas ni
        # descontar dos veces.
        VentaRepository.eliminar_detalles(venta)
        VentaRepository.eliminar_pagos(venta)

        # Guardar detalles y descontar inventario
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
                # Fuerza el rollback del bloque @transaction.atomic (en la
                # vista) aunque la vista termine respondiendo con un
                # JsonResponse normal (no con una excepción HTTP).
                transaction.set_rollback(True)
                mensaje = (
                    "; ".join(error_inventario.messages)
                    if hasattr(error_inventario, "messages")
                    else str(error_inventario)
                )
                raise VentaValidationError(f"{linea['producto'].nombre}: {mensaje}")

        # Guardar detalle de pagos
        for pago in pagos_temp:
            pago.venta = venta
            pago.save()

        return venta

    # ---------------------------------------------------
    # Anular
    # ---------------------------------------------------

    @staticmethod
    def anular(venta, usuario, motivo_anulacion=""):
        """
        Anula una venta ya registrada: la marca como inactiva y reintegra
        al inventario cada producto vendido (vía
        MovimientoInventarioService, con tipo DEVOLUCION_VENTA). Lanza
        VentaValidationError si falta configurar ese tipo de movimiento.
        El motivo de anulación no tiene columna propia en la tabla venta;
        la vista lo persiste en la bitácora (LogAcciones vía
        registrar_log), que es la fuente de auditoría del sistema para
        este tipo de acción.
        """
        tipo_devolucion_venta = VentaRepository.tipo_movimiento_inventario("DEVOLUCION_VENTA")
        if not tipo_devolucion_venta:
            raise VentaValidationError(
                "Falta configurar el tipo de movimiento 'DEVOLUCION_VENTA' en "
                "Inventario. Ejecute: python manage.py seed_tipos_movimiento"
            )

        venta.estado = False
        venta.fecha_actualizacion = timezone.now()
        VentaRepository.guardar(venta)

        detalles = VentaRepository.detalles(venta)
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

        return venta


class ComprobanteEmailService:
    """
    Envío del comprobante de una venta por correo al cliente (RF-012).

    Sigue el mismo patrón ya usado en
    apps.security.services.RecuperacionPasswordService.enviar_correo
    (EmailMultiAlternatives + logo embebido vía Content-ID, en vez de un
    <img src="..."> normal que muchos clientes de correo bloquean por
    defecto), pero con una plantilla propia de Ventas
    ("emails/comprobante_venta_email.html") con la identidad visual de
    La Pana en vez de SIGEPAN/Y&C: este correo lo recibe directamente el
    cliente final de la panadería, no un usuario interno del sistema, así
    que debe verse como un comprobante de La Pana, no como una
    notificación del sistema.
    """

    RUTA_LOGO = (
        Path(settings.BASE_DIR) / "static" / "img" / "logos" / "lapana-logo.jpeg"
    )

    @classmethod
    def enviar(cls, venta, detalles, pagos, datos_empresa):
        """
        Envía el comprobante de `venta` al correo de `venta.cliente`.

        Lanza ValueError (con un mensaje ya listo para mostrar al
        usuario) si la venta no tiene un cliente con correo electrónico
        registrado — es una validación de negocio, no un fallo de envío.
        Cualquier error real de envío (servidor SMTP caído, credenciales
        inválidas, etc.) se deja subir tal cual: la vista que llama a
        este método es quien decide cómo mostrarlo sin romper la página.

        Devuelve el correo destinatario (para el mensaje de éxito).
        """

        if not venta.cliente or not venta.cliente.correo:
            raise ValueError(
                "Esta venta no tiene un cliente con correo electrónico "
                "registrado. Asocie un cliente con correo antes de "
                "reenviar el comprobante."
            )

        destinatario = venta.cliente.correo

        contexto = {
            "venta": venta,
            "detalles": detalles,
            "pagos": pagos,
            "datos_empresa": datos_empresa,
        }

        html = render_to_string(
            "emails/comprobante_venta_email.html",
            contexto,
        )

        correo = EmailMultiAlternatives(
            subject=f"Comprobante de compra {venta.numero_venta} - La Pana",
            body=(
                "Adjunto el comprobante de su compra en La Pana. "
                "Su cliente de correo no soporta contenido HTML."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )

        correo.attach_alternative(html, "text/html")

        with open(cls.RUTA_LOGO, "rb") as archivo:
            logo = MIMEImage(archivo.read())

        logo.add_header("Content-ID", "<lapana_logo>")
        logo.add_header(
            "Content-Disposition", "inline", filename="lapana-logo.jpeg"
        )

        correo.attach(logo)

        correo.send()

        return destinatario
