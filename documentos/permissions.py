from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class PuedeVerDocumentos(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verifica si el usuario está autenticado y tiene el permiso adecuado
        return request.user.is_authenticated and getattr(request.user, 'rol', None) and request.user.rol.puede_ver_documentos

class PuedeEditarDocumentos(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if not getattr(request.user, 'rol', None):
            raise PermissionDenied("Tu usuario no tiene un rol asignado.")
        if not request.user.rol.puede_editar_documentos:
            raise PermissionDenied("No tienes permiso para editar documentos.")
        return True

class PuedeEliminarDocumentos(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verifica si el usuario tiene el permiso para eliminar documentos
        return (
            request.user.is_authenticated 
            and getattr(request.user, 'rol', None)
            and request.user.rol.puede_eliminar_documentos
            and request.user.is_staff  # Solo administradores pueden eliminar
        )

class PuedeAprobarDocumentos(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verifica si el usuario tiene el permiso para aprobar documentos
        return (
            request.user.is_authenticated 
            and getattr(request.user, 'rol', None)
            and request.user.rol.puede_aprobar_documentos
            and request.user.is_superuser  # Solo superusuarios pueden aprobar documentos
        )
