from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from documentos.models import Documento, VersionDocumento
from documentos.serializers import DocumentoSerializer, DocumentoAprobarSerializer
from documentos.permissions import (
    PuedeVerDocumentos, PuedeEditarDocumentos,
    PuedeEliminarDocumentos, PuedeAprobarDocumentos
)
from documentos.utils import crear_notificacion
from documentos.filters import DocumentoFilter
from documentos.services.documento_service import eliminar_documento_seguro
from rest_framework.pagination import PageNumberPagination


class DocumentoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DocumentoListCreateView(generics.ListCreateAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated, PuedeVerDocumentos]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentoFilter

    def perform_create(self, serializer):
        documento = serializer.save(usuario=self.request.user, estado='REVISION')
        crear_notificacion(documento.usuario, f"El documento '{documento.titulo}' ha sido creado y está en revisión.")


class DocumentoListView(generics.ListAPIView):
    queryset = Documento.objects.select_related('proyecto', 'categoria', 'usuario').prefetch_related('tags')
    serializer_class = DocumentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentoFilter


class DocumentoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer

    def get_permissions(self):
        permission_map = {
            'GET': [PuedeVerDocumentos()],
            'PUT': [PuedeEditarDocumentos()],
            'PATCH': [PuedeEditarDocumentos()],
            'DELETE': [PuedeEliminarDocumentos()],
        }
        return permission_map.get(self.request.method, [IsAuthenticated()])

    def perform_update(self, serializer):
        instance = self.get_object()
        archivo_anterior = instance.archivo
        updated_instance = serializer.save()
        if archivo_anterior != updated_instance.archivo:
            VersionDocumento.objects.filter(documento=updated_instance).update(activo=False)
            VersionDocumento.objects.create(
                documento=updated_instance,
                archivo=archivo_anterior,
                usuario=self.request.user,
                activo=True
            )

    def destroy(self, request, *args, **kwargs):
        documento_id = self.get_object().id
        success, mensaje = eliminar_documento_seguro(documento_id)
        if success:
            return Response({"message": mensaje}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)


class DocumentoAprobarView(generics.UpdateAPIView):
    queryset = Documento.objects.all()
    serializer_class = DocumentoAprobarSerializer
    permission_classes = [IsAuthenticated, PuedeAprobarDocumentos]

    def perform_update(self, serializer):
        documento = self.get_object()
        documento.estado = 'APROBADO'
        documento.save()
        crear_notificacion(documento.usuario, f"El documento '{documento.titulo}' ha sido aprobado.")
