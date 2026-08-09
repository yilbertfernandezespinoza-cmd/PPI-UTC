# Servicios del módulo
#
# CompraValidationError + CompraService: capa de negocio del flujo de
# compras (registrar una compra a un proveedor y anularla), extraída de
# views.py::crear_compra/anular_compra para que compras quede con la
# misma arquitectura Model → Repository → Service → View que ya usan
# ventas/inventario. CompraService no depende de HttpRequest: lanza
# CompraValidationError ante cualquier problema de negocio (tipo de
# movimiento sin configurar, o cualquier error que levante
# MovimientoInventarioService al registrar un movimiento) y la vista
# decide cómo mostrarlo (messages.error). Las advertencias que no son
# errores duros -- como no encontrar inventario de una línea al anular --
# se devuelven como lista de texto para que la vista las traduzca a
# messages.warning, en vez de que el servicio dependa del objeto request.

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService

from .repositories import CompraRepository


class CompraValidationError(Exception):
    """
    Error de validación de negocio del flujo de compras: tipo de
    movimiento de inventario sin configurar, o cualquier problema que
    levante MovimientoInventarioService al registrar el movimiento (p.
    ej. stock resultante negativo). Las vistas de este módulo
    (crear_compra, anular_compra) capturan esta excepción y la traducen a
    messages.error.
    """
    pass


class CompraService:
    """
    Lógica de negocio del módulo Compras: registrar una compra nueva
    (incrementando el inventario vía MovimientoInventarioService) y
    anular una compra ya registrada (revirtiendo ese mismo movimiento).
    Las consultas a la base de datos viven en CompraRepository (y en
    InventarioRepository para el inventario, reutilizado tal cual desde
    VentaService); este servicio orquesta esas consultas y aplica las
    reglas de negocio.
    """

    # ---------------------------------------------------
    # Crear compra
    # ---------------------------------------------------

    @staticmethod
    @transaction.atomic
    def crear_compra(compra, detalles, usuario, sucursal):
        """
        Registra una compra nueva junto con sus líneas de detalle e
        incrementa el inventario de cada producto vía
        MovimientoInventarioService (tipo ENTRADA_COMPRA), dejando rastro
        en movimiento_inventario en vez de mutar stock_actual a mano.

        `compra` es una instancia de Compra sin guardar
        (compra_form.save(commit=False) en la vista) y `detalles` una
        lista de instancias de DetalleCompra sin guardar
        (detalle_formset.save(commit=False)), todavía sin id_compra ni
        subtotal asignados.

        Lanza CompraValidationError si falta configurar el tipo de
        movimiento 'ENTRADA_COMPRA', o si el registro del movimiento de
        alguna línea falla. Debe llamarse siempre dentro de una
        transacción atómica (la aplica este mismo método) — si una línea
        falla a mitad de camino, se marca la transacción para rollback
        antes de lanzar la excepción, exactamente igual que antes de esta
        extracción.
        """

        # Tipo de movimiento requerido para poder registrar la entrada de
        # inventario. Se valida antes de guardar nada de la compra para
        # no dejarla a medias si todavía no se sembró el catálogo.
        tipo_entrada_compra = CompraRepository.tipo_movimiento_inventario(
            "ENTRADA_COMPRA"
        )
        if not tipo_entrada_compra:
            raise CompraValidationError(
                "Falta configurar el tipo de movimiento 'ENTRADA_COMPRA' en "
                "Inventario. Ejecute: python manage.py seed_tipos_movimiento"
            )

        # DATOS AUTOMATICOS
        compra.usuario = usuario
        compra.sucursal = sucursal
        compra.fecha = timezone.now()
        compra.estado = True

        # Inicialmente en cero, luego se calcula a partir de los detalles
        compra.total = 0
        CompraRepository.guardar(compra)

        total_compra = 0

        for detalle in detalles:

            detalle.compra = compra

            detalle.subtotal = (
                detalle.cantidad * detalle.precio_unitario
            )

            total_compra += detalle.subtotal

            CompraRepository.guardar_detalle(detalle)

            # ACTUALIZAR INVENTARIO (vía MovimientoInventarioService: crea
            # el registro de inventario si todavía no existe para ese
            # producto+sucursal -antes se omitía en silencio- y deja
            # rastro en movimiento_inventario en vez de mutar
            # stock_actual a mano)
            inventario = InventarioRepository.obtener_o_crear(
                detalle.producto, sucursal
            )

            try:
                MovimientoInventarioService.registrar_movimiento(
                    inventario=inventario,
                    tipo_movimiento=tipo_entrada_compra,
                    usuario=usuario,
                    cantidad=detalle.cantidad,
                    observaciones=f"Compra #{compra.id_compra}",
                )
            except ValidationError as error:
                transaction.set_rollback(True)
                mensaje = (
                    "; ".join(error.messages)
                    if hasattr(error, "messages")
                    else str(error)
                )
                raise CompraValidationError(f"{detalle.producto.nombre}: {mensaje}")

        # ACTUALIZAR TOTAL FINAL
        compra.total = total_compra
        CompraRepository.guardar(compra, update_fields=["total"])

        return compra

    # ---------------------------------------------------
    # Anular compra
    # ---------------------------------------------------

    @staticmethod
    @transaction.atomic
    def anular_compra(compra, usuario):
        """
        Anula una compra ya registrada: revierte cada línea al inventario
        vía MovimientoInventarioService (tipo DEVOLUCION_COMPRA) y marca
        la compra como inactiva.

        Devuelve una tupla (compra, advertencias): `advertencias` es una
        lista de textos para las líneas cuyo producto no tiene inventario
        en la sucursal actual (no se pudo revertir esa línea, pero no se
        considera un error duro que deba abortar la anulación completa)
        -- se devuelve como texto en vez de llamar a messages.warning
        directamente porque el servicio no depende de HttpRequest, igual
        que VentaService.

        Lanza CompraValidationError si falta configurar el tipo de
        movimiento 'DEVOLUCION_COMPRA', o si el registro del movimiento
        de alguna línea falla. Debe llamarse siempre dentro de una
        transacción atómica (la aplica este mismo método).
        """

        detalles = CompraRepository.detalles(compra)

        tipo_devolucion_compra = CompraRepository.tipo_movimiento_inventario(
            "DEVOLUCION_COMPRA"
        )
        if not tipo_devolucion_compra:
            raise CompraValidationError(
                "Falta configurar el tipo de movimiento 'DEVOLUCION_COMPRA' "
                "en Inventario. Ejecute: python manage.py seed_tipos_movimiento"
            )

        advertencias = []

        # DEVOLVER INVENTARIO (vía MovimientoInventarioService)
        for detalle in detalles:

            inventario = InventarioRepository.obtener_para_actualizar(
                detalle.producto, usuario.id_sucursal
            )

            if not inventario:
                advertencias.append(
                    f"No se encontró inventario de {detalle.producto.nombre} "
                    f"en la sucursal actual; no se pudo revertir el stock de "
                    f"esa línea."
                )
                continue

            try:
                MovimientoInventarioService.registrar_movimiento(
                    inventario=inventario,
                    tipo_movimiento=tipo_devolucion_compra,
                    usuario=usuario,
                    cantidad=detalle.cantidad,
                    observaciones=f"Anulación de compra #{compra.id_compra}",
                )
            except ValidationError as error:
                transaction.set_rollback(True)
                mensaje = (
                    "; ".join(error.messages)
                    if hasattr(error, "messages")
                    else str(error)
                )
                raise CompraValidationError(f"{detalle.producto.nombre}: {mensaje}")

        compra.estado = False
        CompraRepository.guardar(compra)

        return compra, advertencias
