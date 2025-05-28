from django.urls import path
from .views import reset_password, RegistroUsuario, LoginView, ListaUsuarios, ListaRoles, DetalleUsuario, AccessDeniedView, DashboardView, current_user

urlpatterns = [
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('', ListaUsuarios.as_view(), name='lista_usuarios'),
    path('roles/', ListaRoles.as_view(), name='lista_roles'),
    path('<int:pk>/', DetalleUsuario.as_view(), name='detalle_usuario'),
    path('<int:user_id>/reset_password/', reset_password, name='reset_password'),
    
    path('me/', current_user, name='current-user'),
    path('access_denied/', AccessDeniedView.as_view(), name='access_denied'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
