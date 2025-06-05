from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models.rol import Rol
from usuarios.serializers.rol_serializer import RolSerializer

class ListaRoles(APIView):
    """
    Devuelve todos los roles disponibles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data)
