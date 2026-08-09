import io
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import openpyxl
from openpyxl.styles import Font


ENCABEZADOS = ["Usuario", "Acción", "Módulo", "Descripción", "IP Origen", "Fecha y Hora"]


def _fila(registro):
    return [
        registro.id_usuario.username if registro.id_usuario else "-",
        registro.tipo_accion,
        registro.id_modulo.nombre if registro.id_modulo else "-",
        registro.descripcion or "-",
        registro.ip_origen or "-",
        registro.fecha_hora.strftime("%d/%m/%Y %H:%M:%S"),
    ]


def exportar_bitacora_pdf(queryset, titulo, nombre_archivo):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    estilos = getSampleStyleSheet()

    elementos = [Paragraph(titulo, estilos["Title"]), Spacer(1, 12)]

    data = [ENCABEZADOS]
    for registro in queryset:
        data.append(_fila(registro))

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C3AED")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.pdf"'
    return response


def exportar_bitacora_excel(queryset, titulo, nombre_archivo):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = titulo[:31]

    ws.append(ENCABEZADOS)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for registro in queryset:
        ws.append(_fila(registro))

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.xlsx"'
    wb.save(response)
    return response