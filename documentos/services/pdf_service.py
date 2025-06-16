from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from io import BytesIO
from documentos.models import Obra
from prediccion.models import Cotizacion

def generar_pdf_resumen_obra(obra_id):
    obra = Obra.objects.get(id=obra_id)
    cotizaciones = Cotizacion.objects.filter(
        obra=obra
    ).prefetch_related('productos_cotizados__producto', 'items_adicionales')

    total_cotizado = sum(float(c.total_general or 0) for c in cotizaciones)
    presupuesto_estimado = float(obra.presupuesto_estimado or 0)
    presupuesto_restante = presupuesto_estimado - total_cotizado
    porcentaje_uso = (total_cotizado / presupuesto_estimado * 100) if presupuesto_estimado else 0

    # Cálculos por cotización
    cotizaciones_contexto = []
    for cot in cotizaciones:
        subtotal = 0
        productos = []
        for p in cot.productos_cotizados.all():
            productos.append({
                "producto": p.producto,
                "cantidad": p.cantidad,
                "precio_unitario": float(p.precio_unitario),
                "total": float(p.total),
            })
            subtotal += float(p.total)

        items = []
        for i in cot.items_adicionales.all():
            items.append({
                "descripcion": i.descripcion,
                "unidad": i.unidad,
                "cantidad": i.cantidad,
                "precio_unitario": float(i.precio_unitario),
                "total": float(i.total),
            })
            subtotal += float(i.total)

        gastos_generales = float(cot.gastos_generales or 0)
        utilidad = float(cot.utilidad or 0)
        contingencia = float(cot.contingencia or 0)

        total_gastos = subtotal * gastos_generales / 100
        total_utilidad = subtotal * utilidad / 100
        total_contingencia = subtotal * contingencia / 100

        cotizaciones_contexto.append({
            "nombre": cot.nombre,
            "proyecto_nombre": cot.proyecto.nombre if cot.proyecto else "",
            "categoria_nombre": cot.categoria.nombre if cot.categoria else "",
            "fecha_validez": cot.fecha_validez,
            "tipo_cambio_origen": cot.tipo_cambio_origen,
            "tipo_cambio_valor": float(cot.tipo_cambio_valor or 0),
            "productos_cotizados": productos,
            "items_adicionales": items,
            "gastos_generales": gastos_generales,
            "utilidad": utilidad,
            "contingencia": contingencia,
            "subtotal": round(subtotal, 2),
            "total_gastos": round(total_gastos, 2),
            "total_utilidad": round(total_utilidad, 2),
            "total_contingencia": round(total_contingencia, 2),
            "total_general": float(cot.total_general or 0),
        })

    html = render_to_string("documentos/resumen_obra.html", {
        "obra": obra,
        "cotizaciones": cotizaciones_contexto,
        "total_cotizado": round(total_cotizado, 2),
        "presupuesto_estimado": round(presupuesto_estimado, 2),
        "presupuesto_restante": round(presupuesto_restante, 2),
        "porcentaje_uso": round(porcentaje_uso, 2),
    })

    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resumen_obra_{obra_id}.pdf"'
    return response
