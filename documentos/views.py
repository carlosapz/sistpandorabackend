# documentos/views.py

# Django imports
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

# Rest Framework imports
from rest_framework import generics, filters, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

# Librerías externas para reportes
import csv
import json
from datetime import datetime
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Modelos locales
from .models import (
    Proyecto, Obra, Categoria, Tag, Documento,
    VersionDocumento, Comentario, Notificacion, HistorialActividad, ReporteHistorial
)

# Serializadores locales
from .serializers import (
    ProyectoSerializer, ObraSerializer, CategoriaSerializer,
    TagSerializer, DocumentoSerializer,
    VersionDocumentoSerializer, ComentarioSerializer, NotificacionSerializer,
    HistorialActividadSerializer, DocumentoAprobarSerializer
)

# Permisos y utilidades
from .permissions import (
    PuedeVerDocumentos, PuedeEditarDocumentos,
    PuedeEliminarDocumentos, PuedeAprobarDocumentos
)
from .utils import crear_notificacion
from .filters import DocumentoFilter

# --- Vistas para Proyectos, Categorías y Tags ---

class ProyectoListCreateView(generics.ListCreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]

class ProyectoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]

class CategoriaListCreateView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

# --- Vistas para Documentos ---

class DocumentoListCreateView(generics.ListCreateAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated, PuedeVerDocumentos]

    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentoFilter

    def perform_create(self, serializer):
        documento = serializer.save(usuario=self.request.user, estado='REVISION')
        mensaje = f"El documento '{documento.titulo}' ha sido creado y está en revisión."
        crear_notificacion(documento.usuario, mensaje)

class DocumentoListView(generics.ListAPIView):
    queryset = Documento.objects.select_related('proyecto', 'categoria', 'usuario').prefetch_related('tags').all()
    serializer_class = DocumentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentoFilter

class DocumentoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer

    def get_permissions(self):
        permission_map = {
            'GET': [PuedeVerDocumentos()],
            'PUT': [PuedeEditarDocumentos()],
            'PATCH': [PuedeEditarDocumentos()],
            'DELETE': [PuedeEliminarDocumentos()],
        }
        return permission_map.get(self.request.method, [IsAuthenticated()])

    def perform_update(self, serializer):
        instance = self.get_object()
        archivo_anterior = instance.archivo

        updated_instance = serializer.save()

        # Solo crear nueva versión si se cambió el archivo
        if archivo_anterior != updated_instance.archivo:
            VersionDocumento.objects.filter(documento=updated_instance).update(activo=False)

            VersionDocumento.objects.create(
                documento=updated_instance,
                archivo=archivo_anterior,
                usuario=self.request.user,
                activo=True
            )


class DocumentoAprobarView(generics.UpdateAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoAprobarSerializer
    permission_classes = [IsAuthenticated, PuedeAprobarDocumentos]

    def perform_update(self, serializer):
        documento = self.get_object()
        documento.estado = 'APROBADO'
        documento.save()

        mensaje = f"El documento '{documento.titulo}' ha sido aprobado."
        crear_notificacion(documento.usuario, mensaje)

# --- Vistas para Versiones y Comentarios ---

class VersionDocumentoListCreateView(generics.ListCreateAPIView):
    serializer_class = VersionDocumentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        documento_id = self.request.query_params.get('documento')
        if documento_id:
            return VersionDocumento.objects.filter(documento_id=documento_id).order_by('-fecha')
        return VersionDocumento.objects.none()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class RestaurarVersionAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VersionDocumento.objects.all()

    def post(self, request, pk):
        version = self.get_object()
        documento = version.documento
        documento.archivo = version.archivo
        documento.save()

        VersionDocumento.objects.filter(documento=documento).update(activo=False)
        version.activo = True
        version.save()

        return Response({'detail': 'Versión restaurada correctamente.'})

class VersionDocumentoDetailView(generics.RetrieveDestroyAPIView):
    queryset = VersionDocumento.objects.all()
    serializer_class = VersionDocumentoSerializer
    permission_classes = [IsAuthenticated]

class ComentarioListCreateView(generics.ListCreateAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class ComentarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

# --- Vistas para Notificaciones y Historial ---

class NotificacionListView(generics.ListAPIView):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        leido = self.request.query_params.get('leido', None)
        queryset = Notificacion.objects.filter(usuario=self.request.user)
        if leido is not None:
            queryset = queryset.filter(leido=(leido.lower() == 'true'))
        return queryset

class MarcarNotificacionLeidaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notificacion = Notificacion.objects.get(pk=pk, usuario=request.user)
            notificacion.leido = True
            notificacion.save()
            return Response({"message": "Notificación marcada como leída."})
        except Notificacion.DoesNotExist:
            raise NotFound("Notificación no encontrada.")

class HistorialActividadListView(generics.ListAPIView):
    queryset = HistorialActividad.objects.all().order_by('-fecha')
    serializer_class = HistorialActividadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['usuario', 'accion', 'fecha', 'documento']

# --- Vistas para Obras ---

class ObraListCreateView(generics.ListCreateAPIView):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]

class ObraDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]

def exportar_historial_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_actividades.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Documento', 'Acción', 'Fecha'])

    historial = HistorialActividad.objects.all()
    for actividad in historial:
        writer.writerow([
            actividad.usuario.username if actividad.usuario else 'Desconocido',
            actividad.documento.titulo if actividad.documento else 'N/A',
            actividad.accion,
            actividad.fecha
        ])

    return response

def exportar_historial_pdf(request):
    # Crear el buffer de memoria para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos del PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=16, alignment=1, spaceAfter=12)
    
    # Título del reporte
    elements.append(Paragraph("Historial de Actividades", title_style))
    
    # Datos para la tabla
    data = [["Usuario", "Documento", "Acción", "Fecha"]]
    historial = HistorialActividad.objects.all().order_by('-fecha')

    for actividad in historial:
        data.append([
            actividad.usuario.username if actividad.usuario else "Desconocido",
            actividad.documento.titulo if actividad.documento else "N/A",
            actividad.accion,
            actividad.fecha.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # Definir la tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el PDF
    doc.build(elements)

    # Configurar la respuesta HTTP para devolver el archivo
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historial_actividades.pdf"'

    return response


def exportar_documentos_csv(request):
    # Crear respuesta HTTP para el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="documentos.csv"'

    # Definir el escritor CSV y los encabezados
    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Descripción', 'Tipo', 'Fecha de Creación', 'Estado', 'Proyecto', 'Categoría', 'Usuario'])

    # Consultar documentos y escribirlos en el archivo CSV
    documentos = Documento.objects.all()
    for documento in documentos:
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

def exportar_documentos_pdf(request):
    # Configurar el buffer de salida para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos y título
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=16, alignment=1, spaceAfter=12)
    subtitle_style = ParagraphStyle('Subtitle', fontSize=12, spaceAfter=6, alignment=0)

    # Título y Encabezado
    elements.append(Paragraph("CONSTRUCTORA PANDORA", title_style))
    elements.append(Paragraph("REPORTE DE DOCUMENTOS", title_style))
    elements.append(Spacer(1, 20))

    # Información del Reporte
    fecha_hora = datetime.now().strftime('%d-%m-%Y %H:%M')
    usuario = request.user.get_full_name() if request.user.is_authenticated else "Usuario Anónimo"
    info_reporte = [
        ["Fecha y Hora del Reporte:", fecha_hora],
        ["Generado por:", usuario]
    ]
    info_table = Table(info_reporte, colWidths=[5 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # Encabezados de la tabla de documentos
    encabezado = [["Folio", "Título", "Descripción", "Tipo", "Fecha de Creación", "Usuario", "Estado"]]
    documentos = Documento.objects.all()
    data = []

    # Agregar datos de los documentos
    for i, documento in enumerate(documentos, start=1):
        data.append([
            str(i),
            documento.titulo,
            documento.descripcion or "N/A",
            documento.tipo,
            documento.fecha_creacion.strftime('%d-%m-%Y'),
            documento.usuario.get_full_name() if documento.usuario else "N/A",
            documento.estado,
        ])

    # Crear tabla de documentos
    table_data = encabezado + data
    table = Table(table_data, colWidths=[1.5 * cm, 3 * cm, 5 * cm, 2 * cm, 3 * cm, 3 * cm, 2 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    # Generar el PDF
    doc.build(elements)

    # Devolver el PDF como respuesta HTTP
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="reporte_documentos.pdf")

#AQUI
@api_view(['GET'])
def exportar_documentos_pdf_filtrado(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    proyecto = request.GET.get('proyecto')

    documentos = Documento.objects.all()

    # Aplicar filtros si existen
    if fecha_inicio:
        documentos = documentos.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        documentos = documentos.filter(fecha_creacion__lte=fecha_fin)
    if estado:
        documentos = documentos.filter(estado=estado)
    if proyecto:
        documentos = documentos.filter(proyecto__nombre__icontains=proyecto)

    # Verificar si hay documentos disponibles
    if not documentos.exists():
        return Response({"error": "No hay documentos disponibles para exportar."}, status=400)

    filtros_aplicados = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado": estado,
        "proyecto": proyecto,
    }
    
    # Registrar historial del reporte
    ReporteHistorial.objects.create(
        usuario=request.user,
        tipo_reporte="PDF",
        filtros_aplicados=json.dumps(filtros_aplicados)
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documentos_report.pdf"'
    
    doc_pdf = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título del reporte
    elements.append(Paragraph("Reporte de Documentos - Constructora Pandora", styles['Title']))

    # Tabla de documentos
    data = [["ID", "Título", "Proyecto", "Estado", "Fecha de Creación"]]
    for doc in documentos:
        data.append([
            doc.id,
            doc.titulo,
            doc.proyecto.nombre if doc.proyecto else "N/A",
            doc.estado,
            doc.fecha_creacion.strftime("%Y-%m-%d")
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc_pdf.build(elements)
    
    return response

@api_view(['GET'])
def exportar_documentos_excel(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')

    documentos = Documento.objects.all()

    if fecha_inicio:
        documentos = documentos.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        documentos = documentos.filter(fecha_creacion__lte=fecha_fin)
    if estado:
        documentos = documentos.filter(estado=estado)

    # Verificar si hay datos antes de generar el Excel
    if not documentos.exists():
        return Response({"error": "No hay documentos disponibles para exportar."}, status=400)

    wb = Workbook()
    ws = wb.active
    ws.title = "Documentos Reporte"

    # Encabezados
    headers = ["ID", "Título", "Proyecto", "Estado", "Fecha de Creación"]
    ws.append(headers)

    # Datos
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categorias_por_proyecto(request, proyecto_id):
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        categorias = proyecto.categorias.all()  # Relación M2M directa
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asociar_categoria_a_proyecto(request, proyecto_id, categoria_id):
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        categoria = Categoria.objects.get(pk=categoria_id)

        if request.data.get("remove"):
            proyecto.categorias.remove(categoria)
            return Response({"detalle": "Categoría eliminada del proyecto."})
        else:
            proyecto.categorias.add(categoria)
            return Response({"detalle": "Categoría asociada correctamente al proyecto."})

    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado."}, status=404)
    except Categoria.DoesNotExist:
        return Response({"error": "Categoría no encontrada."}, status=404)
