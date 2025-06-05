import logging
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Parámetros configurables desde settings.py (poner valores por defecto)
MAX_FAILED_ATTEMPTS = getattr(settings, 'MAX_FAILED_ATTEMPTS', 5)
BLOCK_TIME = getattr(settings, 'BLOCK_TIME', 300)  # en segundos, default 5 minutos

class RegistroIntentosFallidosMiddleware:
    """
    Middleware para registrar y limitar intentos fallidos de inicio de sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Aquí podrías añadir lógica adicional si quieres
        return self.get_response(request)

@receiver(user_login_failed)
def registrar_intento_fallido(sender, credentials, request, **kwargs):
    """
    Señal que se activa cuando hay un intento fallido de login.
    Registra el intento y bloquea la cuenta temporalmente si se exceden los intentos permitidos.
    """
    username = credentials.get('username', 'desconocido')
    ip_address = get_client_ip(request)
    logger.warning(f"Intento fallido de inicio de sesión para {username} desde IP {ip_address}")

    # Verificar si usuario está bloqueado
    blocked_key = f"blocked_{username}"
    if cache.get(blocked_key):
        logger.warning(f"Intento de login bloqueado para usuario: {username}")
        return

    # Contar intentos
    attempts_key = f"login_attempts_{username}"
    attempts = cache.get(attempts_key, 0) + 1
    cache.set(attempts_key, attempts, BLOCK_TIME)

    if attempts >= MAX_FAILED_ATTEMPTS:
        cache.set(blocked_key, True, BLOCK_TIME)
        logger.warning(f"Usuario {username} bloqueado por demasiados intentos fallidos.")

def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
