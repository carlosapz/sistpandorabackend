from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documentos.models import VersionDocumento
from documentos.serializers import VersionDocumentoSerializer


class VersionDocumentoListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea versiones de un documento específico.
    """
    serializer_class = VersionDocumentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        documento_id = self.request.query_params.get('documento')
        if documento_id:
            return VersionDocumento.objects.filter(documento_id=documento_id).order_by('-fecha')
        return VersionDocumento.objects.none()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class VersionDocumentoDetailView(generics.RetrieveDestroyAPIView):
    """
    Recupera o elimina una versión específica.
    """
    queryset = VersionDocumento.objects.all()
    serializer_class = VersionDocumentoSerializer
    permission_classes = [IsAuthenticated]


class RestaurarVersionAPIView(generics.GenericAPIView):
    """
    Restaura una versión previa de un documento.
    """
    permission_classes = [IsAuthenticated]
    queryset = VersionDocumento.objects.all()

    def post(self, request, pk):
        version = self.get_object()
        documento = version.documento
        documento.archivo = version.archivo
        documento.save()

        VersionDocumento.objects.filter(documento=documento).update(activo=False)
        version.activo = True
        version.save()

        return Response({'detail': 'Versión restaurada correctamente.'})
