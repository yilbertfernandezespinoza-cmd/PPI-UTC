import logging
import hashlib
import unicodedata
from .repositories import (
    RolRepository, PermisoRepository, 
    RolPermisoRepository, LogAccionesRepository)
from .models import LogAcciones, RolPermiso, Permiso, Usuario
from apps.configuracion.models import Modulo
from .menu import MENU
from django.urls import reverse
from django.db import transaction
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse


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

        send_mail(
            subject=(
                "Recuperación de contraseña - SIGEPAN"
            ),
            message=(
                f"Hola {usuario.username},\n\n"
                "Se solicitó restablecer su contraseña "
                "de SIGEPAN.\n\n"
                f"Utilice el siguiente enlace:\n{url}\n\n"
                "El enlace tiene una vigencia "
                "de 30 minutos.\n\n"
                "Si usted no solicitó este cambio, "
                "ignore este mensaje."
            ),
            from_email=None,
            recipient_list=[
                correo,
            ],
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

            if grupo["modulo"] in modulos_permitidos:

                nuevo_grupo = {

                    "modulo": grupo["modulo"],

                    "icono": grupo["icono"],

                    "opciones": [],

                    "activo": False,

                }

                for opcion in grupo["opciones"]:

                    nueva_opcion = opcion.copy()

                    url = reverse(opcion["url"])

                    nueva_opcion["url"] = url

                    # ¿La página actual corresponde a esta opción?
                    nueva_opcion["activa"] = (
                        request.path == url
                    )

                    # Si una opción está activa,
                    # el grupo también debe estar activo.
                    if nueva_opcion["activa"]:

                        nuevo_grupo["activo"] = True

                    nuevo_grupo["opciones"].append(
                        nueva_opcion
                    )

                menu.append(nuevo_grupo)
        return menu          