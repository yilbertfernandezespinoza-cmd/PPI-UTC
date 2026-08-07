from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.urls import reverse

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import View

from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin
from apps.security.decorators import login_required, permiso_requerido
from apps.security.services import registrar_log

from .models import Inventario
from .forms import InventarioForm, MovimientoInventarioForm
from .repositories import InventarioRepository, MovimientoInventarioRepository
from .services import MovimientoInventarioService


# =====================================================
# LISTA DE INVENTARIO
# =====================================================
#
# Hallazgo de auditoría de seguridad (04-08-2026): estas 3 vistas no
# tenían NINGÚN control de sesión ni de permisos, a diferencia de
# EntradaInventarioView/MovimientosInventarioListView (más abajo en este
# mismo archivo), que sí usan SessionRequiredMixin/PermissionRequiredMixin.
# Cualquiera con la URL podía ver y editar stock/umbrales sin autenticarse.
# Se usa el decorador @login_required/@permiso_requerido (equivalente para
# vistas basadas en función) en vez de convertirlas a CBV, para mantener el
# arreglo como un parche puntual, reutilizando el módulo de permisos
# "Inventario" que ya existe en la base de datos (lo usan las otras 2
# vistas de este archivo).

@login_required
@permiso_requerido("Inventario", "CONSULTAR")
def lista_inventario(request):

    inventarios = Inventario.objects.all().order_by(
        "id_producto__nombre"
    )

    # Serialización a JSON (07-08): mismo patrón que Categorías/Productos/
    # Proveedores/Ventas/Compras/Cajas — Tabulator.js (SIGEPAN.table.create())
    # en vez de una tabla plana sin buscador ni paginación, para que la
    # lista de inventario no crezca sin control visual a medida que se
    # agregan productos/sucursales.
    inventarios_json = [
        {
            "id_inventario": inventario.id_inventario,
            "producto": inventario.id_producto.nombre,
            "sucursal": inventario.id_sucursal.nombre,
            "stock_actual": inventario.stock_actual,
            "stock_minimo": inventario.stock_minimo,
            "stock_maximo": inventario.stock_maximo,
            "bajo_minimo": inventario.stock_actual <= inventario.stock_minimo,
            "estado": inventario.estado,
            "ver": reverse("inventario:detalle_inventario", args=[inventario.id_inventario]),
            "editar": reverse("inventario:editar_inventario", args=[inventario.id_inventario]),
        }
        for inventario in inventarios
    ]

    return render(
        request,
        "inventario/lista_inventario.html",
        {
            "inventarios": inventarios,
            "inventarios_json": inventarios_json,
        }
    )


# =====================================================
# DETALLE INVENTARIO
# =====================================================

@login_required
@permiso_requerido("Inventario", "CONSULTAR")
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

@login_required
@permiso_requerido("Inventario", "MODIFICAR")
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

            # Corregido (07-08, hallazgo de auditoría): a diferencia de
            # EntradaInventarioView (que sí usa AuditMixin), esta vista
            # (function-based) no dejaba rastro en la bitácora al editar
            # stock_minimo/stock_maximo/ubicacion/estado — el decorador
            # @permiso_requerido solo audita el acceso denegado, no la
            # mutación exitosa.
            registrar_log(
                request=request,
                usuario=request.usuario,
                modulo="Inventario",
                tipo_accion="MODIFICAR",
                descripcion=(
                    f"Se actualizó el inventario de "
                    f"{inventario.id_producto.nombre} en "
                    f"{inventario.id_sucursal.nombre}"
                ),
            )

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