from .auth_views import (
    AccessDeniedView,
    LoginView,
    RegistroUsuario,
)

from .user_views import (
    ListaUsuarios,
    DetalleUsuario,
    reset_password,
    current_user,
)

from .dashboard_views import DashboardView

from .rol_views import ListaRoles