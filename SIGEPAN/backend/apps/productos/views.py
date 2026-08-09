from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .forms import ProductoForm

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
