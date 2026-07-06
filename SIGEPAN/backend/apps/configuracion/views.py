from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Modulo
from .forms import ModuloForm


class ModuloListView(ListView):
    model = Modulo
    template_name = "configuracion/modulos/list.html"
    context_object_name = "modulos"


class ModuloCreateView(CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        messages.success(self.request, "Módulo creado correctamente.")
        return super().form_valid(form)


class ModuloUpdateView(UpdateView):
    model = Modulo
    form_class = ModuloForm
    pk_url_kwarg = "id_modulo"
    template_name = "configuracion/modulos/form.html"
    success_url = reverse_lazy("configuracion:modulo_list")

    def form_valid(self, form):
        messages.success(self.request, "Módulo actualizado correctamente.")
        return super().form_valid(form)