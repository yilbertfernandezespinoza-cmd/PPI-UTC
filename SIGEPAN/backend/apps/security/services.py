import logging
import hashlib
import unicodedata
from .repositories import (
    RolRepository, PermisoRepository, 
    RolPermisoRepository, LogAccionesRepository, UsuarioRepository)
from .models import LogAcciones, RolPermiso, Permiso, Usuario
from apps.configuracion.models import Modulo
from .menu import MENU

from django.urls import reverse
from django.db import transaction
from django.core import signing
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Q
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import (check_password, make_password)

from email.mime.image import MIMEImage
from pathlib import Path


logger = logging.getLogger(__name__)

class UsuarioService:
    """
    Servicio para gestionar la lógica de negocio de usuarios.
    """

    @staticmethod
    def normalizar_texto(texto):
        """
        Convierte un texto a minúsculas y elimina tildes.
        """

        texto = texto.strip().lower()

        texto = unicodedata.normalize(
            "NFKD",
            texto,
        )

        return "".join(
            caracter
            for caracter in texto
            if not unicodedata.combining(caracter)
        )

    @classmethod
    def generar_username(cls, empleado):
        """
        Genera un nombre de usuario único utilizando
        la inicial del nombre y el primer apellido.
        """

        inicial_nombre = cls.normalizar_texto(
            empleado.nombre
        )[0]

        apellido = cls.normalizar_texto(
            empleado.apellido1
        )

        username_base = (
            f"{inicial_nombre}{apellido}"
        )

        username = username_base
        consecutivo = 2

        while Usuario.objects.filter(
            username=username
        ).exists():

            username = (
                f"{username_base}{consecutivo}"
            )

            consecutivo += 1

        return username
    
    @staticmethod
    def cambiar_password(
        request,
        usuario_id,
        password_actual,
        password_nueva,
        password_confirmacion,
    ):
        """
        Cambia la contraseña del usuario
        """

        usuario = UsuarioRepository.obtener_por_id(
            usuario_id
        )

        if not usuario:
            return {
                "success": False,
                "message": "No fue posible encontrar el usuario.",
            }

        if (
            not password_actual
            or not password_nueva
            or not password_confirmacion
        ):
            return {
                "success": False,
                "message": (
                    "Debe completar todos los campos."
                ),
            }

        if password_nueva != password_confirmacion:
            return {
                "success": False,
                "message": (
                    "La nueva contraseña y su confirmación no coinciden."
                ),
            }
        if len(password_nueva) < 8:
            return {
                "success": False,
                "message": (
                    "La contraseña debe tener al menos 8 caracteres."
                ),
            }
        
        if not check_password(
            password_actual,
            usuario.password,
        ):
            return{
                "success": False,
                "message": "La contraseña actual es incorrecta."
            }

        if check_password(
            password_nueva,
            usuario.password,
        ):
            return {
            "success": False,
            "message": (
                "La nueva contraseña debe ser diferente de la actual."
            ),
        }

        usuario.password = make_password(
            password_nueva
        )

        UsuarioRepository.actualizar(
            usuario
        )

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Seguridad",
            tipo_accion="CAMBIAR_PASSWORD",
            descripcion=(
                "El usuario cambió su contraseña desde Mi Perfil."
            ),
        )

        return {
            "success": True,
            "message": "La contraseña se actualizó correctamente.",
        }
    
class RolService:

    @staticmethod
    def listar_roles():
        return RolRepository.listar()

    @staticmethod
    def obtener_rol(id_rol):
        return RolRepository.obtener(id_rol)
    
    @staticmethod
    def actualizar_rol(id_rol, datos):
        """
        Actualiza la información de un rol.
        """

        rol = RolRepository.obtener(id_rol)

        rol.nombre = datos["nombre"]
        rol.descripcion = datos["descripcion"]
        rol.estado = datos["estado"]

        return RolRepository.actualizar(rol)
    
    @staticmethod
    def deshabilitar_rol(id_rol):
        """
        Deshabilita un rol si no tiene usuarios activos asignados.
        """

        rol = RolRepository.obtener(id_rol)

        if rol.usuario_set.filter(estado=True).exists():
            raise ValueError(
                "No se puede deshabilitar el rol porque tiene usuarios activos asignados."
            )

        rol.estado = False

        return RolRepository.actualizar(rol)

class PermisoService:

    @staticmethod
    def listar():
        return PermisoRepository.listar()

    @staticmethod
    def obtener(id_permiso):
        return PermisoRepository.obtener(id_permiso)    
    

def registrar_log(
    request,
    usuario,
    modulo,
    tipo_accion,
    descripcion,
):
    """
    Registra una acción en la bitácora del sistema.
    """
    try:
        modulo_obj =  Modulo.objects.get(nombre=modulo)
    except Modulo.DoesNotExist:
        logger.warning(
            "No se registró la auditoría"
            "El módulo '%s' no existe en la base de datos.",
            modulo
        )

        return
        
    LogAcciones.objects.create(
        id_usuario=usuario,
        id_modulo=modulo_obj,
        tipo_accion=tipo_accion,
        descripcion=descripcion,
        ip_origen=request.META.get("REMOTE_ADDR"),
        navegador=request.META.get("HTTP_USER_AGENT", "")[:150],
    )    

class BitacoraService:

    @staticmethod
    def listar_ingresos():
        """
        Obtiene la bitácora de ingresos al sistema.
        """

        return LogAccionesRepository.listar_ingresos()

    @staticmethod
    def listar_movimientos():
        """
        Obtiene la bitácora de movimientos del sistema.
        """

        return LogAccionesRepository.listar_movimientos()
class RolPermisoService:

    @staticmethod
    @transaction.atomic
    def actualizar_permisos(rol_id, seleccionados,):

        # Elimina los permisos actuales del rol
        RolPermiso.objects.filter(
            id_rol_id=rol_id
        ).delete()

        for valor in seleccionados:
            
            # -------------------------
            # El permiso ya existe
            # -------------------------
            if valor.startswith("P-"):

                permiso_id = int(
                    valor.replace("P-", "")
                )

                RolPermiso.objects.get_or_create(
                    id_rol_id=rol_id,
                    id_permiso_id=permiso_id,
                )

            # -------------------------
            # El permiso no existe
            # -------------------------
            elif valor.startswith("N-"):

                _, modulo_id, accion = valor.split("-")

                modulo = Modulo.objects.get(
                    id_modulo=modulo_id
                )

                permiso, _ = Permiso.objects.get_or_create(
                    id_modulo=modulo,
                    accion=accion,
                    defaults={
                        "descripcion":(
                            f"{accion.title()} en módulo"
                            f"{modulo.nombre}"
                        )
                    }
                )

                RolPermiso.objects.get_or_create(
                    id_rol_id=rol_id,
                    id_permiso=permiso,
                )

class RecuperacionPasswordService:
    """
    Gestiona los tokens temporales para recuperación
    de contraseña.
    """

    SALT = "security.recuperacion_password"
    TIEMPO_EXPIRACION = 1800

    @staticmethod
    def _obtener_firma_password(usuario):
        """
        Genera una firma basada en la contraseña actual.
        """

        return hashlib.sha256(
            usuario.password.encode("utf-8")
        ).hexdigest()

    @classmethod
    def generar_token(cls, usuario):
        """
        Genera un token firmado para el usuario.
        """

        datos = {
            "usuario_id": usuario.id_usuario,
            "password_firma": cls._obtener_firma_password(
                usuario
            ),
        }

        return signing.dumps(
            datos,
            salt=cls.SALT,
            compress=True,
        )

    @classmethod
    def validar_token(cls, token):
        """
        Valida el token y devuelve el usuario asociado.
        """

        try:

            datos = signing.loads(
                token,
                salt=cls.SALT,
                max_age=cls.TIEMPO_EXPIRACION,
            )

            usuario = Usuario.objects.select_related(
                "id_rol"
            ).get(
                id_usuario=datos["usuario_id"],
                estado=True,
                id_rol__estado=True,
            )

            firma_actual = cls._obtener_firma_password(
                usuario
            )

            if firma_actual != datos["password_firma"]:
                return None

            return usuario

        except (
            signing.BadSignature,
            signing.SignatureExpired,
            Usuario.DoesNotExist,
            KeyError,
        ):
            return None

    @classmethod
    def solicitar_recuperacion(
        cls,
        request,
        identificador,
    ):
        """
        Busca un usuario activo y envía el enlace
        de recuperación de contraseña.
        """

        usuario = (
            Usuario.objects
            .select_related(
                "id_rol",
                "id_empleado",
            )
            .filter(
                Q(username__iexact=identificador)
                | Q(
                    id_empleado__correo__iexact=identificador
                ),
                estado=True,
                id_rol__estado=True,
            )
            .first()
        )

        if not usuario:
            return False

        correo = usuario.id_empleado.correo

        if not correo:
            return False

        token = cls.generar_token(usuario)

        url = request.build_absolute_uri(
            reverse(
                "security:restablecer_password",
                kwargs={
                    "token": token,
                },
            )
        )

        contexto = {
            "titulo": "Recuperación de contraseña",
            "nombre": str(usuario.id_empleado),
            "url": url,
            "tiempo_expiracion": 30,
        }

        html = render_to_string(
            "emails/email_recuperar_password.html",
            contexto,
        )

        correo_html = EmailMultiAlternatives(
            subject="Recuperación de contraseña - SIGEPAN",
            body=(
                "Su cliente de correo no soporta "
                "contenido HTML."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[correo],
        )

        correo_html.attach_alternative(
            html,
            "text/html",
        )

        ruta_logo_sigepan = (
            Path(settings.BASE_DIR)
            / "static"
            / "img"
            / "logos"
            / "sigepan-logo.png"
        )

        with open(ruta_logo_sigepan, "rb") as archivo:
            logo_sigepan = MIMEImage(archivo.read())

        logo_sigepan.add_header(
            "Content-ID",
            "<sigepan_logo>",
        )

        logo_sigepan.add_header(
            "Content-Disposition",
            "inline",
            filename="sigepan-logo.png",
        )

        correo_html.attach(logo_sigepan)


        ruta_logo_yc = (
            Path(settings.BASE_DIR)
            / "static"
            / "img"
            / "logos"
            / "Y&C_fondo_transparente.png"
        )

        with open(ruta_logo_yc, "rb") as archivo:
            logo_yc = MIMEImage(archivo.read())

        logo_yc.add_header(
            "Content-ID",
            "<ycsystems_logo>",
        )

        logo_yc.add_header(
            "Content-Disposition",
            "inline",
            filename="Y&C_fondo_transparente.png",
        )

        correo_html.attach(logo_yc)

        correo_html.send()

        registrar_log(
            request=request,
            usuario=usuario,
            modulo="Seguridad",
            tipo_accion="RECUPERAR_PASSWORD",
            descripcion=(
                "El usuario solicitó recuperar su contraseña."
            ),
        )

        return True
    

class MenuService:
    """
    Construye el menu lateral del sistema

    proceso:
    1. obtiene el usuario autenticado
    2. consulta los modulos permitidos
    3. filtra unicamente permisos CONSULTAR
    4. contruye la estructura usando menu.py
    5. devuelve el menu listo para renderizar

    el template sidebar.html unicamente muestra la informacion.

    """
    @staticmethod
    def obtener_menu_usuario(request):
        """
        Construye el menú dinámico según el rol del usuario.
        """

        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            return []

        # Obtener nombres de módulos permitidos
        modulos_permitidos = set(
            Modulo.objects.filter(
                permiso__accion="CONSULTAR",
                permiso__rolpermiso__id_rol__usuario__id_usuario=usuario_id,
                estado=True,
            )
            .distinct()
            .values_list("nombre", flat=True)
        )

        menu = []

        for grupo in MENU:

            nuevo_grupo = {
                "modulo": grupo["modulo"],
                "icono": grupo["icono"],
                "opciones": [],
                "activo": False,
            }

            for opcion in grupo["opciones"]:

                modulo_permiso = opcion.get(
                    "modulo_permiso",
                    grupo["modulo"],
                )

                if modulo_permiso not in modulos_permitidos:
                    continue

                nueva_opcion = opcion.copy()

                nueva_opcion.pop(
                    "modulo_permiso",
                    None,
                )

                url = reverse(opcion["url"])

                nueva_opcion["url"] = url

                nueva_opcion["activa"] = (
                    request.path == url
                )

                if nueva_opcion["activa"]:
                    nuevo_grupo["activo"] = True

                nuevo_grupo["opciones"].append(
                    nueva_opcion
                )

            if nuevo_grupo["opciones"]:
                menu.append(nuevo_grupo)

        return menu    

    @staticmethod
    def obtener_datos_sesion(request):
        """
        Devuelve la información del usuario autenticado para
        ser utilizada en cualquier template del sistema.
        """

        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            return None

        try:

            usuario = (
                Usuario.objects
                .select_related(
                    "id_empleado",
                    "id_rol",
                    "id_sucursal",
                )
                .get(
                    id_usuario=usuario_id,
                    estado=True,
                )
            )

            return {

                "id": usuario.id_usuario,

                "username": usuario.username,

                "nombre_completo": str(
                    usuario.id_empleado
                ),

                "rol": usuario.id_rol.nombre,

                "correo": (
                    usuario.id_empleado.correo
                    if usuario.id_empleado.correo
                    else "No registrado"
                ),

                "telefono": (
                    usuario.id_empleado.telefono
                    if usuario.id_empleado.telefono
                    else "No registrado"
                ),

                "empresa": "La Paná",

                "sucursal": (
                    usuario.id_sucursal.nombre
                    if usuario.id_sucursal
                    else "Sin sucursal"
                ),

            }

        except ObjectDoesNotExist:

            return None    