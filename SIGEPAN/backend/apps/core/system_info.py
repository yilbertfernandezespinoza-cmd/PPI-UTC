"""
===============================================================================
INFORMACIÓN GENERAL DEL SISTEMA
===============================================================================

Centraliza la información institucional de SIGEPAN.

Este archivo evita duplicar datos estáticos dentro de las vistas y facilita
actualizar la versión del sistema sin modificar la lógica del proyecto.

===============================================================================
"""

SYSTEM_INFO = {

    "nombre_sistema": "SIGEPAN",

    "descripcion": (
        "Sistema de Gestión Administrativa para Panaderías."
    ),

    "version": "1.0.0",

    "build": "2026.07",

    "empresa": "La Pana",

    "desarrollado_por": "Y&C SYSTEMS",

    "desarrolladores": [

        "Yilbert Fernández Espinoza",

        "César Campos Torres",

    ],

    "tecnologias": [

        "Python",

        "Django",

        "MySQL",

        "Bootstrap 5",

        "AdminLTE 4",

        "HTML5",

        "CSS3",

        "JavaScript",

    ],

    "caracteristicas": [

        "Arquitectura modular",

        "Seguridad basada en roles",

        "Auditoría de movimientos",

        "Menú dinámico",

        "Interfaz responsive",

    ],

    "ultima_actualizacion": "Julio 2026",

    "contacto": {

        "empresa": "Y&C SYSTEMS",

        "correo": "info@ycsystemscr.com",

        "pais": "Costa Rica",

    },

}