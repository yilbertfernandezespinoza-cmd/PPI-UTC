from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    View,
)

from apps.security.audit import AuditMixin
from apps.security.mixins import SessionRequiredMixin
from apps.security.models import RolPermiso
from apps.security.permissions import PermissionRequiredMixin

from .forms import ClienteForm
from .models import Cliente
from .services import ClienteService

class ClienteListView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    # Corrección (08-08): estaba en minúscula ("clientes"), inconsistente
    # con el resto del sistema (todos los demás módulos usan mayúscula
    # inicial: "Productos", "Ventas", "Caja", etc.) y con menu.py, que ya
    # usaba "Clientes" — esa diferencia hacía que el ítem del menú
    # desapareciera para cualquier rol, porque el permiso real nunca
    # coincidía con lo que el menú buscaba.
    permission_module = "Clientes"
    permission_action = "CONSULTAR"

    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"

    def get_queryset(self):
        return ClienteService.listar()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Serialización de los registros para el componente Tabulator en el template
        clientes_qs = self.get_queryset()
        clientes_data = []

        for cliente in clientes_qs:
            clientes_data.append({
                "id_cliente": cliente.id_cliente,
                "identificacion": cliente.identificacion,
                "tipo_cliente": getattr(cliente, 'tipo_cliente', ''),
                "nombre_completo": getattr(cliente, 'nombre_completo', ''),
                "telefono": getattr(cliente, 'telefono', ''),
                "correo": getattr(cliente, 'correo', ''),
                "estado": getattr(cliente, 'estado', True),
            })

        context["clientes_json"] = clientes_data

        usuario = self.request.usuario

        context["puede_crear"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="clientes",
            id_permiso__accion="CREAR",
        ).exists()

        context["puede_modificar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="clientes",
            id_permiso__accion="MODIFICAR",
        ).exists()

        context["puede_eliminar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="clientes",
            id_permiso__accion="ELIMINAR",
        ).exists()

        return context
    
class ClienteCreateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    CreateView,
):
    # Corrección (08-08): estaba en minúscula ("clientes"), inconsistente
    # con el resto del sistema (todos los demás módulos usan mayúscula
    # inicial: "Productos", "Ventas", "Caja", etc.) y con menu.py, que ya
    # usaba "Clientes" — esa diferencia hacía que el ítem del menú
    # desapareciera para cualquier rol, porque el permiso real nunca
    # coincidía con lo que el menú buscaba.
    permission_module = "Clientes"
    permission_action = "CREAR"

    audit_module = "clientes"

    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:listar")

    def form_valid(self, form):
        cliente = ClienteService.crear(form.cleaned_data)

        self.object = cliente

        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=(
                f"Se creó el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        messages.success(
            self.request,
            "Cliente creado correctamente."
        )

        return redirect(self.success_url)    
    
class ClienteUpdateView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    UpdateView,
):
    # Corrección (08-08): estaba en minúscula ("clientes"), inconsistente
    # con el resto del sistema (todos los demás módulos usan mayúscula
    # inicial: "Productos", "Ventas", "Caja", etc.) y con menu.py, que ya
    # usaba "Clientes" — esa diferencia hacía que el ítem del menú
    # desapareciera para cualquier rol, porque el permiso real nunca
    # coincidía con lo que el menú buscaba.
    permission_module = "Clientes"
    permission_action = "MODIFICAR"

    audit_module = "clientes"

    model = Cliente
    form_class = ClienteForm
    pk_url_kwarg = "id_cliente"
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:listar")

    def form_valid(self, form):
        cliente = ClienteService.actualizar(
            self.kwargs["id_cliente"],
            form.cleaned_data,
        )

        self.object = cliente

        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=(
                f"Se actualizó el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        messages.success(
            self.request,
            "Cliente actualizado correctamente."
        )

        return redirect(self.success_url)   

class ClienteDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):
    # Corrección (08-08): estaba en minúscula ("clientes"), inconsistente
    # con el resto del sistema (todos los demás módulos usan mayúscula
    # inicial: "Productos", "Ventas", "Caja", etc.) y con menu.py, que ya
    # usaba "Clientes" — esa diferencia hacía que el ítem del menú
    # desapareciera para cualquier rol, porque el permiso real nunca
    # coincidía con lo que el menú buscaba.
    permission_module = "Clientes"
    permission_action = "ELIMINAR"

    audit_module = "clientes"

    def post(self, request, id_cliente):
        cliente = ClienteService.cambiar_estado(
            id_cliente
        )

        accion = (
            "deshabilitó"
            if not cliente.estado
            else "habilitó"
        )

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=(
                f"Se {accion} el cliente "
                f"{cliente.nombre_completo}"
            ),
        )

        mensaje = (
            "Cliente deshabilitado correctamente."
            if not cliente.estado
            else "Cliente habilitado correctamente."
        )

        messages.success(
            request,
            mensaje,
        )

        return redirect(
            "clientes:listar"
        ) 

# =====================================================
# BUSCAR CLIENTES POS
# =====================================================

def buscar_cliente_pos(request):
    """
    Búsqueda rápida de clientes para el POS.
    Permite buscar por nombre, apellidos o identificación.
    """
    # Hallazgo de auditoría de seguridad (04-08-2026): este endpoint no
    # validaba sesión y exponía nombre + identificación (cédula/DIMEX) de
    # cualquier cliente sin autenticarse. No se usa @login_required (que
    # redirige a /security/login/, rompiendo el fetch con HTML en vez de
    # JSON) — se valida la sesión a mano y se responde 401 en JSON, mismo
    # patrón ya usado en ventas.buscar_clientes_pos / productos_disponibles_ajuste.
    if not request.session.get("usuario_id"):
        return JsonResponse(
            {"error": "No autenticado."},
            status=401
        )

    texto = request.GET.get(
        "q",
        ""
    ).strip()

    if len(texto) < 2:
        return JsonResponse(
            [],
            safe=False
        )

    clientes = (
        Cliente.objects
        .filter(
            estado=True
        )
        .filter(
            Q(nombre__icontains=texto)
            |
            Q(apellido1__icontains=texto)
            |
            Q(apellido2__icontains=texto)
            |
            Q(identificacion__icontains=texto)
        )
        .order_by(
            "nombre",
            "apellido1"
        )[:10]
    )

    datos = []

    for cliente in clientes:
        datos.append({
            "id": cliente.id_cliente,
            "nombre": cliente.nombre_completo,
            "identificacion": cliente.identificacion,
        })

    return JsonResponse(
        datos,
        safe=False
    )