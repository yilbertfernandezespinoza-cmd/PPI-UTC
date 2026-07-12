from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Modulo, Sucursal
from .forms import ModuloForm, SucursalForm
from apps.security.mixins import SessionRequiredMixin
from apps.security.audit import AuditMixin
from apps.security.permissions import PermissionRequiredMixin

class ModuloListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    permission_module = "Configuración"
    permission_action = "CONSULTAR"
    
    model = Modulo
    template_name = "configuracion/modulos/list.html"
    context_object_name = "modulos"


class ModuloCreateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, CreateView):
    permission_module = "Configuración"
    permission_action = "CREAR"
    
    audit_module = "Configuración"
    model = Modulo
    form_class = ModuloForm
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        response = super().form_valid(form)

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se creó el módulo "
                f"{self.object.nombre}"
            ),
        )

        messages.success(
            self.request,
            "Módulo creado correctamente."
        )

        return response


class ModuloUpdateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, UpdateView):
    permission_module = "Configuración"
    permission_action = "MODIFICAR"
    
    audit_module = "Configuración"
    model = Modulo
    form_class = ModuloForm
    pk_url_kwarg = "id_modulo"
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el módulo {self.object.nombre}",
        )
        messages.success(self.request, "Módulo actualizado correctamente.")
        return super().form_valid(form)
    
class SucursalListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    permission_module = "Configuración"
    permission_action = "CONSULTAR"
    
    model = Sucursal
    template_name = "configuracion/sucursales/list.html"
    context_object_name = "sucursales"


class SucursalCreateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, CreateView):
    permission_module = "Configuración"
    permission_action = "CREAR"

    audit_module = "Configuración"
    model = Sucursal
    form_class = SucursalForm
    template_name = "configuracion/sucursales/form.html"
    success_url = reverse_lazy("configuracion:sucursal_list")

    def form_valid(self, form):

        response = super().form_valid(form)

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se creó la sucursal "
                f"{self.object.nombre}"
            ),
        )

        messages.success(
            self.request,
            "Sucursal creada correctamente."
        )

        return response


class SucursalUpdateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, UpdateView):
    permission_module = "Configuración"
    permission_action = "MODIFICAR"
    
    audit_module = "Configuración"
    model = Sucursal
    form_class = SucursalForm
    pk_url_kwarg = "id_sucursal"
    template_name = "configuracion/sucursales/form.html"
    success_url = reverse_lazy("configuracion:sucursal_list")

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó la sucursal {self.object.nombre}",
        )
        messages.success(self.request, "Sucursal actualizada correctamente.")
        return super().form_valid(form)    