from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.ajustes.models import Ajuste
from apps.ajustes.services import AjusteService
from apps.caja.models import AperturaCaja, Caja
from apps.caja.services import AperturaCajaService, CajaService
from apps.clientes.models import Cliente
from apps.compras.models import Compra, DetalleCompra
from apps.compras.services import CompraService, CompraValidationError
from apps.configuracion.models import MetodoPago, Sucursal
from apps.gastos_operativos.models import GastoOperativo
from apps.gastos_operativos.services import GastoOperativoService
from apps.mermas.models import Merma
from apps.mermas.services import MermaService
from apps.productos.models import Producto
from apps.proveedores.models import Proveedor
from apps.security.models import Usuario
from apps.ventas.models import DetallePago
from apps.ventas.services import VentaService, VentaValidationError
from apps.ventas.models import Venta


class Command(BaseCommand):
    """
    Siembra (idempotente) movimientos de demostración para probar el
    sistema de punta a punta: compras a proveedores, ventas a clientes
    (pasando por el POS real, VentaService.cobrar — no INSERTs directos),
    mermas, ajustes de inventario y gastos operativos.

    A diferencia de seed_productos_demo/seed_clientes_demo/
    seed_proveedores_demo (catálogo maestro, con get_or_create fila por
    fila), este comando genera datos TRANSACCIONALES: no existe una
    clave de negocio natural para hacer get_or_create de una venta o una
    compra. La idempotencia se resuelve por SECCIÓN, no con un candado
    único: cada método _crear_* revisa primero qué ya quedó marcado con
    "[DEMO]" (por proveedor en compras, por venta ya facturada, por
    producto+motivo en mermas/ajustes, por descripción en gastos) y solo
    crea lo que falte. Esto permite reintentar el comando después de
    corregir un error puntual (p. ej. una sucursal mal configurada) sin
    duplicar lo que sí se alcanzó a registrar en una corrida anterior.

    Auto-corrección (07-08, hallazgo de una corrida real): si el usuario
    'admin' ya existía de antes de que se sembrara 'Sucursal Principal'
    (o de una corrida parcial anterior), su columna id_sucursal puede
    haber quedado apuntando a otra sucursal o en NULL. Ventas y Compras
    no dependen de ese campo (reciben la sucursal explícita por
    parámetro), pero Mermas/Ajustes de salida/Gastos operativos sí la
    leen internamente vía `usuario.id_sucursal` — con un valor
    desincronizado, InventarioRepository.obtener_para_actualizar no
    encuentra el inventario y esos tres módulos fallan con "no está
    habilitado en el inventario de esta sucursal" aunque el inventario
    exista perfectamente en 'Sucursal Principal'. Este comando corrige
    ese campo al inicio si no coincide (es una actualización, no un
    borrado — respeta la Regla de Oro).

    Requisitos previos (falla con un mensaje claro si falta alguno):
        python manage.py seed_admin
        python manage.py seed_metodos_pago
        python manage.py seed_tipos_movimiento
        python manage.py seed_productos_demo
        python manage.py seed_clientes_demo
        python manage.py seed_proveedores_demo

    Todo el flujo pasa por las mismas capas de servicio que usa la
    aplicación real (CompraService, VentaService, MermaService,
    AjusteService, GastoOperativoService), así que cada movimiento deja
    el mismo rastro de auditoría (movimiento_inventario, movimiento_caja)
    que dejaría un usuario real usando el sistema — no se toca
    stock_actual ni ninguna otra columna a mano.

    Uso:
        python manage.py seed_movimientos_demo
    """

    help = (
        "Crea compras, ventas, mermas, ajustes y gastos operativos de "
        "demostración, reutilizando los services reales del sistema, si "
        "todavía no se sembraron antes."
    )

    MARCADOR = "[DEMO]"

    # proveedor.identificacion -> [(codigo_producto, cantidad), ...]
    COMPRAS = [
        ("3101112233", [("PAN-001", 50), ("PAN-002", 30), ("PAN-005", 40)]),
        ("3101556677", [("BEB-001", 40), ("BEB-002", 30)]),
        ("3101445566", [("GAL-001", 60), ("GAL-002", 60), ("GAL-003", 50)]),
        ("3101334455", [("REP-001", 40), ("REP-002", 35)]),
        ("3101223344", [("PAS-001", 15), ("PAS-002", 12), ("PAS-003", 10)]),
        # Distribuidora de Empaques CR (3101667788) queda sin compra
        # registrada a propósito: proveedor recién dado de alta, sin
        # movimientos todavía (caso real de QA: no todo proveedor tiene
        # historial).
    ]

    # (identificacion_cliente_o_None, [(codigo, cantidad), ...], forma_pago)
    # forma_pago: "EXACTO:<metodo>" paga el total exacto con un solo
    # método; "VUELTO:<metodo>" paga total + ₡1000 en efectivo (genera
    # vuelto); "DIVIDIDO:<metodo1>:<metodo2>" paga la mitad del total
    # (redondeada) con metodo1 y el resto exacto con metodo2. Los montos
    # siempre se calculan a partir de totales["total"] ya calculado por
    # VentaService — nunca se escribe un monto fijo a mano, para no
    # arriesgar un pago insuficiente por un cálculo manual erróneo (esa
    # validación normalmente la hace VentaService.validar_pagos, que este
    # seed no usa porque construye los pagos directamente).
    VENTAS = [
        (
            "205680123",
            [("PAN-001", 2), ("BEB-001", 1)],
            "EXACTO:Efectivo",
        ),
        (
            "109870456",
            [("PAS-001", 1), ("GAL-001", 3)],
            "EXACTO:Tarjeta",
        ),
        (
            "302450789",
            [("REP-001", 2), ("REP-002", 2), ("BEB-003", 1)],
            "EXACTO:SINPE Móvil",
        ),
        (
            "401230567",
            [("SNK-001", 1), ("BEB-004", 2)],
            "VUELTO:Efectivo",
        ),
        (
            "3101456789",  # Restaurante El Fogón (compra al por mayor)
            [("PAN-006", 3), ("PAN-002", 10)],
            "EXACTO:Transferencia",
        ),
        (
            "3101987654",  # Hotel Vista Verde (compra al por mayor)
            [("PAS-002", 4), ("PAS-003", 2), ("GAL-002", 10)],
            "DIVIDIDO:Tarjeta:Efectivo",
        ),
        (
            None,  # público general
            [("PAN-003", 1), ("BEB-002", 1)],
            "VUELTO:Efectivo",
        ),
        (
            None,  # público general
            [("SNK-002", 1), ("SNK-003", 1), ("GAL-003", 2)],
            "EXACTO:Efectivo",
        ),
    ]

    # (codigo_producto, cantidad, motivo)
    MERMAS = [
        ("PAS-003", 1, "Producto dañado durante el transporte"),
        ("REP-001", 2, "Producto vencido en vitrina"),
        ("BEB-004", 3, "Envases dañados, no aptos para la venta"),
    ]

    # (codigo_producto, cantidad, tipo, motivo)
    AJUSTES = [
        ("PAN-004", 10, Ajuste.Tipo.ENTRADA, "Conteo físico: stock adicional no registrado"),
        ("GAL-002", 5, Ajuste.Tipo.SALIDA, "Conteo físico: faltante detectado en bodega"),
        ("SNK-001", 5, Ajuste.Tipo.ENTRADA, "Corrección de conteo físico mensual"),
    ]

    # (descripcion, categoria, monto)
    GASTOS = [
        ("Alquiler de local - agosto 2026", "Alquiler", Decimal("450000.00")),
        ("Recibo de electricidad e internet", "Servicios públicos (agua, luz, internet)", Decimal("85000.00")),
        ("Detergente, jabón y desinfectante para el local", "Insumos de limpieza", Decimal("32000.00")),
    ]

    def handle(self, *args, **options):

        usuario = Usuario.objects.filter(username="admin").first()
        if not usuario:
            self.stdout.write(self.style.ERROR(
                "No existe el usuario 'admin'. Corra primero: "
                "python manage.py seed_admin"
            ))
            return

        sucursal = Sucursal.objects.filter(nombre="Sucursal Principal").first()
        if not sucursal:
            self.stdout.write(self.style.ERROR(
                "No existe 'Sucursal Principal'. Corra primero: "
                "python manage.py seed_admin"
            ))
            return

        if not MetodoPago.objects.exists():
            self.stdout.write(self.style.ERROR(
                "No hay métodos de pago configurados. Corra primero: "
                "python manage.py seed_metodos_pago"
            ))
            return

        if not Producto.objects.filter(codigo="PAN-001").exists():
            self.stdout.write(self.style.ERROR(
                "No existe el catálogo de productos de demostración. "
                "Corra primero: python manage.py seed_productos_demo"
            ))
            return

        if not Cliente.objects.filter(identificacion="205680123").exists():
            self.stdout.write(self.style.ERROR(
                "No existen los clientes de demostración. Corra primero: "
                "python manage.py seed_clientes_demo"
            ))
            return

        if not Proveedor.objects.filter(identificacion="3101112233").exists():
            self.stdout.write(self.style.ERROR(
                "No existen los proveedores de demostración. Corra "
                "primero: python manage.py seed_proveedores_demo"
            ))
            return

        usuario = self._sincronizar_sucursal_usuario(usuario, sucursal)

        apertura = self._asegurar_caja_abierta(sucursal, usuario)
        if apertura is None:
            return

        self._crear_compras(usuario, sucursal)
        self._crear_ventas(apertura, usuario)
        self._crear_mermas(usuario)
        self._crear_ajustes(usuario)
        self._crear_gastos(usuario)

        self.stdout.write(self.style.SUCCESS("\nListo."))

    # ---------------------------------------------------
    # Corrección de sucursal del usuario admin
    # ---------------------------------------------------

    def _sincronizar_sucursal_usuario(self, usuario, sucursal):
        """
        Corrige usuario.id_sucursal si no coincide con 'Sucursal
        Principal' (ver nota en el docstring de la clase). No borra ni
        reemplaza al usuario: solo actualiza esa columna, igual que
        haría un administrador corrigiendo el perfil de un usuario desde
        Configuración.
        """
        if usuario.id_sucursal_id == sucursal.pk:
            return usuario

        anterior = usuario.id_sucursal_id
        usuario.id_sucursal = sucursal
        usuario.save(update_fields=["id_sucursal"])
        self.stdout.write(self.style.WARNING(
            f"  ! usuario '{usuario.username}' tenía id_sucursal={anterior}, "
            f"no coincidía con 'Sucursal Principal' (id={sucursal.pk}). "
            "Corregido — necesario para que Mermas/Ajustes/Gastos "
            "encuentren el inventario correcto."
        ))
        return usuario

    # ---------------------------------------------------
    # Caja
    # ---------------------------------------------------

    def _asegurar_caja_abierta(self, sucursal, usuario):
        # OJO: no se usa Caja.objects.get_or_create() aquí. saldo_inicial/
        # saldo_actual no tienen default a nivel de modelo (solo a nivel
        # de columna en MySQL) — CajaService.crear() es quien los
        # inicializa en 0 ANTES del primer guardado, igual que hace
        # CajaForm.save(commit=False) + CajaService.crear() en la vista
        # real. Si se guardara la caja antes de pasar por el service (lo
        # que get_or_create hace internamente), Django intentaría
        # insertar NULL en esas dos columnas NOT NULL.
        caja = Caja.objects.filter(nombre="Caja Principal").first()
        if caja:
            self.stdout.write("  = Caja 'Caja Principal' ya existía.")
        else:
            # Auto-corrección (07-08): una corrida anterior de este mismo
            # comando construyó el Caja() sin pasarle `nombre` (bug ya
            # corregido abajo), así que quedó guardada con nombre="" en
            # vez de "Caja Principal". Si esa fila existe, se corrige en
            # vez de crear una caja nueva (evita el IntegrityError de
            # `uk_caja_nombre` y, sobre todo, respeta la Regla de Oro: no
            # se borra el registro, se corrige).
            caja_con_nombre_vacio = Caja.objects.filter(
                sucursal=sucursal,
                descripcion="Caja principal de mostrador",
                nombre="",
            ).first()
            if caja_con_nombre_vacio:
                caja_con_nombre_vacio.nombre = "Caja Principal"
                caja_con_nombre_vacio.save(update_fields=["nombre"])
                caja = caja_con_nombre_vacio
                self.stdout.write(self.style.WARNING(
                    "  ! se encontró una caja de una corrida anterior "
                    "guardada con nombre vacío (bug ya corregido); se "
                    "renombró a 'Caja Principal' en vez de duplicarla."
                ))
            else:
                caja = CajaService.crear(Caja(
                    nombre="Caja Principal",
                    sucursal=sucursal,
                    descripcion="Caja principal de mostrador",
                    fecha_creacion=timezone.now(),
                    fecha_actualizacion=timezone.now(),
                ))
                self.stdout.write("  + Caja 'Caja Principal' creada.")

        apertura = AperturaCaja.objects.filter(caja=caja, estado=True).first()
        if apertura:
            self.stdout.write("  = Ya había una apertura de caja activa.")
            return apertura

        try:
            apertura = AperturaCajaService.abrir(
                caja,
                AperturaCaja(
                    monto_inicial=Decimal("50000.00"),
                    turno="MANANA",
                    observaciones=f"{self.MARCADOR} Apertura para datos de prueba",
                ),
                usuario,
            )
        except Exception as error:
            self.stdout.write(self.style.ERROR(
                f"No se pudo abrir 'Caja Principal': {error}"
            ))
            return None

        self.stdout.write("  + Apertura de caja creada (turno mañana).")
        return apertura

    # ---------------------------------------------------
    # Compras
    # ---------------------------------------------------

    def _crear_compras(self, usuario, sucursal):
        creadas = 0
        omitidas = 0
        for identificacion_proveedor, lineas in self.COMPRAS:
            proveedor = Proveedor.objects.filter(
                identificacion=identificacion_proveedor
            ).first()
            if not proveedor:
                self.stdout.write(self.style.WARNING(
                    f"  ! proveedor {identificacion_proveedor} no existe, se omite la compra."
                ))
                continue

            if Compra.objects.filter(
                proveedor=proveedor,
                observaciones__startswith=self.MARCADOR,
            ).exists():
                omitidas += 1
                self.stdout.write(f"  = ya existía una compra demo a {proveedor.nombre}.")
                continue

            compra = Compra(
                proveedor=proveedor,
                observaciones=f"{self.MARCADOR} Reabastecimiento — {proveedor.nombre}",
            )

            detalles = []
            for codigo, cantidad in lineas:
                producto = Producto.objects.filter(codigo=codigo).first()
                if not producto:
                    self.stdout.write(self.style.WARNING(
                        f"  ! producto {codigo} no existe, se omite esa línea."
                    ))
                    continue
                detalles.append(DetalleCompra(
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_compra,
                ))

            if not detalles:
                continue

            try:
                CompraService.crear_compra(compra, detalles, usuario, sucursal)
            except CompraValidationError as error:
                self.stdout.write(self.style.ERROR(
                    f"  ! no se pudo registrar la compra a {proveedor.nombre}: {error}"
                ))
                continue

            creadas += 1
            self.stdout.write(
                f"  + compra #{compra.id_compra} a {proveedor.nombre} "
                f"(₡{compra.total})"
            )

        self.stdout.write(f"{creadas} compra(s) registradas, {omitidas} ya existían.")

    # ---------------------------------------------------
    # Ventas
    # ---------------------------------------------------

    def _crear_ventas(self, apertura, usuario):
        # Venta no tiene columna de observaciones propia (a diferencia de
        # Compra). En vez de depender de una marca en DetallePago.referencia
        # (poco confiable: una corrida anterior a este cambio pudo haber
        # creado las ventas SIN esa marca, y entonces este chequeo no las
        # vería), se usa un criterio que no depende de ningún dato nuevo:
        # 'Caja Principal' es una caja que solo crea este comando, así que
        # cualquier Venta ya asociada a esa caja/apertura es, por
        # definición, una venta de esta siembra. Si ya hay al menos tantas
        # como las que este comando intenta crear, se asume que la sección
        # ya corrió completa y no se reintenta (todo o nada, igual que
        # antes, pero sin depender de la marca).
        ventas_existentes = Venta.objects.filter(caja=apertura.caja).count()
        if ventas_existentes >= len(self.VENTAS):
            self.stdout.write(
                f"  = ya había {ventas_existentes} venta(s) registradas en "
                "'Caja Principal', se omite esta sección."
            )
            return

        creadas = 0
        for identificacion_cliente, lineas_codigos, forma_pago in self.VENTAS:

            cliente = None
            if identificacion_cliente:
                cliente = Cliente.objects.filter(
                    identificacion=identificacion_cliente
                ).first()
                if not cliente:
                    self.stdout.write(self.style.WARNING(
                        f"  ! cliente {identificacion_cliente} no existe, "
                        "se registra como público general."
                    ))

            lineas = []
            for codigo, cantidad in lineas_codigos:
                producto = Producto.objects.filter(codigo=codigo).first()
                if not producto:
                    self.stdout.write(self.style.WARNING(
                        f"  ! producto {codigo} no existe, se omite esa línea."
                    ))
                    continue
                precio_unitario = producto.precio_venta or Decimal("0.00")
                lineas.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": (precio_unitario * cantidad).quantize(Decimal("0.01")),
                })

            if not lineas:
                continue

            totales = VentaService.calcular_totales(lineas)

            pagos_temp = self._armar_pagos(forma_pago, totales["total"])
            if pagos_temp is None:
                self.stdout.write(self.style.WARNING(
                    f"  ! método de pago no configurado para '{forma_pago}', se omite esa venta."
                ))
                continue

            # Marca de idempotencia de la sección (ver comentario al
            # inicio de _crear_ventas): va en el primer pago de cada
            # venta, sin afectar el monto ni el método real.
            pagos_temp[0].referencia = self.MARCADOR

            venta = Venta()
            try:
                # VentaService.cobrar no trae su propio @transaction.atomic
                # (lo aplica quien la llama, normalmente la vista
                # procesar_venta) — se replica aquí para no dejar detalle
                # de venta o movimiento de inventario a medias si una
                # línea falla.
                with transaction.atomic():
                    VentaService.cobrar(
                        venta=venta,
                        usuario=usuario,
                        apertura=apertura,
                        cliente=cliente,
                        tipo_comprobante="TICKET",
                        lineas=lineas,
                        totales=totales,
                        pagos_temp=pagos_temp,
                        es_venta_nueva=True,
                    )
            except VentaValidationError as error:
                self.stdout.write(self.style.ERROR(
                    f"  ! no se pudo registrar la venta: {error}"
                ))
                continue

            creadas += 1
            nombre_cliente = cliente.nombre_completo if cliente else "Público general"
            self.stdout.write(
                f"  + venta {venta.numero_venta} — {nombre_cliente} (₡{venta.total})"
            )

        self.stdout.write(f"{creadas} venta(s) registradas.")

    def _armar_pagos(self, forma_pago, total):
        """
        Traduce la forma de pago declarativa (ver VENTAS) en una lista de
        DetallePago sin guardar, calculando siempre los montos a partir
        de `total` (nunca un número fijo escrito a mano). Devuelve None
        si algún método de pago referenciado no existe en el catálogo.
        """
        partes = forma_pago.split(":")
        modo = partes[0]

        def obtener_metodo(nombre):
            return MetodoPago.objects.filter(nombre=nombre).first()

        if modo == "EXACTO":
            metodo = obtener_metodo(partes[1])
            if not metodo:
                return None
            return [DetallePago(
                metodo_pago=metodo,
                monto=total,
                referencia="",
                fecha_creacion=timezone.now(),
            )]

        if modo == "VUELTO":
            metodo = obtener_metodo(partes[1])
            if not metodo:
                return None
            return [DetallePago(
                metodo_pago=metodo,
                # Paga de más a propósito (redondeando hacia arriba a la
                # centena) para que quede un vuelto real que probar en el
                # detalle de venta / comprobante.
                monto=(total + Decimal("1000.00")),
                referencia="",
                fecha_creacion=timezone.now(),
            )]

        if modo == "DIVIDIDO":
            metodo1 = obtener_metodo(partes[1])
            metodo2 = obtener_metodo(partes[2])
            if not metodo1 or not metodo2:
                return None
            # La primera mitad se redondea a 2 decimales; la segunda
            # cubre exactamente lo que falta, para que la suma sea
            # idéntica al total sin importar el redondeo.
            primera_mitad = (total / 2).quantize(Decimal("0.01"))
            segunda_mitad = total - primera_mitad
            return [
                DetallePago(
                    metodo_pago=metodo1,
                    monto=primera_mitad,
                    referencia="",
                    fecha_creacion=timezone.now(),
                ),
                DetallePago(
                    metodo_pago=metodo2,
                    monto=segunda_mitad,
                    referencia="",
                    fecha_creacion=timezone.now(),
                ),
            ]

        return None

    # ---------------------------------------------------
    # Mermas
    # ---------------------------------------------------

    def _crear_mermas(self, usuario):
        creadas = 0
        omitidas = 0
        for codigo, cantidad, motivo in self.MERMAS:
            producto = Producto.objects.filter(codigo=codigo).first()
            if not producto:
                continue

            motivo_marcado = f"{self.MARCADOR} {motivo}"
            if Merma.objects.filter(producto=producto, motivo=motivo_marcado).exists():
                omitidas += 1
                self.stdout.write(f"  = ya existía la merma de {producto.nombre}.")
                continue

            try:
                MermaService.registrar(
                    producto=producto,
                    usuario=usuario,
                    cantidad=cantidad,
                    motivo=motivo_marcado,
                    fecha=timezone.now(),
                )
            except Exception as error:
                self.stdout.write(self.style.ERROR(
                    f"  ! no se pudo registrar la merma de {producto.nombre}: {error}"
                ))
                continue
            creadas += 1
            self.stdout.write(f"  + merma: {cantidad} x {producto.nombre}")

        self.stdout.write(f"{creadas} merma(s) registradas, {omitidas} ya existían.")

    # ---------------------------------------------------
    # Ajustes
    # ---------------------------------------------------

    def _crear_ajustes(self, usuario):
        creadas = 0
        omitidas = 0
        for codigo, cantidad, tipo, motivo in self.AJUSTES:
            producto = Producto.objects.filter(codigo=codigo).first()
            if not producto:
                continue

            motivo_marcado = f"{self.MARCADOR} {motivo}"
            if Ajuste.objects.filter(
                producto=producto, tipo=tipo, motivo=motivo_marcado
            ).exists():
                omitidas += 1
                self.stdout.write(f"  = ya existía el ajuste de {producto.nombre}.")
                continue

            try:
                AjusteService.registrar(
                    producto=producto,
                    usuario=usuario,
                    cantidad=cantidad,
                    tipo=tipo,
                    motivo=motivo_marcado,
                    fecha=timezone.now(),
                )
            except Exception as error:
                self.stdout.write(self.style.ERROR(
                    f"  ! no se pudo registrar el ajuste de {producto.nombre}: {error}"
                ))
                continue
            creadas += 1
            self.stdout.write(f"  + ajuste {tipo}: {cantidad} x {producto.nombre}")

        self.stdout.write(f"{creadas} ajuste(s) registrados, {omitidas} ya existían.")

    # ---------------------------------------------------
    # Gastos operativos
    # ---------------------------------------------------

    def _crear_gastos(self, usuario):
        creadas = 0
        omitidas = 0
        for descripcion, categoria, monto in self.GASTOS:

            descripcion_marcada = f"{self.MARCADOR} {descripcion}"
            if GastoOperativo.objects.filter(descripcion=descripcion_marcada).exists():
                omitidas += 1
                self.stdout.write(f"  = ya existía el gasto '{descripcion}'.")
                continue

            try:
                GastoOperativoService.registrar(
                    usuario=usuario,
                    descripcion=descripcion_marcada,
                    categoria=categoria,
                    monto=monto,
                    fecha_gasto=timezone.now(),
                )
            except Exception as error:
                self.stdout.write(self.style.ERROR(
                    f"  ! no se pudo registrar el gasto '{descripcion}': {error}"
                ))
                continue
            creadas += 1
            self.stdout.write(f"  + gasto: {descripcion} (₡{monto})")

        self.stdout.write(f"{creadas} gasto(s) operativo(s) registrados, {omitidas} ya existían.")
