from datetime import datetime
from io import BytesIO
import csv
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.http import HttpResponse
from documentos.models import Documento


def exportar_documentos_pdf(documentos_queryset):
    """
    Genera un PDF con la lista de documentos.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    elements.append(Paragraph("Listado de Documentos", title_style))
    elements.append(Spacer(1, 12))

    data = [["Título", "Proyecto", "Categoría", "Fecha", "Estado"]]
    for docu in documentos_queryset:
        data.append([
            docu.titulo,
            docu.proyecto.nombre,
            docu.categoria.nombre if docu.categoria else "Sin categoría",
            docu.fecha_creacion.strftime('%Y-%m-%d'),
            docu.estado
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


def exportar_documentos_excel(documentos_queryset):
    """
    Genera un archivo Excel con la lista de documentos.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Documentos"

    headers = ["Título", "Proyecto", "Categoría", "Fecha", "Estado"]
    ws.append(headers)

    for docu in documentos_queryset:
        ws.append([
            docu.titulo,
            docu.proyecto.nombre,
            docu.categoria.nombre if docu.categoria else "Sin categoría",
            docu.fecha_creacion.strftime('%Y-%m-%d'),
            docu.estado
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f'documentos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response


def exportar_documentos_csv(documentos_queryset):
    """
    Genera un archivo CSV con la lista de documentos.
    """
    response = HttpResponse(content_type='text/csv')
    filename = f'documentos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Título", "Proyecto", "Categoría", "Fecha", "Estado"])

    for docu in documentos_queryset:
        writer.writerow([
            docu.titulo,
            docu.proyecto.nombre,
            docu.categoria.nombre if docu.categoria else "Sin categoría",
            docu.fecha_creacion.strftime('%Y-%m-%d'),
            docu.estado
        ])

    return response
