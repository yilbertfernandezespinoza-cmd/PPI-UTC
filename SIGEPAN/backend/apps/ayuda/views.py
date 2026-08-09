from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import redirect

from apps.ayuda.models import Ayuda
from apps.ayuda.forms import AyudaForm
from apps.ayuda.services import AyudaService

from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin
from apps.security.audit import AuditMixin


class AyudaListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """
    Lista todas las ayudas registradas.
    """

    permission_module = "Ayudas"
    permission_action = "CONSULTAR"

    model = Ayuda
    template_name = "ayuda/list.html"
    context_object_name = "ayudas"

    def get_queryset(self):
        return AyudaService.listar()


class AyudaCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    permission_module = "Ayudas"
    permission_action = "CREAR"

    audit_module = "Ayudas"

    model = Ayuda
    form_class = AyudaForm
    template_name = "ayuda/form.html"
    success_url = reverse_lazy("ayuda:list")

    def form_valid(self, form):

        try:

            AyudaService.crear(
                modulo_id=form.cleaned_data["modulo"].id_modulo,
                pantalla=form.cleaned_data["pantalla"],
                titulo=form.cleaned_data["titulo"],
                contenido=form.cleaned_data["contenido"],
                icono=form.cleaned_data["icono"],
                orden=form.cleaned_data["orden"],
            )

            self.registrar_auditoria(
                tipo_accion="CREAR",
                descripcion="Se creó una ayuda.",
            )

            messages.success(
                self.request,
                "Ayuda creada correctamente.",
            )

            return redirect(self.success_url)

        except ValueError as e:

            messages.error(
                self.request,
                str(e),
            )

            return self.form_invalid(form)


class AyudaUpdateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    UpdateView,
):
    permission_module = "Ayudas"
    permission_action = "MODIFICAR"

    audit_module = "Ayudas"

    model = Ayuda
    form_class = AyudaForm
    template_name = "ayuda/form.html"

    pk_url_kwarg = "id_ayuda"

    success_url = reverse_lazy("ayuda:list")

    def form_valid(self, form):

        try:

            AyudaService.actualizar(
                id_ayuda=self.object.id_ayuda,
                modulo_id=form.cleaned_data["modulo"].id_modulo,
                pantalla=form.cleaned_data["pantalla"],
                titulo=form.cleaned_data["titulo"],
                contenido=form.cleaned_data["contenido"],
                icono=form.cleaned_data["icono"],
                orden=form.cleaned_data["orden"],
            )

            self.registrar_auditoria(
                tipo_accion="MODIFICAR",
                descripcion="Se actualizó una ayuda.",
            )

            messages.success(
                self.request,
                "Ayuda actualizada correctamente.",
            )

            return redirect(self.success_url)

        except ValueError as e:

            messages.error(
                self.request,
                str(e),
            )

            return self.form_invalid(form)


class AyudaDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):

    permission_module = "Ayudas"
    permission_action = "ELIMINAR"

    audit_module = "Ayudas"

    def post(self, request, id_ayuda):

        try:

            nuevo_estado = AyudaService.cambiar_estado(
                id_ayuda
            )

            if nuevo_estado:

                self.registrar_auditoria(
                    tipo_accion="MODIFICAR",
                    descripcion="Se activó una ayuda.",
                )

                messages.success(
                    request,
                    "Ayuda activada correctamente.",
                )

            else:

                self.registrar_auditoria(
                    tipo_accion="ELIMINAR",
                    descripcion="Se deshabilitó una ayuda.",
                )

                messages.success(
                    request,
                    "Ayuda deshabilitada correctamente.",
                )

        except ValueError as e:

            messages.error(
                request,
                str(e),
            )

        return redirect(
            reverse_lazy("ayuda:list")
        )