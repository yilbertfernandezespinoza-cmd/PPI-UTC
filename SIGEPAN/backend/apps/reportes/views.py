from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from apps.security.mixins import SessionRequiredMixin
from apps.security.permissions import PermissionRequiredMixin
from apps.security.services import registrar_log
from apps.configuracion.models import Sucursal

from .services import ReporteService
from .exports import exportar_pdf, exportar_excel
from .google_sheets import exportar_a_google_sheets


class ReporteVentasView(SessionRequiredMixin, PermissionRequiredMixin, View):

    permission_module = "Reportes"
    permission_action = "CONSULTAR"
    template_name = "reportes/ventas.html"

    def get(self, request):

        fecha_inicio = request.GET.get("fecha_inicio", "")
        fecha_fin = request.GET.get("fecha_fin", "")
        sucursal_id = request.GET.get("sucursal", "")

        queryset, total = ReporteService.reporte_ventas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal_id=sucursal_id,
        )

        formato = request.GET.get("formato")

        if formato in ("pdf", "excel", "sheets"):

            encabezados = ["N° Venta", "Fecha", "Cliente", "Usuario", "Sucursal", "Método de pago", "Total"]

            filas = [
                [
                    v.numero_venta,
                    v.fecha.strftime("%d/%m/%Y %H:%M"),
                    v.cliente.nombre if v.cliente else "Consumidor final",
                    v.usuario.username,
                    v.caja.sucursal.nombre if v.caja and v.caja.sucursal else "-",
                    v.metodo_pago.nombre,
                    float(v.total),
                ]
                for v in queryset
            ]

            if formato == "sheets":
                try:
                    url_hoja = exportar_a_google_sheets(
                        request.usuario, "Reporte de Ventas", encabezados, filas
                    )
                    registrar_log(
                        request, request.usuario, "Reportes", "EXPORTAR",
                        "Exportó reporte de ventas a Google Sheets"
                    )
                    return redirect(url_hoja)
                except ValidationError as error:
                    messages.error(request, str(error))
                    return redirect("reportes:ventas")

            registrar_log(
                request, request.usuario, "Reportes", "EXPORTAR",
                f"Exportó reporte de ventas a {formato.upper()}"
            )

            if formato == "pdf":
                return exportar_pdf(encabezados, filas, "Reporte de Ventas", "reporte_ventas")
            return exportar_excel(encabezados, filas, "Reporte de Ventas", "reporte_ventas")

        return render(request, self.template_name, {
            "ventas": queryset,
            "total": total,
            "sucursales": Sucursal.objects.filter(estado=True).order_by("nombre"),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "sucursal_id": sucursal_id,
        })


class ReporteInventarioView(SessionRequiredMixin, PermissionRequiredMixin, View):

    permission_module = "Reportes"
    permission_action = "CONSULTAR"
    template_name = "reportes/inventario.html"

    def get(self, request):

        sucursal_id = request.GET.get("sucursal", "")
        solo_bajo_minimo = request.GET.get("bajo_minimo") == "1"

        queryset = ReporteService.reporte_inventario(
            sucursal_id=sucursal_id,
            solo_bajo_minimo=solo_bajo_minimo,
        )

        formato = request.GET.get("formato")

        if formato in ("pdf", "excel", "sheets"):

            encabezados = ["Producto", "Sucursal", "Stock actual", "Stock mínimo", "Stock máximo"]

            filas = [
                [
                    i.id_producto.nombre,
                    i.id_sucursal.nombre,
                    i.stock_actual,
                    i.stock_minimo,
                    i.stock_maximo,
                ]
                for i in queryset
            ]

            if formato == "sheets":
                try:
                    url_hoja = exportar_a_google_sheets(
                        request.usuario, "Reporte de Inventario", encabezados, filas
                    )
                    registrar_log(
                        request, request.usuario, "Reportes", "EXPORTAR",
                        "Exportó reporte de inventario a Google Sheets"
                    )
                    return redirect(url_hoja)
                except ValidationError as error:
                    messages.error(request, str(error))
                    return redirect("reportes:inventario")

            registrar_log(
                request, request.usuario, "Reportes", "EXPORTAR",
                f"Exportó reporte de inventario a {formato.upper()}"
            )

            if formato == "pdf":
                return exportar_pdf(encabezados, filas, "Reporte de Inventario", "reporte_inventario")
            return exportar_excel(encabezados, filas, "Reporte de Inventario", "reporte_inventario")

        return render(request, self.template_name, {
            "inventario": queryset,
            "sucursales": Sucursal.objects.filter(estado=True).order_by("nombre"),
            "sucursal_id": sucursal_id,
            "solo_bajo_minimo": solo_bajo_minimo,
        })


class ReporteTributarioView(SessionRequiredMixin, PermissionRequiredMixin, View):

    permission_module = "Reportes"
    permission_action = "CONSULTAR"
    template_name = "reportes/tributario.html"

    def get(self, request):

        fecha_inicio = request.GET.get("fecha_inicio", "")
        fecha_fin = request.GET.get("fecha_fin", "")

        total_ventas, por_metodo = ReporteService.reporte_tributario(fecha_inicio, fecha_fin)

        formato = request.GET.get("formato")

        if formato in ("pdf", "excel", "sheets"):

            encabezados = ["Método de pago", "Total"]
            filas = [[m["metodo_pago__nombre"] or "Sin especificar", float(m["total"])] for m in por_metodo]
            filas.append(["TOTAL GENERAL", float(total_ventas)])

            if formato == "sheets":
                try:
                    url_hoja = exportar_a_google_sheets(
                        request.usuario, "Reporte Tributario Mensual", encabezados, filas
                    )
                    registrar_log(
                        request, request.usuario, "Reportes", "EXPORTAR",
                        "Exportó reporte tributario a Google Sheets"
                    )
                    return redirect(url_hoja)
                except ValidationError as error:
                    messages.error(request, str(error))
                    return redirect("reportes:tributario")

            registrar_log(
                request, request.usuario, "Reportes", "EXPORTAR",
                f"Exportó reporte tributario a {formato.upper()}"
            )

            if formato == "pdf":
                return exportar_pdf(encabezados, filas, "Reporte Tributario Mensual", "reporte_tributario")
            return exportar_excel(encabezados, filas, "Reporte Tributario Mensual", "reporte_tributario")

        return render(request, self.template_name, {
            "total_ventas": total_ventas,
            "por_metodo": por_metodo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        })


class ReporteUtilidadView(SessionRequiredMixin, PermissionRequiredMixin, View):

    permission_module = "Reportes"
    permission_action = "CONSULTAR"
    template_name = "reportes/utilidad.html"

    def get(self, request):

        fecha_inicio = request.GET.get("fecha_inicio", "")
        fecha_fin = request.GET.get("fecha_fin", "")

        total_ventas, costos, utilidad = ReporteService.reporte_utilidad(fecha_inicio, fecha_fin)

        formato = request.GET.get("formato")

        if formato in ("pdf", "excel", "sheets"):

            encabezados = ["Ventas totales", "Costos estimados", "Utilidad bruta"]
            filas = [[float(total_ventas), float(costos), float(utilidad)]]

            if formato == "sheets":
                try:
                    url_hoja = exportar_a_google_sheets(
                        request.usuario, "Reporte de Utilidad Estimada", encabezados, filas
                    )
                    registrar_log(
                        request, request.usuario, "Reportes", "EXPORTAR",
                        "Exportó reporte de utilidad a Google Sheets"
                    )
                    return redirect(url_hoja)
                except ValidationError as error:
                    messages.error(request, str(error))
                    return redirect("reportes:utilidad")

            registrar_log(
                request, request.usuario, "Reportes", "EXPORTAR",
                f"Exportó reporte de utilidad a {formato.upper()}"
            )

            if formato == "pdf":
                return exportar_pdf(encabezados, filas, "Reporte de Utilidad Estimada", "reporte_utilidad")
            return exportar_excel(encabezados, filas, "Reporte de Utilidad Estimada", "reporte_utilidad")

        return render(request, self.template_name, {
            "total_ventas": total_ventas,
            "costos": costos,
            "utilidad": utilidad,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        })