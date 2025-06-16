from django.urls import path
from .views import (
    ProductoListView, ProductoCreateView,
    PrecioPrediccionView, HistoricoPrediccionesView, historial_precios_producto,
    CotizacionCreateView, CotizacionListView, CotizacionDetailView,
    CotizacionRetrieveUpdateView, CotizacionRecalcularView,
    eliminar_cotizacion, descargar_cotizacion_pdf,
    obtener_dolar_view, obtener_dolar_paralelo_view,
    lanzar_tarea_pdf, lanzar_tarea_prediccion,
    tipo_cambio_view, api_eliminar_prediccion_tipo_cambio,
    generar_cotizacion_futura, cotizacion_futura_views,
    CotizacionFuturaDetailView, api_guardar_dolar_diario,
    descargar_reporte_pdf, clonar_cotizacion,
    cotizaciones_por_obra, cotizaciones_por_categoria_y_proyecto,
)

from .views.proforma_views import crear_proforma, ProformaListView, ProformaDetailView


urlpatterns = [
    # === PRODUCTOS & PREDICCIÓN ===
    path('productos/', ProductoListView.as_view(), name='producto-list'),
    path('productos/crear/', ProductoCreateView.as_view(), name='producto-crear'),
    path('predecir/', PrecioPrediccionView.as_view(), name='precio-prediccion'),
    path('historico-predicciones/<int:producto_id>/', HistoricoPrediccionesView.as_view(), name='historico_predicciones'),
    path('historial/<int:producto_id>/', historial_precios_producto, name='historial-precios'),

    # === COTIZACIONES ===
    path('cotizaciones/', CotizacionListView.as_view(), name='cotizacion-list'),
    path('cotizaciones/crear/', CotizacionCreateView.as_view(), name='cotizacion-crear'),
    path('cotizaciones/<int:pk>/', CotizacionRetrieveUpdateView.as_view(), name='cotizacion-retrieve-update'),
    path('cotizaciones/<int:pk>/detalle/', CotizacionDetailView.as_view(), name='cotizacion-detalle'),
    path('cotizaciones/<int:pk>/eliminar/', eliminar_cotizacion, name='eliminar_cotizacion'),
    path('cotizaciones/<int:pk>/descargar/', descargar_cotizacion_pdf, name='cotizacion-descargar'),
    path("cotizaciones/<int:pk>/reporte/", descargar_reporte_pdf, name="descargar_reporte_pdf"),
    path('cotizaciones/<int:pk>/recalcular/', CotizacionRecalcularView.as_view(), name='cotizacion-recalcular'),
    path("cotizaciones/<int:pk>/clonar/", clonar_cotizacion, name="clonar_cotizacion"),
    path('cotizaciones/<int:cotizacion_id>/simular-futuro/', generar_cotizacion_futura, name='cotizacion-simular-futuro'),
    path("cotizaciones-futuras/<int:id>/comparar/", cotizacion_futura_views.comparar_cotizacion_futura, name="comparar_cotizacion_futura"),
    path("cotizaciones-futuras/", cotizacion_futura_views.listar_cotizaciones_futuras, name="listar_cotizaciones_futuras"),
    path("cotizaciones-futuras/<int:pk>/", CotizacionFuturaDetailView.as_view(), name="cotizaciones-futuras-detail"),
    path("cotizaciones-futuras/<int:pk>/eliminar/", cotizacion_futura_views.eliminar_cotizacion_futura, name="eliminar-cotizacion-futura"),

    path("cotizaciones/obra/<int:obra_id>/", cotizaciones_por_obra, name="cotizaciones-por-obra"),
    path("cotizaciones/proyecto/<int:proyecto_id>/categoria/<int:categoria_id>/", cotizaciones_por_categoria_y_proyecto, name="cotizaciones-por-categoria-proyecto"),

    path('proformas/', ProformaListView.as_view(), name='proforma-list'),  # Listar todas las proformas
    path('proformas/crear/', crear_proforma, name='crear-proforma'),  # Crear una nueva proforma
    path('proformas/<int:pk>/', ProformaDetailView.as_view(), name='proforma-detail'),  # Ver detalles de una proforma
    



    # === MONEDAS / TIPO DE CAMBIO ===
    path('dolar/', obtener_dolar_view, name='obtener_dolar'),
    path('dolar-paralelo/', obtener_dolar_paralelo_view, name='obtener_dolar_paralelo'),

    # === TIPO DE CAMBIO / PREDICCIÓN DE DÓLAR ===
    
    path('tipo-cambio/guardar-historico/', tipo_cambio_view.api_guardar_tipo_cambio_historico, name='guardar_tipo_cambio_historico'),
    path('tipo-cambio/predicciones/', tipo_cambio_view.api_listar_predicciones_tipo_cambio, name='listar_predicciones_tipo_cambio'),
    path('tipo-cambio/predicciones/generar/', tipo_cambio_view.api_generar_prediccion_tipo_cambio, name='generar_prediccion_tipo_cambio'),
    path('tipo-cambio/verificar-archivos/', tipo_cambio_view.api_verificar_archivos_modelo_csv, name='verificar_archivos_modelo_csv'),
    path('tipo-cambio/subir-archivos/', tipo_cambio_view.api_subir_archivos_modelo_csv, name='subir_archivos_modelo_csv'),
    path('tipo-cambio/historico/', tipo_cambio_view.api_historico_tipo_cambio, name='historico_tipo_cambio'),
    path('tipo-cambio/historico-ccv/', tipo_cambio_view.api_historico_tipo_cambio_ccv, name='historico_tipo_cambio_ccv'),
    path('tipo-cambio/predicciones/comparar/', tipo_cambio_view.api_comparar_predicciones_tipo_cambio, name='comparar_predicciones_tipo_cambio'),
    path("tipo-cambio/predicciones/<int:pk>/eliminar/", api_eliminar_prediccion_tipo_cambio, name="eliminar_prediccion_tipo_cambio"),

    path("registro-dolar/", api_guardar_dolar_diario, name="api_guardar_dolar_diario"),


    # === TESTS / CELERY ===
    path("test/pdf/", lanzar_tarea_pdf),
    path("test/predict/", lanzar_tarea_prediccion),
]
