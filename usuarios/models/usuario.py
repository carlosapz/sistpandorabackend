from django.contrib.auth.models import AbstractUser, Group, Permission # type: ignore
from django.db import models # type: ignore
from .rol import Rol  # Importa tu modelo de rol

class Usuario(AbstractUser):
    """
    Modelo de usuario extendido para soportar roles personalizados y permisos adicionales.
    """
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="Grupos a los que pertenece este usuario.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Permisos específicos para este usuario.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username

    def tiene_permiso(self, permiso):
        """
        Verifica si el usuario tiene un permiso específico por rol.
        """
        if self.rol and hasattr(self.rol, permiso):
            return getattr(self.rol, permiso)
        return False
