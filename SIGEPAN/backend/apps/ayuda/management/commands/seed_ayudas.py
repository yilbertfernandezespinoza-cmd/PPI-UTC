from django.core.management.base import BaseCommand

from apps.ayuda.models import Ayuda
from apps.configuracion.models import Modulo


class Command(BaseCommand):
    """
    Siembra (idempotente) el contenido de ayuda contextual (RF-032) para
    todas las pantallas del sistema que todavía no tienen una tarjeta de
    "?" con contenido en su template.

    Es seguro ejecutarlo varias veces: usa get_or_create sobre
    (modulo, pantalla) — la misma restricción única de la tabla real — así
    que NUNCA sobreescribe una ayuda que ya exista (por ejemplo, si el
    usuario editó a mano el contenido de "Productos", "Ventas", "Caja" o
    "Dashboard" desde la UI de administración de Ayudas, este comando no
    la toca).

    Uso:
        python manage.py seed_ayudas
    """

    help = (
        "Crea el contenido de ayuda contextual para las pantallas del "
        "sistema que todavía no tienen una (no sobreescribe las que ya "
        "existen)."
    )

    # (modulo, pantalla, titulo, icono, contenido)
    # "modulo" debe coincidir EXACTO con el nombre real en la tabla
    # `modulo` (mismo valor usado como modulo_permiso / nombre de grupo en
    # apps/security/menu.py). "pantalla" debe coincidir con el segundo
    # argumento del `{% boton_ayuda "Modulo" "pantalla" %}` puesto en cada
    # template.
    AYUDAS = [
        (
            "Configuración", "datos_empresa", "Datos de la Empresa",
            "bi-building-gear",
            "Aquí se configura la información fiscal del negocio "
            "(nombre comercial, cédula jurídica, régimen tributario, "
            "dirección, teléfono y correo) que se usa en comprobantes y "
            "reportes. Es un registro único: no se crean varios, solo se "
            "edita el existente.",
        ),
        (
            "Configuración", "sucursales", "Sucursales",
            "bi-building",
            "Administra las sucursales del negocio. Cada usuario, caja e "
            "inventario está vinculado a una sucursal específica, así que "
            "las ventas, compras y el stock siempre se controlan por "
            "sucursal por separado.",
        ),
        (
            "Configuración", "tributaria", "Configuración Tributaria",
            "bi-percent",
            "Define las tasas de impuesto (IVA) que aplican a ventas y/o "
            "compras. Si hay varias tasas activas marcadas para ventas, "
            "el sistema las suma automáticamente al calcular el impuesto "
            "de cada venta. Desactivar una tasa aquí deja de aplicarla "
            "desde ese momento, sin afectar ventas ya registradas.",
        ),
        (
            "Configuración", "metodos_pago", "Métodos de Pago",
            "bi-credit-card",
            "Catálogo de métodos de pago (efectivo, tarjeta, SINPE, etc.) "
            "que aparecen como opciones de cobro en el Punto de Venta. Un "
            "método inactivo deja de mostrarse en el POS, pero las ventas "
            "ya cobradas con ese método no se ven afectadas.",
        ),
        (
            "Configuración", "cargos", "Cargos",
            "bi-briefcase",
            "Catálogo de puestos de trabajo (cajero, panadero, "
            "administrador, etc.) que se asignan a cada empleado. Se usa "
            "solo como referencia informativa del empleado, no controla "
            "permisos — eso se hace en Seguridad → Usuarios y Asignación "
            "de Permisos.",
        ),
        (
            "Configuración", "empleados", "Empleados",
            "bi-person-badge",
            "Registro del personal del negocio (nombre, identificación, "
            "cargo, contacto). Un empleado es distinto de un usuario: el "
            "empleado es la persona real, mientras que el usuario es la "
            "cuenta con la que esa persona inicia sesión en el sistema "
            "(se crea en Seguridad → Usuarios).",
        ),
        (
            "Configuración", "ayudas", "Administración de Ayudas",
            "bi-question-circle",
            "Desde aquí se administra el contenido de ayuda contextual "
            "(el botón \"?\" que aparece en cada pantalla del sistema). "
            "Cada ayuda pertenece a un módulo y una pantalla específicos "
            "— solo puede existir una ayuda por esa combinación. Puedes "
            "editar el título, el texto y opcionalmente subir una imagen "
            "de apoyo.",
        ),
        (
            "Categorías", "categorias", "Categorías de Productos",
            "bi-tags",
            "Administra las categorías que agrupan los productos (por "
            "ejemplo: Panadería, Repostería, Bebidas). Se usan para "
            "organizar el catálogo y para las pestañas de la cuadrícula "
            "de productos del Punto de Venta.",
        ),
        (
            "Clientes", "clientes", "Clientes",
            "bi-people",
            "Registro de clientes del negocio. Al cobrar una venta en el "
            "POS puedes asociarla a un cliente registrado aquí, o dejarla "
            "como \"Público General\" si el cliente no está registrado.",
        ),
        (
            "Proveedores", "proveedores", "Proveedores",
            "bi-truck",
            "Registro de proveedores del negocio. Se usan al registrar una "
            "compra, para saber a quién se le compró la mercadería.",
        ),
        (
            "Inventario", "inventario", "Inventario",
            "bi-box-seam",
            "Muestra las existencias actuales (stock) de cada producto por "
            "sucursal. El stock se actualiza automáticamente con cada "
            "venta, compra, merma o ajuste — normalmente no se edita "
            "directamente aquí.",
        ),
        (
            "Inventario", "entrada_inventario", "Entrada de Inventario",
            "bi-box-arrow-in-down",
            "Permite registrar una entrada manual de stock que no viene de "
            "una compra formal (por ejemplo, la carga inicial de "
            "existencias al arrancar el sistema). Queda registrada en los "
            "Movimientos de Inventario igual que cualquier otro cambio de "
            "stock.",
        ),
        (
            "Inventario", "movimientos_inventario", "Movimientos de Inventario",
            "bi-arrow-left-right",
            "Bitácora completa de todos los cambios de stock del sistema: "
            "ventas, compras, devoluciones, mermas, ajustes y entradas "
            "manuales. Es el registro de auditoría del inventario — no se "
            "puede editar ni borrar, solo consultar.",
        ),
        (
            "Compras", "compras", "Compras",
            "bi-cart-plus",
            "Registra las compras a proveedores. Al guardar una compra, el "
            "inventario de cada producto se incrementa automáticamente en "
            "la sucursal del usuario que la registra. Anular una compra "
            "revierte ese incremento de stock.",
        ),
        (
            "Ventas", "nueva_venta", "Punto de Venta (POS)",
            "bi-cash-stack",
            "Pantalla de cobro para el cajero. Requiere tener una caja "
            "abierta. Busca o toca los productos para agregarlos al "
            "carrito, elige un cliente (opcional) y el método de pago, y "
            "presiona \"Cobrar\" para completar la venta. \"Pausar\" guarda "
            "la venta como pendiente sin descontar inventario, para "
            "retomarla después desde Ventas Pendientes.",
        ),
        (
            "Mermas", "mermas", "Mermas",
            "bi-exclamation-triangle",
            "Registra pérdidas de inventario por productos vencidos, "
            "dañados o extraviados. Cada merma reduce el stock del "
            "producto en la sucursal del usuario. Es un registro "
            "histórico: no se puede editar ni eliminar una vez creado.",
        ),
        (
            "Ajustes", "ajustes_inventario", "Ajustes de Inventario",
            "bi-sliders",
            "Permite corregir manualmente el stock de un producto cuando "
            "no coincide con un conteo físico. Una entrada incrementa el "
            "stock (puede ser de cualquier producto activo); una salida lo "
            "reduce (solo de productos que ya tienen inventario registrado "
            "en la sucursal). La lista de productos disponibles cambia "
            "según el tipo que elijas.",
        ),
        (
            "Gastos Operativos", "gastos_operativos", "Gastos Operativos",
            "bi-cash-coin",
            "Registra gastos del negocio que no son compras de mercadería "
            "(alquiler, servicios, mantenimiento, etc.). Requiere tener "
            "una caja abierta, ya que el gasto se descuenta del saldo de "
            "esa caja.",
        ),
        (
            "Reportes", "reporte_ventas", "Reporte de Ventas",
            "bi-cash-stack",
            "Reporte de ventas filtrable por fecha y sucursal, exportable "
            "a PDF, Excel o Google Sheets. Útil para revisar el "
            "desempeño de ventas de un período específico.",
        ),
        (
            "Reportes", "reporte_inventario", "Reporte de Inventario",
            "bi-box-seam",
            "Reporte del estado del inventario, filtrable por sucursal y "
            "por productos bajo el mínimo de stock. Exportable a PDF, "
            "Excel o Google Sheets.",
        ),
        (
            "Reportes", "reporte_tributario", "Reporte Tributario",
            "bi-receipt-cutoff",
            "Resumen mensual de ventas agrupado por método de pago, "
            "pensado como apoyo para la declaración de impuestos. La "
            "agrupación se ajusta automáticamente a los métodos de pago "
            "configurados en el sistema.",
        ),
        (
            "Reportes", "reporte_utilidad", "Reporte de Utilidad",
            "bi-graph-up-arrow",
            "Estima la utilidad del período a partir de la diferencia "
            "entre el precio de venta y el precio de compra de cada línea "
            "vendida. Es un estimado basado en los precios registrados en "
            "el sistema, no un cálculo contable formal.",
        ),
        (
            "Seguridad", "usuarios", "Usuarios",
            "bi-people",
            "Administra las cuentas con las que el personal inicia sesión "
            "en el sistema (usuario, contraseña, rol y sucursal "
            "asignada). Un usuario es distinto de un empleado: aquí se "
            "controla el acceso al sistema, no los datos personales del "
            "trabajador (eso está en Configuración → Empleados).",
        ),
        (
            "Seguridad", "asignacion_permisos", "Asignación de Permisos",
            "bi-person-check",
            "Define qué puede hacer cada rol en cada módulo del sistema "
            "(Consultar, Crear, Modificar, Eliminar). Los cambios aplican "
            "de inmediato a todos los usuarios que tengan ese rol — si "
            "quitas un permiso, los usuarios de ese rol pierden acceso a "
            "esa acción en su próxima solicitud, sin necesidad de cerrar "
            "sesión.",
        ),
        (
            "Seguridad", "bitacora_ingresos", "Bitácora de Ingresos",
            "bi-box-arrow-in-right",
            "Historial de inicios de sesión al sistema, filtrable por "
            "usuario y rango de fechas, exportable a PDF o Excel. Sirve "
            "para auditar quién y cuándo accedió al sistema.",
        ),
        (
            "Seguridad", "bitacora_movimientos", "Bitácora de Movimientos",
            "bi-journal-text",
            "Registro de auditoría de las acciones realizadas en el "
            "sistema (crear, modificar, eliminar, intentos de acceso "
            "denegado, etc.), filtrable por usuario y fecha, exportable a "
            "PDF o Excel. Es la bitácora general de todo lo que pasa en "
            "SIGEPAN, no solo de inicios de sesión.",
        ),
        (
            "Seguridad", "acerca_de", "Acerca de SIGEPAN",
            "bi-info-circle",
            "Información general del sistema: versión, tecnologías "
            "utilizadas, desarrolladores y datos de contacto para "
            "soporte.",
        ),
    ]

    def handle(self, *args, **options):
        creadas = 0
        existentes = 0
        modulos_faltantes = set()

        for nombre_modulo, pantalla, titulo, icono, contenido in self.AYUDAS:

            modulo = Modulo.objects.filter(nombre=nombre_modulo).first()

            if not modulo:
                modulos_faltantes.add(nombre_modulo)
                self.stdout.write(
                    self.style.WARNING(
                        f"  Módulo '{nombre_modulo}' no existe en esta base "
                        f"de datos; se omite la ayuda de '{pantalla}'."
                    )
                )
                continue

            _ayuda, fue_creada = Ayuda.objects.get_or_create(
                modulo=modulo,
                pantalla=pantalla,
                defaults={
                    "titulo": titulo,
                    "contenido": contenido,
                    "icono": icono,
                    "orden": 1,
                    "estado": True,
                },
            )

            if fue_creada:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  + creada: {nombre_modulo} / {pantalla}")
                )
            else:
                existentes += 1
                self.stdout.write(f"  = ya existía: {nombre_modulo} / {pantalla}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo. {creadas} ayuda(s) nueva(s), {existentes} ya existían."
            )
        )

        if modulos_faltantes:
            self.stdout.write(
                self.style.WARNING(
                    "\nOjo: no se encontraron estos módulos en la tabla "
                    "`modulo` (revisa que el nombre coincida exacto con "
                    "apps/security/menu.py): "
                    + ", ".join(sorted(modulos_faltantes))
                )
            )
