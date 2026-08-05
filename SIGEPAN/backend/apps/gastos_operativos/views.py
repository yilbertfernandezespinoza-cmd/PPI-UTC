from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, View

from apps.configuracion.models import Sucursal
from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.models import RolPermiso
from apps.security.permissions import PermissionRequiredMixin

from .forms import CATEGORIAS_SUGERIDAS, GastoOperativoForm
from .models import GastoOperativo
from .services import GastoOperativoService


class GastoOperativoListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Gastos Operativos"
    permission_action = "CONSULTAR"

    model = GastoOperativo
    template_name = "gastos_operativos/list.html"
    context_object_name = "gastos"

    def get_queryset(self):
        return GastoOperativoService.filtrar(
            id_sucursal=self.request.GET.get("sucursal") or None,
            categoria=self.request.GET.get("categoria") or None,
            desde=self.request.GET.get("desde") or None,
            hasta=self.request.GET.get("hasta") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sucursales"] = Sucursal.objects.filter(estado=True).order_by("nombre")
        context["categorias"] = CATEGORIAS_SUGERIDAS
        context["filtro_sucursal"] = self.request.GET.get("sucursal", "")
        context["filtro_categoria"] = self.request.GET.get("categoria", "")
        context["filtro_desde"] = self.request.GET.get("desde", "")
        context["filtro_hasta"] = self.request.GET.get("hasta", "")

        usuario = self.request.usuario

        context["puede_eliminar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Gastos Operativos",
            id_permiso__accion="ELIMINAR",
        ).exists()

        return context


class GastoOperativoCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    FormView,
):
    permission_module = "Gastos Operativos"
    permission_action = "CREAR"

    audit_module = "Gastos Operativos"

    form_class = GastoOperativoForm
    template_name = "gastos_operativos/form.html"
    success_url = reverse_lazy("gastos_operativos:listar")

    def form_valid(self, form):
        try:
            gasto = GastoOperativoService.registrar(
                usuario=self.request.usuario,
                descripcion=form.cleaned_data["descripcion"],
                categoria=form.cleaned_data["categoria"],
                monto=form.cleaned_data["monto"],
                fecha_gasto=form.cleaned_data["fecha_gasto"],
                observaciones=form.cleaned_data.get("observaciones"),
            )
        except ValidationError as error:
            messages.error(
                self.request,
                "; ".join(error.messages) if hasattr(error, "messages") else str(error),
            )
            return self.form_invalid(form)

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se registró un gasto operativo de ₡{gasto.monto} "
                f"({gasto.categoria}): {gasto.descripcion}"
            ),
        )

        mensaje = "Gasto operativo registrado correctamente."
        if gasto.caja:
            mensaje += " Se generó el movimiento de caja correspondiente."

        messages.success(self.request, mensaje)

        return redirect(self.success_url)


class GastoOperativoDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):
    permission_module = "Gastos Operativos"
    permission_action = "ELIMINAR"

    audit_module = "Gastos Operativos"

    def post(self, request, id_gasto):
        gasto = GastoOperativoService.cambiar_estado(id_gasto)

        accion = "deshabilitó" if not gasto.estado else "habilitó"

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=f"Se {accion} el gasto operativo #{gasto.id_gasto}",
        )

        mensaje = (
            "Gasto operativo deshabilitado correctamente."
            if not gasto.estado
            else "Gasto operativo habilitado correctamente."
        )

        messages.success(request, mensaje)

        return redirect("gastos_operativos:listar")
