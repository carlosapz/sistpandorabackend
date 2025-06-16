# prediccion/views/registro_dolar_view.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from prediccion.models import RegistroDolarSistema
from prediccion.utils.currency_utils import obtener_dolar_paralelo

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_guardar_dolar_diario(request):
    hoy = date.today()

    if RegistroDolarSistema.objects.filter(fecha=hoy).exists():
        return Response({"mensaje": f"Ya se registró el valor del dólar hoy ({hoy})"}, status=200)

    valor = obtener_dolar_paralelo()
    RegistroDolarSistema.objects.create(fecha=hoy, valor=valor)

    return Response({"mensaje": f"Valor registrado: {valor} Bs en fecha {hoy}"})
