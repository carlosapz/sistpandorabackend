import logging
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.cache import cache  # Para limitar los intentos fallidos

logger = logging.getLogger(__name__)

# Número máximo de intentos fallidos permitidos
MAX_FAILED_ATTEMPTS = 5
BLOCK_TIME = 300  # Tiempo en segundos (5 minutos) antes de permitir nuevos intentos

class RegistroIntentosFallidosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

@receiver(user_login_failed)
def registrar_intento_fallido(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'desconocido')
    ip_address = request.META.get('REMOTE_ADDR')  # Obtener la IP de la solicitud
    logger.warning(f"Intento fallido de inicio de sesión para {username} desde IP {ip_address}")
    
    # Limitar intentos fallidos
    key = f"login_attempts_{username}"
    attempts = cache.get(key, 0)
    
    if attempts >= MAX_FAILED_ATTEMPTS:
        # Bloquear la cuenta por un tiempo si se superan los intentos
        cache.set(f"blocked_{username}", True, BLOCK_TIME)
        logger.warning(f"Cuenta bloqueada temporalmente por intentos fallidos: {username}")
    else:
        # Incrementar el contador de intentos fallidos
        cache.set(key, attempts + 1, BLOCK_TIME)
