from datetime import datetime

from apps.security.services import MenuService


class DashboardService:

    @staticmethod
    def obtener_dashboard(request):

        hora = datetime.now().hour

        if hora < 12:
            saludo = "Buenos días"
        elif hora < 18:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"

        menu_dashboard = MenuService.obtener_menu_usuario(request)

        accesos_rapidos = []

        for grupo in menu_dashboard:

            for opcion in grupo["opciones"]:

                if not opcion.get("dashboard", False):
                    continue

                accesos_rapidos.append({

                    "titulo": opcion["titulo"],

                    "icono": opcion["icono"],

                    "color": opcion.get(
                        "color",
                        "primary"
                    ),

                    "url": opcion["url"],
                })


        return {

            "saludo": saludo,

            "fecha": datetime.now(),

            "accesos_rapidos": accesos_rapidos,

            "mostrar_accesos": True,
            
            "mostrar_actividad": True,

            "mostrar_alertas": True,

            "kpis": [
                {
                    "titulo": "Ventas del día",
                    "valor": "--",
                    "icono": "bi bi-cash-stack",
                    "color": "success",
                },
                {
                    "titulo": "Productos",
                    "valor": "--",
                    "icono": "bi bi-box-seam",
                    "color": "primary",
                },
                {
                    "titulo": "Clientes",
                    "valor": "--",
                    "icono": "bi bi-people",
                    "color": "warning",
                },
                {
                    "titulo": "Usuarios",
                    "valor": "--",
                    "icono": "bi bi-person-badge",
                    "color": "info",
                },
            ],
        }