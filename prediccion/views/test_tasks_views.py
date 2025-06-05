# prediccion/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from prediccion.tasks import generate_cotizacion_pdf, predict_price_async

@api_view(["POST"])
def lanzar_tarea_pdf(request):
    cotizacion_id = request.data.get("cotizacion_id")
    task = generate_cotizacion_pdf.delay(cotizacion_id)
    return Response({"status": "Tarea enviada", "task_id": task.id})

@api_view(["POST"])
def lanzar_tarea_prediccion(request):
    producto_id = request.data.get("producto_id")
    task = predict_price_async.delay(producto_id)
    return Response({"status": "Tarea enviada", "task_id": task.id})
