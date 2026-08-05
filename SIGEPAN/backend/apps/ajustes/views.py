from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from apps.productos.models import Producto
from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin

from .forms import AjusteForm
from .models import Ajuste
from .services import AjusteService


class AjusteListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Ajustes"
    permission_action = "CONSULTAR"

    model = Ajuste
    template_name = "ajustes/list.html"
    context_object_name = "ajustes"

    def get_queryset(self):
        return AjusteService.filtrar(
            id_producto=self.request.GET.get("producto") or None,
            tipo=self.request.GET.get("tipo") or None,
            desde=self.request.GET.get("desde") or None,
            hasta=self.request.GET.get("hasta") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.filter(estado=True).order_by("nombre")
        context["tipos"] = Ajuste.Tipo.choices
        context["filtro_producto"] = self.request.GET.get("producto", "")
        context["filtro_tipo"] = self.request.GET.get("tipo", "")
        context["filtro_desde"] = self.request.GET.get("desde", "")
        context["filtro_hasta"] = self.request.GET.get("hasta", "")
        return context


class AjusteDetailView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    permission_module = "Ajustes"
    permission_action = "CONSULTAR"

    model = Ajuste
    template_name = "ajustes/detalle.html"
    context_object_name = "ajuste"
    pk_url_kwarg = "id_ajuste"

    def get_object(self, queryset=None):
        return AjusteService.obtener(self.kwargs["id_ajuste"])


class AjusteCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    permission_module = "Ajustes"
    permission_action = "CREAR"

    audit_module = "Ajustes"

    model = Ajuste
    form_class = AjusteForm
    template_name = "ajustes/form.html"
    success_url = reverse_lazy("ajustes:listar")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["producto"].queryset = (
            Producto.objects.filter(estado=True).order_by("nombre")
        )
        return form

    def form_valid(self, form):
        try:
            ajuste = AjusteService.registrar(
                producto=form.cleaned_data["producto"],
                usuario=self.request.usuario,
                cantidad=form.cleaned_data["cantidad"],
                tipo=form.cleaned_data["tipo"],
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

        self.object = ajuste

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se registró un ajuste de {ajuste.get_tipo_display()} de "
                f"{ajuste.cantidad} unidad(es) de {ajuste.producto.nombre} "
                f"— motivo: {ajuste.motivo}"
            ),
        )

        messages.success(
            self.request,
            "Ajuste registrado correctamente. El inventario fue actualizado."
        )

        return redirect(self.success_url)
