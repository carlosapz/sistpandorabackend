from documentos.models import Notificacion, VersionDocumento, Documento

def crear_notificacion_documento(documento, mensaje):
    Notificacion.objects.create(usuario=documento.usuario, mensaje=mensaje)

def crear_nueva_version(documento, archivo_anterior, usuario):
    VersionDocumento.objects.filter(documento=documento).update(activo=False)
    VersionDocumento.objects.create(
        documento=documento,
        archivo=archivo_anterior,
        usuario=usuario,
        activo=True
    )

def eliminar_documento_seguro(documento_id):
    try:
        doc = Documento.objects.get(id=documento_id)
        # Seguridad adicional por si el CASCADE no aplica
        doc.historiales.all().delete()
        doc.versiones.all().delete()
        doc.delete()
        return True, "Documento eliminado correctamente"
    except Documento.DoesNotExist:
        return False, "El documento no existe"
    except Exception as e:
        return False, str(e)
