from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Modulo, Sucursal, ConfiguracionTributaria
from .forms import ModuloForm, SucursalForm, ConfiguracionTributariaForm
from apps.security.mixins import SessionRequiredMixin
from apps.security.audit import AuditMixin
from apps.security.permissions import PermissionRequiredMixin
from apps.security.models import RolPermiso

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
    
class ConfiguracionTributariaListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView
):
    permission_module = "Configuración"
    permission_action = "CONSULTAR"

    model = ConfiguracionTributaria
    template_name = "configuracion/tributaria/list.html"
    context_object_name = "configuraciones_tributarias"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        usuario = self.request.usuario

        context["puede_crear"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Configuración",
            id_permiso__accion="CREAR",
        ).exists()

        context["puede_modificar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Configuración",
            id_permiso__accion="MODIFICAR",
        ).exists()

        return context


class ConfiguracionTributariaCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView
):
    permission_module = "Configuración"
    permission_action = "CREAR"

    audit_module = "Configuración"
    model = ConfiguracionTributaria
    form_class = ConfiguracionTributariaForm
    template_name = "configuracion/tributaria/form.html"
    success_url = reverse_lazy("configuracion:tributaria_list")

    def form_valid(self, form):
        response = super().form_valid(form)

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se creó la configuración tributaria "
                f"{self.object.nombre}"
            ),
        )

        messages.success(
            self.request,
            "Configuración tributaria creada correctamente."
        )

        return response


class ConfiguracionTributariaUpdateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    UpdateView
):
    permission_module = "Configuración"
    permission_action = "MODIFICAR"

    audit_module = "Configuración"
    model = ConfiguracionTributaria
    form_class = ConfiguracionTributariaForm
    pk_url_kwarg = "id_configuracion_tributaria"
    template_name = "configuracion/tributaria/form.html"
    success_url = reverse_lazy("configuracion:tributaria_list")

    def form_valid(self, form):
        response = super().form_valid(form)

        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=(
                f"Se actualizó la configuración tributaria "
                f"{self.object.nombre}"
            ),
        )

        messages.success(
            self.request,
            "Configuración tributaria actualizada correctamente."
        )

        return response    