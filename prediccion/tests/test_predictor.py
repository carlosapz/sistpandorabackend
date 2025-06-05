import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from prediccion.models.producto import Producto
from prediccion.services import predictor
from unittest import mock

@pytest.mark.django_db
def test_predecir_precio_actual_valido():
    # Crear archivo dummy .h5
    modelo_path = os.path.join(os.path.dirname(__file__), 'test_data', 'cemento_portland_precio_unitario_usd_dynamic.h5')
    with open(modelo_path, 'rb') as f:
        modelo_content = f.read()

    modelo_file = SimpleUploadedFile("cemento_portland_precio_unitario_usd_dynamic.h5", modelo_content)

    # Leer CSV desde test_data
    csv_path = os.path.join(os.path.dirname(__file__), 'test_data', 'cemento_portland.csv')
    with open(csv_path, 'rb') as f:
        csv_content = f.read()

    csv_file = SimpleUploadedFile("cemento_portland.csv", csv_content)

    # Crear producto de prueba
    producto = Producto.objects.create(
        nombre="Cemento Portland",
        unidad_medida="bolsa (50 kg)",
        modelo_lstm=modelo_file,
        csv_datos=csv_file,
        activo=True
    )

    # MOCK de load_model → devuelve un mock model que tiene .predict
    with mock.patch('prediccion.services.predictor.load_model') as mocked_load_model:
        mocked_model = mock.Mock()
        mocked_model.predict.return_value = [[10.0]]  # Precio dummy
        mocked_load_model.return_value = mocked_model

        # Llamar a la función de predicción
        precio = predictor.predecir_precio_actual(producto, "Oficial", 6.96)

        # Verificar resultado
        assert isinstance(precio, float)
        assert precio > 0
