from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .forms import ProductoForm
from django.http import JsonResponse
from django.db.models import Q


# Listar productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos})

# Crear producto
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/nuevo.html', {'form': form})

# Editar producto
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form})

# Eliminar producto (deshabilitación lógica)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.estado = False  # deshabilitación lógica
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


    return JsonResponse(
        datos,
        safe=False
    )

