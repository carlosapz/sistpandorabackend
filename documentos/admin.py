from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    Documento,
    Proyecto,
    Categoria,
    Tag,
    VersionDocumento,
    Comentario,
    Notificacion,
    HistorialActividad,
    ReporteHistorial,
    Obra
)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """
    Administración para el modelo Documento.
    Permite listar, buscar, filtrar y realizar acciones masivas.
    """
    list_display = [
        'titulo', 'proyecto', 'categoria', 'estado',
        'fecha_creacion', 'fecha_actualizacion', 'usuario'
    ]
    search_fields = ['titulo', 'descripcion', 'tipo']
    list_filter = ['estado', 'categoria', 'proyecto', 'fecha_creacion', 'tipo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    autocomplete_fields = ['proyecto', 'categoria', 'usuario', 'tags']
    list_per_page = 25

    actions = ['mark_as_approved', 'mark_as_rejected']

    def mark_as_approved(self, request, queryset):
        queryset.update(estado='APROBADO')
        self.message_user(request, "Documentos aprobados exitosamente")
    mark_as_approved.short_description = "Marcar documentos seleccionados como Aprobados"

    def mark_as_rejected(self, request, queryset):
        queryset.update(estado='RECHAZADO')
        self.message_user(request, "Documentos rechazados exitosamente")
    mark_as_rejected.short_description = "Marcar documentos seleccionados como Rechazados"


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """
    Administración para el modelo Proyecto.
    """
    list_display = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'responsable']
    search_fields = ['nombre']
    list_filter = ['fecha_inicio', 'fecha_fin']
    readonly_fields = []
    autocomplete_fields = ['responsable']
    list_per_page = 25


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Administración para el modelo Categoria.
    """
    list_display = ['nombre']
    search_fields = ['nombre']
    list_per_page = 25


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Administración para el modelo Tag.
    """
    list_display = ['nombre']
    search_fields = ['nombre']
    list_per_page = 25


@admin.register(VersionDocumento)
class VersionDocumentoAdmin(admin.ModelAdmin):
    """
    Administración para versiones de documentos.
    """
    list_display = ['documento', 'fecha', 'usuario', 'activo']
    list_filter = ['fecha', 'usuario', 'activo']
    readonly_fields = ['fecha']
    autocomplete_fields = ['documento', 'usuario']
    list_per_page = 25


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """
    Administración para comentarios de documentos.
    """
    list_display = ['documento', 'usuario', 'fecha']
    search_fields = ['contenido', 'documento__titulo', 'usuario__username']
    list_filter = ['fecha', 'usuario']
    readonly_fields = ['fecha']
    autocomplete_fields = ['documento', 'usuario']
    list_per_page = 25


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """
    Administración para notificaciones.
    """
    list_display = ['usuario', 'mensaje', 'fecha_creacion', 'leido']
    list_filter = ['leido', 'fecha_creacion', 'usuario']
    search_fields = ['mensaje', 'usuario__username']
    readonly_fields = ['fecha_creacion']
    autocomplete_fields = ['usuario']
    list_per_page = 25


@admin.register(HistorialActividad)
class HistorialActividadAdmin(admin.ModelAdmin):
    """
    Administración para historial de actividades.
    """
    list_display = ['usuario', 'documento', 'accion', 'fecha']
    list_filter = ['accion', 'fecha', 'usuario', 'documento']
    search_fields = ['documento__titulo', 'usuario__username', 'accion']
    readonly_fields = ['fecha']
    autocomplete_fields = ['usuario', 'documento']
    list_per_page = 25


@admin.register(ReporteHistorial)
class ReporteHistorialAdmin(admin.ModelAdmin):
    """
    Administración para reportes de historial.
    """
    list_display = ['usuario', 'fecha_generacion', 'tipo_reporte', 'filtros_aplicados']
    list_filter = ['fecha_generacion', 'usuario', 'tipo_reporte']
    search_fields = ['usuario__username', 'filtros_aplicados', 'tipo_reporte']
    readonly_fields = ['fecha_generacion']
    autocomplete_fields = ['usuario']
    list_per_page = 25


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    """
    Administración para obras.
    """
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']
    list_per_page = 25


# Override User admin para personalizar si quieres
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)
