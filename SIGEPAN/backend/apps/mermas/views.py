from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from apps.productos.models import Producto
from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin

from .forms import MermaForm
from .models import Merma
from .services import MermaService


class MermaListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Mermas"
    permission_action = "CONSULTAR"

    model = Merma
    template_name = "mermas/list.html"
    context_object_name = "mermas"

    def get_queryset(self):
        return MermaService.filtrar(
            id_producto=self.request.GET.get("producto") or None,
            desde=self.request.GET.get("desde") or None,
            hasta=self.request.GET.get("hasta") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.filter(estado=True).order_by("nombre")
        context["filtro_producto"] = self.request.GET.get("producto", "")
        context["filtro_desde"] = self.request.GET.get("desde", "")
        context["filtro_hasta"] = self.request.GET.get("hasta", "")
        return context


class MermaDetailView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    permission_module = "Mermas"
    permission_action = "CONSULTAR"

    model = Merma
    template_name = "mermas/detalle.html"
    context_object_name = "merma"
    pk_url_kwarg = "id_merma"

    def get_object(self, queryset=None):
        return MermaService.obtener(self.kwargs["id_merma"])


class MermaCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    permission_module = "Mermas"
    permission_action = "CREAR"

    audit_module = "Mermas"

    model = Merma
    form_class = MermaForm
    template_name = "mermas/form.html"
    success_url = reverse_lazy("mermas:listar")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Solo ofrecer productos con inventario (stock > 0) en la
        # sucursal del usuario — evita registrar mermas de productos que
        # esa sucursal ni siquiera maneja.
        usuario = self.request.usuario

        form.fields["producto"].queryset = (
            Producto.objects
            .filter(
                estado=True,
                inventario__id_sucursal=usuario.id_sucursal,
                inventario__stock_actual__gt=0,
            )
            .distinct()
            .order_by("nombre")
        )

        return form

    def form_valid(self, form):
        try:
            merma = MermaService.registrar(
                producto=form.cleaned_data["producto"],
                usuario=self.request.usuario,
                cantidad=form.cleaned_data["cantidad"],
                motivo=form.cleaned_data["motivo"],
                fecha=form.cleaned_data["fecha"],
                observaciones=form.cleaned_data.get("observaciones"),
            )
        except ValidationError as error:
            messages.error(
                self.request,
                "; ".join(error.messages) if hasattr(error, "messages") else str(error),
            )
            return self.form_invalid(form)

        self.object = merma

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se registró una merma de {merma.cantidad} unidad(es) de "
                f"{merma.producto.nombre} — motivo: {merma.motivo}"
            ),
        )

        messages.success(
            self.request,
            "Merma registrada correctamente. El inventario fue actualizado."
        )

        return redirect(self.success_url)
