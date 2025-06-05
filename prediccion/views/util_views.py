from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_dolar_view(request):
    """
    Devuelve el precio del dólar oficial.
    """
    precio = obtener_precio_dolar()
    return Response({"moneda": "BOB", "valor": precio}) if precio else Response({"error": "No se pudo obtener."}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_dolar_paralelo_view(request):
    """
    Devuelve el precio del dólar paralelo.
    """
    precio = obtener_dolar_paralelo()
    return Response({"moneda": "BOB", "valor": precio}) if precio else Response({"error": "No se pudo obtener."}, status=500)
