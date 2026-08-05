from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.db.models import Q

from .models import Producto
from .forms import ProductoForm
from .services import ProductoService


# Listar productos
# Listar productos
def lista_productos(request):
    productos = Producto.objects.select_related('id_categoria').all()

    productos_json = []
    for producto in productos:
        productos_json.append({
            "id_producto": producto.id_producto,
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "precio_compra": str(producto.precio_compra),
            "precio_venta": str(producto.precio_venta) if producto.precio_venta is not None else "",
            "unidad_medida": producto.unidad_medida,
            "categoria": producto.id_categoria.nombre,
            "estado": producto.estado,
            "editar": f"/productos/editar/{producto.id_producto}/",
            "eliminar": f"/productos/eliminar/{producto.id_producto}/",
        })

    return render(request, 'productos/lista.html', {
        'productos': productos,
        'productos_json': productos_json,
    })


# Crear producto
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)

            producto.precio_venta = ProductoService.calcular_precio_venta(
                producto.precio_compra,
                producto.porcentaje_utilidad,
                producto.porcentaje_impuesto,
            )

            archivo = form.cleaned_data.get('imagen')
            if archivo:
                ruta = default_storage.save(f"productos/{archivo.name}", archivo)
                producto.imagen = ruta
            else:
                producto.imagen = None

            producto.save()
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/nuevo.html', {'form': form})


# Editar producto
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    imagen_actual = producto.imagen

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto_actualizado = form.save(commit=False)

            producto_actualizado.precio_venta = ProductoService.calcular_precio_venta(
                producto_actualizado.precio_compra,
                producto_actualizado.porcentaje_utilidad,
                producto_actualizado.porcentaje_impuesto,
            )

            archivo = form.cleaned_data.get('imagen')
            if archivo:
                ruta = default_storage.save(f"productos/{archivo.name}", archivo)
                producto_actualizado.imagen = ruta
            else:
                producto_actualizado.imagen = imagen_actual

            producto_actualizado.save()
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form})


# Eliminar producto (deshabilitación lógica)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.estado = False
        producto.save()
        return redirect('productos:lista_productos')
    return render(request, 'productos/eliminar.html', {'producto': producto})


# =====================================================
# BUSCAR PRODUCTOS POS
# =====================================================
#
# Usado por el buscador de texto del POS (?q=...) y, desde la migración del
# POS a la cuadrícula de categorías (RF-012), también por los tiles de
# producto de cada pestaña de categoría (?categoria_id=...). Con q sin
# categoria_id el comportamiento es idéntico al de siempre (mínimo 2
# caracteres, top 10 resultados) — no se rompe ningún llamador existente.
# Con categoria_id se ignora el mínimo de 2 caracteres (la cuadrícula debe
# poder listar todos los productos de una categoría sin que el cajero
# escriba nada) y se amplía el límite a 60 tiles.

def buscar_producto_pos(request):

    texto = request.GET.get(
        "q",
        ""
    ).strip()

    categoria_id = request.GET.get(
        "categoria_id",
        ""
    ).strip()

    if not categoria_id and len(texto) < 2:

        return JsonResponse(
            [],
            safe=False
        )

    productos = (
        Producto.objects
        .filter(
            estado=True
        )
    )

    if categoria_id:
        productos = productos.filter(id_categoria_id=categoria_id)

    if texto:
        productos = productos.filter(
            Q(nombre__icontains=texto)
            |
            Q(codigo__icontains=texto)
        )

    limite = 60 if categoria_id else 10

    productos = productos.order_by(
        "nombre"
    )[:limite]

    datos = []

    for producto in productos:
        datos.append({

            "id":
                producto.id_producto,

            "codigo":
                producto.codigo,

            "nombre":
                producto.nombre,

            "precio":
                str(
                    producto.precio_venta
                ),

            "unidad":
                producto.unidad_medida,

            "impuesto":
                str(
                    producto.porcentaje_impuesto
                ),

            "categoria_id":
                producto.id_categoria_id,

        })

    return JsonResponse(datos, safe=False)