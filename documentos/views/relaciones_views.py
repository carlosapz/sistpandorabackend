from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documentos.models import Proyecto, Categoria
from documentos.serializers import CategoriaSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categorias_por_proyecto(request, proyecto_id):
    """
    Retorna las categorías asociadas a un proyecto.
    """
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        categorias = proyecto.categorias.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asociar_categoria_a_proyecto(request, proyecto_id, categoria_id):
    """
    Asocia o elimina una categoría de un proyecto.
    Enviar { "remove": true } en el body para eliminar.
    """
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        categoria = Categoria.objects.get(pk=categoria_id)

        if request.data.get("remove"):
            proyecto.categorias.remove(categoria)
            return Response({"detalle": "Categoría eliminada del proyecto."})
        else:
            proyecto.categorias.add(categoria)
            return Response({"detalle": "Categoría asociada correctamente al proyecto."})

    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado."}, status=404)
    except Categoria.DoesNotExist:
        return Response({"error": "Categoría no encontrada."}, status=404)
