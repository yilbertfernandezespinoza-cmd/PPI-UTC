from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render


from .forms import RolForm, PermisoForm, UsuarioForm, LoginForm
from .models import Rol, Permiso, Usuario, RolPermiso
from .mixins import SessionRequiredMixin
from .services import registrar_log, RolPermisoService, RolService, BitacoraService
from .audit import AuditMixin
from .permissions import PermissionRequiredMixin
from apps.configuracion.models import Modulo

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
    
    def _guardar_permisos(self, request):

        rol_id = request.POST.get("rol")

        if not rol_id:

            messages.error(
                request,
                "Debe seleccionar un rol."
            )

            return redirect(
                "security:rol_permiso_list"
            )

        seleccionados = request.POST.getlist(
            "permisos"
        )

        RolPermisoService.actualizar_permisos(
            rol_id,
            seleccionados,
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
    
    def _crear_rol(self, request):

        form = RolForm(request.POST)

        if form.is_valid():

            rol = form.save()

            self.registrar_auditoria(
                tipo_accion="CREAR",
                descripcion=f"Se creó el rol {rol.nombre}",
            )

            messages.success(
                request,
                "Rol creado correctamente."
            )

            return redirect(
                f"{reverse_lazy('security:rol_permiso_list')}?rol={rol.id_rol}"
            )

        messages.error(
            request,
            "Verifique la información del formulario."
        )

        return redirect(
            reverse_lazy("security:rol_permiso_list")
        )

    def _editar_rol(self, request):

        rol_id = request.POST.get("rol_id")

        rol = RolService.obtener_rol(rol_id)

        form = RolForm(
            request.POST,
            instance=rol,
        )

        if form.is_valid():

            rol = RolService.actualizar_rol(
                rol_id,
                form.cleaned_data,
            )

            self.registrar_auditoria(
                tipo_accion="MODIFICAR",
                descripcion=f"Se actualizó el rol {rol.nombre}",
            )

            messages.success(
                request,
                "Rol actualizado correctamente."
            )

            return redirect(
                f"{reverse_lazy('security:rol_permiso_list')}?rol={rol.id_rol}"
            )

        messages.error(
            request,
            "Verifique la información del formulario."
        )

        return redirect(
            f"{reverse_lazy('security:rol_permiso_list')}?rol={rol_id}"
        )

    def _eliminar_rol(self, request):

        rol_id = request.POST.get("rol_id")

        rol = RolService.obtener_rol(rol_id)

        nombre_rol = rol.nombre

        try:
    
            RolService.eliminar_rol(rol_id)

        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect(
                f"{reverse_lazy('security:rol_permiso_list')}?rol={rol_id}"
            )

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=f"Se eliminó el rol {nombre_rol}",
        )

        messages.success(
            request,
            "Rol eliminado correctamente."
        )

        return redirect(
            reverse_lazy("security:rol_permiso_list")
        )

    def post(self, request, *args, **kwargs):
        accion = request.POST.get("accion")
        
        if accion == "guardar_permisos":
            return self._guardar_permisos(request)
        
        if accion == "crear_rol":
            return self._crear_rol(request)
           
        if accion == "editar_rol":
            return self._editar_rol(request)
        
        
        if accion == "eliminar_rol":
            return self._eliminar_rol(request)
        
        messages.error(
            request,
            "La acción solicitada no es válida."
        )

        return redirect(
            reverse_lazy("security:rol_permiso_list")
        )
class UsuarioListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"
    
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        usuario = self.request.usuario

        context["puede_crear"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Seguridad",
            id_permiso__accion="CREAR",
        ).exists()

        context["puede_modificar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Seguridad",
            id_permiso__accion="MODIFICAR",
        ).exists()

        return context

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


class UsuarioUpdateView(SessionRequiredMixin, PermissionRequiredMixin, AuditMixin, UpdateView):
    permission_module = "Seguridad"
    permission_action = "MODIFICAR"
    
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


class BitacoraIngresosListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Muestra la bitácora de ingresos al sistema.
    """

    template_name = "security/bitacora_ingresos/list.html"
    context_object_name = "registros"

    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get_queryset(self):
        return BitacoraService.listar_ingresos()
    
class BitacoraMovimientosListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Muestra la bitácora de movimientos del sistema.
    """

    template_name = "security/bitacora_movimientos/list.html"
    context_object_name = "registros"

    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get_queryset(self):
        return BitacoraService.listar_movimientos()    