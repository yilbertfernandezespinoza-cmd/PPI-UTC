from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor
from .forms import ProveedorForm
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log

@login_required
@permiso_requerido("Proveedores", "CONSULTAR")
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/lista.html', {'proveedores': proveedores})

@login_required
@permiso_requerido("Proveedores", "CREAR")
def nuevo_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Proveedores",
                tipo_accion="CREAR",
                descripcion=f"Se creó el proveedor {proveedor.nombre}",
            )
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'proveedores/nuevo.html', {'form': form})

@login_required
@permiso_requerido("Proveedores", "MODIFICAR")
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Proveedores",
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó el proveedor {proveedor.nombre}",
            )
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores/editar.html', {'form': form})

@login_required
@permiso_requerido("Proveedores", "ELIMINAR")
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.estado = False
        proveedor.save()
        registrar_log(
            request=request,
            usuario=request.usuario,
            modulo="Proveedores",
            tipo_accion="ELIMINAR",
            descripcion=f"Se deshabilitó el proveedor {proveedor.nombre}",
        )
        return redirect('proveedores:lista_proveedores')
    return render(request, 'proveedores/eliminar.html', {'proveedor': proveedor})
