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
                "titulo": "Configuración Tributaria",
                "url": "configuracion:tributaria_list",
                "icono": "bi-percent",
            },
            {
                "titulo": "Cargos",
                "url": "empleados:cargo_list",
                "icono": "bi-briefcase",
            },
            {
                "titulo": "Empleados",
                "url": "empleados:empleado_list",
                "icono": "bi-person-badge",
            },
            {
                "titulo": "Ayudas",
                "url": "ayuda:list",
                "icono": "bi-question-circle",
            },
        ]
    },


    {
        "modulo": "Catálogos",
        "icono": "bi-boxes",
        "opciones": [
            {
                "modulo_permiso": "Categorías",
                "titulo": "Categorías",
                "url": "categorias:lista_categorias",
                "icono": "bi-tags",
            },
            {
                "modulo_permiso": "Productos",
                "titulo": "Productos",
                "url": "productos:lista_productos",
                "icono": "bi-box",

                "dashboard":True,
                "color":"warning",
            },
            {
                "modulo_permiso": "Clientes",
                "titulo": "Clientes",
                "url": "clientes:listar",
                "icono": "bi-people",

                "dashboard":True,
                "color":"primary",
            },
        ]
    },

    {
        "modulo": "Operaciones",
        "icono": "bi-cart-check",
        "opciones": [

            {
                "modulo_permiso": "Proveedores",
                "titulo": "Proveedores",
                "url": "proveedores:lista_proveedores",
                "icono": "bi-truck",

                 "dashboard": True,
                "color": "secondary",
            },

            {
                "modulo_permiso": "Inventario",
                "titulo": "Inventario",
                "url": "inventario:lista_inventario",
                "icono": "bi-box-seam",

                "dashboard": True,
                "color": "danger",
            },

            {
                "modulo_permiso": "Compras",
                "titulo": "Compras",
                "url": "compras:lista_compras",
                "icono": "bi-cart-plus",

                "dashboard": True,
                "color": "info",
            },

            {
                "modulo_permiso": "Ventas",
                "titulo": "Ventas",
                "url": "ventas:lista_ventas",
                "icono": "bi-cash-stack",

                "dashboard": True,
                "color": "success",
            },

            {
                "modulo_permiso": "Caja",
                "titulo": "Caja",
                "url": "caja:lista_cajas",
                "icono": "bi-safe2",

                "dashboard": True,
                "color": "dark",
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
            {
                "titulo": "Bitácora de Ingresos",
                "url": "security:bitacora_ingresos",
                "icono": "bi-box-arrow-in-right",
            },
            {
                "titulo": "Bitácora de Movimientos",
                "url": "security:bitacora_movimientos",
                "icono": "bi-journal-text",
            },

            {
                "titulo": "Acerca de SIGEPAN",
                "url":"acerca_de",
                "icono":"bi-info-circle",
            },

        ]
    },

]