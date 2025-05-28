# documentos/filters.py
import django_filters
from .models import Documento, Tag

class DocumentoFilter(django_filters.FilterSet):
    fecha_creacion = django_filters.DateFromToRangeFilter(field_name="fecha_creacion", label='Rango de fecha')
    proyecto = django_filters.NumberFilter(field_name='proyecto__id')
    categoria = django_filters.NumberFilter(field_name='categoria__id')
    estado = django_filters.ChoiceFilter(choices=Documento.ESTADO_CHOICES, label='Estado')
    tipo = django_filters.CharFilter(field_name='tipo', lookup_expr='iexact', label='Tipo')
    prioridad = django_filters.CharFilter(field_name='prioridad', lookup_expr='iexact', label='Prioridad')
    usuario = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Usuario')
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), field_name='tags', label='Etiquetas')
    search = django_filters.CharFilter(field_name='titulo', lookup_expr='icontains', label='Buscar por título')

    class Meta:
        model = Documento
        fields = [
            'proyecto', 'categoria', 'estado',
            'tipo', 'prioridad', 'usuario', 'tags', 'fecha_creacion', 'search'
        ]
