from .services import MenuService


def menu_usuario(request):
    """
    Agrega el menú dinámico al contexto de todas las vistas.
    """

    if not request.session.get("usuario_id"):

        return {
            "menu": []
        }

    return {
        "menu": MenuService.obtener_menu_usuario(request)
    }