from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria
from .forms import CategoriaForm
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log


@login_required
@permiso_requerido("Categorías", "CONSULTAR")
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/lista.html', {'categorias': categorias})


@login_required
@permiso_requerido("Categorías", "CREAR")
def nueva_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Categorías",
                tipo_accion="CREAR",
                descripcion=f"Se creó la categoría {categoria.nombre}",
            )
            return redirect('categorias:lista_categorias')  # 👈 importante usar el namespace
    else:
        form = CategoriaForm()
    return render(request, 'categorias/nueva.html', {'form': form})


@login_required
@permiso_requerido("Categorías", "MODIFICAR")
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Categorías",
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó la categoría {categoria.nombre}",
            )
            return redirect('categorias:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'categorias/editar.html', {'form': form})


@login_required
@permiso_requerido("Categorías", "ELIMINAR")
def cambiar_estado_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        categoria.estado = not categoria.estado
        categoria.save()
        registrar_log(
            request=request,
            usuario=request.usuario,
            modulo="Categorías",
            tipo_accion="MODIFICAR",
            descripcion=(
                f"Se {'activó' if categoria.estado else 'desactivó'} "
                f"la categoría {categoria.nombre}"
            ),
        )
        return redirect("categorias:lista_categorias")

    return render(
        request,
        "categorias/cambiar_estado.html",
        {"categoria": categoria}
    )
