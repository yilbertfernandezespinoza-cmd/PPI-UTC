from django.contrib import admin
from .models import Rol


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):

    list_display = (
        "id_rol",
        "nombre",
        "estado",
        "fecha_creacion",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

    ordering = (
        "nombre",
    )