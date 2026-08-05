from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction


from .models import (
    Compra,
    DetalleCompra
)


from .forms import (
    CompraForm,
    DetalleCompraFormSet
)


from apps.security.models import Usuario

from apps.inventario.models import TipoMovimientoInventario
from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService


# =====================================================
# LISTAR COMPRAS
# =====================================================

def lista_compras(request):

    compras = Compra.objects.all().order_by("-fecha")

    return render(
        request,
        "compras/lista_compras.html",
        {"compras": compras}
    )


# =====================================================
# CREAR COMPRA
# =====================================================

@transaction.atomic
def crear_compra(request):

    usuario_id = request.session.get("usuario_id")

    usuario_actual = get_object_or_404(
        Usuario,
        id_usuario=usuario_id
    )

    if request.method == "POST":

        compra_form = CompraForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST)

        if compra_form.is_valid() and detalle_formset.is_valid():

            compra = compra_form.save(commit=False)

            # DATOS AUTOMATICOS
            compra.usuario = usuario_actual
            compra.sucursal = usuario_actual.id_sucursal
            compra.fecha = timezone.now()
            compra.estado = True

            # Inicialmente en cero, luego se calcula
            compra.total = 0
            compra.save()

            detalles = detalle_formset.save(commit=False)

            total_compra = 0

            tipo_entrada = TipoMovimientoInventario.objects.get(
                nombre="ENTRADA_COMPRA"
            )

            for detalle in detalles:

                detalle.compra = compra

                detalle.subtotal = (
                    detalle.cantidad * detalle.precio_unitario
                )

                total_compra += detalle.subtotal

                detalle.save()

                # ACTUALIZAR INVENTARIO (con trazabilidad real)
                inventario = InventarioRepository.obtener_o_crear(
                    id_producto=detalle.producto,
                    id_sucursal=usuario_actual.id_sucursal,
                )

                MovimientoInventarioService.registrar_movimiento(
                    inventario=inventario,
                    tipo_movimiento=tipo_entrada,
                    usuario=usuario_actual,
                    cantidad=detalle.cantidad,
                    observaciones=f"Compra #{compra.id_compra}",
                )

            # ACTUALIZAR TOTAL FINAL
            compra.total = total_compra
            compra.save(update_fields=["total"])

            messages.success(request, "Compra registrada correctamente.")

            return redirect(
                "compras:detalle_compra",
                id_compra=compra.id_compra
            )

    else:
        compra_form = CompraForm()
        detalle_formset = DetalleCompraFormSet()

    return render(
        request,
        "compras/crear_compra.html",
        {
            "compra_form": compra_form,
            "detalle_formset": detalle_formset
        }
    )


# =====================================================
# DETALLE DE COMPRA
# =====================================================

def detalle_compra(request, id_compra):

    compra = get_object_or_404(Compra, id_compra=id_compra)

    detalles = DetalleCompra.objects.filter(compra=compra)

    return render(
        request,
        "compras/detalle_compra.html",
        {
            "compra": compra,
            "detalles": detalles
        }
    )


# =====================================================
# ANULAR COMPRA
# =====================================================

@transaction.atomic
def anular_compra(request, id_compra):

    compra = get_object_or_404(Compra, id_compra=id_compra)

    if request.method == "POST":

        if compra.estado:

            detalles = DetalleCompra.objects.filter(compra=compra)

            usuario_id = request.session.get("usuario_id")

            usuario_actual = get_object_or_404(
                Usuario,
                id_usuario=usuario_id
            )

            # DEVOLVER INVENTARIO (con trazabilidad real)
            tipo_devolucion = TipoMovimientoInventario.objects.get(
                nombre="DEVOLUCION_COMPRA"
            )

            try:
                for detalle in detalles:

                    inventario = InventarioRepository.obtener_o_crear(
                        id_producto=detalle.producto,
                        id_sucursal=usuario_actual.id_sucursal,
                    )

                    MovimientoInventarioService.registrar_movimiento(
                        inventario=inventario,
                        tipo_movimiento=tipo_devolucion,
                        usuario=usuario_actual,
                        cantidad=detalle.cantidad,
                        observaciones=f"Anulación de compra #{compra.id_compra}",
                    )

                compra.estado = False
                compra.save()

                messages.success(request, "Compra anulada correctamente.")

            except ValidationError as error:
                messages.error(
                    request,
                    f"No se pudo anular la compra: {error}"
                )

        return redirect("compras:lista_compras")

    return render(
        request,
        "compras/anular_compra.html",
        {"compra": compra}
    )