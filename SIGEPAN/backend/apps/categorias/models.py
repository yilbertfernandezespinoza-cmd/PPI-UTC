from django.db import models

from apps.core.base_models import BaseModel


class Categoria(BaseModel):
    """
    Modelo que representa la tabla categoria.

    La tabla real ya tiene las columnas estado, fecha_creacion y
    fecha_actualizacion (antes declaradas a mano en este modelo,
    duplicando exactamente lo que BaseModel ya provee: mismos tipos,
    mismos defaults, mismo auto_now_add/auto_now), así que puede
    heredar de BaseModel — permite deshabilitar una categoría sin
    borrarla, igual que Cliente/Gasto Operativo.
    """

    id_categoria = models.AutoField(primary_key=True, db_column="id_categoria")
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed=False (06-08): la tabla `categoria` ya existe en la BD
        # real (Database First), igual que el resto del proyecto. Antes
        # esta app usaba migraciones reales de Django como excepción al
        # resto del sistema — inconsistencia detectada el 06-08, mismo
        # tratamiento aplicado a `producto`, `ayuda` y `cliente`. Las
        # migraciones existentes (`apps/categorias/migrations/`) se dejan
        # tal cual pero quedan inertes.
        managed = False
        db_table = "categoria"   # <--  nombre exacto de la tabla en sigepan_db
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre
