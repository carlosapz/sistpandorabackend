from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from documentos.models import Obra
from documentos.serializers import ObraSerializer

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from documentos.services.pdf_service import generar_pdf_resumen_obra
from rest_framework.renderers import BaseRenderer


# CUSTOM PDF RENDERER
class PDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


# VISTA LISTA Y CREA OBRAS
class ObraListCreateView(generics.ListCreateAPIView):
    queryset = Obra.objects.all().order_by('-fecha_inicio')
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]


# VISTA DETALLE, ACTUALIZA Y ELIMINA OBRAS
class ObraDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]


# VISTA QUE GENERA Y DEVUELVE EL PDF
@api_view(["GET"])
@renderer_classes([PDFRenderer])  # ✅ Acepta application/pdf
def descargar_resumen_obra_pdf(request, obra_id):
    token = request.GET.get("token")
    if not token:
        return Response({"detail": "Token requerido."}, status=401)

    jwt_auth = JWTAuthentication()
    try:
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        request.user = user  # Importante para futuras validaciones
    except Exception:
        raise AuthenticationFailed("Token inválido o expirado")

    return generar_pdf_resumen_obra(obra_id)
