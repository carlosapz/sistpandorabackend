# views/cotizacion_futura_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from prediccion.serializers.cotizacion_futura_serializer import CotizacionFuturaSerializer
from prediccion.services.cotizacion_futura_service import simular_cotizacion_futura
from prediccion.models.tipo_cambio import PrediccionTipoCambio
from prediccion.models import Cotizacion, CotizacionFutura, ProductoCotizado, ProductoCotizadoFuturo

# ✅ GENERAR
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generar_cotizacion_futura(request, cotizacion_id):
    pred_id = request.data.get("prediccion_tipo_cambio_id")

    if not pred_id:
        return Response({"error": "Debe proporcionar 'prediccion_tipo_cambio_id'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    except Cotizacion.DoesNotExist:
        return Response({"error": "Cotización no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    try:
        prediccion = PrediccionTipoCambio.objects.get(id=pred_id)
    except PrediccionTipoCambio.DoesNotExist:
        return Response({"error": "Predicción no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if not prediccion.prediccion_json or len(prediccion.prediccion_json) == 0:
        return Response({"error": "Predicción seleccionada no tiene datos."}, status=status.HTTP_400_BAD_REQUEST)

    ultimo_valor = prediccion.prediccion_json[-1]["valor"]

    # ✅ AHORA sí pasamos horizonte_dias
    simulacion = simular_cotizacion_futura(
        cotizacion,
        ultimo_valor,
        horizonte_dias=prediccion.horizonte_dias,
        user=request.user
    )

    serializer = CotizacionFuturaSerializer(simulacion)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ✅ COMPARAR

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def comparar_cotizacion_futura(request, id):
    try:
        cot_futura = CotizacionFutura.objects.get(pk=id)
        cot_original = cot_futura.cotizacion_original

        # ✅ Totales (conversión correcta)
        total_original = float(cot_original.total_general or 0.0)
        total_futura = float(cot_futura.total_bs or 0.0)

        diferencia_total_bs = total_futura - total_original
        diferencia_total_pct = (diferencia_total_bs / total_original) * 100 if total_original > 0 else 0

        # ✅ Productos originales
        productos_original = {
            p.producto.id: {
                "nombre": p.producto.nombre,
                "precio_unitario": float(p.precio_unitario)
            }
            for p in ProductoCotizado.objects.filter(cotizacion=cot_original)
        }

        # ✅ Productos futuros → desde productos_simulados (JSON)
        productos_futuros = {
            p["producto_id"]: {
                "precio_unitario": float(p["precio_unitario"])
            }
            for p in cot_futura.productos_simulados
        }

        # ✅ Comparar productos
        productos_comparados = []

        for prod_id, prod_orig in productos_original.items():
            precio_orig = prod_orig["precio_unitario"]
            precio_fut = productos_futuros.get(prod_id, {}).get("precio_unitario", precio_orig)

            diferencia_bs = precio_fut - precio_orig
            diferencia_pct = (diferencia_bs / precio_orig) * 100 if precio_orig > 0 else 0

            productos_comparados.append({
                "nombre": prod_orig["nombre"],
                "precio_original": round(precio_orig, 2),
                "precio_futura": round(precio_fut, 2),
                "diferencia_bs": round(diferencia_bs, 2),
                "diferencia_pct": round(diferencia_pct, 2)
            })

        # ✅ Respuesta
        data = {
            "cotizacion_original": {
                "id": cot_original.id,
                "nombre": cot_original.nombre,
                "total_general": total_original,
                "tipo_cambio_origen": cot_original.tipo_cambio_origen,
                "tipo_cambio_valor": float(cot_original.tipo_cambio_valor or 0.0)
            },
            "cotizacion_futura": {
                "id": cot_futura.id,
                "nombre": cot_futura.nombre,
                "total_general": total_futura,
                "tipo_cambio_origen": cot_futura.tipo_cambio_origen,
                "tipo_cambio_valor": float(cot_futura.dolar_usado or 0.0)
            },
            "productos_comparados": productos_comparados,
            "diferencia_total_bs": round(diferencia_total_bs, 2),
            "diferencia_total_pct": round(diferencia_total_pct, 2)
        }

        return Response(data)

    except CotizacionFutura.DoesNotExist:
        return Response({"error": "Cotización futura no encontrada"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



# ✅ LISTAR
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_cotizaciones_futuras(request):
    cotizaciones_futuras = CotizacionFutura.objects.order_by("-fecha_generacion")
    serializer = CotizacionFuturaSerializer(cotizaciones_futuras, many=True)
    return Response(serializer.data)

# ✅ DETALLE
class CotizacionFuturaDetailView(generics.RetrieveAPIView):
    queryset = CotizacionFutura.objects.all()
    serializer_class = CotizacionFuturaSerializer

# ✅ ELIMINAR
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_cotizacion_futura(request, pk):
    try:
        cot_futura = CotizacionFutura.objects.get(pk=pk)
        cot_futura.delete()
        return Response({"detail": "Cotización futura eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)
    except CotizacionFutura.DoesNotExist:
        return Response({"error": "Cotización futura no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
