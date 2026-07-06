from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .forms import RolForm, PermisoForm
from .models import Rol, Permiso


class RolListView(ListView):
    model = Rol
    template_name = "security/roles/list.html"
    context_object_name = "roles"


class RolCreateView(CreateView):
    model = Rol
    form_class = RolForm
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol creado correctamente.")
        return super().form_valid(form)


class RolUpdateView(UpdateView):
    model = Rol
    form_class = RolForm
    pk_url_kwarg = "id_rol"
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol actualizado correctamente.")
        return super().form_valid(form)
    
class PermisoListView(ListView):
    model = Permiso
    template_name = "security/permisos/list.html"
    context_object_name = "permisos"

    def get_queryset(self):
        return (
            Permiso.objects
            .select_related("id_modulo")
            .order_by("id_modulo__nombre", "accion")
        )


class PermisoCreateView(CreateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")

    def form_valid(self, form):
        messages.success(self.request, "Permiso creado correctamente.")
        return super().form_valid(form)


class PermisoUpdateView(UpdateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")
    pk_url_kwarg = "id_permiso"

    def form_valid(self, form):
        messages.success(self.request, "Permiso actualizado correctamente.")
        return super().form_valid(form)    