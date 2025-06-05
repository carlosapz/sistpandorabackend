import logging
from rest_framework.permissions import BasePermission # type: ignore
from rest_framework.exceptions import PermissionDenied # type: ignore

logger = logging.getLogger(__name__)

class PuedeVerDocumentos(BasePermission):
    """
    Permiso para permitir a un usuario ver documentos.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Puedes agregar lógica extra aquí si necesitas
            return True
        logger.warning(f"Acceso denegado para ver documentos - Usuario: {request.user}")
        return False


class PuedeEditarDocumentos(BasePermission):
    """
    Permiso para permitir a un usuario editar documentos.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.has_perm('documentos.change_documento'):
            return True
        logger.warning(f"Acceso denegado para editar documentos - Usuario: {request.user}")
        raise PermissionDenied("No tiene permiso para editar documentos.")


class PuedeEliminarDocumentos(BasePermission):
    """
    Permiso para permitir a un usuario eliminar documentos.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.has_perm('documentos.delete_documento'):
            return True
        logger.warning(f"Acceso denegado para eliminar documentos - Usuario: {request.user}")
        raise PermissionDenied("No tiene permiso para eliminar documentos.")


class PuedeAprobarDocumentos(BasePermission):
    """
    Permiso para permitir a un usuario aprobar documentos.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.has_perm('documentos.approve_documento'):
            return True
        logger.warning(f"Acceso denegado para aprobar documentos - Usuario: {request.user}")
        raise PermissionDenied("No tiene permiso para aprobar documentos.")
