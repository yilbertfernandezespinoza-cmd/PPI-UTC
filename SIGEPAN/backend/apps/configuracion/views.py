from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Modulo, Sucursal
from .forms import ModuloForm, SucursalForm
from apps.security.mixins import SessionRequiredMixin

class ModuloListView(SessionRequiredMixin, ListView):
    model = Modulo
    template_name = "configuracion/modulos/list.html"
    context_object_name = "modulos"


class ModuloCreateView(SessionRequiredMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        messages.success(self.request, "Módulo creado correctamente.")
        return super().form_valid(form)


class ModuloUpdateView(SessionRequiredMixin, UpdateView):
    model = Modulo
    form_class = ModuloForm
    pk_url_kwarg = "id_modulo"
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        messages.success(self.request, "Módulo actualizado correctamente.")
        return super().form_valid(form)
    
class SucursalListView(SessionRequiredMixin, ListView):
    model = Sucursal
    template_name = "configuracion/sucursales/list.html"
    context_object_name = "sucursales"


class SucursalCreateView(SessionRequiredMixin, CreateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "configuracion/sucursales/form.html"
    success_url = reverse_lazy("configuracion:sucursal_list")

    def form_valid(self, form):
        messages.success(self.request, "Sucursal creada correctamente.")
        return super().form_valid(form)


class SucursalUpdateView(SessionRequiredMixin, UpdateView):
    model = Sucursal
    form_class = SucursalForm
    pk_url_kwarg = "id_sucursal"
    template_name = "configuracion/sucursales/form.html"
    success_url = reverse_lazy("configuracion:sucursal_list")

    def form_valid(self, form):
        messages.success(self.request, "Sucursal actualizada correctamente.")
        return super().form_valid(form)    