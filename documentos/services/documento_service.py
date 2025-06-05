# documentos/services/documento_service.py

from documentos.models import Notificacion, VersionDocumento

def crear_notificacion_documento(documento, mensaje):
    """
    Crea una notificación para el usuario del documento.
    """
    Notificacion.objects.create(
        usuario=documento.usuario,
        mensaje=mensaje
    )

def crear_nueva_version(documento, archivo_anterior, usuario):
    """
    Crea una nueva versión de un documento.
    """
    VersionDocumento.objects.filter(documento=documento).update(activo=False)

    VersionDocumento.objects.create(
        documento=documento,
        archivo=archivo_anterior,
        usuario=usuario,
        activo=True
    )
