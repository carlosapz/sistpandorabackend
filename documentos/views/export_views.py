import csv
import json
from datetime import datetime
from io import BytesIO

from django.http import HttpResponse, FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from documentos.models import Documento, HistorialActividad, ReporteHistorial


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_historial_csv(request):
    """
    Exporta historial de actividades en formato CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\"historial_actividades.csv\"'

    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Documento', 'Acción', 'Fecha'])

    for actividad in HistorialActividad.objects.all():
        writer.writerow([
            actividad.usuario.username if actividad.usuario else 'Desconocido',
            actividad.documento.titulo if actividad.documento else 'N/A',
            actividad.accion,
            actividad.fecha
        ])
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_historial_pdf(request):
    """
    Exporta historial de actividades en formato PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=16, alignment=1, spaceAfter=12)

    elements.append(Paragraph("Historial de Actividades", title_style))

    data = [["Usuario", "Documento", "Acción", "Fecha"]]
    for actividad in HistorialActividad.objects.all().order_by('-fecha'):
        data.append([
            actividad.usuario.username if actividad.usuario else "Desconocido",
            actividad.documento.titulo if actividad.documento else "N/A",
            actividad.accion,
            actividad.fecha.strftime("%Y-%m-%d %H:%M:%S")
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="historial_actividades.pdf")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_documentos_csv(request):
    """
    Exporta todos los documentos como CSV plano.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\"documentos.csv\"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Descripción', 'Tipo', 'Fecha de Creación', 'Estado', 'Proyecto', 'Categoría', 'Usuario'])

    for documento in Documento.objects.all():
        writer.writerow([
            documento.id,
            documento.titulo,
            documento.descripcion,
            documento.tipo,
            documento.fecha_creacion,
            documento.estado,
            documento.proyecto.nombre if documento.proyecto else '',
            documento.categoria.nombre if documento.categoria else '',
            documento.usuario.username
        ])
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_documentos_pdf(request):
    """
    Exporta todos los documentos en un PDF con tabla y encabezados.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=16, alignment=1, spaceAfter=12)
    elements.append(Paragraph("CONSTRUCTORA PANDORA", title_style))
    elements.append(Paragraph("REPORTE DE DOCUMENTOS", title_style))
    elements.append(Spacer(1, 20))

    fecha_hora = datetime.now().strftime('%d-%m-%Y %H:%M')
    usuario = request.user.get_full_name() if request.user.is_authenticated else "Usuario Anónimo"
    info_table = Table([
        ["Fecha y Hora del Reporte:", fecha_hora],
        ["Generado por:", usuario]
    ], colWidths=[5 * cm, 10 * cm])
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    encabezado = [["Folio", "Título", "Descripción", "Tipo", "Fecha", "Usuario", "Estado"]]
    data = []
    for i, docu in enumerate(Documento.objects.all(), start=1):
        data.append([
            str(i),
            docu.titulo,
            docu.descripcion or "N/A",
            docu.tipo,
            docu.fecha_creacion.strftime('%d-%m-%Y'),
            docu.usuario.get_full_name() if docu.usuario else "N/A",
            docu.estado
        ])

    table = Table(encabezado + data, colWidths=[1.5*cm, 3*cm, 5*cm, 2*cm, 3*cm, 3*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="reporte_documentos.pdf")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_documentos_pdf_filtrado(request):
    """
    Exporta a PDF documentos filtrados por fecha, estado o proyecto.
    Registra historial del reporte.
    """
    filtros = {
        "fecha_inicio": request.GET.get('fecha_inicio'),
        "fecha_fin": request.GET.get('fecha_fin'),
        "estado": request.GET.get('estado'),
        "proyecto": request.GET.get('proyecto')
    }

    documentos = Documento.objects.all()
    if filtros["fecha_inicio"]:
        documentos = documentos.filter(fecha_creacion__gte=filtros["fecha_inicio"])
    if filtros["fecha_fin"]:
        documentos = documentos.filter(fecha_creacion__lte=filtros["fecha_fin"])
    if filtros["estado"]:
        documentos = documentos.filter(estado=filtros["estado"])
    if filtros["proyecto"]:
        documentos = documentos.filter(proyecto__nombre__icontains=filtros["proyecto"])

    if not documentos.exists():
        return Response({"error": "No hay documentos disponibles para exportar."}, status=400)

    ReporteHistorial.objects.create(
        usuario=request.user,
        tipo_reporte="PDF",
        filtros_aplicados=json.dumps(filtros)
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Reporte de Documentos - Constructora Pandora", styles['Title'])]

    data = [["ID", "Título", "Proyecto", "Estado", "Fecha de Creación"]]
    for docu in documentos:
        data.append([
            docu.id,
            docu.titulo,
            docu.proyecto.nombre if docu.proyecto else "N/A",
            docu.estado,
            docu.fecha_creacion.strftime("%Y-%m-%d")
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="documentos_report.pdf")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_documentos_excel(request):
    """
    Exporta documentos a Excel. Se puede filtrar por fecha y estado.
    """
    documentos = Documento.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')

    if fecha_inicio:
        documentos = documentos.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        documentos = documentos.filter(fecha_creacion__lte=fecha_fin)
    if estado:
        documentos = documentos.filter(estado=estado)

    if not documentos.exists():
        return Response({"error": "No hay documentos disponibles para exportar."}, status=400)

    wb = Workbook()
    ws = wb.active
    ws.title = "Documentos Reporte"

    headers = ["ID", "Título", "Proyecto", "Estado", "Fecha de Creación"]
    ws.append(headers)

    for doc in documentos:
        ws.append([
            doc.id,
            doc.titulo,
            doc.proyecto.nombre if doc.proyecto else "N/A",
            doc.estado,
            doc.fecha_creacion.strftime("%Y-%m-%d")
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="documentos_report.xlsx"'
    wb.save(response)
    return response
