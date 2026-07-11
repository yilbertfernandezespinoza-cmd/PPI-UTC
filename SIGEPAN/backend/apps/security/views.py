from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render


from .forms import RolForm, PermisoForm, UsuarioForm, LoginForm
from .models import Rol, Permiso, Usuario, RolPermiso
from .mixins import SessionRequiredMixin
from .services import registrar_log, RolPermisoService
from .audit import AuditMixin
from .permissions import PermissionRequiredMixin
from apps.configuracion.models import Modulo

class RolListView(SessionRequiredMixin, ListView):
    model = Rol
    template_name = "security/roles/list.html"
    context_object_name = "roles"


class RolCreateView(SessionRequiredMixin, AuditMixin, CreateView):
    audit_module = "Seguridad"
    model = Rol
    form_class = RolForm
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el rol {self.object.nombre}",
        )
        messages.success(self.request, "Rol creado correctamente.")
        return response


class RolUpdateView(SessionRequiredMixin, AuditMixin, UpdateView):
    audit_module = "Seguridad"
    model = Rol
    form_class = RolForm
    pk_url_kwarg = "id_rol"
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el rol {self.object.nombre}",
        )
        messages.success(self.request, "Rol actualizado correctamente.")
        return response
    
class PermisoListView(SessionRequiredMixin, ListView):
    model = Permiso
    template_name = "security/permisos/list.html"
    context_object_name = "permisos"

    def get_queryset(self):
        return (
            Permiso.objects
            .select_related("id_modulo")
            .order_by("id_modulo__nombre", "accion")
        )


class PermisoCreateView(SessionRequiredMixin, AuditMixin, CreateView):
    audit_module = "Seguridad"
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="CREAR",
            descripcion=f"Se creó el permiso {self.object.accion}",
        )
        messages.success(self.request, "Permiso creado correctamente.")
        return response


class PermisoUpdateView(SessionRequiredMixin,  AuditMixin, UpdateView):
    audit_module = "Seguridad"
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")
    pk_url_kwarg = "id_permiso"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=f"Se actualizó el permiso {self.object.accion}",
        )
        messages.success(self.request, "Permiso actualizado correctamente.")
        return response
class RolPermisoListView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, ListView):
    model = RolPermiso
    template_name = "security/rol_permisos/asignar.html"
    context_object_name = "modulos"

    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    audit_module = "Seguridad"

    def get_queryset(self):
        """
        Devuelve todos los módulos activos para construir la matriz de permisos.
        """
        return Modulo.objects.filter(
            estado = True            
        ).order_by("nombre")
    
    def get_context_data(self, **kwargs):
        print(">>> Entró a get_context_data")
        context = super().get_context_data(**kwargs)

        # Todos los roles
        context["roles"] = Rol.objects.filter(
            estado=True
        ).order_by("nombre")

        # Rol seleccionado
        rol_id = self.request.GET.get("rol")

        if rol_id:

            context["rol_seleccionado"] = int(rol_id)

        else:

            primer_rol = Rol.objects.filter(
                estado=True
            ).order_by("nombre").first()

            context["rol_seleccionado"] = (
                primer_rol.id_rol if primer_rol else None
            )
            # Permisos asignados al rol seleccionado
        permisos_asignados = []

        if context["rol_seleccionado"]:

            permisos_asignados = set(
                RolPermiso.objects.filter(
                    id_rol=context["rol_seleccionado"]
                ).values_list(
                    "id_permiso_id",
                    flat=True,
                )
            )

        context["permisos_asignados"] = permisos_asignados

        matriz_permisos = []

        acciones = [
            "CONSULTAR",
            "CREAR",
            "MODIFICAR",
            "ELIMINAR",
        ]

        for modulo in context["modulos"]:

            fila = {
                "modulo": modulo,
                "permisos": []
            }

            for accion in acciones:

                permiso = Permiso.objects.filter(
                    id_modulo=modulo,
                    accion=accion,
                ).first()

                if permiso:

                    valor = f"P-{permiso.id_permiso}"

                else:

                    valor = f"N-{modulo.id_modulo}-{accion}"
                
                fila["permisos"].append({

                    "accion": accion,

                    "valor": valor,

                    "marcado": (
                        permiso.id_permiso in permisos_asignados
                        if permiso
                        else False
                    )

                })

            matriz_permisos.append(fila)

        context["matriz_permisos"] = matriz_permisos

        context["rol_form"] = RolForm()
        
        return context
    
    def post(self, request, *args, **kwargs):

        rol_id = request.POST.get("rol")

        if not rol_id:

            messages.error(
                request,
                "Debe seleccionar un rol."
            )

            return redirect("security:rol_permiso_list")

        seleccionados = request.POST.getlist("permisos")

        RolPermisoService.actualizar_permisos(
            rol_id, seleccionados,
        )

        rol = Rol.objects.get(
            id_rol=rol_id
        )

        self.registrar_auditoria(
            tipo_accion="MODIFICAR",
            descripcion=(
                f"Se actualizaron los permisos "
                f"del rol {rol.nombre}"
            ),
        )

        messages.success(
            request,
            "Permisos actualizados correctamente."
        )

        return redirect(
            f"{reverse_lazy('security:rol_permiso_list')}?rol={rol_id}"
        )


class UsuarioListView(SessionRequiredMixin, ListView):
    model = Usuario
    template_name = "security/usuarios/list.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return (
            Usuario.objects
            .select_related(
                "id_empleado",
                "id_rol",
                "id_sucursal"
            )
            .order_by("username")
        )

class UsuarioCreateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, CreateView):
    permission_module = "Seguridad"
    permission_action = "CREAR"
    audit_module = "Seguridad"
    model = Usuario
    form_class = UsuarioForm
    template_name = "security/usuarios/form.html"
    success_url = reverse_lazy("security:usuario_list")
    

    def form_valid(self, form):
        response = super().form_valid(form)
        self.registrar_auditoria(
            tipo_accion= "CREAR",
            descripcion = f"se creo el usuario {self.object.username}",
        )
        messages.success(self.request, "Usuario creado correctamente.")
        return response


class UsuarioUpdateView(SessionRequiredMixin, AuditMixin, UpdateView):
    audit_module = "Seguridad"
    model = Usuario
    form_class = UsuarioForm
    template_name = "security/usuarios/form.html"
    success_url = reverse_lazy("security:usuario_list")
    pk_url_kwarg = "id_usuario"

    def form_valid(self, form):
        response = super().form_valid(form)

        self.registrar_auditoria(
            tipo_accion= "MODIFICAR",
            descripcion = f"se modificó el usuario {self.object.username}",
        )
        messages.success(self.request, "Usuario actualizado correctamente.")
        return response   
    
def login_view(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            try:

                usuario = Usuario.objects.get(
                    username=username,
                    estado=True,
                )

                if check_password(password, usuario.password):

                    request.session["usuario_id"] = usuario.id_usuario
                    request.session["username"] = usuario.username
                    request.session["empleado"] = str(usuario.id_empleado)
                    request.session["rol"] = usuario.id_rol.nombre

                    registrar_log(
                        request=request,
                        usuario=usuario,
                        modulo="Seguridad",
                        tipo_accion="LOGIN",
                        descripcion=f"Inicio de sesión del usuario {usuario.username}",
                    )
                    messages.success(
                        request,
                        f"Bienvenido {usuario.id_empleado}"
                    )

                    return redirect("/")

                else:

                    messages.error(
                        request,
                        "La contraseña es incorrecta."
                    )

            except Usuario.DoesNotExist:

                messages.error(
                    request,
                    "El usuario no existe o está inactivo."
                )

    else:

        form = LoginForm()

    return render(
        request,
        "security/login/login.html",
        {
            "form": form
        },
    )    

def logout_view(request):
    
    usuario_id = request.session.get("usuario_id")
    usuario = None

    if usuario_id:
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)

        except Usuario.DoesNotExist:
            pass
    if usuario:

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Seguridad",
            tipo_accion="LOGOUT",
            descripcion=f"Cierre de sesión del usuario {usuario.username}",
        )        

    request.session.pop("usuario_id", None)
    request.session.pop("username", None)
    request.session.pop("empleado", None)
    request.session.pop("rol", None)
    request.session.pop("sucursal", None)

    messages.success(
        request,
        "Sesión finalizada correctamente."
    )

    return redirect("security:login")