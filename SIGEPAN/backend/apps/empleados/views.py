from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Cargo, Empleado
from .forms import CargoForm, EmpleadoForm
from apps.security.mixins import SessionRequiredMixin
from apps.security.audit import AuditMixin
from apps.security.permissions import PermissionRequiredMixin

class CargoListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    permission_module = "Configuración"
    permission_action = "CONSULTAR"
    
    model = Cargo
    template_name = "empleados/cargos/list.html"
    context_object_name = "cargos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Serialización para el componente Tabulator (mismo patrón que
        # clientes/gastos_operativos): no se toca el queryset existente.
        context["cargos_json"] = [
            {
                "id_cargo": cargo.id_cargo,
                "nombre": cargo.nombre,
                "descripcion": cargo.descripcion or "-",
                "estado": cargo.estado,
                "editar": reverse("empleados:cargo_update", args=[cargo.id_cargo]),
            }
            for cargo in context["cargos"]
        ]

        return context


class CargoCreateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, CreateView):
    permission_module = "Configuración"
    permission_action = "CREAR"
    
    audit_module = "Configuración"
    model = Cargo
    form_class = CargoForm
    template_name = "empleados/cargos/form.html"
    success_url = reverse_lazy("empleados:cargo_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el cargo {self.object.nombre}",
        )
        messages.success(self.request, "Cargo creado correctamente.")
        return response


class CargoUpdateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, UpdateView):
    permission_module = "Configuración"
    permission_action = "MODIFICAR"

    audit_module = "Configuración"
    model = Cargo
    form_class = CargoForm
    template_name = "empleados/cargos/form.html"
    success_url = reverse_lazy("empleados:cargo_list")
    pk_url_kwarg = "id_cargo"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el cargo {self.object.nombre}",
        )
        messages.success(self.request, "Cargo actualizado correctamente.")
        return response
    
class EmpleadoListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    permission_module = "Configuración"
    permission_action = "CONSULTAR"

    model = Empleado
    template_name = "empleados/empleados/list.html"
    context_object_name = "empleados"

    def get_queryset(self):
        return (
            Empleado.objects
            .select_related("id_cargo")
            .order_by("nombre", "apellido1")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Serialización para el componente Tabulator (mismo patrón que
        # clientes/gastos_operativos): no se toca el queryset existente.
        context["empleados_json"] = [
            {
                "id_empleado": empleado.id_empleado,
                "identificacion": empleado.identificacion,
                "nombre_completo": " ".join(
                    filter(None, [empleado.nombre, empleado.apellido1, empleado.apellido2])
                ),
                "cargo": empleado.id_cargo.nombre if empleado.id_cargo else "-",
                "telefono": empleado.telefono or "-",
                "correo": empleado.correo or "-",
                "estado": empleado.estado,
                "editar": reverse("empleados:empleado_update", args=[empleado.id_empleado]),
            }
            for empleado in context["empleados"]
        ]

        return context


class EmpleadoCreateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, CreateView):
    permission_module = "Configuración"
    permission_action = "CREAR"

    audit_module = "Configuración"
    
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleados/form.html"
    success_url = reverse_lazy("empleados:empleado_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el empleado {self.object.nombre} {self.object.apellido1}",
        )
        messages.success(self.request, "Empleado creado correctamente.")
        return response


class EmpleadoUpdateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, UpdateView):
    permission_module = "Configuración"
    permission_action = "MODIFICAR"

    audit_module = "Configuración"
    
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleados/form.html"
    success_url = reverse_lazy("empleados:empleado_list")
    pk_url_kwarg = "id_empleado"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el empleado {self.object.nombre} {self.object.apellido1}",
        )
        messages.success(self.request, "Empleado actualizado correctamente.")
        return response    