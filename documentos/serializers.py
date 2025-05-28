from rest_framework import serializers
from .models import Proyecto, Obra, Categoria, Tag, Documento, VersionDocumento, Comentario, Notificacion, HistorialActividad
from django.core.exceptions import ValidationError
import os

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class ProyectoSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = ['id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'responsable', 'categorias']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nombre']

class DocumentoSerializer(serializers.ModelSerializer):
    proyecto = ProyectoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    usuario = serializers.ReadOnlyField(source='usuario.username')

    proyecto_id = serializers.PrimaryKeyRelatedField(queryset=Proyecto.objects.all(), source='proyecto', write_only=True, allow_null=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source='categoria', write_only=True, allow_null=True)
    tags_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', write_only=True, many=True, required=False)

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg']

    class Meta:
        model = Documento
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'archivo', 'fecha_creacion',
            'usuario', 'proyecto', 'categoria', 'tags', 'estado',
            'proyecto_id', 'categoria_id', 'tags_ids'
        ]
        read_only_fields = ['fecha_creacion', 'usuario', 'estado']

    def validate_archivo(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Tipo de archivo no permitido: {ext}. Solo se permiten: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError("El archivo excede el tamaño máximo permitido de 10 MB.")
        return value

    def validate(self, data):
        if not data.get('tags') and not data.get('proyecto'):
            raise serializers.ValidationError(
                "El documento debe estar asociado a un proyecto o tener al menos una etiqueta."
            )

        titulo = data.get('titulo') or (self.instance.titulo if self.instance else None)
        proyecto = data.get('proyecto') or (self.instance.proyecto if self.instance else None)

        if titulo and proyecto:
            qs = Documento.objects.filter(titulo=titulo, proyecto=proyecto)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Ya existe un documento con el título '{titulo}' en el proyecto '{proyecto.nombre}'. "
                    "Usa un nombre diferente o edita el documento existente."
                )
        return data

class VersionDocumentoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VersionDocumento
        fields = ['id', 'documento', 'archivo', 'fecha', 'usuario', 'activo']
        read_only_fields = ['fecha', 'usuario', 'activo']

class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Comentario
        fields = ['id', 'documento', 'usuario', 'contenido', 'fecha']
        read_only_fields = ['fecha', 'usuario']

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class HistorialActividadSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username')
    documento = serializers.CharField(source='documento.titulo')

    class Meta:
        model = HistorialActividad
        fields = ['id', 'usuario', 'documento', 'accion', 'fecha']

class DocumentoAprobarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['estado']

class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = '__all__'
