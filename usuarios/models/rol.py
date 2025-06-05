from django.db import models  # type: ignore

class Rol(models.Model):
    """
    Modelo que define un rol de usuario, con permisos personalizados para la aplicación.
    """
    nombre = models.CharField(max_length=50, unique=True)
    permisos = models.JSONField(default=dict)
    puede_ver_documentos = models.BooleanField(default=True)
    puede_editar_documentos = models.BooleanField(default=False)
    puede_eliminar_documentos = models.BooleanField(default=False)
    puede_aprobar_documentos = models.BooleanField(default=False)
    puede_gestionar_usuarios = models.BooleanField(default=False)
    puede_gestionar_costos = models.BooleanField(default=False)
    puede_gestionar_reportes = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
