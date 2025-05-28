from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    Documento, Proyecto, Categoria, Tag,
    VersionDocumento, Comentario, Notificacion, HistorialActividad, ReporteHistorial
)

# Documento Admin
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'categoria', 'estado', 'fecha_creacion', 'fecha_actualizacion', 'usuario']
    search_fields = ['titulo', 'descripcion', 'tipo']
    list_filter = ['estado', 'categoria', 'proyecto', 'fecha_creacion', 'tipo']
    actions = ['mark_as_approved', 'mark_as_rejected']
    
    def mark_as_approved(self, request, queryset):
        queryset.update(estado='APROBADO')
        self.message_user(request, "Documentos aprobados exitosamente")
    mark_as_approved.short_description = "Marcar documentos seleccionados como Aprobados"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(estado='RECHAZADO')
        self.message_user(request, "Documentos rechazados exitosamente")
    mark_as_rejected.short_description = "Marcar documentos seleccionados como Rechazados"

# Proyecto Admin
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'responsable']
    search_fields = ['nombre']
    list_filter = ['fecha_inicio', 'fecha_fin']

# Categoria Admin
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

# Tag Admin
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

# Version Documento Admin
@admin.register(VersionDocumento)
class VersionDocumentoAdmin(admin.ModelAdmin):
    list_display = ['documento', 'fecha', 'usuario']
    list_filter = ['fecha', 'usuario']

# Comentario Admin
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['documento', 'usuario', 'fecha']
    search_fields = ['contenido', 'documento__titulo', 'usuario__username']
    list_filter = ['fecha', 'usuario']

# Notificacion Admin
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'mensaje', 'fecha_creacion', 'leido']
    list_filter = ['leido', 'fecha_creacion', 'usuario']
    search_fields = ['mensaje', 'usuario__username']

# Historial Actividad Admin
@admin.register(HistorialActividad)
class HistorialActividadAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'documento', 'accion', 'fecha']
    list_filter = ['accion', 'fecha', 'usuario', 'documento']
    search_fields = ['documento__titulo', 'usuario__username', 'accion']

# Reporte Historial Admin
@admin.register(ReporteHistorial)
class ReporteHistorialAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_generacion', 'filtros_aplicados']
    list_filter = ['fecha_generacion', 'usuario']
    search_fields = ['usuario__username', 'filtros_aplicados']

# Verificar si el modelo está registrado antes de desregistrarlo
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass  # Si no está registrado, simplemente pasamos la excepción

admin.site.register(User, UserAdmin)
