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

def buscar_producto_pos(request):

    texto = request.GET.get(
        "q",
        ""
    ).strip()


    if len(texto) < 2:

        return JsonResponse(
            [],
            safe=False
        )


    productos = (
        Producto.objects
        .filter(
            estado=True
        )
        .filter(
            Q(nombre__icontains=texto)
            |
            Q(codigo__icontains=texto)
        )
        .order_by(
            "nombre"
        )[:10]
    )


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

        })


    return JsonResponse(
        datos,
        safe=False
    )

