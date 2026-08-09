import io
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import openpyxl
from openpyxl.styles import Font


def exportar_pdf(encabezados, filas, titulo, nombre_archivo):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    estilos = getSampleStyleSheet()

    elementos = [Paragraph(titulo, estilos["Title"]), Spacer(1, 12)]

    data = [encabezados] + filas
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


def exportar_excel(encabezados, filas, titulo, nombre_archivo):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = titulo[:31]

    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append(fila)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.xlsx"'
    wb.save(response)
    return response