# prediccion/tests/test_api_predict.py
import os
import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from usuarios.models import Usuario  # Usa tu modelo de usuario personalizado
from prediccion.models import Producto

@pytest.mark.django_db
def test_api_predecir_precio():
    client = APIClient()

    # 🔐 Crear usuario y obtener token real
    user = Usuario.objects.create_user(username="testuser", password="12345678")
    
    # 🪙 Obtener token real vía login
    response_login = client.post("/api/token/", {
        "username": "testuser",
        "password": "12345678"
    }, format="json")

    assert response_login.status_code == 200, f"Error login: {response_login.content}"
    token = response_login.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # 📦 Cargar archivos desde test_data
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')

    with open(os.path.join(test_data_dir, 'cemento_portland_precio_unitario_usd_dynamic.h5'), 'rb') as f:
        modelo_content = f.read()
    modelo_file = SimpleUploadedFile("cemento_model.h5", modelo_content)

    with open(os.path.join(test_data_dir, 'cemento_portland.csv'), 'rb') as f:
        csv_content = f.read()
    csv_file = SimpleUploadedFile("cemento_portland.csv", csv_content)

    # 🛠 Crear producto
    producto = Producto.objects.create(
        nombre="Cemento Portland",
        unidad_medida="bolsa (50 kg)",
        modelo_lstm=modelo_file,
        csv_datos=csv_file,
        activo=True
    )

    # 🚀 Hacer POST a la API
    response = client.post("/api/prediccion/predecir/", {
        "producto_id": producto.id,
        "tipo_cambio_valor": 6.96,
        "tipo_cambio_origen": "Oficial"
    }, format="json")

    assert response.status_code == 200, f"Error: {response.status_code}, {response.content}"
