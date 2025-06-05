from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from usuarios.models.usuario import Usuario
from usuarios.models.rol import Rol
from usuarios.serializers.usuario_serializer import UsuarioSerializer
from usuarios.permissions import permiso_especifico

class AccessDeniedView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"error": "Acceso denegado. No tienes permisos para acceder a este recurso."},
            status=status.HTTP_403_FORBIDDEN
        )

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
