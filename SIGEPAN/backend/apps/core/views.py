from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .system_info import SYSTEM_INFO

@never_cache
def home(request):
    """
    Vista principal de SIGEPAN.

    Requiere una sesión activa del sistema.
    y evita mostrar contenido almacenado en caché.
    """
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("security:login")
    
    return render(request, "core/home.html")

@never_cache
def acerca_de(request):
    """
    Muestra la información general del sistema SIGEPAN.
    """

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("security:login")

    return render(
        request,
        "core/acerca_de.html",
        SYSTEM_INFO,
    )