from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from usuarios.models.usuario import Usuario
from usuarios.models.rol import Rol
from usuarios.serializers.usuario_serializer import UsuarioSerializer
from usuarios.serializers.rol_serializer import RolSerializer
from usuarios.permissions import permiso_especifico

class UsuarioPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100

class RegistroUsuario(APIView):
    """
    Permite el registro de nuevos usuarios por admin/usuarios autorizados.
    """
    permission_classes = [IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')]

    def post(self, request):
        data = request.data.copy()
        if 'rol' not in data or not data['rol']:
            try:
                rol_default = Rol.objects.get(nombre="Usuario General")
                data['rol'] = rol_default.id
            except Rol.DoesNotExist:
                return Response(
                    {"error": "El rol por defecto no existe"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            usuario = serializer.save()
            usuario.set_password(data['password'])
            usuario.is_staff = data.get('is_staff', False)
            usuario.is_active = data.get('is_active', True)
            usuario.is_superuser = data.get('is_superuser', False)
            usuario.save()
            return Response({
                "message": "Usuario registrado exitosamente",
                "user_id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "first_name": usuario.first_name,
                "last_name": usuario.last_name,
                "rol": usuario.rol.nombre if usuario.rol else None
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListaUsuarios(generics.ListAPIView):
    """
    Lista usuarios del sistema (requiere permisos).
    """
    queryset = Usuario.objects.select_related('rol')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')]
    pagination_class = UsuarioPagination

    def get_permissions(self):
        permissions = super().get_permissions()
        if not self.request.user.has_perm('puede_gestionar_usuarios'):
            raise PermissionDenied('No tienes permisos para acceder a este recurso.')
        return permissions

class DetalleUsuario(generics.RetrieveUpdateDestroyAPIView):
    """
    Detalle, edición y borrado de usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')]

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()
        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Obtiene los datos del usuario autenticado actual.
    """
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')])
def reset_password(request, user_id):
    """
    Restablece la contraseña de un usuario a '123' (ejemplo, cambiar por algo seguro en producción).
    """
    try:
        usuario = Usuario.objects.get(id=user_id)
        usuario.set_password('123')
        usuario.save()
        return Response({'message': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
