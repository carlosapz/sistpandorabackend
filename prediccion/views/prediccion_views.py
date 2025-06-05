from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from prediccion.models.producto import Producto
from prediccion.models.prediccion_historica import PrediccionHistorica
from prediccion.serializers.prediccion_historica_serializer import PrediccionHistoricaSerializer
from documentos.models import Proyecto, Categoria
from prediccion.services.predictor import predecir_precio_actual
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo

import traceback
import pandas as pd

class PrecioPrediccionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Calcula la predicción de precio para un producto y guarda el resultado como histórico.
        """
        producto_id = request.data.get("producto_id")
        proyecto_id = request.data.get("proyecto_id")
        categoria_id = request.data.get("categoria_id")
        tipo_cambio_origen = request.data.get("tipo_cambio_origen", "Oficial")
        tipo_cambio_valor = request.data.get("tipo_cambio_valor")

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

            precio_estimado_bs = predecir_precio_actual(producto, tipo_cambio_origen, tipo_cambio_valor)
            precio_estimado_usd = (precio_estimado_bs / float(tipo_cambio_valor)) if tipo_cambio_valor else None

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

@method_decorator(cache_page(60 * 5), name='dispatch') 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historico_predicciones_producto(request, producto_id):
    """
    Devuelve el historial de predicciones para un producto.
    """
    try:
        predicciones = PrediccionHistorica.objects.select_related('producto', 'usuario').filter(
            producto_id=producto_id
        ).order_by("-fecha_prediccion")

        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        serializer = PrediccionHistoricaSerializer(predicciones[start:end], many=True)
        return Response({
            "count": predicciones.count(),
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@cache_page(60 * 10)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_precios_producto(request, producto_id):
    """
    Devuelve el historial de precios de un producto en base a su CSV.
    """
    try:
        producto = Producto.objects.get(id=producto_id)
        if not producto.csv_datos:
            return Response({"error": "Producto sin datos."}, status=400)

        tipo_cambio = request.query_params.get("tipo", "oficial").lower()

        df = pd.read_csv(producto.csv_datos.path)

        # Validación de columnas
        if "fecha" not in df.columns or "precio_unitario_bob" not in df.columns:
            return Response({"error": "CSV inválido o incompleto."}, status=400)

        # Cálculo de precio según tipo de cambio
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
