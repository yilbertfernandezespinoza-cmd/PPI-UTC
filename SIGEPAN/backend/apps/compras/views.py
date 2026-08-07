from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone


from .models import Compra


from .forms import (
    CompraForm,
    DetalleCompraFormSet
)


from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log

from .repositories import CompraRepository
from .services import CompraService, CompraValidationError


# =====================================================
# LISTAR COMPRAS
# =====================================================

@login_required
@permiso_requerido("Compras", "CONSULTAR")
def lista_compras(request):

    compras = CompraRepository.listar()

    # Serialización a JSON (07-08): la tabla migra de jQuery DataTables
    # (ya no funciona, base.html no carga jQuery desde que el proyecto
    # adoptó Tabulator.js) al mismo patrón que ya usa Clientes.
    compras_json = [
        {
            "id_compra": compra.id_compra,
            "proveedor": compra.proveedor.nombre if compra.proveedor else "-",
            "fecha": timezone.localtime(compra.fecha).strftime("%d/%m/%Y %H:%M"),
            "total": str(compra.total),
            "estado": compra.estado,
            "detalle": reverse("compras:detalle_compra", args=[compra.id_compra]),
            "anular": reverse("compras:anular_compra", args=[compra.id_compra]),
        }
        for compra in compras
    ]

    return render(
        request,
        "compras/lista_compras.html",
        {
            "compras": compras,
            "compras_json": compras_json,
        }
    )


# =====================================================
# CREAR COMPRA
# =====================================================

@login_required
@permiso_requerido("Compras", "CREAR")
@transaction.atomic
def crear_compra(request):

    if request.method == "POST":

        compra_form = CompraForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST)

        if compra_form.is_valid() and detalle_formset.is_valid():

            usuario_actual = request.usuario

            compra = compra_form.save(commit=False)
            detalles = detalle_formset.save(commit=False)

            # La lógica de negocio (validar el tipo de movimiento, guardar
            # compra/detalles, incrementar inventario) vive en
            # CompraService.crear_compra().
            try:
                compra = CompraService.crear_compra(
                    compra=compra,
                    detalles=detalles,
                    usuario=usuario_actual,
                    sucursal=usuario_actual.id_sucursal,
                )
            except CompraValidationError as error:
                messages.error(request, str(error))
                return redirect("compras:crear_compra")

            messages.success(request, "Compra registrada correctamente.")

            registrar_log(
                request=request,
                usuario=usuario_actual,
                modulo="Compras",
                tipo_accion="CREAR",
                descripcion=f"Se registró la compra #{compra.id_compra}",
            )

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

@login_required
@permiso_requerido("Compras", "CONSULTAR")
def detalle_compra(request, id_compra):

    compra = get_object_or_404(Compra, id_compra=id_compra)

    detalles = CompraRepository.detalles(compra)

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

@login_required
@permiso_requerido("Compras", "ELIMINAR")
@transaction.atomic
def anular_compra(request, id_compra):

    compra = get_object_or_404(Compra, id_compra=id_compra)

    if request.method == "POST":

        if compra.estado:

            usuario_actual = request.usuario

            # La lógica de negocio (validar el tipo de movimiento,
            # revertir inventario, marcar la compra como inactiva) vive
            # en CompraService.anular_compra().
            try:
                compra, advertencias = CompraService.anular_compra(
                    compra, usuario_actual
                )
            except CompraValidationError as error:
                messages.error(request, str(error))
                return redirect("compras:lista_compras")

            for advertencia in advertencias:
                messages.warning(request, advertencia)

            messages.success(request, "Compra anulada correctamente.")

            registrar_log(
                request=request,
                usuario=usuario_actual,
                modulo="Compras",
                tipo_accion="MODIFICAR",
                descripcion=f"Se anuló la compra #{compra.id_compra}",
            )

        return redirect("compras:lista_compras")

    return render(
        request,
        "compras/anular_compra.html",
        {"compra": compra}
    )
