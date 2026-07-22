from .services import MenuService
from apps.core.system_info import SYSTEM_INFO

def menu_usuario(request):
    """
    Agrega el menú dinámico al contexto de todas las vistas.
    """

    if not request.session.get("usuario_id"):

        return {
            "menu": [],
            "usuario_sesion": None,
            "system_info": SYSTEM_INFO,
        }

    return {
        "menu": MenuService.obtener_menu_usuario(request),

        "usuario_sesion": (
            MenuService.obtener_datos_sesion(request)
        ),

        "system_info": SYSTEM_INFO
    }