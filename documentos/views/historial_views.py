from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from documentos.models import HistorialActividad
from documentos.serializers import HistorialActividadSerializer


class HistorialActividadListView(generics.ListAPIView):
    """
    Lista el historial de actividades realizadas por los usuarios.
    Se puede filtrar por usuario, acción, fecha y documento.
    """
    queryset = HistorialActividad.objects.all().order_by('-fecha')
    serializer_class = HistorialActividadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['usuario', 'accion', 'fecha', 'documento']
