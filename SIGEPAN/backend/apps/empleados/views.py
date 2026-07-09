from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Cargo, Empleado
from .forms import CargoForm, EmpleadoForm
from apps.security.mixins import SessionRequiredMixin
from apps.security.audit import AuditMixin

class CargoListView(SessionRequiredMixin, ListView):
    model = Cargo
    template_name = "empleados/cargos/list.html"
    context_object_name = "cargos"


class CargoCreateView(SessionRequiredMixin, AuditMixin, CreateView):
    audit_module = "Empleados"
    model = Cargo
    form_class = CargoForm
    template_name = "empleados/cargos/form.html"
    success_url = reverse_lazy("empleados:cargo_list")

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el cargo {self.object.nombre}",
        )
        messages.success(self.request, "Cargo creado correctamente.")
        return super().form_valid(form)


class CargoUpdateView(SessionRequiredMixin, AuditMixin, UpdateView):
    audit_module = "Empleados"
    model = Cargo
    form_class = CargoForm
    template_name = "empleados/cargos/form.html"
    success_url = reverse_lazy("empleados:cargo_list")
    pk_url_kwarg = "id_cargo"

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el cargo {self.object.nombre}",
        )
        messages.success(self.request, "Cargo actualizado correctamente.")
        return super().form_valid(form)
    
class EmpleadoListView(SessionRequiredMixin, ListView):
    model = Empleado
    template_name = "empleados/empleados/list.html"
    context_object_name = "empleados"

    def get_queryset(self):
        return (
            Empleado.objects
            .select_related("id_cargo")
            .order_by("nombre", "apellido1")
        )


class EmpleadoCreateView(SessionRequiredMixin, AuditMixin, CreateView):
    audit_module = "Empleados"
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleados/form.html"
    success_url = reverse_lazy("empleados:empleado_list")

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el empleado {self.object.nombre} {self.object.apellido1}",
        )
        messages.success(self.request, "Empleado creado correctamente.")
        return super().form_valid(form)


class EmpleadoUpdateView(SessionRequiredMixin, AuditMixin, UpdateView):
    audit_module = "Empleados"
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleados/form.html"
    success_url = reverse_lazy("empleados:empleado_list")
    pk_url_kwarg = "id_empleado"

    def form_valid(self, form):
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el empleado {self.object.nombre} {self.object.apellido1}",
        )
        messages.success(self.request, "Empleado actualizado correctamente.")
        return super().form_valid(form)    