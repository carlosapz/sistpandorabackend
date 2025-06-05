from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models.usuario import Usuario
from usuarios.models.rol import Rol

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "rol", "is_staff", "is_superuser", "is_active")
    list_filter = ("rol", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "rol__nombre")
    ordering = ("username",)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ["nombre", "puede_ver_documentos", "puede_editar_documentos", "puede_eliminar_documentos", "puede_aprobar_documentos"]
