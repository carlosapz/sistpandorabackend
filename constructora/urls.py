# constructora/urls.py
from django.contrib import admin # type: ignore
from django.conf.urls.static import static # type: ignore
from django.conf import settings # type: ignore
from django.urls import path, include # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # type: ignore

from django.http import JsonResponse # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/documentos/', include('documentos.urls')),

    path("api/prediccion/", include("prediccion.urls")),

    path("api/dashboard/", include("dashboard.urls")),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', lambda request: JsonResponse({"message": "Backend Pandora "}))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)