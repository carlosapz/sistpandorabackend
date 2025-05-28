# dashboard/urls.py

from django.urls import path
from .views import (
    cotizaciones_recientes,
    dashboard_resumen,
    cotizaciones_por_vencer,
    monitoreo_materiales,
)

urlpatterns = [
    path("cotizaciones/recientes/", cotizaciones_recientes, name="dashboard-cotizaciones-recientes"),
    path("resumen/", dashboard_resumen, name="dashboard-resumen"),
    path("cotizaciones/vencer/", cotizaciones_por_vencer, name="cotizaciones-por-vencer"),
    path("materiales/", monitoreo_materiales),
]

