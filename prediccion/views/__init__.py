from .producto_views import ProductoListView, ProductoCreateView
from .cotizacion_views import (
    CotizacionCreateView, CotizacionListView, CotizacionDetailView,
    CotizacionRetrieveUpdateView, CotizacionRecalcularView,
    eliminar_cotizacion, descargar_cotizacion_pdf
)
from .prediccion_views import (
    PrecioPrediccionView, historico_predicciones_producto, historial_precios_producto
)
from .util_views import obtener_dolar_view, obtener_dolar_paralelo_view
from .test_tasks_views import lanzar_tarea_prediccion, lanzar_tarea_pdf