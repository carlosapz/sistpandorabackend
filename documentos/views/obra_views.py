from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from documentos.models import Obra
from documentos.serializers import ObraSerializer


class ObraListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea obras en el sistema.
    """
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]


class ObraDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, actualiza o elimina una obra específica.
    """
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]
