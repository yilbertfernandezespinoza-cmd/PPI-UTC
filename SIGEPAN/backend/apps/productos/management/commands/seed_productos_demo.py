from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.categorias.models import Categoria
from apps.configuracion.models import Sucursal
from apps.inventario.models import Inventario
from apps.productos.models import Producto
from apps.productos.services import ProductoService


class Command(BaseCommand):
    """
    Agregado 07-08: siembra (idempotente) un catálogo de demostración de
    20 productos de panadería, sus categorías y su inventario inicial en
    "Sucursal Principal", para que el sistema tenga datos con qué
    funcionar apenas se termina de instalar (POS, reportes, dashboard,
    alertas de stock bajo, etc.) en vez de arrancar completamente vacío.

    No es un catálogo obligatorio del sistema (a diferencia de
    seed_permisos_modulos o seed_metodos_pago): es contenido de ejemplo,
    pensado para pruebas y para que el profesor pueda ver el sistema
    funcionando con datos reales sin tener que digitarlos a mano.

    Usa get_or_create en todo — correrlo varias veces no duplica nada.
    El precio de venta de cada producto se calcula con la misma fórmula
    real del sistema (ProductoService.calcular_precio_venta), no un
    número inventado, para que quede consistente con lo que vería un
    usuario creando un producto a mano desde el formulario.

    Deja a propósito 4 productos con stock por debajo del mínimo
    (Mollete, Palito de Queso, Cheesecake, Agua Embotellada) para que la
    tarjeta de "alertas de stock bajo" del dashboard (RF-020) tenga algo
    que mostrar desde el primer momento.

    Requiere que ya exista la sucursal "Sucursal Principal" — créala
    primero con `python manage.py seed_admin`.

    Uso:
        python manage.py seed_productos_demo
    """

    help = (
        "Crea 20 productos de ejemplo (panadería), sus categorías e "
        "inventario inicial en Sucursal Principal, si todavía no existen."
    )

    CATEGORIAS = [
        ("Panes", "Panes salados y dulces de elaboración diaria"),
        ("Repostería", "Croissants, empanadas y bocadillos horneados"),
        ("Pasteles", "Pasteles y postres por porción"),
        ("Galletas", "Galletas individuales y surtidos"),
        ("Bebidas", "Café, jugos y bebidas embotelladas"),
        ("Snacks", "Sandwiches y bocadillos listos para llevar"),
    ]

    # (codigo, nombre, categoria, precio_compra, unidad_medida)
    PRODUCTOS = [
        ("PAN-001", "Pan Baguette", "Panes", "200.00", Producto.UNIDAD_UNIDAD),
        ("PAN-002", "Pan Campesino", "Panes", "350.00", Producto.UNIDAD_UNIDAD),
        ("PAN-003", "Pan Integral", "Panes", "300.00", Producto.UNIDAD_UNIDAD),
        ("PAN-004", "Mollete (Pan Dulce)", "Panes", "150.00", Producto.UNIDAD_UNIDAD),
        ("PAN-005", "Pan Bono", "Panes", "180.00", Producto.UNIDAD_UNIDAD),
        ("PAN-006", "Docena de Pan Dulce Surtido", "Panes", "1500.00", Producto.UNIDAD_DOCENA),
        ("REP-001", "Croissant", "Repostería", "280.00", Producto.UNIDAD_UNIDAD),
        ("REP-002", "Empanada de Queso", "Repostería", "220.00", Producto.UNIDAD_UNIDAD),
        ("REP-003", "Empanada de Piña", "Repostería", "220.00", Producto.UNIDAD_UNIDAD),
        ("REP-004", "Palito de Queso", "Repostería", "180.00", Producto.UNIDAD_UNIDAD),
        ("PAS-001", "Pastel de Chocolate (porción)", "Pasteles", "700.00", Producto.UNIDAD_UNIDAD),
        ("PAS-002", "Pastel Tres Leches (porción)", "Pasteles", "750.00", Producto.UNIDAD_UNIDAD),
        ("PAS-003", "Cheesecake (porción)", "Pasteles", "800.00", Producto.UNIDAD_UNIDAD),
        ("GAL-001", "Galleta de Avena", "Galletas", "120.00", Producto.UNIDAD_UNIDAD),
        ("GAL-002", "Galleta Chispas de Chocolate", "Galletas", "120.00", Producto.UNIDAD_UNIDAD),
        ("BEB-001", "Café Americano", "Bebidas", "350.00", Producto.UNIDAD_UNIDAD),
        ("BEB-002", "Café con Leche", "Bebidas", "450.00", Producto.UNIDAD_UNIDAD),
        ("BEB-003", "Jugo Natural", "Bebidas", "400.00", Producto.UNIDAD_UNIDAD),
        ("BEB-004", "Agua Embotellada", "Bebidas", "250.00", Producto.UNIDAD_UNIDAD),
        ("SNK-001", "Sandwich Jamón y Queso", "Snacks", "800.00", Producto.UNIDAD_UNIDAD),
    ]

    # codigo -> (stock_actual, stock_minimo, stock_maximo)
    # Los 4 marcados abajo quedan a propósito por debajo del mínimo.
    STOCK = {
        "PAN-001": (40, 15, 80),
        "PAN-002": (25, 10, 60),
        "PAN-003": (20, 10, 50),
        "PAN-004": (15, 20, 60),   # bajo stock (a propósito)
        "PAN-005": (30, 10, 60),
        "PAN-006": (8, 3, 20),
        "REP-001": (35, 15, 70),
        "REP-002": (30, 10, 60),
        "REP-003": (30, 10, 60),
        "REP-004": (10, 15, 40),  # bajo stock (a propósito)
        "PAS-001": (12, 5, 25),
        "PAS-002": (10, 5, 25),
        "PAS-003": (3, 5, 20),    # bajo stock (a propósito)
        "GAL-001": (50, 20, 100),
        "GAL-002": (50, 20, 100),
        "BEB-001": (100, 30, 200),
        "BEB-002": (80, 30, 200),
        "BEB-003": (40, 15, 80),
        "BEB-004": (25, 30, 100),  # bajo stock (a propósito)
        "SNK-001": (20, 10, 40),
    }

    def handle(self, *args, **options):
        sucursal = Sucursal.objects.filter(nombre="Sucursal Principal").first()
        if sucursal is None:
            self.stdout.write(
                self.style.ERROR(
                    "No existe la sucursal 'Sucursal Principal'. Corre "
                    "primero 'python manage.py seed_admin' y vuelve a "
                    "intentarlo."
                )
            )
            return

        categorias = self._crear_categorias()
        self._crear_productos_e_inventario(categorias, sucursal)

        self.stdout.write(self.style.SUCCESS("\nListo."))

    def _crear_categorias(self):
        categorias = {}
        for nombre, descripcion in self.CATEGORIAS:
            categoria, creado = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion},
            )
            categorias[nombre] = categoria
            self.stdout.write(
                f"Categoría '{nombre}': {'creada' if creado else 'ya existía'}"
            )
        return categorias

    def _crear_productos_e_inventario(self, categorias, sucursal):
        creados = 0
        existentes = 0

        for codigo, nombre, nombre_categoria, precio_compra, unidad in self.PRODUCTOS:
            precio_compra = Decimal(precio_compra)
            porcentaje_utilidad = Decimal("30.00")
            porcentaje_impuesto = Decimal("13.00")

            producto, creado = Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "id_categoria": categorias[nombre_categoria],
                    "nombre": nombre,
                    "unidad_medida": unidad,
                    "precio_compra": precio_compra,
                    "porcentaje_utilidad": porcentaje_utilidad,
                    "porcentaje_impuesto": porcentaje_impuesto,
                    "precio_venta": ProductoService.calcular_precio_venta(
                        precio_compra, porcentaje_utilidad, porcentaje_impuesto
                    ),
                },
            )

            if creado:
                creados += 1
                self.stdout.write(f"  + creado: {codigo} — {nombre}")
            else:
                existentes += 1
                self.stdout.write(f"  = ya existía: {codigo} — {nombre}")

            stock_actual, stock_minimo, stock_maximo = self.STOCK[codigo]
            Inventario.objects.get_or_create(
                id_producto=producto,
                id_sucursal=sucursal,
                defaults={
                    "stock_actual": stock_actual,
                    "stock_minimo": stock_minimo,
                    "stock_maximo": stock_maximo,
                },
            )

        self.stdout.write(
            f"\n{creados} producto(s) nuevos, {existentes} ya existían "
            f"(inventario asegurado para todos en '{sucursal.nombre}')."
        )
