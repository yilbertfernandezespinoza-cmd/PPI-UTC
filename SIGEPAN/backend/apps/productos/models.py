from django.db import models
from apps.categorias.models import Categoria
from apps.core.base_models import BaseModel

class Producto(BaseModel):

    # Unidades de medida disponibles para un producto de panadería.
    # RF-011: el <select> de unidad_medida estaba vacío porque el campo era
    # un CharField sin `choices` — el widget forms.Select no tenía de dónde
    # sacar opciones y el formulario nunca podía validar. Se agregan choices
    # explícitos; la columna sigue siendo varchar(30) sin cambios, así que
    # los productos ya guardados con "Unidad" (el default anterior) no se
    # ven afectados.
    UNIDAD_UNIDAD = "Unidad"
    UNIDAD_DOCENA = "Docena"
    UNIDAD_KILOGRAMO = "Kilogramo"
    UNIDAD_GRAMO = "Gramo"
    UNIDAD_LIBRA = "Libra"
    UNIDAD_LITRO = "Litro"
    UNIDAD_MILILITRO = "Mililitro"
    UNIDAD_PAQUETE = "Paquete"
    UNIDAD_CAJA = "Caja"
    UNIDAD_BOLSA = "Bolsa"

    UNIDADES_MEDIDA = [
        (UNIDAD_UNIDAD, "Unidad"),
        (UNIDAD_DOCENA, "Docena"),
        (UNIDAD_KILOGRAMO, "Kilogramo (kg)"),
        (UNIDAD_GRAMO, "Gramo (g)"),
        (UNIDAD_LIBRA, "Libra (lb)"),
        (UNIDAD_LITRO, "Litro (l)"),
        (UNIDAD_MILILITRO, "Mililitro (ml)"),
        (UNIDAD_PAQUETE, "Paquete"),
        (UNIDAD_CAJA, "Caja"),
        (UNIDAD_BOLSA, "Bolsa"),
    ]

    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        db_column="id_categoria",
        related_name="productos"
    )
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_utilidad = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=13.00)
    unidad_medida = models.CharField(
        max_length=30,
        default=UNIDAD_UNIDAD,
        choices=UNIDADES_MEDIDA,
    )
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    # estado, fecha_creacion y fecha_actualizacion ahora vienen de BaseModel
    # (apps.core.base_models): la tabla `producto` ya tenía exactamente estas
    # tres columnas con estos mismos tipos/defaults (BooleanField default=True,
    # DateTimeField auto_now_add=True/auto_now=True, mismos nombres de columna
    # por defecto), así que heredar no cambia el esquema real, solo evita
    # duplicar la declaración — mismo patrón que GastoOperativo
    # (apps/gastos_operativos/models.py).

    class Meta:
        # managed=False (06-08): la tabla `producto` ya existe en la BD
        # real (Database First), igual que el resto del proyecto. Antes
        # esta app usaba migraciones reales de Django (0001_initial.py +
        # 0002_alter_producto_unidad_medida.py) como excepción al resto
        # del sistema — inconsistencia detectada el 06-08. Con
        # managed=False, Django deja de intentar reconciliar el modelo
        # contra ese historial de migraciones, así que ya no hace falta
        # correr `migrate productos` para nada (ni siquiera para la
        # migración 0002, que solo cambiaba metadata de `choices`, sin
        # tocar la columna real). Las migraciones existentes se dejan
        # tal cual (borrarlas es riesgoso) pero quedan inertes — mismo
        # tratamiento ya aplicado a `ayuda.Ayuda` y `cliente.Cliente`.
        managed = False
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
