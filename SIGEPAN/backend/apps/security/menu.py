"""

===============================================================================
MENU PRINCIPAL DEL SISTEMA
===============================================================================

Este archivo define la estructura de navegación de SIGEPAN.

Responsabilidades:
- Organizar los módulos.
- Definir el orden de navegación.
- Definir iconos.
- Definir las vistas disponibles.

NO realiza validaciones de permisos.

Los permisos son evaluados por MenuService.

===============================================================================
"""


MENU = [

    {
        "modulo": "Configuración",
        "icono": "bi-gear",
        "opciones": [

            {
                "titulo": "Sucursales",
                "url": "configuracion:sucursal_list",
                "icono": "bi-building",
            },
            {
                "titulo": "Módulos",
                "url": "configuracion:modulo_list",
                "icono": "bi-grid",
            },

        ]
    },

    {
        "modulo": "Seguridad",
        "icono": "bi-shield-lock",
        "opciones": [

            {
                "titulo": "Usuarios",
                "url": "security:usuario_list",
                "icono": "bi-people",
            },
            {
                "titulo": "Asignación de Permisos",
                "url": "security:rol_permiso_list",
                "icono": "bi-person-check",
            },

        ]
    },

]