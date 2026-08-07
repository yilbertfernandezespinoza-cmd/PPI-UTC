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
                "titulo": "Datos de la Empresa",
                "url": "configuracion:datos_empresa",
                "icono": "bi-building-gear",
            },
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
                "titulo": "Métodos de Pago",
                "url": "configuracion:metodo_pago_list",
                "icono": "bi-credit-card",
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
                "modulo_permiso": "Inventario",
                "titulo": "Entrada de Inventario",
                "url": "inventario:entrada_inventario",
                "icono": "bi-box-arrow-in-down",
            },

            {
                "modulo_permiso": "Inventario",
                "titulo": "Movimientos de Inventario",
                "url": "inventario:lista_movimientos",
                "icono": "bi-arrow-left-right",
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
                # El acceso rápido del dashboard debe abrir directamente una
                # venta nueva (POS), no el reporte de ventas diarias — el
                # link del menú lateral sí debe seguir yendo al reporte
                # (lista_ventas), por eso se usa una URL aparte solo para
                # la tarjeta del dashboard en vez de cambiar "url".
                "url_dashboard": "ventas:crear_venta",
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

            {
                "modulo_permiso": "Mermas",
                "titulo": "Mermas",
                "url": "mermas:listar",
                "icono": "bi-exclamation-triangle",
            },

            {
                "modulo_permiso": "Ajustes",
                "titulo": "Ajustes de Inventario",
                "url": "ajustes:listar",
                "icono": "bi-sliders",
            },

            {
                "modulo_permiso": "Gastos Operativos",
                "titulo": "Gastos Operativos",
                "url": "gastos_operativos:listar",
                "icono": "bi-cash-coin",
            },

        ]
    },

    {
        "modulo": "Reportes",
        "icono": "bi-file-earmark-bar-graph",
        "opciones": [

            {
                "titulo": "Reporte de Ventas",
                "url": "reportes:ventas",
                "icono": "bi-cash-stack",
            },
            {
                "titulo": "Reporte de Inventario",
                "url": "reportes:inventario",
                "icono": "bi-box-seam",
            },
            {
                "titulo": "Reporte Tributario",
                "url": "reportes:tributario",
                "icono": "bi-receipt-cutoff",
            },
            {
                "titulo": "Reporte de Utilidad",
                "url": "reportes:utilidad",
                "icono": "bi-graph-up-arrow",
            },
            {
                "titulo": "Reporte de Mermas",
                "url": "reportes:mermas",
                "icono": "bi-exclamation-triangle",
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

        ]
    },

]

# "Acerca de SIGEPAN" (07-08, RF-008): se retiró de este árbol de módulos
# porque no es un submódulo de Seguridad, sino una pantalla informativa de
# todo el sistema — quedaba "mal ubicada" ahí. Se muestra ahora como ítem
# fijo al final del menú lateral (ver templates/includes/sidebar.html),
# igual que "Inicio" al principio: visible para cualquier usuario, sin
# pasar por el árbol de permisos por módulo.