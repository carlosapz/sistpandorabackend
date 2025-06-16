from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from prediccion.services.tipo_cambio_service import guardar_tipo_cambio_historico
from prediccion.services.forecast_prophet import generar_forecast_prophet  # <- ¡Nuevo import!
from prediccion.models import PrediccionTipoCambio, TipoCambioHistorico
from prediccion.serializers.prediccion_tipo_cambio_serializer import PrediccionTipoCambioSerializer

import pandas as pd
import os


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_guardar_tipo_cambio_historico(request):
    result = guardar_tipo_cambio_historico()
    return Response({"mensaje": result})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_generar_prediccion_tipo_cambio(request):
    horizonte = int(request.data.get("horizonte_dias", 30))
    origen = request.data.get("tipo_cambio_origen", "Paralelo")
    comentario = request.data.get("comentario", "")

    # ⚡ Generar la predicción con Prophet
    prediccion_json = generar_forecast_prophet(horizonte_dias=horizonte, tipo_cambio_origen=origen)

    # ✅ Guardar en la base de datos como antes
    pred = PrediccionTipoCambio.objects.create(
        horizonte_dias=horizonte,
        tipo_cambio_origen=origen,
        prediccion_json=prediccion_json,
        comentario=comentario,
        nombre_modelo="prophet_v1"
    )

    serializer = PrediccionTipoCambioSerializer(pred)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_listar_predicciones_tipo_cambio(request):
    predicciones = PrediccionTipoCambio.objects.order_by("-fecha_prediccion")
    serializer = PrediccionTipoCambioSerializer(predicciones, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_verificar_archivos_modelo_csv(request):
    MODEL_PATH = "modelos_tipo_cambio/lstm_tipo_cambio_paralelo_mejorado.keras"
    CSV_PATH = "modelos_tipo_cambio/historico_dolarboliviahoy.csv"

    model_exists = os.path.exists(MODEL_PATH)
    csv_exists = os.path.exists(CSV_PATH)

    return Response({
        "model_exists": model_exists,
        "csv_exists": csv_exists
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def api_subir_archivos_modelo_csv(request):
    MODEL_DIR = "modelos_tipo_cambio"
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_file = request.FILES.get("model_file")
    csv_file = request.FILES.get("csv_file")

    response = {}

    if model_file:
        model_path = os.path.join(MODEL_DIR, "lstm_tipo_cambio_paralelo_mejorado.keras")
        with open(model_path, "wb+") as f:
            for chunk in model_file.chunks():
                f.write(chunk)
        response["model_saved"] = True
    else:
        response["model_saved"] = False

    if csv_file:
        csv_path = os.path.join(MODEL_DIR, "historico_dolarboliviahoy.csv")
        with open(csv_path, "wb+") as f:
            for chunk in csv_file.chunks():
                f.write(chunk)
        response["csv_saved"] = True
    else:
        response["csv_saved"] = False

    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_historico_tipo_cambio(request):
    historico = TipoCambioHistorico.objects.order_by("fecha").values("fecha", "tipo_cambio_paralelo")
    data = [
        {"fecha": h["fecha"], "valor": h["tipo_cambio_paralelo"]}
        for h in historico
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_historico_tipo_cambio_ccv(request):
    csv_path = "modelos_tipo_cambio/historico_dolarboliviahoy.csv"

    try:
        df = pd.read_csv(csv_path)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        start_date = request.GET.get("start")
        end_date = request.GET.get("end")

        if start_date:
            df = df[df["fecha"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["fecha"] <= pd.to_datetime(end_date)]

        data = [
            {"fecha": row["fecha"].strftime("%Y-%m-%d"), "valor": row["precio_compra"]}
            for _, row in df.iterrows()
        ]

        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_comparar_predicciones_tipo_cambio(request):
    id1 = request.GET.get("id1")
    id2 = request.GET.get("id2")

    if not id1 or not id2:
        return Response({"error": "Debe proporcionar id1 y id2"}, status=400)

    try:
        p1 = PrediccionTipoCambio.objects.get(pk=id1)
        p2 = PrediccionTipoCambio.objects.get(pk=id2)
    except PrediccionTipoCambio.DoesNotExist:
        return Response({"error": "Predicción no encontrada"}, status=404)

    s = PrediccionTipoCambioSerializer

    return Response({
        "prediccion_1": s(p1).data,
        "prediccion_2": s(p2).data
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def api_eliminar_prediccion_tipo_cambio(request, pk):
    try:
        pred = PrediccionTipoCambio.objects.get(pk=pk)
        pred.delete()
        return Response({"mensaje": "Predicción eliminada correctamente"})
    except PrediccionTipoCambio.DoesNotExist:
        return Response({"error": "Predicción no encontrada"}, status=404)
