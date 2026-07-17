from .services import MenuService
from apps.core.system_info import SYSTEM_INFO

def menu_usuario(request):
    """
    Agrega el menú dinámico al contexto de todas las vistas.
    """

    if not request.session.get("usuario_id"):

        return {
            "menu": []
        }

    return {
        "menu": MenuService.obtener_menu_usuario(request),

        "system_info": SYSTEM_INFO
    }