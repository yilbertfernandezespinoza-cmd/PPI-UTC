from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from apps.inventario.models import Inventario
from apps.productos.models import Producto
from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.models import Usuario
from apps.security.permissions import PermissionRequiredMixin

from .forms import AjusteForm
from .models import Ajuste
from .services import AjusteService


class AjusteListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_module = "Ajustes"
    permission_action = "CONSULTAR"

    model = Ajuste
    template_name = "ajustes/list.html"
    context_object_name = "ajustes"

    def get_queryset(self):
        return AjusteService.filtrar(
            id_producto=self.request.GET.get("producto") or None,
            tipo=self.request.GET.get("tipo") or None,
            desde=self.request.GET.get("desde") or None,
            hasta=self.request.GET.get("hasta") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.filter(estado=True).order_by("nombre")
        context["tipos"] = Ajuste.Tipo.choices
        context["filtro_producto"] = self.request.GET.get("producto", "")
        context["filtro_tipo"] = self.request.GET.get("tipo", "")
        context["filtro_desde"] = self.request.GET.get("desde", "")
        context["filtro_hasta"] = self.request.GET.get("hasta", "")

        # Serialización a JSON (07-08): mismo patrón Tabulator ya aplicado
        # en el resto del sistema.
        context["ajustes_json"] = [
            {
                "fecha": timezone.localtime(ajuste.fecha).strftime("%d/%m/%Y %H:%M"),
                "producto": ajuste.producto.nombre,
                "tipo": ajuste.tipo,
                "tipo_display": ajuste.get_tipo_display(),
                "cantidad": ajuste.cantidad,
                "motivo": ajuste.motivo,
                "usuario": str(ajuste.usuario),
                "detalle": reverse("ajustes:detalle", args=[ajuste.id_ajuste]),
            }
            for ajuste in context["ajustes"]
        ]

        return context


class AjusteDetailView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    permission_module = "Ajustes"
    permission_action = "CONSULTAR"

    model = Ajuste
    template_name = "ajustes/detalle.html"
    context_object_name = "ajuste"
    pk_url_kwarg = "id_ajuste"

    def get_object(self, queryset=None):
        return AjusteService.obtener(self.kwargs["id_ajuste"])


class AjusteCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    permission_module = "Ajustes"
    permission_action = "CREAR"

    audit_module = "Ajustes"

    model = Ajuste
    form_class = AjusteForm
    template_name = "ajustes/form.html"
    success_url = reverse_lazy("ajustes:listar")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["producto"].queryset = (
            Producto.objects.filter(estado=True).order_by("nombre")
        )
        return form

    def form_valid(self, form):
        try:
            ajuste = AjusteService.registrar(
                producto=form.cleaned_data["producto"],
                usuario=self.request.usuario,
                cantidad=form.cleaned_data["cantidad"],
                tipo=form.cleaned_data["tipo"],
                motivo=form.cleaned_data["motivo"],
                fecha=form.cleaned_data["fecha"],
                observaciones=form.cleaned_data.get("observaciones"),
            )
        except ValidationError as error:
            messages.error(
                self.request,
                "; ".join(error.messages) if hasattr(error, "messages") else str(error),
            )
            return self.form_invalid(form)

        self.object = ajuste

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se registró un ajuste de {ajuste.get_tipo_display()} de "
                f"{ajuste.cantidad} unidad(es) de {ajuste.producto.nombre} "
                f"— motivo: {ajuste.motivo}"
            ),
        )

        messages.success(
            self.request,
            "Ajuste registrado correctamente. El inventario fue actualizado."
        )

        return redirect(self.success_url)


# =====================================================
# PRODUCTOS DISPONIBLES SEGÚN TIPO DE AJUSTE (AJAX)
# =====================================================
#
# El formulario mostraba siempre el mismo catálogo completo de productos
# activos sin importar el tipo de ajuste elegido, aunque AjusteService.
# registrar() ya rechaza una SALIDA sobre un producto sin inventario en la
# sucursal del usuario — la UX dejaba intentar algo que el servidor ya
# sabía que iba a fallar. Este endpoint deja que el formulario refresque
# la lista de productos por AJAX cuando el usuario cambia el tipo,
# aplicando el mismo criterio que ya usa el Service.

def productos_disponibles_ajuste(request):
    # Endpoint AJAX (fetch desde ajustes/form.html): se valida la sesión a
    # mano y se responde 401 en JSON, mismo patrón que buscar_producto_pos
    # / buscar_clientes_pos (no se usa login_required para no romper el
    # fetch con una redirección HTML).
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse({"error": "No autenticado."}, status=401)

    usuario = (
        Usuario.objects
        .filter(id_usuario=usuario_id, estado=True)
        .select_related("id_sucursal")
        .first()
    )
    if not usuario:
        return JsonResponse({"error": "No autenticado."}, status=401)

    tipo = request.GET.get("tipo", "").strip().upper()

    productos = Producto.objects.filter(estado=True)

    if tipo == Ajuste.Tipo.SALIDA:
        if not usuario.id_sucursal:
            productos = productos.none()
        else:
            ids_con_inventario = Inventario.objects.filter(
                id_sucursal=usuario.id_sucursal
            ).values_list("id_producto", flat=True)
            productos = productos.filter(id_producto__in=ids_con_inventario)

    productos = productos.order_by("nombre")

    datos = [
        {"id": producto.id_producto, "nombre": producto.nombre}
        for producto in productos
    ]

    return JsonResponse(datos, safe=False)
