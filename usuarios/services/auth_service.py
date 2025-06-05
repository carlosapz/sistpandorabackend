from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def autenticar_usuario(username, password):
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    return None
