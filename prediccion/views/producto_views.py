from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from prediccion.models.producto import Producto
from prediccion.serializers.producto_serializer import ProductoSerializer
from rest_framework.pagination import PageNumberPagination

class ProductoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductoListView(generics.ListAPIView):
    """
    Lista todos los productos activos.
    """
    queryset = Producto.objects.filter(activo=True).order_by('nombre')
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductoPagination

class ProductoCreateView(generics.CreateAPIView):
    """
    Permite crear un nuevo producto.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
