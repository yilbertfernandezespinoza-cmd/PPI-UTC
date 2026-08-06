# Repositorios del módulo

from decimal import Decimal

from django.db.models import Q, Sum

from apps.caja.models import AperturaCaja, MovimientoCaja
from apps.categorias.models import Categoria
from apps.clientes.models import Cliente
from apps.configuracion.models import ConfiguracionTributaria, DatosEmpresa, MetodoPago
from apps.inventario.models import TipoMovimientoInventario
from apps.productos.models import Producto

from .models import DetallePago, DetalleVenta, Venta


class VentaRepository:
    """
    Repositorio para el acceso a datos del módulo Ventas (POS).

    Además de las tablas propias (venta, detalle_venta, detalle_pago),
    expone algunas consultas de solo lectura sobre modelos de otras apps
    (AperturaCaja, MetodoPago, Categoria, ConfiguracionTributaria,
    TipoMovimientoInventario, DatosEmpresa, Producto, Cliente) que el
    flujo del POS necesita constantemente. Se centralizan aquí — en vez
    de repetirlas sueltas en views.py — porque son consultas específicas
    del caso de uso "Ventas", no operaciones genéricas de esas apps (que
    ya tienen su propio Repository cuando corresponde, p. ej.
    InventarioRepository para el bloqueo de stock, reutilizado tal cual
    desde VentaService).
    """

    # ---------------------------------------------------
    # Venta
    # ---------------------------------------------------

    @staticmethod
    def con_relaciones_basicas():
        """Queryset base de ventas con el cliente precargado (listados)."""
        return Venta.objects.select_related("cliente")

    @staticmethod
    def con_relaciones_completas():
        """Queryset de ventas con todas las relaciones que necesita un
        comprobante/detalle: cliente, usuario, caja, sucursal y método de
        pago."""
        return Venta.objects.select_related(
            "cliente", "usuario", "caja", "caja__sucursal", "metodo_pago"
        )

    @staticmethod
    def listar_por_rango(inicio, fin):
        """Ventas cuya fecha cae en [inicio, fin), ordenadas de más
        reciente a más antigua. Usado por el reporte diario de ventas."""
        return (
            VentaRepository.con_relaciones_basicas()
            .filter(fecha__gte=inicio, fecha__lt=fin)
            .order_by("-fecha")
        )

    @staticmethod
    def total_recaudado(queryset):
        """Suma de `total` de un queryset de ventas ya filtrado (p. ej.
        solo las activas del día)."""
        return queryset.aggregate(total=Sum("total"))["total"] or Decimal("0.00")

    @staticmethod
    def obtener_activa_sesion(id_venta):
        """Venta en curso (activa en el POS o retomada de pendientes),
        identificada por el id guardado en la sesión. Devuelve None si no
        se envía id o no existe."""
        if not id_venta:
            return None
        return Venta.objects.filter(id_venta=id_venta).first()

    @staticmethod
    def listar_pendientes(ids_pendientes):
        """Ventas pausadas cuyo id está en la lista guardada en sesión."""
        return Venta.objects.filter(
            id_venta__in=ids_pendientes
        ).select_related("cliente", "usuario", "metodo_pago")

    @staticmethod
    def guardar(venta):
        """Persiste (crea o actualiza) una venta."""
        venta.save()
        return venta

    @staticmethod
    def eliminar(venta):
        """Elimina una venta (usado solo al descartar un borrador
        pausado — una venta ya cobrada nunca se borra, se anula)."""
        venta.delete()

    # ---------------------------------------------------
    # DetalleVenta
    # ---------------------------------------------------

    @staticmethod
    def detalles(venta):
        return DetalleVenta.objects.filter(venta=venta)

    @staticmethod
    def detalles_con_producto(venta):
        return DetalleVenta.objects.filter(venta=venta).select_related("producto")

    @staticmethod
    def eliminar_detalles(venta):
        DetalleVenta.objects.filter(venta=venta).delete()

    @staticmethod
    def crear_detalle(**datos):
        return DetalleVenta.objects.create(**datos)

    # ---------------------------------------------------
    # DetallePago
    # ---------------------------------------------------

    @staticmethod
    def pagos(venta):
        return DetallePago.objects.filter(venta=venta)

    @staticmethod
    def pagos_con_metodo(venta):
        return DetallePago.objects.filter(venta=venta).select_related("metodo_pago")

    @staticmethod
    def eliminar_pagos(venta):
        DetallePago.objects.filter(venta=venta).delete()

    # ---------------------------------------------------
    # Clientes (búsqueda del POS)
    # ---------------------------------------------------

    @staticmethod
    def cliente_por_id(pk):
        """Cliente por id, sin filtrar por estado — igual que el
        comportamiento original de procesar_venta (un cliente ya
        seleccionado en el carrito puede completarse aunque se haya
        desactivado mientras tanto)."""
        return Cliente.objects.filter(pk=pk).first()

    @staticmethod
    def cliente_activo_por_identificacion_exacta(query):
        return Cliente.objects.filter(estado=True, identificacion__iexact=query).first()

    @staticmethod
    def buscar_clientes_activos(query):
        """
        Búsqueda combinada por cédula (prioridad) y nombre/apellidos,
        limitada a 10 resultados. Se concatenan dos querysets simples
        (más legibles que un annotate con orden calculado) para que las
        coincidencias de cédula aparezcan primero, ya que es el
        identificador único y confiable; las coincidencias de
        nombre/apellido van después porque un mismo nombre puede
        pertenecer a muchas personas distintas.
        """
        por_identificacion = Cliente.objects.filter(
            estado=True,
            identificacion__icontains=query,
        ).order_by("identificacion")

        por_nombre = Cliente.objects.filter(
            Q(nombre__icontains=query)
            | Q(apellido1__icontains=query)
            | Q(apellido2__icontains=query),
            estado=True,
        ).exclude(
            pk__in=por_identificacion.values("pk")
        ).order_by("nombre")

        return (list(por_identificacion) + list(por_nombre))[:10]

    # ---------------------------------------------------
    # Catálogos y consultas auxiliares del POS (otras apps)
    # ---------------------------------------------------

    @staticmethod
    def apertura_activa(usuario):
        """Caja abierta del usuario actual (AperturaCaja), con la caja y
        su sucursal precargadas."""
        return AperturaCaja.objects.filter(
            usuario=usuario, estado=True
        ).select_related("caja", "caja__sucursal").first()

    @staticmethod
    def metodos_pago_pos():
        """Catálogo de métodos de pago activos para los checkboxes del
        POS, excluyendo el método interno 'Pendiente'."""
        return MetodoPago.objects.filter(estado=True).exclude(
            nombre__iexact="Pendiente"
        ).order_by("nombre")

    @staticmethod
    def metodo_pago_pendiente():
        """Método de pago interno 'Pendiente', usado solo para marcar una
        venta pausada. Se crea si todavía no existe."""
        metodo, _creado = MetodoPago.objects.get_or_create(
            nombre__iexact="Pendiente",
            defaults={"nombre": "Pendiente"},
        )
        return metodo

    @staticmethod
    def metodo_pago_valido(pk):
        return MetodoPago.objects.filter(pk=pk, estado=True).first()

    @staticmethod
    def tasa_iva_activa():
        """Suma de las tasas de ConfiguracionTributaria activas que
        aplican a ventas."""
        return ConfiguracionTributaria.objects.filter(
            estado=True,
            aplica_ventas=True,
        ).aggregate(total=Sum("porcentaje"))["total"] or Decimal("0.00")

    @staticmethod
    def categorias_activas():
        return Categoria.objects.filter(estado=True).order_by("nombre")

    @staticmethod
    def datos_empresa():
        datos, _creado = DatosEmpresa.objects.get_or_create(
            id_datos_empresa=1,
            defaults={"nombre_comercial": "", "cedula_juridica": ""},
        )
        return datos

    @staticmethod
    def tipo_movimiento_inventario(nombre):
        return TipoMovimientoInventario.objects.filter(nombre=nombre).first()

    @staticmethod
    def crear_movimiento_caja(**datos):
        return MovimientoCaja.objects.create(**datos)

    @staticmethod
    def producto_activo(pk):
        return Producto.objects.filter(pk=pk, estado=True).first()
