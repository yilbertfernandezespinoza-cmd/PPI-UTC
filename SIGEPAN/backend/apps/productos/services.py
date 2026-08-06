# Servicios del módulo
from decimal import Decimal, ROUND_HALF_UP

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from .repositories import ProductoRepository


class ProductoService:

    @staticmethod
    def calcular_precio_venta(precio_compra, porcentaje_utilidad, porcentaje_impuesto):
        """
        Calcula el precio de venta a partir del precio de compra,
        el porcentaje de utilidad y el porcentaje de impuesto.

        precio_con_utilidad = precio_compra * (1 + utilidad / 100)
        precio_venta = precio_con_utilidad * (1 + impuesto / 100)
        """

        precio_compra = Decimal(precio_compra or 0)
        porcentaje_utilidad = Decimal(porcentaje_utilidad or 0)
        porcentaje_impuesto = Decimal(porcentaje_impuesto or 0)

        precio_con_utilidad = precio_compra * (
            Decimal("1") + (porcentaje_utilidad / Decimal("100"))
        )

        precio_venta = precio_con_utilidad * (
            Decimal("1") + (porcentaje_impuesto / Decimal("100"))
        )

        return precio_venta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def listar():
        return ProductoRepository.listar()

    @staticmethod
    def obtener_por_id(pk):
        return ProductoRepository.obtener_por_id(pk)

    @staticmethod
    def _resolver_imagen(archivo, ruta_actual=None):
        """
        Resuelve qué guardar en la columna `imagen` (varchar con la ruta,
        no un ImageField real) a partir de form.cleaned_data["imagen"].

        Ese valor puede venir en 3 formas distintas: un archivo nuevo
        (UploadedFile) si el usuario subió uno; False si marcó el
        checkbox "Clear" del ClearableFileInput; o el string de la ruta
        ya existente si no tocó el campo al editar (Django lo devuelve
        así para los FileField/ImageField cuando hay un `initial` y no
        llega nada nuevo en el POST). Por eso se valida explícitamente
        con `isinstance(archivo, UploadedFile)` en vez de un simple
        `if archivo:` — un string no vacío también es "truthy" y no
        tiene atributo `.name` de archivo, lo que producía un
        AttributeError cada vez que se editaba un producto con imagen ya
        asignada sin subir una nueva. Mismo patrón que
        apps.ayuda.views._resolver_ruta_imagen.
        """

        if isinstance(archivo, UploadedFile):
            return default_storage.save(f"productos/{archivo.name}", archivo)

        if archivo is False:
            return None

        return ruta_actual

    @staticmethod
    @transaction.atomic
    def crear(form):
        """
        Crea un producto a partir de un ProductoForm ya validado
        (form.is_valid() == True), calculando el precio de venta y
        resolviendo la imagen subida (si la hay).
        """

        producto = form.save(commit=False)

        producto.precio_venta = ProductoService.calcular_precio_venta(
            producto.precio_compra,
            producto.porcentaje_utilidad,
            producto.porcentaje_impuesto,
        )

        archivo = form.cleaned_data.get("imagen")
        producto.imagen = ProductoService._resolver_imagen(archivo, ruta_actual=None)

        producto.save()

        return producto

    @staticmethod
    @transaction.atomic
    def actualizar(form, producto):
        """
        Actualiza un producto existente a partir de un ProductoForm ya
        validado (instance=producto), recalculando el precio de venta y
        conservando la imagen actual si no se subió una nueva.
        """

        imagen_actual = producto.imagen

        producto_actualizado = form.save(commit=False)

        producto_actualizado.precio_venta = ProductoService.calcular_precio_venta(
            producto_actualizado.precio_compra,
            producto_actualizado.porcentaje_utilidad,
            producto_actualizado.porcentaje_impuesto,
        )

        archivo = form.cleaned_data.get("imagen")
        producto_actualizado.imagen = ProductoService._resolver_imagen(
            archivo, ruta_actual=imagen_actual
        )

        producto_actualizado.save()

        return producto_actualizado

    @staticmethod
    @transaction.atomic
    def deshabilitar(producto):
        """
        Deshabilita (lógicamente) un producto ya obtenido.
        """
        return ProductoRepository.cambiar_estado(producto, False)

    @staticmethod
    def buscar_pos(texto="", categoria_id="", limite=10):
        return ProductoRepository.buscar_pos(
            texto=texto, categoria_id=categoria_id, limite=limite
        )
