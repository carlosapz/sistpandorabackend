from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from documentos.models import Comentario
from documentos.serializers import ComentarioSerializer


class ComentarioListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea comentarios para documentos.
    """
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ComentarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detalle, edición o eliminación de un comentario.
    """
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]
