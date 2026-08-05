from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone



from .forms import RolForm, PermisoForm, UsuarioForm, LoginForm, RecuperarPasswordForm, RestablecerPasswordForm
from .models import Rol, Permiso, Usuario, RolPermiso
from .mixins import SessionRequiredMixin
from .services import (registrar_log, RolPermisoService, RolService, BitacoraService, RecuperacionPasswordService, UsuarioService, procesar_callback_google)
from .audit import AuditMixin
from .permissions import PermissionRequiredMixin
from apps.configuracion.models import Modulo
from datetime import datetime, timedelta
from apps.empleados.models import Empleado
from apps.security.services import generar_url_google
from .exports import exportar_bitacora_pdf, exportar_bitacora_excel

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
        context["roles"] = (
            RolService
            .listar_roles()
            .order_by("nombre")
        )

        # Rol seleccionado
        rol_id = self.request.GET.get("rol")

        if rol_id:

            context["rol_seleccionado"] = int(rol_id)

        else:

            primer_rol = (
                RolService
                .listar_roles()
                .order_by("nombre")
                .first()
            )

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

    def _deshabilitar_rol(self, request):

        rol_id = request.POST.get("rol_id")

        rol = RolService.obtener_rol(rol_id)

        nombre_rol = rol.nombre

        try:

            RolService.deshabilitar_rol(rol_id)

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
            descripcion=f"Se deshabilitó el rol {nombre_rol}",
        )

        messages.success(
            request,
            "Rol deshabilitado correctamente."
        )

        return redirect(
            f"{reverse_lazy('security:rol_permiso_list')}?rol={rol_id}"
        )

    def post(self, request, *args, **kwargs):

        accion = request.POST.get("accion")

        if accion == "guardar_permisos":

            if not self.usuario_tiene_permiso(
                "Seguridad",
                "MODIFICAR",
            ):
                messages.error(
                    request,
                    "No tiene permisos para modificar permisos."
                )

                return redirect(
                    reverse_lazy("security:rol_permiso_list")
                )

            return self._guardar_permisos(request)

        if accion == "crear_rol":

            if not self.usuario_tiene_permiso(
                "Seguridad",
                "CREAR",
            ):
                messages.error(
                    request,
                    "No tiene permisos para crear roles."
                )

                return redirect(
                    reverse_lazy("security:rol_permiso_list")
                )

            return self._crear_rol(request)

        if accion == "editar_rol":

            if not self.usuario_tiene_permiso(
                "Seguridad",
                "MODIFICAR",
            ):
                messages.error(
                    request,
                    "No tiene permisos para modificar roles."
                )

                return redirect(
                    reverse_lazy("security:rol_permiso_list")
                )

            return self._editar_rol(request)

        if accion == "deshabilitar_rol":

            if not self.usuario_tiene_permiso(
                "Seguridad",
                "ELIMINAR",
            ):
                messages.error(
                    request,
                    "No tiene permisos para deshabilitar roles."
                )

                return redirect(
                reverse_lazy("security:rol_permiso_list")
                )

            return self._deshabilitar_rol(request)

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

        queryset = (
            Usuario.objects
            .select_related(
                "id_empleado",
                "id_rol",
                "id_sucursal",
            )
            .order_by("username")
        )

        busqueda = self.request.GET.get(
            "buscar",
            "",
        ).strip()

        if busqueda:

            queryset = queryset.filter(
                Q(username__icontains=busqueda)
                | Q(id_empleado__correo__icontains=busqueda)
                | Q(id_empleado__nombre__icontains=busqueda)
                | Q(id_empleado__apellido1__icontains=busqueda)
            )

        return queryset
    
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

        context["busqueda"] = self.request.GET.get(
            "buscar",
            "",
        )
        context["puede_eliminar"] = RolPermiso.objects.filter(
            id_rol=usuario.id_rol,
            id_permiso__id_modulo__nombre="Seguridad",
            id_permiso__accion="ELIMINAR",
        ).exists()

        return context

class UsuarioEmpleadoDatosView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    """
    Devuelve el correo del empleado y el nombre
    de usuario disponible para crear su cuenta.
    """

    permission_module = "Seguridad"
    permission_action = "CREAR"

    def get(self, request, id_empleado):

        try:

            empleado = Empleado.objects.get(
                id_empleado=id_empleado,
                estado=True,
            )

        except Empleado.DoesNotExist:

            return JsonResponse(
                {
                    "error": (
                        "El empleado no existe "
                        "o está inactivo."
                    )
                },
                status=404,
            )

        if not empleado.correo:

            return JsonResponse(
                {
                    "error": (
                        "El empleado no tiene un "
                        "correo registrado."
                    )
                },
                status=400,
            )

        if Usuario.objects.filter(
            id_empleado=empleado
        ).exists():

            return JsonResponse(
                {
                    "error": (
                        "El empleado ya tiene una "
                        "cuenta de usuario asignada."
                    )
                },
                status=400,
            )

        username = UsuarioService.generar_username(
            empleado
        )

        return JsonResponse(
            {
                "correo": empleado.correo,
                "username": username,
            }
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
    

class UsuarioDisableView(
    SessionRequiredMixin,
    PermissionRequiredMixin,
    AuditMixin,
    View,
):
    permission_module = "Seguridad"
    permission_action = "ELIMINAR"

    audit_module = "Seguridad"

    def post(self, request, id_usuario):

        usuario = Usuario.objects.get(
            id_usuario=id_usuario
        )

        if usuario.id_usuario == request.usuario.id_usuario:

            messages.error(
                request,
                "No puede deshabilitar su propio usuario."
            )

            return redirect(
                "security:usuario_list"
            )

        usuario.estado = False
        usuario.save(
            update_fields=["estado"]
        )

        self.registrar_auditoria(
            tipo_accion="ELIMINAR",
            descripcion=(
                f"Se deshabilitó el usuario "
                f"{usuario.username}"
            ),
        )

        messages.success(
            request,
            "Usuario deshabilitado correctamente."
        )

        return redirect(
            "security:usuario_list"
        )    

def recuperar_password_view(request):
    """
    Permite solicitar la recuperación de contraseña.
    """

    if request.method == "POST":

        form = RecuperarPasswordForm(request.POST)

        if form.is_valid():

            identificador = form.cleaned_data[
                "identificador"
            ]

            RecuperacionPasswordService.solicitar_recuperacion(
                request=request,
                identificador=identificador,
            )

            messages.success(
                request,
                (
                    "Si la cuenta existe y tiene un correo "
                    "registrado, recibirá las instrucciones "
                    "para recuperar su contraseña."
                ),
            )

            return redirect(
                "security:login"
            )

    else:

        form = RecuperarPasswordForm()

    return render(
        request,
        "security/login/recuperar_password.html",
        {
            "form": form,
        },
    )


def restablecer_password_view(request, token):
    """
    Permite establecer una nueva contraseña mediante
    un token temporal válido.
    """

    usuario = (
        RecuperacionPasswordService
        .validar_token(token)
    )

    if not usuario:

        messages.error(
            request,
            (
                "El enlace de recuperación no es válido "
                "o ha expirado."
            ),
        )

        return redirect(
            "security:login"
        )

    if request.method == "POST":

        form = RestablecerPasswordForm(
            request.POST
        )

        if form.is_valid():

            usuario.password = make_password(
                form.cleaned_data["password"]
            )

            usuario.save(
                update_fields=[
                    "password",
                ]
            )

            registrar_log(
                request=request,
                usuario=usuario,
                modulo="Seguridad",
                tipo_accion="CAMBIAR_PASSWORD",
                descripcion=(
                    "El usuario restableció su contraseña "
                    "correctamente."
                ),
            )

            messages.success(
                request,
                (
                    "La contraseña fue actualizada "
                    "correctamente."
                ),
            )

            return redirect(
                "security:login"
            )

    else:

        form = RestablecerPasswordForm()

    return render(
        request,
        "security/login/restablecer_password.html",
        {
            "form": form,
        },
    )

def login_view(request):

    if request.session.get("usuario_id"):
    
        return redirect("dashboard:inicio")
    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            try:

                usuario = Usuario.objects.get(
                    username=username,
                    estado=True,
                    id_rol__estado=True,
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

                    return redirect("dashboard:inicio")

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

def cambiar_usuario_view(request):

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
            descripcion=f"Cambio de usuario: {usuario.username} cerró sesión para permitir el ingreso de otro usuario.",
        )

    request.session.pop("usuario_id", None)
    request.session.pop("username", None)
    request.session.pop("empleado", None)
    request.session.pop("rol", None)
    request.session.pop("sucursal", None)

    messages.info(
        request,
        "Sesión cerrada. Ingrese con otro usuario."
    )

    return redirect("security:login")

class BitacoraIngresosListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "security/bitacora_ingresos/list.html"
    context_object_name = "registros"
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get_queryset(self):
        return BitacoraService.filtrar_ingresos(
            usuario=self.request.GET.get("usuario", ""),
            fecha_inicio=self.request.GET.get("fecha_inicio", ""),
            fecha_fin=self.request.GET.get("fecha_fin", ""),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.request.GET.get("usuario", "")
        context["fecha_inicio"] = self.request.GET.get("fecha_inicio", "")
        context["fecha_fin"] = self.request.GET.get("fecha_fin", "")
        return context


class BitacoraMovimientosListView(SessionRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "security/bitacora_movimientos/list.html"
    context_object_name = "registros"
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get_queryset(self):
        return BitacoraService.filtrar_movimientos(
            usuario=self.request.GET.get("usuario", ""),
            fecha_inicio=self.request.GET.get("fecha_inicio", ""),
            fecha_fin=self.request.GET.get("fecha_fin", ""),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.request.GET.get("usuario", "")
        context["fecha_inicio"] = self.request.GET.get("fecha_inicio", "")
        context["fecha_fin"] = self.request.GET.get("fecha_fin", "")
        return context

class BitacoraIngresosExportPdfView(SessionRequiredMixin, PermissionRequiredMixin, View):
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get(self, request):
        queryset = BitacoraService.filtrar_ingresos(
            usuario=request.GET.get("usuario", ""),
            fecha_inicio=request.GET.get("fecha_inicio", ""),
            fecha_fin=request.GET.get("fecha_fin", ""),
        )
        registrar_log(request, request.usuario, "Seguridad", "EXPORTAR", "Exportó bitácora de ingresos a PDF")
        return exportar_bitacora_pdf(queryset, "Bitácora de Ingresos", "bitacora_ingresos")


class BitacoraIngresosExportExcelView(SessionRequiredMixin, PermissionRequiredMixin, View):
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get(self, request):
        queryset = BitacoraService.filtrar_ingresos(
            usuario=request.GET.get("usuario", ""),
            fecha_inicio=request.GET.get("fecha_inicio", ""),
            fecha_fin=request.GET.get("fecha_fin", ""),
        )
        registrar_log(request, request.usuario, "Seguridad", "EXPORTAR", "Exportó bitácora de ingresos a Excel")
        return exportar_bitacora_excel(queryset, "Bitácora de Ingresos", "bitacora_ingresos")


class BitacoraMovimientosExportPdfView(SessionRequiredMixin, PermissionRequiredMixin, View):
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get(self, request):
        queryset = BitacoraService.filtrar_movimientos(
            usuario=request.GET.get("usuario", ""),
            fecha_inicio=request.GET.get("fecha_inicio", ""),
            fecha_fin=request.GET.get("fecha_fin", ""),
        )
        registrar_log(request, request.usuario, "Seguridad", "EXPORTAR", "Exportó bitácora de movimientos a PDF")
        return exportar_bitacora_pdf(queryset, "Bitácora de Movimientos", "bitacora_movimientos")


class BitacoraMovimientosExportExcelView(SessionRequiredMixin, PermissionRequiredMixin, View):
    permission_module = "Seguridad"
    permission_action = "CONSULTAR"

    def get(self, request):
        queryset = BitacoraService.filtrar_movimientos(
            usuario=request.GET.get("usuario", ""),
            fecha_inicio=request.GET.get("fecha_inicio", ""),
            fecha_fin=request.GET.get("fecha_fin", ""),
        )
        registrar_log(request, request.usuario, "Seguridad", "EXPORTAR", "Exportó bitácora de movimientos a Excel")
        return exportar_bitacora_excel(queryset, "Bitácora de Movimientos", "bitacora_movimientos")

class PerfilView(TemplateView):
    template_name = "security/perfil/perfil.html"    

    def post(self, request, *args, **kwargs):

        resultado = UsuarioService.cambiar_password(
            request=request,
            usuario_id=request.session.get("usuario_id"),
            password_actual=request.POST.get("password_actual"),
            password_nueva=request.POST.get("password_nueva"),
            password_confirmacion=request.POST.get("password_confirmacion"),
        )
        print(resultado)
        if resultado["success"]:
            messages.success(request, resultado["message"])
        else:
            messages.error(request, resultado["message"])

        return redirect("security:perfil")
    

def google_vincular(request):

    if not request.session.get("usuario_id"):

        messages.error(
            request,
            "Debe iniciar sesión."
        )

        return redirect("security:login")

    """
    Redirige al usuario hacia Google para iniciar
    el proceso de vinculación.
    """

    try:
        authorization_url, state, code_verifier = generar_url_google()

        request.session["google_state"] = state
        request.session["google_code_verifier"] = code_verifier

        return redirect(authorization_url)

    except Exception as e:

        messages.error(
            request,
            f"No fue posible iniciar la vinculación con Google. {e}"
        )

        return redirect("security:perfil")    
    
def google_callback(request):

    if not request.session.get("usuario_id"):

        messages.error(
            request,
            "Debe iniciar sesión."
        )

        return redirect("security:login")

    try:

        datos_google = procesar_callback_google(request)

        usuario = Usuario.objects.get(
            id_usuario=request.session["usuario_id"]
        )

        usuario.google_id = datos_google["google_id"]
        usuario.google_email = datos_google["google_email"]
        usuario.google_token = datos_google["token"]

        if datos_google.get("refresh_token"):
            usuario.google_refresh_token = datos_google["refresh_token"]

        usuario.save(
            update_fields=[
                "google_id",
                "google_email",
                "google_token",
                "google_refresh_token"
            ]
        )

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Seguridad",
            tipo_accion="MODIFICAR",
            descripcion="El usuario vinculó su cuenta de Google.",
        )

        messages.success(
            request,
            "Cuenta de Google vinculada correctamente."
        )

    except Exception as e:

        messages.error(
            request,
            f"No fue posible vincular la cuenta de Google. {e}"
        )

    return redirect("security:perfil")

def google_desvincular(request):

    if not request.session.get("usuario_id"):

        messages.error(
            request,
            "Debe iniciar sesión."
        )

        return redirect("security:login")

    try:

        usuario = Usuario.objects.get(
            id_usuario=request.session["usuario_id"]
        )

        usuario.google_email = None
        usuario.google_id = None
        usuario.google_token = None
        usuario.google_refresh_token = None

        usuario.save(
            update_fields=[
                "google_email",
                "google_id",
                "google_token",
                "google_refresh_token",
            ]
        )

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Seguridad",
            tipo_accion="MODIFICAR",
            descripcion="El usuario desvinculó su cuenta de Google.",
        )

        messages.success(
            request,
            "Cuenta de Google desvinculada correctamente."
        )

    except Exception as e:

        messages.error(
            request,
            f"No fue posible desvincular la cuenta de Google. {e}"
        )

    return redirect("security:perfil")