from django.http import HttpResponse
from django.test import SimpleTestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.views import View

from apps.security.mixins import SessionRequiredMixin
from types import SimpleNamespace
from unittest.mock import patch
from apps.security.models import Usuario
from apps.security.permissions import PermissionRequiredMixin
from django.contrib.messages.middleware import MessageMiddleware

class SecurityBaseTestCase(SimpleTestCase):
    """
    Clase base para pruebas del módulo de Seguridad.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def agregar_sesion(self, request):
        """
        Agrega soporte de sesión y mensajes
        al request de prueba.
        """

        session_middleware = SessionMiddleware(
            lambda request: None
        )

        session_middleware.process_request(request)

        message_middleware = MessageMiddleware(
            lambda request: None
        )

        message_middleware.process_request(request)

        return request


class VistaProtegidaPrueba(
    SessionRequiredMixin,
    View,
):
    """
    Vista utilizada únicamente para probar
    el control de sesión.
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse("Acceso permitido")

class VistaConPermisoPrueba(
    PermissionRequiredMixin,
    View,
):
    """
    Vista utilizada únicamente para probar
    el control de permisos.
    """

    permission_module = "Seguridad"
    permission_action = "CREAR"

    def get(self, request, *args, **kwargs):
        return HttpResponse("Permiso concedido")
    
class SessionRequiredMixinTest(SecurityBaseTestCase):
    """
    Pruebas para la validación de sesión.
    """

    def test_usuario_sin_sesion_es_redirigido_al_login(self):

        request = self.factory.get("/protegida/")

        request = self.agregar_sesion(request)

        response = VistaProtegidaPrueba.as_view()(
            request
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            "/security/login/",
        )

    def test_usuario_con_sesion_valida_puede_acceder(self):

        request = self.factory.get("/protegida/")

        request = self.agregar_sesion(request)

        request.session["usuario_id"] = 1

        empleado = SimpleNamespace(
            nombre="Empleado Prueba"
        )

        rol = SimpleNamespace(
            nombre="Administrador"
        )

        sucursal = SimpleNamespace(
            nombre="Principal"
        )

        usuario = SimpleNamespace(
            id_usuario=1,
            username="admin",
            id_empleado=empleado,
            id_rol=rol,
            id_sucursal=sucursal,
        )

        with patch(
            "apps.security.mixins.Usuario.objects.select_related"
        ) as select_related_mock:

            select_related_mock.return_value.get.return_value = (
                usuario
            )

            response = VistaProtegidaPrueba.as_view()(
                request
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.content,
            b"Acceso permitido",
        )

        self.assertEqual(
            request.usuario,
            usuario,
        )

        self.assertEqual(
            request.empleado,
            empleado,
        )

        self.assertEqual(
            request.rol,
            rol,
        )

        self.assertEqual(
            request.sucursal,
            sucursal,
        )

    def test_usuario_inexistente_o_inactivo_limpia_sesion(self):

        request = self.factory.get("/protegida/")

        request = self.agregar_sesion(request)

        request.session["usuario_id"] = 999

        with patch(
            "apps.security.mixins.Usuario.objects.select_related"
        ) as select_related_mock:

            select_related_mock.return_value.get.side_effect = (
                Usuario.DoesNotExist
            )

            response = VistaProtegidaPrueba.as_view()(
                request
            )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
           response.url,
            "/security/login/",
        )

        self.assertIsNone(
            request.session.get("usuario_id")
        )    

class PermissionRequiredMixinTest(SecurityBaseTestCase):
    """
    Pruebas para la validación de permisos.
    """

    def test_usuario_sin_permiso_es_redirigido(self):

        request = self.factory.get("/protegida/")

        request = self.agregar_sesion(request)

        request.usuario = SimpleNamespace(
            id_rol=SimpleNamespace(
                id_rol=2
            )
        )

        with patch(
            "apps.security.permissions."
            "RolPermiso.objects.filter"
        ) as filter_mock, patch(
            "apps.security.permissions."
            "registrar_log"
        ) as registrar_log_mock:

            filter_mock.return_value.exists.return_value = False

            response = VistaConPermisoPrueba.as_view()(
                request
            )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            "/",
        )

        registrar_log_mock.assert_called_once()

        argumentos = registrar_log_mock.call_args.kwargs

        self.assertEqual(
            argumentos["tipo_accion"],
            "ACCESO_DENEGADO",
        )

        self.assertEqual(
            argumentos["modulo"],
            "Seguridad",
        )

        self.assertEqual(
            argumentos["descripcion"],
            "Intento de ejecutar CREAR sin autorización.",
        )

    def test_usuario_con_permiso_puede_acceder(self):

        request = self.factory.get("/protegida/")

        request = self.agregar_sesion(request)

        request.usuario = SimpleNamespace(
            id_rol=SimpleNamespace(
                id_rol=1
            )
        )

        with patch(
            "apps.security.permissions."
            "RolPermiso.objects.filter"
        ) as filter_mock:

            filter_mock.return_value.exists.return_value = True

            response = VistaConPermisoPrueba.as_view()(
                request
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.content,
            b"Permiso concedido",
        )    

