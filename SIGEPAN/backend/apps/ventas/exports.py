# Generación del comprobante de venta como PDF real (RF-012).
#
# Agregado 06-08: antes ComprobanteEmailService.enviar() solo mandaba el
# HTML de la plantilla como cuerpo del correo — sin ningún archivo
# adjunto. Muchos clientes de correo (Outlook incluido, según se vio en
# una prueba real) terminan mostrando ese HTML como texto plano sin
# formato. Este módulo genera un PDF real del comprobante, con el mismo
# contenido que "comprobante_venta.html", para adjuntarlo al correo.
#
# Se usa una fuente TTF propia (DejaVu Sans, en static/fonts/) en vez de
# las fuentes base de reportlab (Helvetica) porque Helvetica no tiene el
# glifo del símbolo de colón costarricense "₡" (U+20A1) — se probó y
# aparece como un cuadro vacío. DejaVu sí lo soporta y se distribuye
# junto al proyecto (no depende de qué fuentes tenga instaladas el
# sistema operativo de cada máquina).

import io
from pathlib import Path

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .utils import calcular_vuelto_venta


RUTA_FUENTE_REGULAR = Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans.ttf"
RUTA_FUENTE_NEGRITA = Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans-Bold.ttf"
RUTA_LOGO = Path(settings.BASE_DIR) / "static" / "img" / "logos" / "lapana-logo.jpeg"

_FUENTES_REGISTRADAS = False


def _registrar_fuentes():
    """
    Registra las fuentes DejaVu en reportlab una sola vez por proceso
    (registrar la misma fuente dos veces no rompe nada, pero no aporta).
    """

    global _FUENTES_REGISTRADAS

    if _FUENTES_REGISTRADAS:
        return

    pdfmetrics.registerFont(TTFont("DejaVuSans", str(RUTA_FUENTE_REGULAR)))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(RUTA_FUENTE_NEGRITA)))

    _FUENTES_REGISTRADAS = True


def _colon(valor):
    """Formatea un monto en colones, igual que `floatformat:2` en el template."""
    return f"₡{float(valor):,.2f}"


def generar_comprobante_pdf(venta, detalles, pagos, datos_empresa):
    """
    Genera el PDF del comprobante de `venta` y devuelve los bytes listos
    para adjuntar a un correo (o servir como descarga). Replica el
    contenido de comprobante_venta.html: datos del emisor, datos del
    cliente, detalle de productos, totales y pagos.
    """

    _registrar_fuentes()

    buffer = io.BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    estilos = getSampleStyleSheet()

    estilo_normal = ParagraphStyle(
        "Normal-DejaVu", parent=estilos["Normal"], fontName="DejaVuSans", fontSize=9,
    )
    estilo_titulo = ParagraphStyle(
        "Titulo-DejaVu", parent=estilos["Heading2"], fontName="DejaVuSans-Bold",
        fontSize=12, spaceAfter=6,
    )
    estilo_total = ParagraphStyle(
        "Total-DejaVu", parent=estilos["Normal"], fontName="DejaVuSans-Bold", fontSize=13,
    )

    elementos = []

    # ---------- Encabezado: logo + datos del emisor ----------
    if RUTA_LOGO.exists():
        logo = Image(str(RUTA_LOGO), width=25 * mm, height=25 * mm)
        elementos.append(logo)
        elementos.append(Spacer(1, 6))

    datos_emisor = (
        f"Cédula Física: {datos_empresa.cedula_juridica or '2-0557-0979'}<br/>"
        f"Dirección: {datos_empresa.direccion_fiscal or 'San José, Moravia, San Vicente, Urbanización Saint Claire'}<br/>"
        f"Teléfono: {datos_empresa.telefono or '4082-3934'}<br/>"
        f"{datos_empresa.correo or 'lapanacostarrica@gmail.com'}"
    )
    elementos.append(Paragraph(datos_emisor, estilo_normal))
    elementos.append(Spacer(1, 10))

    # ---------- Referencia del comprobante ----------
    elementos.append(
        Paragraph(
            f"<b>Comprobante:</b> {venta.numero_venta} &nbsp;&nbsp;&nbsp; "
            f"<b>Tipo:</b> {venta.tipo_comprobante}",
            estilo_normal,
        )
    )
    elementos.append(Spacer(1, 10))

    # ---------- Datos del cliente ----------
    elementos.append(Paragraph("Datos del cliente", estilo_titulo))

    nombre_cliente = venta.cliente.nombre_completo if venta.cliente else "Consumidor Final"
    cedula_cliente = venta.cliente.identificacion if venta.cliente and venta.cliente.identificacion else "—"
    correo_cliente = venta.cliente.correo if venta.cliente and venta.cliente.correo else "—"

    elementos.append(
        Paragraph(
            f"<b>Cliente:</b> {nombre_cliente} &nbsp;&nbsp;&nbsp; "
            f"<b>Cédula del cliente:</b> {cedula_cliente}<br/>"
            f"<b>Correo:</b> {correo_cliente} &nbsp;&nbsp;&nbsp; "
            f"<b>Cajero:</b> {venta.usuario or '—'}<br/>"
            f"<b>Hora:</b> {venta.fecha.strftime('%d/%m/%Y %H:%M')}",
            estilo_normal,
        )
    )
    elementos.append(Spacer(1, 12))

    # ---------- Detalle de la compra ----------
    elementos.append(Paragraph("Detalle de la compra", estilo_titulo))

    filas_detalle = [["Producto", "Cant.", "Precio Unit.", "Subtotal"]]
    for detalle in detalles:
        nombre_producto = detalle.producto.nombre if detalle.producto else str(detalle.producto)
        filas_detalle.append([
            nombre_producto,
            str(detalle.cantidad),
            _colon(detalle.precio_unitario),
            _colon(detalle.subtotal),
        ])

    if len(filas_detalle) == 1:
        filas_detalle.append(["No hay productos en este comprobante.", "", "", ""])

    tabla_detalle = Table(
        filas_detalle,
        colWidths=[70 * mm, 20 * mm, 30 * mm, 30 * mm],
    )
    tabla_detalle.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(tabla_detalle)
    elementos.append(Spacer(1, 10))

    # ---------- Totales ----------
    filas_totales = [["Subtotal:", _colon(venta.subtotal)]]
    if venta.descuento and venta.descuento > 0:
        filas_totales.append(["Descuento:", f"-{_colon(venta.descuento)}"])
    filas_totales.append(["Impuesto:", _colon(venta.impuesto)])
    filas_totales.append(["Total:", _colon(venta.total)])

    tabla_totales = Table(filas_totales, colWidths=[40 * mm, 40 * mm], hAlign="RIGHT")
    tabla_totales.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTNAME", (0, -1), (-1, -1), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -2), 9),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.HexColor("#0F172A")),
        ("TOPPADDING", (0, -1), (-1, -1), 6),
    ]))
    elementos.append(tabla_totales)
    elementos.append(Spacer(1, 14))

    # ---------- Pagos ----------
    elementos.append(Paragraph("Pagos", estilo_titulo))

    if pagos:
        filas_pagos = [["Método de pago", "Monto", "Referencia"]]
        for pago in pagos:
            filas_pagos.append([
                str(pago.metodo_pago),
                _colon(pago.monto),
                pago.referencia or "—",
            ])

        tabla_pagos = Table(filas_pagos, colWidths=[50 * mm, 30 * mm, 40 * mm])
        tabla_pagos.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
            ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elementos.append(tabla_pagos)

        # ---------- Vuelto ----------
        # Solo se imprime la línea si hubo excedente (pago en efectivo por
        # encima del total) — ver calcular_vuelto_venta en utils.py.
        vuelto = calcular_vuelto_venta(venta, pagos)
        if vuelto > 0:
            elementos.append(Spacer(1, 4))
            tabla_vuelto = Table(
                [["Vuelto entregado:", _colon(vuelto)]],
                colWidths=[40 * mm, 40 * mm],
                hAlign="RIGHT",
            )
            tabla_vuelto.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ]))
            elementos.append(tabla_vuelto)
    else:
        elementos.append(Paragraph("No hay pagos registrados para esta venta.", estilo_normal))

    elementos.append(Spacer(1, 16))

    # ---------- Pie ----------
    elementos.append(
        Paragraph(
            "¡Gracias por su compra! — La Pana",
            ParagraphStyle(
                "Pie-DejaVu", parent=estilo_normal, alignment=1,
                textColor=colors.HexColor("#666666"),
            ),
        )
    )

    documento.build(elementos)

    buffer.seek(0)
    return buffer.getvalue()
