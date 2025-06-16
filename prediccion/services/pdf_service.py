import os
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from io import BytesIO
from django.utils import timezone
from django.http import HttpResponse
from prediccion.models.cotizacion import Cotizacion
import logging

logger = logging.getLogger(__name__)

def generar_pdf_cotizacion(usuario, cotizacion_id):
    """
    Genera el PDF de una cotización usando WeasyPrint.

    Args:
        usuario: instancia de usuario autenticado
        cotizacion_id: ID de la cotización

    Returns:
        HttpResponse con el PDF generado
    """
    cotizacion = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria').get(
        pk=cotizacion_id, usuario=usuario
    )

    productos = cotizacion.productos_cotizados.select_related('producto').all()

    # Renderizar HTML con contexto
    html_string = render_to_string("cotizacion_pdf.html", {
        "cotizacion": cotizacion,
        "productos": productos,
    })

    # Puedes agregar estilos CSS adicionales (opcional)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
    css = CSS(filename=css_path) if os.path.exists(css_path) else None

    # Convertir HTML a PDF en memoria (sin escribir a disco)
    pdf_io = BytesIO()
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    html.write_pdf(target=pdf_io, stylesheets=[css] if css else None)

    pdf_io.seek(0)

    # Retornar PDF como descarga
    response = HttpResponse(pdf_io, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.id}.pdf"'

    logger.info(f"✅ PDF generado con WeasyPrint para cotización {cotizacion.id}")

    return response


def generar_pdf_reporte(usuario, cotizacion_id):
    from prediccion.models.cotizacion_futura import CotizacionFutura

    cotizacion = Cotizacion.objects.select_related('usuario', 'proyecto', 'categoria').prefetch_related('productos_cotizados__producto', 'simulaciones_futuras').get(
        pk=cotizacion_id, usuario=usuario
    )

    productos = cotizacion.productos_cotizados.all()

    html_string = render_to_string("reporte_cotizacion_pdf.html", {
        "cotizacion": cotizacion,
        "productos": productos,
        "now": timezone.now()
    })

    pdf_io = BytesIO()
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    html.write_pdf(target=pdf_io)

    pdf_io.seek(0)
    response = HttpResponse(pdf_io, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{cotizacion.id}.pdf"'

    return response
