from rest_framework.permissions import BasePermission

class TienePermisoEspecifico(BasePermission):
    def __init__(self, permiso_requerido):
        self.permiso_requerido = permiso_requerido

    def has_permission(self, request, view):
        usuario = request.user
        if usuario.is_superuser:
            return True
        if hasattr(usuario, "rol") and usuario.rol and usuario.rol.permisos:
            return usuario.rol.permisos.get(self.permiso_requerido, False)
        return False

def permiso_especifico(permiso):
    class PermisoEspecificoWrapper(TienePermisoEspecifico):
        def __init__(self):
            super().__init__(permiso_requerido=permiso)
    return PermisoEspecificoWrapper
