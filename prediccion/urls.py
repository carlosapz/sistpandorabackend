from django.urls import path  # type: ignore
from .views import (
    ProductoListView,
    PrecioPrediccionView,
    historial_precios_producto,
    CotizacionCreateView,
    CotizacionListView,
    CotizacionDetailView,
    CotizacionRetrieveUpdateView,
    CotizacionRecalcularView,
    eliminar_cotizacion,
    descargar_cotizacion_pdf,
    obtener_dolar_view,
    obtener_dolar_paralelo_view,
    historico_predicciones_producto,
    ProductoCreateView,
)

urlpatterns = [
    # Rutas para Productos y Predicción
    path('productos/', ProductoListView.as_view(), name='producto-list'),
    path('productos/crear/', ProductoCreateView.as_view(), name='producto-crear'),
    path('predecir/', PrecioPrediccionView.as_view(), name='precio-prediccion'),
    
    # Ruta para Historial de Precios
    path("historial/<int:producto_id>/", historial_precios_producto, name="historial-precios"),
    
    # Rutas para Cotizaciones
    path('cotizaciones/', CotizacionListView.as_view(), name='cotizacion-list'),
    path('cotizaciones/crear/', CotizacionCreateView.as_view(), name='cotizacion-crear'),
    path('cotizaciones/<int:pk>/', CotizacionRetrieveUpdateView.as_view(), name='cotizacion-retrieve-update'),
    path('cotizaciones/<int:pk>/detalle/', CotizacionDetailView.as_view(), name='cotizacion-detalle'), 
    path('cotizaciones/<int:pk>/eliminar/', eliminar_cotizacion, name='eliminar_cotizacion'),
    path('cotizaciones/<int:pk>/descargar/', descargar_cotizacion_pdf, name='cotizacion-descargar'),
    path('cotizaciones/<int:pk>/recalcular/', CotizacionRecalcularView.as_view(), name='cotizacion-recalcular'),

    path('api/prediccion/cotizaciones/<int:pk>/recalcular/', CotizacionRecalcularView.as_view(), name='recalcular_cotizacion'),
    path("historico-predicciones/<int:producto_id>/", historico_predicciones_producto, name="historico_predicciones"),


    path("dolar/", obtener_dolar_view, name="obtener_dolar"),
    path("dolar-paralelo/", obtener_dolar_paralelo_view, name="obtener_dolar_paralelo"),

]
