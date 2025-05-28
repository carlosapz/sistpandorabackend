from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Rol(models.Model):
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

class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

class HistorialActividad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion}"