from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from dateutil import parser
from datetime import timedelta
from .models import PrediccionHistorica


import pandas as pd
import traceback

from .models import Producto, Cotizacion
from .serializers import ProductoSerializer, CotizacionSerializer, ProductoCotizadoSerializer, PrediccionHistoricaSerializer
from .services.predictor import predecir_precio_actual
from documentos.models import Proyecto, Categoria
from .utils import obtener_precio_dolar, obtener_dolar_paralelo

class ProductoListView(generics.ListAPIView):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer

class ProductoCreateView(generics.CreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

class PrecioPrediccionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        producto_id = request.data.get("producto_id")
        proyecto_id = request.data.get("proyecto_id")
        categoria_id = request.data.get("categoria_id")
        tipo_cambio_origen = request.data.get("tipo_cambio_origen", "Oficial")
        tipo_cambio_valor = request.data.get("tipo_cambio_valor")

        print(f"[DEBUG] tipo_cambio_origen recibido: {tipo_cambio_origen}")
        print(f"[DEBUG] tipo_cambio_valor recibido: {tipo_cambio_valor}")

        if not producto_id:
            return Response({"error": "Falta producto_id."}, status=400)

        try:
            if tipo_cambio_valor is not None:
                tipo_cambio_valor = float(tipo_cambio_valor)
        except ValueError:
            return Response({"error": "tipo_cambio_valor debe ser numérico"}, status=400)

        try:
            producto = Producto.objects.get(id=producto_id)
            if proyecto_id:
                Proyecto.objects.get(id=proyecto_id)
            if categoria_id:
                Categoria.objects.get(id=categoria_id)

            # 1. Hacer la predicción
            precio_estimado_bs = predecir_precio_actual(
                producto, tipo_cambio_origen, tipo_cambio_valor
            )

            # 2. Calcular precio en USD
            precio_estimado_usd = (
                precio_estimado_bs / float(tipo_cambio_valor)
                if tipo_cambio_valor
                else None
            )

            # 3. Guardar en PrediccionHistorica
            PrediccionHistorica.objects.create(
                producto=producto,
                precio_estimado_bs=precio_estimado_bs,
                precio_estimado_usd=precio_estimado_usd,
                tipo_cambio_utilizado=tipo_cambio_valor or 0,
                tipo_cambio_origen=tipo_cambio_origen,
                usuario=request.user,
            )

            return Response({
                "producto": producto.nombre,
                "unidad_medida": producto.unidad_medida,
                "precio_estimado": precio_estimado_bs
            }, status=200)

        except (Producto.DoesNotExist, Proyecto.DoesNotExist, Categoria.DoesNotExist) as e:
            return Response({"error": str(e)}, status=404)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=400)

        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historico_predicciones_producto(request, producto_id):
    try:
        predicciones = PrediccionHistorica.objects.filter(
            producto_id=producto_id
        ).order_by("fecha_prediccion")

        serializer = PrediccionHistoricaSerializer(predicciones, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_precios_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)

        if not producto.csv_datos:
            return Response({"error": "Producto sin datos."}, status=400)

        tipo_cambio = request.query_params.get("tipo", "oficial").lower()

        df = pd.read_csv(producto.csv_datos.path)

        if "fecha" not in df.columns or "precio_unitario_bob" not in df.columns:
            return Response({"error": "CSV inválido o incompleto."}, status=400)

        if tipo_cambio == "paralelo":
            if "precio_unitario_usd" not in df.columns:
                return Response({"error": "CSV sin columna 'precio_unitario_usd'"}, status=400)
            df["precio_bs"] = df["precio_unitario_usd"] * obtener_dolar_paralelo()
        else:
            df["precio_bs"] = df["precio_unitario_bob"]

        df = df[["fecha", "precio_bs"]].dropna()
        df = df.sort_values("fecha")

        datos = [
            {"fecha": row["fecha"], "precio": round(row["precio_bs"], 2)}
            for _, row in df.iterrows()
        ]

        return Response({
            "producto": producto.nombre,
            "unidad": producto.unidad_medida,
            "datos": datos
        })

    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado."}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

class CotizacionCreateView(generics.CreateAPIView):
    queryset = Cotizacion.objects.all()
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

    def get_queryset(self):
        return Cotizacion.objects.filter(usuario=self.request.user).order_by('-fecha')

class CotizacionDetailView(generics.RetrieveAPIView):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]

class CotizacionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Cotizacion.objects.all()
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
            cotizacion = Cotizacion.objects.get(id=pk)

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

            for producto_cotizado in cotizacion.productos_cotizados.all():
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
    try:
        cotizacion = Cotizacion.objects.get(pk=pk)
        cotizacion.delete()
        return Response({"message": "Cotización eliminada."}, status=204)
    except Cotizacion.DoesNotExist:
        return Response({"error": "Cotización no encontrada."}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def descargar_cotizacion_pdf(request, pk):
    try:
        cotizacion = Cotizacion.objects.get(pk=pk, usuario=request.user)
        html_string = render_to_string("cotizacion_pdf.html", {
            "cotizacion": cotizacion,
            "productos": cotizacion.productos_cotizados.all(),
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.id}.pdf"'
        pisa.CreatePDF(html_string, dest=response)

        return response
    except Cotizacion.DoesNotExist:
        return HttpResponse("Cotización no encontrada", status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_dolar_view(request):
    precio = obtener_precio_dolar()
    return Response({"moneda": "BOB", "valor": precio}) if precio else Response({"error": "No se pudo obtener."}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_dolar_paralelo_view(request):
    precio = obtener_dolar_paralelo()
    return Response({"moneda": "BOB", "valor": precio}) if precio else Response({"error": "No se pudo obtener."}, status=500)
