from django.urls import path
from .views import (
    DocumentoListCreateView, DocumentoListView, DocumentoDetailView,
    DocumentoAprobarView, exportar_documentos_csv, exportar_documentos_pdf,
    exportar_documentos_excel, exportar_documentos_pdf_filtrado,  # ✅ NUEVA IMPORTACIÓN
    ProyectoListCreateView, ProyectoDetailView,
    CategoriaListCreateView, TagListCreateView,
    VersionDocumentoListCreateView, VersionDocumentoDetailView, RestaurarVersionAPIView, ComentarioListCreateView,
    ComentarioDetailView, NotificacionListView, HistorialActividadListView,
    exportar_historial_csv, exportar_historial_pdf, ObraListCreateView, ObraDetailView,
    MarcarNotificacionLeidaView, categorias_por_proyecto, asociar_categoria_a_proyecto
)

app_name = 'documentos'

urlpatterns = [
    # Proyectos
    path('proyectos/', ProyectoListCreateView.as_view(), name='proyecto-list-create'),
    path('proyectos/<int:pk>/', ProyectoDetailView.as_view(), name='proyecto-detail'),
    path('proyectos/<int:proyecto_id>/categorias/', categorias_por_proyecto, name='categorias-por-proyecto'),
    path('proyectos/<int:proyecto_id>/categorias/<int:categoria_id>/asociar/', asociar_categoria_a_proyecto, name='asociar-categoria-a-proyecto'),

    # Categorías
    path('categorias/', CategoriaListCreateView.as_view(), name='categoria-list-create'),

    # Tags
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),

    # Documentos
    path('', DocumentoListCreateView.as_view(), name='documento-list-create'),
    path('filtrar/', DocumentoListView.as_view(), name='documento-list-filtrar'),
    path('<int:pk>/', DocumentoDetailView.as_view(), name='documento-detail'),
    path('<int:pk>/aprobar/', DocumentoAprobarView.as_view(), name='documento-aprobar'),
    path('versiones/', VersionDocumentoListCreateView.as_view(), name='version-documento-list-create'),

    # Exportar documentos
    path('exportar/csv/', exportar_documentos_csv, name='exportar-documentos-csv'),
    path('exportar/pdf/', exportar_documentos_pdf, name='exportar-documentos-pdf'),
    path('exportar/excel/', exportar_documentos_excel, name='exportar-documentos-excel'),
    path('exportar/pdf-filtrado/', exportar_documentos_pdf_filtrado, name='exportar-documentos-pdf-filtrado'),

    # Historial actividades
    path('historial/', HistorialActividadListView.as_view(), name='historial-actividad-list'),
    path('historial/exportar/csv/', exportar_historial_csv, name='exportar-historial-csv'),
    path('historial/exportar/pdf/', exportar_historial_pdf, name='exportar-historial-pdf'),

    # Obras
    path('obras/', ObraListCreateView.as_view(), name='obra-list-create'),
    path('obras/<int:pk>/', ObraDetailView.as_view(), name='obra-detail'),

    # Versiones documentos
    path('versiones/', VersionDocumentoListCreateView.as_view(), name='version-documento-list-create'),
    path('versiones/<int:pk>/restaurar/', RestaurarVersionAPIView.as_view(), name='restaurar-version'),
    path('versiones/<int:pk>/', VersionDocumentoDetailView.as_view(), name='version-documento-detail'),

    # Comentarios documentos
    path('comentarios/', ComentarioListCreateView.as_view(), name='comentario-list-create'),
    path('comentarios/<int:pk>/', ComentarioDetailView.as_view(), name='comentario-detail'),

    # Notificaciones
    path('notificaciones/', NotificacionListView.as_view(), name='notificacion-list'),
    path('notificaciones/<int:pk>/leer/', MarcarNotificacionLeidaView.as_view(), name='marcar-notificacion-leida'),
]
