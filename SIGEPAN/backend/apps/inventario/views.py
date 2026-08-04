from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import View

from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin

from .models import Inventario
from .forms import InventarioForm, MovimientoInventarioForm
from .repositories import InventarioRepository, MovimientoInventarioRepository
from .services import MovimientoInventarioService


# =====================================================
# LISTA DE INVENTARIO
# =====================================================

def lista_inventario(request):

    inventarios = Inventario.objects.all().order_by(
        "id_producto__nombre"
    )

    return render(
        request,
        "inventario/lista_inventario.html",
        {"inventarios": inventarios}
    )


# =====================================================
# DETALLE INVENTARIO
# =====================================================

def detalle_inventario(request, id_inventario):

    inventario = get_object_or_404(
        Inventario,
        id_inventario=id_inventario
    )

    return render(
        request,
        "inventario/detalle_inventario.html",
        {"inventario": inventario}
    )


# =====================================================
# EDITAR CONFIGURACION INVENTARIO
# =====================================================

def editar_inventario(request, id_inventario):

    inventario = get_object_or_404(
        Inventario,
        id_inventario=id_inventario
    )

    if request.method == "POST":

        form = InventarioForm(
            request.POST,
            instance=inventario
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Inventario actualizado correctamente."
            )

            return redirect("inventario:lista_inventario")

    else:
        form = InventarioForm(instance=inventario)

    return render(
        request,
        "inventario/editar_inventario.html",
        {
            "form": form,
            "inventario": inventario
        }
    )


# =====================================================
# ENTRADA DE INVENTARIO (RF-028)
# =====================================================

class EntradaInventarioView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):

    permission_module = "Inventario"
    permission_action = "CREAR"
    audit_module = "Inventario"

    def get(self, request):
        form = MovimientoInventarioForm()

        return render(
            request,
            "inventario/entrada_inventario.html",
            {"form": form}
        )

    def post(self, request):
        form = MovimientoInventarioForm(request.POST)

        if form.is_valid():

            producto = form.cleaned_data["producto"]
            sucursal = form.cleaned_data["sucursal"]
            tipo_movimiento = form.cleaned_data["tipo_movimiento"]
            cantidad = form.cleaned_data["cantidad"]
            observaciones = form.cleaned_data["observaciones"]

            inventario = InventarioRepository.obtener_o_crear(
                id_producto=producto,
                id_sucursal=sucursal,
            )

            try:
                MovimientoInventarioService.registrar_movimiento(
                    inventario=inventario,
                    tipo_movimiento=tipo_movimiento,
                    usuario=request.usuario,
                    cantidad=cantidad,
                    observaciones=observaciones,
                )

                self.registrar_auditoria(
                    "CREAR",
                    f"Entrada de inventario: {cantidad} de "
                    f"{producto.nombre} en {sucursal.nombre} "
                    f"({tipo_movimiento.nombre})",
                )

                messages.success(
                    request,
                    "Entrada de inventario registrada correctamente."
                )

                return redirect("inventario:lista_inventario")

            except ValidationError as error:
                messages.error(request, str(error))

        return render(
            request,
            "inventario/entrada_inventario.html",
            {"form": form}
        )


# =====================================================
# HISTORIAL DE MOVIMIENTOS (RF-028)
# =====================================================

class MovimientosInventarioListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    View,
):

    permission_module = "Inventario"
    permission_action = "CONSULTAR"

    def get(self, request):
        movimientos = MovimientoInventarioRepository.listar()

        return render(
            request,
            "inventario/lista_movimientos.html",
            {"movimientos": movimientos}
        )