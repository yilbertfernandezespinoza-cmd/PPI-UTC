from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render


from .forms import RolForm, PermisoForm, UsuarioForm, LoginForm
from .models import Rol, Permiso, Usuario
from .mixins import SessionRequiredMixin


class RolListView(SessionRequiredMixin, ListView):
    model = Rol
    template_name = "security/roles/list.html"
    context_object_name = "roles"


class RolCreateView(SessionRequiredMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol creado correctamente.")
        return super().form_valid(form)


class RolUpdateView(SessionRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    pk_url_kwarg = "id_rol"
    template_name = "security/roles/form.html"
    success_url = reverse_lazy("security:rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol actualizado correctamente.")
        return super().form_valid(form)
    
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


class PermisoCreateView(SessionRequiredMixin, CreateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")

    def form_valid(self, form):
        messages.success(self.request, "Permiso creado correctamente.")
        return super().form_valid(form)


class PermisoUpdateView(SessionRequiredMixin, UpdateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "security/permisos/form.html"
    success_url = reverse_lazy("security:permiso_list")
    pk_url_kwarg = "id_permiso"

    def form_valid(self, form):
        messages.success(self.request, "Permiso actualizado correctamente.")
        return super().form_valid(form)    
    
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

class UsuarioCreateView(SessionRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = "security/usuarios/form.html"
    success_url = reverse_lazy("security:usuario_list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)


class UsuarioUpdateView(SessionRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = "security/usuarios/form.html"
    success_url = reverse_lazy("security:usuario_list")
    pk_url_kwarg = "id_usuario"

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)    
    
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