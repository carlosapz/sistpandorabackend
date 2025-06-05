from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from documentos.models import Notificacion
from documentos.serializers import NotificacionSerializer


class NotificacionListView(generics.ListAPIView):
    """
    Lista las notificaciones del usuario autenticado.
    Permite filtrar por si están leídas o no.
    """
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        leido = self.request.query_params.get('leido', None)
        queryset = Notificacion.objects.filter(usuario=self.request.user)
        if leido is not None:
            queryset = queryset.filter(leido=(leido.lower() == 'true'))
        return queryset


class MarcarNotificacionLeidaView(APIView):
    """
    Marca una notificación como leída.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notificacion = Notificacion.objects.get(pk=pk, usuario=request.user)
            notificacion.leido = True
            notificacion.save()
            return Response({"message": "Notificación marcada como leída."})
        except Notificacion.DoesNotExist:
            raise NotFound("Notificación no encontrada.")
