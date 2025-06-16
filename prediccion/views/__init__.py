from .producto_views import ProductoListView, ProductoCreateView
from .cotizacion_views import (
    CotizacionCreateView, CotizacionListView, CotizacionDetailView,
    CotizacionRetrieveUpdateView, CotizacionRecalcularView,
    eliminar_cotizacion, descargar_cotizacion_pdf, descargar_reporte_pdf,
    clonar_cotizacion, cotizaciones_por_obra, cotizaciones_por_categoria_y_proyecto
)
from .prediccion_views import (
    PrecioPrediccionView, HistoricoPrediccionesView, historial_precios_producto
)
from .util_views import obtener_dolar_view, obtener_dolar_paralelo_view
from .test_tasks_views import lanzar_tarea_prediccion, lanzar_tarea_pdf
from .tipo_cambio_view import (
    api_guardar_tipo_cambio_historico, api_listar_predicciones_tipo_cambio
)
from .tipo_cambio_view import (
    api_generar_prediccion_tipo_cambio, api_historico_tipo_cambio, api_eliminar_prediccion_tipo_cambio
)
from .cotizacion_futura_views import generar_cotizacion_futura, comparar_cotizacion_futura, listar_cotizaciones_futuras, CotizacionFuturaDetailView
from .registro_dolar_view  import api_guardar_dolar_diario
from .proforma_views import crear_proforma, ProformaDetailView, ProformaListView