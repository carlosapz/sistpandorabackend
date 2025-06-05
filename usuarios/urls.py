from django.urls import path
from usuarios.views.auth_views import RegistroUsuario, LoginView, AccessDeniedView
from usuarios.views.user_views import (
    ListaUsuarios, DetalleUsuario, current_user, reset_password
)
from usuarios.views.dashboard_views import DashboardView
from usuarios.views.rol_views import ListaRoles

urlpatterns = [
    # Auth
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),

    # Usuarios
    path('', ListaUsuarios.as_view(), name='lista_usuarios'),
    path('roles/', ListaRoles.as_view(), name='lista_roles'),
    path('<int:pk>/', DetalleUsuario.as_view(), name='detalle_usuario'),
    path('<int:user_id>/reset_password/', reset_password, name='reset_password'),
    
    path('me/', current_user, name='current-user'),

    # Roles
    path('roles/', ListaRoles.as_view(), name='lista_roles'),

    # Access Denied
    path('access_denied/', AccessDeniedView.as_view(), name='access_denied'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
