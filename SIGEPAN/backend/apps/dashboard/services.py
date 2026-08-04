from datetime import datetime

from apps.security.services import MenuService
from .repositories import DashboardRepository


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

        rol_nombre = ""
        if getattr(request, "rol", None):
            rol_nombre = (request.rol.nombre or "").upper()

        es_cajero = rol_nombre == "CAJERO"
        mostrar_gerencial = not es_cajero

        menu_dashboard = MenuService.obtener_menu_usuario(request)
        accesos_rapidos = []
        for grupo in menu_dashboard:
            for opcion in grupo["opciones"]:
                if not opcion.get("dashboard", False):
                    continue
                accesos_rapidos.append({
                    "titulo": opcion["titulo"],
                    "icono": opcion["icono"],
                    "color": opcion.get("color", "primary"),
                    "url": opcion["url"],
                })

        kpis = []
        top_productos = []
        ventas_por_sucursal = []

        if mostrar_gerencial:
            kpis = [
                {
                    "titulo": "Ventas del día",
                    "valor": f"₡{DashboardRepository.ventas_del_dia():,.2f}",
                    "icono": "bi bi-cash-stack",
                    "color": "success",
                },
                {
                    "titulo": "Ventas del mes",
                    "valor": f"₡{DashboardRepository.ventas_del_mes():,.2f}",
                    "icono": "bi bi-graph-up",
                    "color": "primary",
                },
                {
                    "titulo": "Ventas de hoy (cantidad)",
                    "valor": DashboardRepository.cantidad_ventas_del_dia(),
                    "icono": "bi bi-receipt",
                    "color": "info",
                },
                {
                    "titulo": "Ticket promedio (hoy)",
                    "valor": f"₡{DashboardRepository.ticket_promedio_del_dia():,.2f}",
                    "icono": "bi bi-calculator",
                    "color": "warning",
                },
            ]
            top_productos = DashboardRepository.top_productos()
            ventas_por_sucursal = DashboardRepository.ventas_por_sucursal()

        return {
            "saludo": saludo,
            "fecha": datetime.now(),
            "accesos_rapidos": accesos_rapidos,
            "mostrar_kpis": mostrar_gerencial,
            "mostrar_accesos": True,
            "mostrar_actividad": mostrar_gerencial,
            "mostrar_alertas": mostrar_gerencial,
            "kpis": kpis,
            "top_productos": top_productos,
            "ventas_por_sucursal": ventas_por_sucursal,
        }