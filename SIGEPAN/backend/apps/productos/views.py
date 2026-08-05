from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from django.db.models import Q

from .models import Producto
from .forms import ProductoForm
from .services import ProductoService
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log


# Listar productos
@login_required
@permiso_requerido("Productos", "CONSULTAR")
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
@login_required
@permiso_requerido("Productos", "CREAR")
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
            if isinstance(archivo, UploadedFile):
                ruta = default_storage.save(f"productos/{archivo.name}", archivo)
                producto.imagen = ruta
            else:
                producto.imagen = None

            producto.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Productos",
                tipo_accion="CREAR",
                descripcion=f"Se creó el producto {producto.nombre}",
            )
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/nuevo.html', {'form': form})


# Editar producto
@login_required
@permiso_requerido("Productos", "MODIFICAR")
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

            # form.cleaned_data['imagen'] puede venir en 3 formas distintas:
            # un archivo nuevo (UploadedFile) si el usuario subió uno; False
            # si marcó el checkbox "Clear" del ClearableFileInput; o el
            # string de la ruta ya existente si no tocó el campo (Django lo
            # devuelve así para los FileField/ImageField cuando hay un
            # `initial` y no llega nada nuevo en el POST). Antes se hacía
            # `if archivo:` y se le sacaba `.name` directo — como un string
            # no vacío también es "truthy", esto reventaba con
            # AttributeError cada vez que se editaba un producto con
            # imagen ya asignada sin subir una nueva.
            archivo = form.cleaned_data.get('imagen')
            if isinstance(archivo, UploadedFile):
                ruta = default_storage.save(f"productos/{archivo.name}", archivo)
                producto_actualizado.imagen = ruta
            elif archivo is False:
                producto_actualizado.imagen = None
            else:
                producto_actualizado.imagen = imagen_actual

            producto_actualizado.save()
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Productos",
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó el producto {producto_actualizado.nombre}",
            )
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form})


# Eliminar producto (deshabilitación lógica)
@login_required
@permiso_requerido("Productos", "ELIMINAR")
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.estado = False
        producto.save()
        registrar_log(
            request=request,
            usuario=request.usuario,
            modulo="Productos",
            tipo_accion="MODIFICAR",
            descripcion=f"Se deshabilitó el producto {producto.nombre}",
        )
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
#
# Nota de seguridad: es un endpoint AJAX (fetch/XHR desde el POS), así que en
# vez de @login_required (que redirige a /security/login/, rompiendo el
# fetch del navegador con HTML en vez de JSON) se valida la sesión a mano y
# se responde 401 en JSON si no hay usuario autenticado.

def buscar_producto_pos(request):

    if not request.session.get("usuario_id"):
        return JsonResponse(
            {"error": "No autenticado."},
            status=401,
        )

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
