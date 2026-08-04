from django import template

from apps.ayuda.repositories import AyudaRepository

register = template.Library()


@register.inclusion_tag("ayuda/partials/boton_contextual.html")
def boton_ayuda(modulo, pantalla):
    ayuda = AyudaRepository.obtener_por_modulo_pantalla(modulo, pantalla)
    return {
        "ayuda": ayuda,
        "modulo_id": modulo.replace(" ", "_"),
        "pantalla_id": pantalla.replace(" ", "_"),
    }