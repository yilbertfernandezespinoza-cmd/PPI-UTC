from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .forms import ClienteForm
from .models import Cliente
from .services import ClienteService

from apps.security.permissions import PermissionRequiredMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.audit import AuditMixin

from apps.security.models import RolPermiso

class ClienteListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Clientes"
    permission_action = "CONSULTAR"

    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"

    def get_queryset(self):

        return ClienteService.listar()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        usuario = self.request.usuario

        context["puede_crear"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Clientes",
            id_permiso__accion="CREAR",
        ).exists()

        context["puede_modificar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Clientes",
            id_permiso__accion="MODIFICAR",
        ).exists()

        context["puede_eliminar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Clientes",
            id_permiso__accion="ELIMINAR",
        ).exists()

        return context
    
class ClienteCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    permission_module = "Clientes"
    permission_action = "CREAR"

    audit_module = "Clientes"

    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:listar")

    def form_valid(self, form):

        cliente = ClienteService.crear(form.cleaned_data)

        self.object = cliente

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se creó el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        messages.success(
            self.request,
            "Cliente creado correctamente."
        )

        return redirect(self.success_url)    
    
class ClienteUpdateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    UpdateView,
):
    permission_module = "Clientes"
    permission_action = "MODIFICAR"

    audit_module = "Clientes"

    model = Cliente
    form_class = ClienteForm
    pk_url_kwarg = "id_cliente"
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:listar")

    def form_valid(self, form):

        cliente = ClienteService.actualizar(
            self.kwargs["id_cliente"],
            form.cleaned_data,
        )

        self.object = cliente

        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=(
                f"Se actualizó el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        messages.success(
            self.request,
            "Cliente actualizado correctamente."
        )

        return redirect(self.success_url)   

from django.views.generic import View


class ClienteDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):
    permission_module = "Clientes"
    permission_action = "ELIMINAR"

    audit_module = "Clientes"

    def post(self, request, id_cliente):

        cliente = ClienteService.cambiar_estado(
            id_cliente
        )

        accion = (
            "deshabilitó"
            if not cliente.estado
            else "habilitó"
        )

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=(
                f"Se {accion} el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        mensaje = (
            "Cliente deshabilitado correctamente."
            if not cliente.estado
            else "Cliente habilitado correctamente."
        )

        messages.success(
            request,
            mensaje,
        )

        return redirect(
            "clientes:listar"
        ) 