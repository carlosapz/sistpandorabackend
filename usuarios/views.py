from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth import authenticate

from .models import Usuario, Rol
from .serializers import UsuarioSerializer, RolSerializer
from .permissions import permiso_especifico

class AccessDeniedView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"error": "Acceso denegado. No tienes permisos para acceder a este recurso."},
            status=status.HTTP_403_FORBIDDEN
        )

class RegistroUsuario(APIView):
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

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Inicio de sesión exitoso",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol.nombre if user.rol else None
            }, status=status.HTTP_200_OK)

        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

class ListaUsuarios(generics.ListAPIView):
    queryset = Usuario.objects.select_related('rol')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')]

    def get_permissions(self):
        permissions = super().get_permissions()
        if not self.request.user.has_perm('puede_gestionar_usuarios'):
            raise PermissionDenied('No tienes permisos para acceder a este recurso.')
        return permissions

class ListaRoles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data)

class DetalleUsuario(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [
        IsAuthenticated,
        permiso_especifico('puede_gestionar_usuarios')
    ]

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()
        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Bienvenido al Dashboard"},
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, permiso_especifico('puede_gestionar_usuarios')])
def reset_password(request, user_id):
    try:
        usuario = Usuario.objects.get(id=user_id)
        usuario.set_password('123')
        usuario.save()
        return Response({'message': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
