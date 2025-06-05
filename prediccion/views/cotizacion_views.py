from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from dateutil import parser
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from prediccion.models.cotizacion import Cotizacion, ProductoCotizado
from prediccion.serializers.cotizacion_serializer import CotizacionSerializer
from prediccion.services.predictor import predecir_precio_actual
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo
from prediccion.services.pdf_service import generar_pdf_cotizacion  # 👈 nuevo import

class CotizacionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class CotizacionCreateView(generics.CreateAPIView):
    queryset = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria')
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        tipo_cambio = self.request.data.get("tipo_cambio_valor") or obtener_precio_dolar()
        if tipo_cambio is None:
            raise ValueError("No se pudo obtener tipo de cambio.")
        serializer.save(
            tipo_cambio_dolar=tipo_cambio,
            fecha_validez=timezone.now() + timedelta(weeks=1)
        )

class CotizacionListView(generics.ListAPIView):
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CotizacionPagination

    def get_queryset(self):
        return Cotizacion.objects.select_related('proyecto', 'categoria', 'usuario').filter(
            usuario=self.request.user
        ).order_by('-fecha')

@method_decorator(cache_page(60 * 5), name='dispatch')
class CotizacionDetailView(generics.RetrieveAPIView):
    queryset = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria')
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]

class CotizacionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria')
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_update(self, serializer):
        fecha_validez = self.request.data.get('fecha_validez')
        fecha_validez = parser.parse(fecha_validez) if fecha_validez else timezone.now() + timedelta(days=7)
        serializer.save(fecha_validez=fecha_validez)

class CotizacionRecalcularView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            cotizacion = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria').get(id=pk)

            tipo_cambio_origen = request.data.get('tipo_cambio_origen', 'oficial')
            tipo_cambio_valor = request.data.get('tipo_cambio_valor')

            if tipo_cambio_valor is None:
                tipo_cambio_valor = obtener_dolar_paralelo() if tipo_cambio_origen.lower() == 'paralelo' else obtener_precio_dolar()

            try:
                tipo_cambio_valor = float(tipo_cambio_valor)
            except (TypeError, ValueError):
                return Response({"error": "tipo_cambio_valor inválido"}, status=400)

            cotizacion.tipo_cambio_dolar = tipo_cambio_valor
            cotizacion.fecha_validez = timezone.now() + timedelta(weeks=1)

            nuevo_total = 0
            productos_cotizados = cotizacion.productos_cotizados.select_related('producto')

            for producto_cotizado in productos_cotizados:
                producto = producto_cotizado.producto
                nuevo_precio_unitario = predecir_precio_actual(
                    producto,
                    tipo_cambio_origen=tipo_cambio_origen,
                    tipo_cambio_valor=tipo_cambio_valor
                )
                producto_cotizado.precio_unitario = nuevo_precio_unitario
                producto_cotizado.total = nuevo_precio_unitario * producto_cotizado.cantidad
                producto_cotizado.save()
                nuevo_total += producto_cotizado.total

            cotizacion.total_general = nuevo_total
            cotizacion.save()

            return Response({"message": "Cotización recalculada correctamente."}, status=200)

        except Cotizacion.DoesNotExist:
            return Response({"error": "Cotización no encontrada."}, status=404)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_cotizacion(request, pk):
    """
    Elimina una cotización.
    """
    try:
        cotizacion = Cotizacion.objects.get(pk=pk)
        cotizacion.delete()
        return Response({"message": "Cotización eliminada."}, status=204)
    except Cotizacion.DoesNotExist:
        return Response({"error": "Cotización no encontrada."}, status=404)

@cache_page(60 * 5)  # Cache 5 mins
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def descargar_cotizacion_pdf(request, pk):
    """
    Genera y descarga el PDF de una cotización.
    """
    try:
        response = generar_pdf_cotizacion(request.user, pk)
        return response
    except Cotizacion.DoesNotExist:
        return HttpResponse("Cotización no encontrada", status=404)
    except Exception as e:
        return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
