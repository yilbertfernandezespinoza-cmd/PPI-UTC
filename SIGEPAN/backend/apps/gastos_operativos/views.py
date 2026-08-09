from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView, View

from apps.configuracion.models import Sucursal
from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.models import RolPermiso
from apps.security.permissions import PermissionRequiredMixin

from .forms import CATEGORIAS_SUGERIDAS, GastoOperativoForm
from .models import GastoOperativo
from .services import GastoOperativoService


def _resolver_ruta_comprobante(form):
    """
    Resuelve qué guardar en la columna `comprobante` (varchar con la
    ruta, no un FileField real) a partir de form.cleaned_data
    ["comprobante"] — mismo patrón que `_resolver_ruta_imagen` en
    `apps/ayuda/views.py`. Como este formulario es solo de creación (no
    hay edición de un gasto ya registrado), no hace falta el caso
    "conservar la ruta actual" que sí necesita Ayuda: si no se sube
    archivo, simplemente no hay comprobante (None).
    """

    archivo = form.cleaned_data.get("comprobante")

    if isinstance(archivo, UploadedFile):
        return default_storage.save(f"gastos_operativos/{archivo.name}", archivo)

    return None


class GastoOperativoListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Gastos Operativos"
    permission_action = "CONSULTAR"

    model = GastoOperativo
    template_name = "gastos_operativos/list.html"
    context_object_name = "gastos"

    def get_queryset(self):
        return GastoOperativoService.filtrar(
            id_sucursal=self.request.GET.get("sucursal") or None,
            categoria=self.request.GET.get("categoria") or None,
            desde=self.request.GET.get("desde") or None,
            hasta=self.request.GET.get("hasta") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sucursales"] = Sucursal.objects.filter(estado=True).order_by("nombre")
        context["categorias"] = CATEGORIAS_SUGERIDAS
        context["filtro_sucursal"] = self.request.GET.get("sucursal", "")
        context["filtro_categoria"] = self.request.GET.get("categoria", "")
        context["filtro_desde"] = self.request.GET.get("desde", "")
        context["filtro_hasta"] = self.request.GET.get("hasta", "")

        usuario = self.request.usuario

        context["puede_eliminar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Gastos Operativos",
            id_permiso__accion="ELIMINAR",
        ).exists()

        # Serialización a JSON (07-08): mismo patrón Tabulator ya aplicado
        # en el resto del sistema.
        context["gastos_json"] = [
            {
                "id_gasto": gasto.id_gasto,
                "fecha_gasto": timezone.localtime(gasto.fecha_gasto).strftime("%d/%m/%Y %H:%M"),
                "sucursal": gasto.sucursal.nombre if gasto.sucursal else "-",
                "categoria": gasto.categoria,
                "descripcion": gasto.descripcion,
                "monto": str(gasto.monto),
                "comprobante": f"/media/{gasto.comprobante}" if gasto.comprobante else "",
                "caja": gasto.caja.nombre if gasto.caja else "",
                "usuario": str(gasto.usuario),
                "estado": gasto.estado,
                "estado_url": reverse("gastos_operativos:estado", args=[gasto.id_gasto]),
            }
            for gasto in context["gastos"]
        ]

        return context


class GastoOperativoCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    FormView,
):
    permission_module = "Gastos Operativos"
    permission_action = "CREAR"

    audit_module = "Gastos Operativos"

    form_class = GastoOperativoForm
    template_name = "gastos_operativos/form.html"
    success_url = reverse_lazy("gastos_operativos:listar")

    def get_form_kwargs(self):
        # FormView por defecto solo pasa request.POST al form, no
        # request.FILES — necesario para que el campo `comprobante`
        # (FileField) reciba el archivo subido. El template ya tiene
        # enctype="multipart/form-data" (ver form.html).
        kwargs = super().get_form_kwargs()
        kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        try:
            gasto = GastoOperativoService.registrar(
                usuario=self.request.usuario,
                descripcion=form.cleaned_data["descripcion"],
                categoria=form.cleaned_data["categoria"],
                monto=form.cleaned_data["monto"],
                fecha_gasto=form.cleaned_data["fecha_gasto"],
                observaciones=form.cleaned_data.get("observaciones"),
                comprobante=_resolver_ruta_comprobante(form),
            )
        except ValidationError as error:
            messages.error(
                self.request,
                "; ".join(error.messages) if hasattr(error, "messages") else str(error),
            )
            return self.form_invalid(form)

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se registró un gasto operativo de ₡{gasto.monto} "
                f"({gasto.categoria}): {gasto.descripcion}"
            ),
        )

        mensaje = "Gasto operativo registrado correctamente."
        if gasto.caja:
            mensaje += " Se generó el movimiento de caja correspondiente."

        messages.success(self.request, mensaje)

        return redirect(self.success_url)


class GastoOperativoDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):
    permission_module = "Gastos Operativos"
    permission_action = "ELIMINAR"

    audit_module = "Gastos Operativos"

    def post(self, request, id_gasto):
        gasto = GastoOperativoService.cambiar_estado(id_gasto)

        accion = "deshabilitó" if not gasto.estado else "habilitó"

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=f"Se {accion} el gasto operativo #{gasto.id_gasto}",
        )

        mensaje = (
            "Gasto operativo deshabilitado correctamente."
            if not gasto.estado
            else "Gasto operativo habilitado correctamente."
        )

        messages.success(request, mensaje)

        return redirect("gastos_operativos:listar")
