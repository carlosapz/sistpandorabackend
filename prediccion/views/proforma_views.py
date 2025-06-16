# prediccion/views/proforma_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from prediccion.models.proforma import Proforma
from prediccion.serializers.proforma_serializer import ProformaSerializer

# Crear una nueva Proforma
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_proforma(request):
    """
    Crea una nueva Proforma con los productos e ítems adicionales proporcionados.
    """
    productos_data = request.data.get('productos', [])
    items_adicionales_data = request.data.get('items_adicionales', [])

    # Crea una nueva Proforma
    proforma = Proforma.objects.create(cliente=request.data['cliente'])
    
    # Añadir productos e ítems adicionales a la proforma
    for producto in productos_data:
        proforma.productos.add(producto)
    for item in items_adicionales_data:
        proforma.items_adicionales.add(item)

    # Calcular el total estimado
    proforma.total_estimado = proforma.calcular_total()
    proforma.save()

    return Response({'message': 'Proforma creada correctamente', 'id': proforma.id})


# Obtener los detalles de una Proforma
class ProformaDetailView(generics.RetrieveAPIView):
    """
    Muestra los detalles de una proforma.
    """
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    permission_classes = [IsAuthenticated]


# Listar todas las Proformas
class ProformaListView(generics.ListAPIView):
    """
    Lista todas las proformas creadas.
    """
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    permission_classes = [IsAuthenticated]
