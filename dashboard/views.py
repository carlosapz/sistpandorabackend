from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from random import choice
from datetime import date, timedelta
from django.utils import timezone

from documentos.models import Proyecto, Documento
from prediccion.models import Cotizacion, Producto
from prediccion.serializers import CotizacionSerializer
from usuarios.models import HistorialActividad
from prediccion.utils import obtener_precio_dolar, obtener_dolar_paralelo

import pandas as pd

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    user = request.user

    proyectos_activos = Proyecto.objects.filter(activo=True).count()
    documentos_total = Documento.objects.count()
    alertas = HistorialActividad.objects.filter(accion="RECHAZO").count()
    ultimas_cotizaciones = Cotizacion.objects.filter(usuario=user).order_by("-fecha")[:5]
    cotizaciones_data = [
        {
            "nombre": c.nombre,
            "presupuesto": f"${c.total_general:,.0f}",
            "estado": "Vigente",  # o "Vencida", si c.fecha_validez < hoy
            "color": "green"
        }
        for c in ultimas_cotizaciones
    ]

    # Producto aleatorio con datos CSV válidos
    productos_validos = Producto.objects.exclude(csv_datos='').filter(csv_datos__isnull=False)
    producto = choice(productos_validos) if productos_validos.exists() else None

    historial_data = []
    if producto and producto.csv_datos:
        try:
            df = pd.read_csv(producto.csv_datos.path)
            df = df.sort_values("fecha")
            if "precio_unitario_bob" in df.columns:
                historial_data = [
                    {"fecha": row["fecha"], "precio": row["precio_unitario_bob"]}
                    for _, row in df.iterrows()
                ]
        except Exception as e:
            historial_data = []

    return Response({
        "usuario": user.username,
        "proyectos_activos": proyectos_activos,
        "documentos": documentos_total,
        "presupuestos": ultimas_cotizaciones.count(),
        "precision_ia": "94.2%",  # Placeholder hasta enlazar IA real
        "alertas": alertas,
        "tendencia": "Positiva",
        "ultimas_cotizaciones": cotizaciones_data,
        "dolar": {
            "oficial": obtener_precio_dolar(),
            "paralelo": obtener_dolar_paralelo()
        },
        "grafico_producto": {
            "nombre": producto.nombre if producto else None,
            "historial": historial_data
        }
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cotizaciones_recientes(request):
    cotizaciones = Cotizacion.objects.filter(usuario=request.user).order_by('-fecha')[:5]
    data = [
        {
            "cliente": c.proyecto.nombre if c.proyecto else "Sin nombre",
            "presupuesto": f"${c.total_general:,.0f}",
            "precision": "98.2%",  # lógica futura
            "estado": "En progreso",  # lógica futura
            "color": "green"
        } for c in cotizaciones
    ]
    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cotizaciones_por_vencer(request):
    hoy = date.today()
    limite = hoy + timedelta(days=7)

    cotizaciones = Cotizacion.objects.filter(
        usuario=request.user,
        fecha_validez__range=(hoy, limite)
    ).values(
        "proyecto__nombre",
        "fecha_validez",
        "total_general"
    )

    return Response(list(cotizaciones))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monitoreo_materiales(request):
    productos_validos = Producto.objects.exclude(csv_datos='').filter(csv_datos__isnull=False)[:5]
    resultado = []

    for producto in productos_validos:
        try:
            df = pd.read_csv(producto.csv_datos.path)
            if "precio_unitario_bob" not in df.columns:
                continue

            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            precio_estimado = df["precio_unitario_bob"].iloc[-1]  # último precio
            resultado.append({
                "id": producto.id,
                "nombre": producto.nombre,
                "unidad_medida": producto.unidad_medida,
                "precio_estimado": precio_estimado,
            })
        except Exception:
            continue

    return Response(resultado)
