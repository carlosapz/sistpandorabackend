from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from documentos.models import Proyecto, Categoria, Tag
from documentos.serializers import ProyectoSerializer, CategoriaSerializer, TagSerializer

class ProyectoListCreateView(generics.ListCreateAPIView):
    """
    Listar y crear proyectos.
    """
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]


class ProyectoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtener, actualizar o eliminar un proyecto.
    """
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]


class CategoriaListCreateView(generics.ListCreateAPIView):
    """
    Listar y crear categorías.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


class TagListCreateView(generics.ListCreateAPIView):
    """
    Listar y crear etiquetas (tags).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
